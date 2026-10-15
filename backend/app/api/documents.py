
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.ingestion.document_loader import load_document
from app.retrieval.chunker import chunk_document
from app.retrieval.vector_store import VectorStore
from app.storage.database import DocumentDatabase

router = APIRouter(prefix="/api/documents", tags=["Documents"])

document_stores: dict[str, VectorStore] = {}
document_metadata: dict[str, dict] = {}

database = DocumentDatabase()

INDEX_DIRECTORY = Path(__file__).resolve().parents[2] / "data" / "indexes"


def index_path(document_id: str) -> Path:
    """Build a safe path for an application-generated document ID."""
    return INDEX_DIRECTORY / f"{document_id}.faiss"


def restore_saved_documents() -> None:
    """Restore saved indexes, rebuilding only when an index is missing."""
    INDEX_DIRECTORY.mkdir(parents=True, exist_ok=True)

    for metadata in database.list_documents():
        document_id = metadata["document_id"]
        chunks = database.load_chunks(document_id)

        if not chunks:
            raise RuntimeError(
                f"Saved document {document_id} has no stored chunks."
            )

        store = VectorStore(model_name=metadata["model_name"])
        saved_index = index_path(document_id)

        if saved_index.is_file():
            try:
                store.load_index(saved_index, chunks)
            except (ValueError, RuntimeError):
                # Recover from an incompatible or inconsistent index.
                store.restore_chunks(chunks)
                store.save_index(saved_index)
        else:
            store.restore_chunks(chunks)
            store.save_index(saved_index)

        document_stores[document_id] = store
        document_metadata[document_id] = {
            "filename": metadata["filename"],
            "extracted_units": metadata["extracted_units"],
            "chunks_created": metadata["chunks_created"],
        }


@asynccontextmanager
async def document_lifespan(app):
    """Load persisted documents before serving requests."""
    restore_saved_documents()
    yield


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or ""
    content = await file.read()

    try:
        units = load_document(filename, content)
        chunks = chunk_document(units)

        if not chunks:
            raise ValueError("No usable text chunks were created.")

        document_id = str(uuid4())
        store = VectorStore()
        store.add_chunks(chunks)

        INDEX_DIRECTORY.mkdir(parents=True, exist_ok=True)
        saved_index = index_path(document_id)

        # Persist the index before registering the document.
        store.save_index(saved_index)

        try:
            database.save_document(
                document_id=document_id,
                filename=filename,
                extracted_units=len(units),
                chunks=chunks,
                model_name=store.model_name,
            )
        except Exception:
            # Remove the index if the database transaction fails.
            saved_index.unlink(missing_ok=True)
            raise

        metadata = {
            "filename": filename,
            "extracted_units": len(units),
            "chunks_created": len(chunks),
        }

        document_stores[document_id] = store
        document_metadata[document_id] = metadata

        return {
            "message": "Document uploaded and indexed successfully.",
            "document_id": document_id,
            **metadata,
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="The document could not be indexed and saved.",
        ) from exc

    finally:
        await file.close()


@router.get("/")
def list_documents():
    return {"documents": database.list_documents()}

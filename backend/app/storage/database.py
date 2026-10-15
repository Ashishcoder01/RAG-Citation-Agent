
import sqlite3
from pathlib import Path

from app.retrieval.chunker import TextChunk


DATABASE_PATH = Path(__file__).resolve().parents[2] / "rag_citation_agent.db"


class DocumentDatabase:
    """Persist document metadata and extracted text chunks in SQLite."""

    def __init__(self, database_path: Path = DATABASE_PATH):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        """Create tables if they do not exist; preserve existing records."""
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    extracted_units INTEGER NOT NULL,
                    chunks_created INTEGER NOT NULL,
                    model_name TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    chunk_id TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    page_number INTEGER,
                    section_number INTEGER,
                    text TEXT NOT NULL,
                    FOREIGN KEY (document_id)
                        REFERENCES documents(document_id)
                        ON DELETE CASCADE,
                    UNIQUE (document_id, chunk_id)
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_document_chunks_document_id
                ON document_chunks(document_id)
                """
            )

    def save_document(
        self,
        document_id: str,
        filename: str,
        extracted_units: int,
        chunks: list[TextChunk],
        model_name: str,
    ) -> None:
        """Save document metadata and all chunks in one transaction."""
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    document_id,
                    filename,
                    extracted_units,
                    chunks_created,
                    model_name
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    filename,
                    extracted_units,
                    len(chunks),
                    model_name,
                ),
            )

            connection.executemany(
                """
                INSERT INTO document_chunks (
                    document_id,
                    chunk_id,
                    source_name,
                    page_number,
                    section_number,
                    text
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        document_id,
                        chunk.chunk_id,
                        chunk.source_name,
                        chunk.page_number,
                        chunk.section_number,
                        chunk.text,
                    )
                    for chunk in chunks
                ],
            )

    def list_documents(self) -> list[dict]:
        """Return saved document metadata."""
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    document_id,
                    filename,
                    extracted_units,
                    chunks_created,
                    model_name,
                    created_at
                FROM documents
                ORDER BY created_at DESC, document_id
                """
            ).fetchall()

            return [dict(row) for row in rows]

    def load_chunks(self, document_id: str) -> list[TextChunk]:
        """Load chunks with their original citation metadata."""
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    chunk_id,
                    source_name,
                    page_number,
                    section_number,
                    text
                FROM document_chunks
                WHERE document_id = ?
                ORDER BY id
                """,
                (document_id,),
            ).fetchall()

            return [
                TextChunk(
                    chunk_id=row["chunk_id"],
                    source_name=row["source_name"],
                    page_number=row["page_number"],
                    section_number=row["section_number"],
                    text=row["text"],
                )
                for row in rows
            ]

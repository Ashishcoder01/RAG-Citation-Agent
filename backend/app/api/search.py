
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.documents import document_stores

router = APIRouter(prefix="/api/search", tags=["Search"])


class SearchRequest(BaseModel):
    document_id: str = Field(min_length=1)
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResultItem(BaseModel):
    chunk_id: str
    source_name: str
    page_number: int | None
    section_number: int | None
    score: float
    text: str


class SearchResponse(BaseModel):
    document_id: str
    query: str
    results: list[SearchResultItem]


@router.post("/", response_model=SearchResponse)
def search_documents(request: SearchRequest):
    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query must not be empty.",
        )

    store = document_stores.get(request.document_id)

    if store is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found. Upload the document again or check its ID.",
        )

    try:
        matches = store.search(query, top_k=request.top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    results = [
        SearchResultItem(
            chunk_id=match.chunk.chunk_id,
            source_name=match.chunk.source_name,
            page_number=match.chunk.page_number,
            section_number=match.chunk.section_number,
            score=match.score,
            text=match.chunk.text,
        )
        for match in matches
    ]

    return SearchResponse(
        document_id=request.document_id,
        query=query,
        results=results,
    )

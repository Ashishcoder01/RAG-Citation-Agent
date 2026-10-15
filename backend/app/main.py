
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import (
    document_lifespan,
    router as documents_router,
)
from app.api.search import router as search_router
from app.api.answers import router as answers_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with document_lifespan(app):
        yield


app = FastAPI(
    title="RAG Citation Agent",
    description=(
        "A retrieval-augmented generation API with document ingestion, "
        "semantic search, and citation-validated answers."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "RAG Citation Agent API is running.",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "RAG Citation Agent",
    }


app.include_router(documents_router)
app.include_router(search_router)
app.include_router(answers_router)

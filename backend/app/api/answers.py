
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.answer_service import AnswerService
from app.api.documents import document_stores
from app.llm.groq_provider import GroqProvider
from app.llm.ollama_provider import OllamaProvider

# Load .env from the project root:
# RAG-Citation-Agent/.env
PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

router = APIRouter(prefix="/api/answers", tags=["Answers"])


def create_provider():
    """Select the LLM provider using the LLM_PROVIDER environment variable."""
    provider_name = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

    if provider_name == "groq":
        print("[LLM] Using Groq provider.")
        return GroqProvider()

    if provider_name == "ollama":
        print("[LLM] Using Ollama provider.")
        return OllamaProvider()

    raise ValueError(
        f"Unsupported LLM_PROVIDER '{provider_name}'. "
        "Choose 'groq' or 'ollama'."
    )


answer_service = AnswerService(
    provider=create_provider(),
    verify_claims=True,
)


class AnswerRequest(BaseModel):
    document_id: str = Field(min_length=1)
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


@router.post("/")
def generate_answer(request: AnswerRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question must not be empty.",
        )

    store = document_stores.get(request.document_id)

    if store is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found. Upload the document again or check its ID.",
        )

    try:
        search_results = store.search(
            question,
            top_k=request.top_k,
        )

        result = answer_service.answer(
            question=question,
            search_results=search_results,
        )

        return {
            "document_id": request.document_id,
            "question": result.question,
            "answer": result.answer,
            "citations_valid": result.citations_valid,
            "cited_evidence_ids": result.cited_evidence_ids,
            "invalid_citation_ids": result.invalid_citation_ids,
            "missing_citation": result.missing_citation,
            "claim_verifications": result.claim_verifications,
            "evidence": result.evidence,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        # Log the detailed error locally, but don't expose provider
        # details or credentials in the API response.
        print(f"[LLM ERROR] {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="The answer provider failed to generate a response.",
        ) from exc

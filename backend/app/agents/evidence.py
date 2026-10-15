
from dataclasses import dataclass

from app.retrieval.vector_store import SearchResult


@dataclass
class Evidence:
    evidence_id: str
    source_name: str
    page_number: int | None
    section_number: int | None
    text: str
    relevance_score: float


def build_evidence(
    results: list[SearchResult],
) -> list[Evidence]:
    evidence_items: list[Evidence] = []

    for index, result in enumerate(results, start=1):
        chunk = result.chunk

        evidence_items.append(
            Evidence(
                evidence_id=f"E{index}",
                source_name=chunk.source_name,
                page_number=chunk.page_number,
                section_number=chunk.section_number,
                text=chunk.text,
                relevance_score=result.score,
            )
        )

    return evidence_items


def format_evidence(evidence_items: list[Evidence]) -> str:
    """Format retrieved evidence for a future LLM prompt."""
    formatted_items = []

    for item in evidence_items:
        if item.page_number is not None:
            location = f"page {item.page_number}"
        elif item.section_number is not None:
            location = f"section {item.section_number}"
        else:
            location = "location unavailable"

        formatted_items.append(
            f"[{item.evidence_id}] "
            f"Source: {item.source_name}, {location}\n"
            f"Evidence: {item.text}"
        )

    return "\n\n".join(formatted_items)

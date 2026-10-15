
from dataclasses import dataclass

from app.ingestion.document_loader import DocumentUnit


@dataclass
class TextChunk:
    chunk_id: str
    source_name: str
    page_number: int | None
    section_number: int | None
    text: str


def chunk_document(
    units: list[DocumentUnit],
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[TextChunk]:
    """Split document units into overlapping character-based chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    chunks: list[TextChunk] = []
    step = chunk_size - overlap

    for unit_index, unit in enumerate(units):
        text = unit.text.strip()

        if not text:
            continue

        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    TextChunk(
                        chunk_id=f"doc{unit_index}_chunk{chunk_index}",
                        source_name=unit.source_name,
                        page_number=unit.page_number,
                        section_number=unit.section_number,
                        text=chunk_text,
                    )
                )
                chunk_index += 1

            if end == len(text):
                break

            start += step

    return chunks

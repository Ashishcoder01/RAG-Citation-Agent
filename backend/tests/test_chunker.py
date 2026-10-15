
import pytest

from app.ingestion.document_loader import DocumentUnit
from app.retrieval.chunker import chunk_document


def test_short_document_creates_one_chunk():
    unit = DocumentUnit(
        source_name="guide.pdf",
        page_number=1,
        section_number=None,
        text="This is a short document.",
    )

    chunks = chunk_document([unit])

    assert len(chunks) == 1
    assert chunks[0].source_name == "guide.pdf"
    assert chunks[0].page_number == 1
    assert chunks[0].text == "This is a short document."


def test_long_document_creates_overlapping_chunks():
    unit = DocumentUnit(
        source_name="guide.pdf",
        page_number=2,
        section_number=None,
        text="A" * 2500,
    )

    chunks = chunk_document([unit], chunk_size=1000, overlap=200)

    assert len(chunks) == 3
    assert chunks[0].text[-200:] == chunks[1].text[:200]
    assert all(chunk.page_number == 2 for chunk in chunks)


def test_invalid_chunk_settings_are_rejected():
    with pytest.raises(ValueError):
        chunk_document([], chunk_size=0)

    with pytest.raises(ValueError):
        chunk_document([], chunk_size=100, overlap=100)


def test_empty_units_are_skipped():
    unit = DocumentUnit(
        source_name="guide.pdf",
        page_number=1,
        section_number=None,
        text="   ",
    )

    assert chunk_document([unit]) == []

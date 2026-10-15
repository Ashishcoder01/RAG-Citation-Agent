
import pytest

from app.ingestion.document_loader import load_document


def test_rejects_unsupported_file_type():
    with pytest.raises(ValueError, match="Unsupported file type"):
        load_document("notes.txt", b"Hello world")


def test_rejects_empty_file():
    with pytest.raises(ValueError, match="empty"):
        load_document("notes.pdf", b"")


def test_rejects_oversized_file():
    content = b"x" * (20 * 1024 * 1024 + 1)

    with pytest.raises(ValueError, match="20 MB"):
        load_document("notes.pdf", content)


def test_extracts_pdf_page_numbers():
    import pymupdf

    pdf = pymupdf.open()
    page = pdf.new_page()
    page.insert_text((72, 72), "Citation grounding test")
    content = pdf.tobytes()
    pdf.close()

    units = load_document("sample.pdf", content)

    assert len(units) == 1
    assert units[0].source_name == "sample.pdf"
    assert units[0].page_number == 1
    assert "Citation grounding test" in units[0].text

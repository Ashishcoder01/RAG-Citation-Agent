
from app.agents.evidence import build_evidence, format_evidence
from app.retrieval.chunker import TextChunk
from app.retrieval.vector_store import SearchResult


def test_evidence_preserves_source_and_page():
    result = SearchResult(
        chunk=TextChunk(
            chunk_id="chunk1",
            source_name="report.pdf",
            page_number=4,
            section_number=None,
            text="The report contains a summary of the results.",
        ),
        score=0.82,
    )

    evidence = build_evidence([result])

    assert len(evidence) == 1
    assert evidence[0].evidence_id == "E1"
    assert evidence[0].source_name == "report.pdf"
    assert evidence[0].page_number == 4
    assert evidence[0].relevance_score == 0.82


def test_formatted_evidence_includes_citation_location():
    result = SearchResult(
        chunk=TextChunk(
            chunk_id="chunk1",
            source_name="report.pdf",
            page_number=4,
            section_number=None,
            text="The report contains a summary of the results.",
        ),
        score=0.82,
    )

    formatted = format_evidence(build_evidence([result]))

    assert "[E1]" in formatted
    assert "report.pdf" in formatted
    assert "page 4" in formatted
    assert "summary of the results" in formatted


def test_empty_evidence_formats_as_empty_string():
    assert format_evidence([]) == ""


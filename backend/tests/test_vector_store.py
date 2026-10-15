
from app.retrieval.chunker import TextChunk
from app.retrieval.vector_store import VectorStore


def test_search_returns_relevant_chunk_and_metadata():
    store = VectorStore()

    chunks = [
        TextChunk(
            chunk_id="chunk1",
            source_name="security.pdf",
            page_number=3,
            section_number=None,
            text=(
                "Multi-factor authentication improves account security "
                "by requiring multiple forms of verification."
            ),
        ),
        TextChunk(
            chunk_id="chunk2",
            source_name="cooking.pdf",
            page_number=1,
            section_number=None,
            text=(
                "Pasta is often cooked in boiling water until it becomes tender."
            ),
        ),
    ]

    store.add_chunks(chunks)
    results = store.search("How can I make account login more secure?", top_k=1)

    assert len(results) == 1
    assert results[0].chunk.chunk_id == "chunk1"
    assert results[0].chunk.source_name == "security.pdf"
    assert results[0].chunk.page_number == 3
    assert -1.0 <= results[0].score <= 1.0


def test_empty_index_returns_no_results():
    store = VectorStore()

    assert store.search("What is in the documents?") == []


def test_invalid_queries_are_rejected():
    store = VectorStore()

    try:
        store.search("   ")
        assert False, "Expected empty-query validation to fail"
    except ValueError:
        pass

    try:
        store.search("test", top_k=0)
        assert False, "Expected top_k validation to fail"
    except ValueError:
        pass

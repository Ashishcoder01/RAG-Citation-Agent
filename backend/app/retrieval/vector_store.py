
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.retrieval.chunker import TextChunk


DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass
class SearchResult:
    chunk: TextChunk
    score: float


class VectorStore:
    """Local semantic search using normalized embeddings and FAISS."""

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self._model: SentenceTransformer | None = None
        self._index: faiss.IndexFlatIP | None = None
        self._chunks: list[TextChunk] = []

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def add_chunks(self, chunks: list[TextChunk]) -> None:
        """Embed and index chunks while preserving their metadata."""
        if not chunks:
            return

        texts = [chunk.text for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        embeddings = np.asarray(embeddings, dtype=np.float32)

        if self._index is None:
            self._index = faiss.IndexFlatIP(embeddings.shape[1])
        elif self._index.d != embeddings.shape[1]:
            raise ValueError("Embedding dimensions do not match the index.")

        self._index.add(embeddings)
        self._chunks.extend(chunks)

    def restore_chunks(self, chunks: list[TextChunk]) -> None:
        """Rebuild the FAISS index from persisted chunks."""
        if self._chunks or self._index is not None:
            raise ValueError(
                "Cannot restore chunks into a non-empty vector store."
            )

        self.add_chunks(chunks)

    def save_index(self, path: str | Path) -> None:
        """Save the FAISS index to disk."""
        if self._index is None or not self._chunks:
            raise ValueError("Cannot save an empty vector store.")

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(destination))

    def load_index(
        self,
        path: str | Path,
        chunks: list[TextChunk],
    ) -> None:
        """Load a saved FAISS index and attach its persisted chunk metadata."""
        if self._index is not None or self._chunks:
            raise ValueError(
                "Cannot load an index into a non-empty vector store."
            )

        if not chunks:
            raise ValueError("Cannot load an index without saved chunks.")

        index_path = Path(path)
        if not index_path.is_file():
            raise FileNotFoundError("The saved FAISS index was not found.")

        index = faiss.read_index(str(index_path))

        if index.ntotal != len(chunks):
            raise ValueError(
                "FAISS index size does not match the saved chunk count."
            )

        expected_dimension = self.model.get_sentence_embedding_dimension()
        if index.d != expected_dimension:
            raise ValueError(
                "FAISS index dimensions do not match the embedding model."
            )

        self._index = index
        self._chunks = list(chunks)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Return the most similar indexed chunks, ranked by cosine similarity."""
        if not query.strip():
            raise ValueError("Query must not be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if self._index is None or not self._chunks:
            return []

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        query_embedding = np.asarray(query_embedding, dtype=np.float32)

        limit = min(top_k, len(self._chunks))
        scores, indices = self._index.search(query_embedding, limit)

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue

            results.append(
                SearchResult(
                    chunk=self._chunks[int(index)],
                    score=float(score),
                )
            )

        return results

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)

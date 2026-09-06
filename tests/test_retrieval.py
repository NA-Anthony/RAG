from langchain_core.documents import Document

import core.retrieval as retrieval
from core.vector_store import VectorStore


class FakeEmbeddings:
    def embed_query(self, _: str) -> list[float]:
        return [1.0, 0.0]


def test_semantic_search_returns_sources_without_llm(tmp_path, monkeypatch) -> None:
    store = VectorStore(tmp_path, "retrieval_collection")
    document = Document(
        page_content="Le mode sémantique ne contacte aucun LLM.",
        metadata={
            "chunk_id": "c1",
            "document_id": "d1",
            "source": "guide.md",
            "file_type": "Markdown",
            "file_hash": "h1",
            "size_bytes": 42,
            "chunk_index": 0,
        },
    )
    store.add_chunks([document], [[1.0, 0.0]])
    monkeypatch.setattr(retrieval, "get_embedding_model", lambda: FakeEmbeddings())

    results = retrieval.semantic_search(store, "Comment fonctionne le mode ?", max_distance=0.1)
    assert len(results) == 1
    assert results[0].relevance == "élevée"
    assert results[0].as_source()["source"] == "guide.md"


def test_empty_query_returns_no_result(tmp_path) -> None:
    assert retrieval.semantic_search(VectorStore(tmp_path, "empty_collection"), "") == []

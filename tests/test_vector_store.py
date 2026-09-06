from langchain_core.documents import Document

from core.vector_store import VectorStore


def make_document() -> Document:
    return Document(
        page_content="Paris est la capitale de la France.",
        metadata={
            "chunk_id": "chunk-1",
            "document_id": "doc-1",
            "source": "geo.txt",
            "file_type": "TXT",
            "file_hash": "hash-1",
            "size_bytes": 40,
            "chunk_index": 0,
        },
    )


def test_chroma_persists_lists_and_deletes(tmp_path) -> None:
    store = VectorStore(tmp_path, "test_collection")
    store.add_chunks([make_document()], [[1.0, 0.0]])
    assert store.count() == 1
    assert store.list_documents()[0].chunk_count == 1

    reopened = VectorStore(tmp_path, "test_collection")
    assert reopened.count() == 1
    reopened.delete_document("doc-1")
    assert reopened.count() == 0

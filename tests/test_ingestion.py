from core.document_loader import load_candidate
from core.file_validation import validate_file
import core.ingestion as ingestion
from core.text_splitter import split_documents
from core.vector_store import VectorStore


def test_document_to_persistent_chroma_pipeline(tmp_path, monkeypatch) -> None:
    candidate = validate_file("cours.txt", ("Contenu pédagogique local. " * 30).encode())
    chunks = split_documents(load_candidate(candidate), chunk_size=180, chunk_overlap=30)
    vectors = [[1.0, float(index)] for index, _ in enumerate(chunks)]
    store = VectorStore(tmp_path / "chroma", "integration_collection")
    monkeypatch.setattr(ingestion, "save_upload", lambda _: tmp_path / "cours.txt")

    report = ingestion.persist_ingestion(store, [candidate], chunks, vectors)
    assert report.document_count == 1
    assert report.chunk_count == len(chunks)
    assert VectorStore(tmp_path / "chroma", "integration_collection").count() == len(chunks)

    duplicate = ingestion.persist_ingestion(store, [candidate], chunks, vectors)
    assert duplicate.document_count == 0
    assert duplicate.chunk_count == 0

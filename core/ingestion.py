"""Orchestration de l'enregistrement d'un lot déjà validé."""

from __future__ import annotations

from dataclasses import dataclass

from langchain_core.documents import Document

from core.file_validation import FileCandidate
from core.vector_store import VectorStore, remove_saved_upload, save_upload


@dataclass(frozen=True)
class IngestionReport:
    document_count: int
    chunk_count: int


def persist_ingestion(
    store: VectorStore,
    candidates: list[FileCandidate],
    chunks: list[Document],
    embeddings: list[list[float]],
) -> IngestionReport:
    known = store.known_hashes()
    fresh_candidates = [candidate for candidate in candidates if candidate.file_hash not in known]
    fresh_ids = {candidate.document_id for candidate in fresh_candidates}
    fresh_pairs = [
        (chunk, vector)
        for chunk, vector in zip(chunks, embeddings, strict=True)
        if str(chunk.metadata["document_id"]) in fresh_ids
    ]
    fresh_chunks = [pair[0] for pair in fresh_pairs]
    fresh_embeddings = [pair[1] for pair in fresh_pairs]
    stored = store.add_chunks(fresh_chunks, fresh_embeddings)
    for candidate in fresh_candidates:
        save_upload(candidate)
    return IngestionReport(document_count=len(fresh_candidates), chunk_count=stored)


def delete_from_library(store: VectorStore, document_id: str) -> None:
    store.delete_document(document_id)
    remove_saved_upload(document_id)


def clear_library(store: VectorStore) -> None:
    document_ids = [document.document_id for document in store.list_documents()]
    store.clear()
    for document_id in document_ids:
        remove_saved_upload(document_id)

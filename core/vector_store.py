"""Stockage ChromaDB persistant, sans service ni API externe."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_core.documents import Document

from config.settings import settings
from core.file_validation import FileCandidate


@dataclass(frozen=True)
class LibraryDocument:
    document_id: str
    source: str
    file_type: str
    file_hash: str
    chunk_count: int
    size_bytes: int


class VectorStore:
    def __init__(
        self,
        persist_directory: str | Path | None = None,
        collection_name: str | None = None,
    ) -> None:
        self.persist_directory = Path(persist_directory or settings.chroma_dir)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name or settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        chunks: list[Document],
        embeddings: list[list[float]],
    ) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError("Chaque chunk doit posséder exactement un embedding.")
        if not chunks:
            return 0

        indexed_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []
        for chunk in chunks:
            metadata = {
                key: value
                for key, value in chunk.metadata.items()
                if value is not None and isinstance(value, (str, int, float, bool))
            }
            metadata["indexed_at"] = indexed_at
            ids.append(str(metadata["chunk_id"]))
            documents.append(chunk.page_content)
            metadatas.append(metadata)

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        return len(ids)

    def list_documents(self) -> list[LibraryDocument]:
        payload = self.collection.get(include=["metadatas"])
        metadatas = payload.get("metadatas") or []
        counts = Counter(str(metadata["document_id"]) for metadata in metadatas)
        first_by_id: dict[str, dict] = {}
        for metadata in metadatas:
            first_by_id.setdefault(str(metadata["document_id"]), metadata)

        return sorted(
            [
                LibraryDocument(
                    document_id=document_id,
                    source=str(metadata["source"]),
                    file_type=str(metadata["file_type"]),
                    file_hash=str(metadata["file_hash"]),
                    chunk_count=counts[document_id],
                    size_bytes=int(metadata.get("size_bytes", 0)),
                )
                for document_id, metadata in first_by_id.items()
            ],
            key=lambda item: item.source.casefold(),
        )

    def known_hashes(self) -> set[str]:
        return {document.file_hash for document in self.list_documents()}

    def count(self) -> int:
        return self.collection.count()

    def delete_document(self, document_id: str) -> None:
        self.collection.delete(where={"document_id": document_id})

    def clear(self) -> None:
        for document in self.list_documents():
            self.delete_document(document.document_id)


def save_upload(candidate: FileCandidate, uploads_dir: str | Path | None = None) -> Path:
    target_dir = Path(uploads_dir or settings.uploads_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{candidate.document_id}{candidate.extension}"
    target.write_bytes(candidate.data)
    return target


def remove_saved_upload(document_id: str, uploads_dir: str | Path | None = None) -> None:
    target_dir = Path(uploads_dir or settings.uploads_dir)
    for candidate in target_dir.glob(f"{document_id}.*"):
        if candidate.is_file():
            candidate.unlink()

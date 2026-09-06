"""Recherche sémantique pure : aucun modèle génératif n'est appelé ici."""

from __future__ import annotations

from dataclasses import dataclass

from config.settings import settings
from core.embeddings import get_embedding_model
from core.vector_store import VectorStore


@dataclass(frozen=True)
class SearchResult:
    content: str
    metadata: dict
    distance: float

    @property
    def relevance(self) -> str:
        if self.distance <= 0.35:
            return "élevée"
        if self.distance <= 0.65:
            return "moyenne"
        return "faible"

    def as_source(self) -> dict:
        return {
            "source": str(self.metadata["source"]),
            "content": self.content,
            "page": self.metadata.get("page"),
            "chunk_index": self.metadata.get("chunk_index"),
            "relevance": self.relevance,
        }


def semantic_search(
    store: VectorStore,
    question: str,
    *,
    k: int | None = None,
    max_distance: float | None = None,
) -> list[SearchResult]:
    clean_question = question.strip()
    if not clean_question or store.count() == 0:
        return []

    query_vector = get_embedding_model().embed_query(clean_question)
    payload = store.query(query_vector, k=k or settings.retrieval_k)
    documents = (payload.get("documents") or [[]])[0] or []
    metadatas = (payload.get("metadatas") or [[]])[0] or []
    distances = (payload.get("distances") or [[]])[0] or []
    threshold = settings.max_distance if max_distance is None else max_distance
    return [
        SearchResult(content=content, metadata=metadata, distance=float(distance))
        for content, metadata, distance in zip(documents, metadatas, distances, strict=True)
        if float(distance) <= threshold
    ]

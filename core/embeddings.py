"""Embeddings multilingues exécutés et mis en cache localement."""

from __future__ import annotations

from functools import lru_cache
import math
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings

from config.settings import settings


@lru_cache(maxsize=1)
def get_embedding_model(
    model_name: str | None = None,
    cache_folder: str | Path | None = None,
) -> HuggingFaceEmbeddings:
    """Charge une seule instance CPU et normalise ses vecteurs."""
    chosen_model = model_name or settings.embedding_model
    chosen_cache = Path(cache_folder or settings.model_cache_dir)
    chosen_cache.mkdir(parents=True, exist_ok=True)
    return HuggingFaceEmbeddings(
        model_name=chosen_model,
        cache_folder=str(chosen_cache),
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True, "show_progress_bar": False},
    )


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or not left:
        raise ValueError("Les deux vecteurs doivent avoir la même dimension non nulle.")
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


def embed_chunks(contents: list[str]) -> list[list[float]]:
    if not contents:
        return []
    return get_embedding_model().embed_documents(contents)

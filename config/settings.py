"""Réglages centralisés et surchargeables par variables d'environnement."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    app_name: str = "RAG Local"
    collection_name: str = "rag_local_documents"
    embedding_model: str = os.getenv(
        "RAG_EMBEDDING_MODEL",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )
    ollama_model: str = os.getenv("RAG_OLLAMA_MODEL", "qwen2.5:3b-instruct")
    ollama_base_url: str = os.getenv(
        "RAG_OLLAMA_BASE_URL", "http://127.0.0.1:11434"
    )
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "150"))
    retrieval_k: int = int(os.getenv("RAG_RETRIEVAL_K", "4"))
    max_file_size_mb: int = 25
    uploads_dir: Path = PROJECT_ROOT / "data" / "uploads"
    chroma_dir: Path = PROJECT_ROOT / "data" / "chroma_db"
    model_cache_dir: Path = PROJECT_ROOT / os.getenv("RAG_MODEL_CACHE", "data/models")
    styles_path: Path = PROJECT_ROOT / "assets" / "styles.css"


settings = Settings()

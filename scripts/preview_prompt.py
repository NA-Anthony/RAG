#!/usr/bin/env python3
"""Affiche un prompt RAG fictif pour contrôle pédagogique, sans appeler Ollama."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from core.prompt import build_rag_messages
from core.retrieval import SearchResult


def main() -> None:
    result = SearchResult(
        content="Le mode Recherche sémantique retourne les chunks sans appeler de LLM.",
        metadata={"source": "exemple.md", "page": 2, "chunk_index": 4},
        distance=0.2,
    )
    for message in build_rag_messages("Comment fonctionne la recherche ?", [result]):
        print(f"\n--- {message.type.upper()} ---\n{message.content}")


if __name__ == "__main__":
    main()

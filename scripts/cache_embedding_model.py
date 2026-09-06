#!/usr/bin/env python3
"""Télécharge l'embedding local et vérifie sa cohérence sémantique."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from core.embeddings import cosine_similarity, get_embedding_model


def main() -> int:
    model = get_embedding_model()
    sentences = [
        "Le document explique comment installer le logiciel.",
        "Ce guide décrit l'installation de l'application.",
        "Les baleines migrent dans les océans.",
    ]
    vectors = model.embed_documents(sentences)
    related = cosine_similarity(vectors[0], vectors[1])
    unrelated = cosine_similarity(vectors[0], vectors[2])
    print(f"Dimension : {len(vectors[0])}")
    print(f"Similarité liée : {related:.3f}")
    print(f"Similarité sans rapport : {unrelated:.3f}")
    if related <= unrelated:
        print("ERREUR : le contrôle de similarité a échoué.")
        return 1
    print("OK : modèle d'embeddings local prêt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

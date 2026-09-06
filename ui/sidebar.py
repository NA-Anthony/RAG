"""Barre latérale de l'application."""

from __future__ import annotations

import streamlit as st


def render_sidebar_mock() -> None:
    """Affiche le squelette visuel avant connexion à la logique métier."""
    with st.sidebar:
        st.title("RAG Local")
        st.caption("🟢 Traitement local et confidentiel")
        st.divider()
        st.subheader("Ajouter des documents")
        st.file_uploader(
            "PDF, TXT ou Markdown",
            type=["pdf", "txt", "md", "markdown"],
            accept_multiple_files=True,
            disabled=True,
        )
        st.button("Indexer les documents", type="primary", disabled=True, use_container_width=True)
        st.divider()
        st.subheader("Mode de réponse")
        st.toggle("Assistant RAG avec Ollama", value=False, disabled=True)
        st.caption("Mode actuel : Recherche sémantique")
        st.divider()
        st.subheader("Bibliothèque")
        st.info("Aucun document indexé.")

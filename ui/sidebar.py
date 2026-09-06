"""Barre latérale de l'application."""

from __future__ import annotations

import streamlit as st


from ui.states import reset_conversation


def render_sidebar() -> str:
    """Affiche les contrôles dont l'état survit aux réexécutions."""
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
        rag_enabled = st.toggle(
            "Assistant RAG avec Ollama",
            value=st.session_state.mode == "rag",
            key="rag_mode_toggle",
        )
        st.session_state.mode = "rag" if rag_enabled else "search"
        active_label = "Assistant RAG" if rag_enabled else "Recherche sémantique"
        st.caption(f"Mode actuel : {active_label}")
        st.button(
            "Nouvelle conversation",
            on_click=reset_conversation,
            use_container_width=True,
        )
        st.divider()
        st.subheader("Bibliothèque")
        st.info("Aucun document indexé.")
    return st.session_state.mode

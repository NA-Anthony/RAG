"""Barre latérale de l'application."""

from __future__ import annotations

import streamlit as st

from config.settings import settings
from core.file_validation import FileCandidate, human_size, validate_files
from ui.states import reset_conversation


def _show_candidate(candidate: FileCandidate) -> None:
    label = f"{candidate.name} · {candidate.file_type} · {human_size(candidate.size_bytes)}"
    if candidate.is_valid:
        st.success(label, icon="✅")
    elif candidate.status == "duplicate":
        st.warning(f"{label}\n\n{candidate.error}", icon="♻️")
    else:
        st.error(f"{label}\n\n{candidate.error}", icon="⚠️")


def render_sidebar(
    *, indexed_hashes: set[str] | None = None
) -> tuple[str, list[FileCandidate], bool]:
    """Affiche les contrôles et retourne les fichiers validés."""
    with st.sidebar:
        st.title("RAG Local")
        st.caption("🟢 Traitement local et confidentiel")
        st.divider()
        st.subheader("Ajouter des documents")
        uploaded_files = st.file_uploader(
            "PDF, TXT ou Markdown",
            type=["pdf", "txt", "md", "markdown"],
            accept_multiple_files=True,
        )
        candidates = validate_files(
            ((uploaded.name, uploaded.getvalue()) for uploaded in uploaded_files),
            indexed_hashes=indexed_hashes or set(),
            max_size_mb=settings.max_file_size_mb,
        )
        for candidate in candidates:
            _show_candidate(candidate)
        valid_candidates = [candidate for candidate in candidates if candidate.is_valid]
        st.session_state.selected_files = valid_candidates
        index_requested = st.button(
            "Indexer les documents",
            type="primary",
            disabled=not valid_candidates,
            use_container_width=True,
        )
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
    return st.session_state.mode, valid_candidates, index_requested

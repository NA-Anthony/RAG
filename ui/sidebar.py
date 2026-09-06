"""Barre latérale de l'application."""

from __future__ import annotations

import streamlit as st

from config.settings import settings
from core.file_validation import FileCandidate, human_size, validate_files
from core.vector_store import LibraryDocument
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
    *, library: list[LibraryDocument] | None = None
) -> tuple[str, list[FileCandidate], bool, dict | None]:
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
        documents = library or []
        candidates = validate_files(
            ((uploaded.name, uploaded.getvalue()) for uploaded in uploaded_files),
            indexed_hashes={document.file_hash for document in documents},
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
        action: dict | None = None
        if not documents:
            st.info("Aucun document indexé.")
        else:
            st.caption(
                f"{len(documents)} document(s) · "
                f"{sum(document.chunk_count for document in documents)} chunks"
            )
            for document in documents:
                st.markdown(f"**{document.source}**")
                st.caption(f"{document.file_type} · {document.chunk_count} chunks")
                left, right = st.columns(2)
                if left.button("Réindexer", key=f"reindex-{document.document_id}"):
                    action = {"type": "reindex", "document": document}
                if right.button("Supprimer", key=f"delete-{document.document_id}"):
                    st.session_state.confirm_delete_id = document.document_id
                if st.session_state.confirm_delete_id == document.document_id:
                    st.warning(f"Supprimer définitivement {document.source} ?")
                    confirm, cancel = st.columns(2)
                    if confirm.button("Confirmer", key=f"confirm-{document.document_id}"):
                        action = {"type": "delete", "document": document}
                        st.session_state.confirm_delete_id = ""
                    if cancel.button("Annuler", key=f"cancel-{document.document_id}"):
                        st.session_state.confirm_delete_id = ""
                        st.rerun()
            st.divider()
            if st.button("Vider toute la bibliothèque", use_container_width=True):
                st.session_state.confirm_clear = True
            if st.session_state.confirm_clear:
                st.error("Cette action supprimera tous les documents et chunks.")
                confirm, cancel = st.columns(2)
                if confirm.button("Tout supprimer", type="primary"):
                    action = {"type": "clear"}
                    st.session_state.confirm_clear = False
                if cancel.button("Conserver"):
                    st.session_state.confirm_clear = False
                    st.rerun()
    return st.session_state.mode, valid_candidates, index_requested, action

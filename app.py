"""Point d'entrée Streamlit du RAG local."""

from __future__ import annotations

import streamlit as st

from config.settings import settings
from core.document_loader import load_candidates
from ui.chat import handle_mock_question, render_history, render_welcome
from ui.sidebar import render_sidebar
from ui.states import init_session_state


st.set_page_config(
    page_title=settings.app_name,
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_styles() -> None:
    if settings.styles_path.exists():
        st.markdown(
            f"<style>{settings.styles_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


def main() -> None:
    load_styles()
    init_session_state()
    _, selected_files, index_requested = render_sidebar()
    if index_requested:
        with st.status("Extraction locale des documents…", expanded=True) as status:
            result = load_candidates(selected_files)
            st.write(f"{len(result.documents)} page(s) ou document(s) texte extrait(s).")
            st.session_state.extracted_documents = result.documents
            st.session_state.errors = result.errors
            st.session_state.indexing_status = "extracted" if result.documents else "failed"
            status.update(
                label="Extraction terminée" if result.documents else "Échec de l'extraction",
                state="complete" if result.documents else "error",
            )
        st.session_state.indexing_report = {
            "documents": len(selected_files),
            "message": "Texte extrait. Le découpage sera connecté à l'étape suivante.",
        }
    for error in st.session_state.errors:
        st.error(error)
    if st.session_state.indexing_status == "extracted":
        st.info(st.session_state.indexing_report["message"], icon="✅")
        with st.expander("Aperçu du texte extrait"):
            for document in st.session_state.extracted_documents[:5]:
                page = document.metadata.get("page")
                location = f" — page {page}" if page else ""
                st.markdown(f"**{document.metadata['source']}{location}**")
                preview = document.page_content[:1200]
                st.text(preview + ("…" if len(document.page_content) > 1200 else ""))
    if st.session_state.messages:
        render_history()
    else:
        render_welcome()
    handle_mock_question()


if __name__ == "__main__":
    main()

"""Point d'entrée Streamlit du RAG local."""

from __future__ import annotations

import streamlit as st

from config.settings import settings
from core.document_loader import load_candidates
from core.embeddings import embed_chunks
from core.ingestion import persist_ingestion
from core.text_splitter import split_documents
from core.vector_store import VectorStore
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


@st.cache_resource
def get_vector_store() -> VectorStore:
    return VectorStore()


def main() -> None:
    load_styles()
    init_session_state()
    store = get_vector_store()
    _, selected_files, index_requested = render_sidebar(indexed_hashes=store.known_hashes())
    if index_requested:
        with st.status("Extraction locale des documents…", expanded=True) as status:
            result = load_candidates(selected_files)
            st.write(f"{len(result.documents)} page(s) ou document(s) texte extrait(s).")
            st.session_state.extracted_documents = result.documents
            st.session_state.errors = result.errors
            if result.documents:
                st.write("Découpage en fragments avec conservation des sources…")
                st.session_state.chunks = split_documents(
                    result.documents,
                    chunk_size=settings.chunk_size,
                    chunk_overlap=settings.chunk_overlap,
                )
                st.write(f"{len(st.session_state.chunks)} chunk(s) créé(s).")
                st.write("Chargement du modèle local et création des embeddings…")
                st.session_state.chunk_embeddings = embed_chunks(
                    [chunk.page_content for chunk in st.session_state.chunks]
                )
                dimension = len(st.session_state.chunk_embeddings[0])
                st.write(f"{len(st.session_state.chunk_embeddings)} vecteur(s) de dimension {dimension} créé(s).")
                st.write("Enregistrement dans la base vectorielle persistante…")
                report = persist_ingestion(
                    store,
                    selected_files,
                    st.session_state.chunks,
                    st.session_state.chunk_embeddings,
                )
                st.session_state.indexing_report = {
                    "documents": report.document_count,
                    "chunks": report.chunk_count,
                    "message": (
                        f"{report.document_count} document(s) et {report.chunk_count} chunk(s) "
                        "indexés localement."
                    ),
                }
            st.session_state.indexing_status = "indexed" if result.documents else "failed"
            status.update(
                label="Extraction terminée" if result.documents else "Échec de l'extraction",
                state="complete" if result.documents else "error",
            )
    for error in st.session_state.errors:
        st.error(error)
    if st.session_state.indexing_status == "indexed":
        st.info(st.session_state.indexing_report["message"], icon="✅")
        with st.expander("Contrôler les premiers chunks"):
            for chunk in st.session_state.chunks[:5]:
                page = chunk.metadata.get("page")
                location = f" — page {page}" if page else ""
                index = chunk.metadata["chunk_index"]
                st.markdown(
                    f"**{chunk.metadata['source']}{location} — chunk {index} "
                    f"({len(chunk.page_content)} caractères)**"
                )
                st.text(chunk.page_content)
    if st.session_state.messages:
        render_history()
    else:
        render_welcome()
    handle_mock_question()


if __name__ == "__main__":
    main()

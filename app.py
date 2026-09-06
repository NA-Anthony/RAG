"""Point d'entrée Streamlit du RAG local."""

from __future__ import annotations

import streamlit as st

from config.settings import settings
from core.document_loader import load_candidates
from core.embeddings import embed_chunks
from core.ingestion import clear_library, delete_from_library, persist_ingestion
from core.text_splitter import split_documents
from core.vector_store import VectorStore, load_saved_upload
from ui.chat import handle_question, render_history, render_welcome
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


def run_indexing(
    store: VectorStore,
    selected_files: list,
    *,
    replace_document_ids: set[str] | None = None,
) -> None:
    with st.status("Indexation locale des documents…", expanded=True) as status:
        try:
            result = load_candidates(selected_files)
            st.write(f"{len(result.documents)} page(s) ou document(s) texte extrait(s).")
            st.session_state.extracted_documents = result.documents
            st.session_state.errors = list(result.errors)
            if not result.documents:
                raise ValueError("Aucun texte exploitable n'a pu être extrait.")
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
            st.write(
                f"{len(st.session_state.chunk_embeddings)} vecteur(s) de dimension {dimension} créé(s)."
            )
            for document_id in replace_document_ids or set():
                store.delete_document(document_id)
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
        except Exception as error:  # noqa: BLE001 - frontière UI
            st.session_state.indexing_status = "failed"
            message = f"Indexation interrompue : {error}"
            if message not in st.session_state.errors:
                st.session_state.errors.append(message)
            status.update(label="Échec de l'indexation", state="error")
            return
        st.session_state.indexing_status = "indexed"
        status.update(
            label="Indexation terminée",
            state="complete",
        )


def main() -> None:
    load_styles()
    init_session_state()
    store = get_vector_store()
    library = store.list_documents()
    _, selected_files, index_requested, library_action = render_sidebar(library=library)
    mode_label = "Assistant RAG · Ollama local" if st.session_state.mode == "rag" else "Recherche sémantique · sans LLM"
    st.caption(f"Mode actif : {mode_label}")
    if library_action:
        action_type = library_action["type"]
        if action_type == "delete":
            document = library_action["document"]
            delete_from_library(store, document.document_id)
            st.session_state.library_notice = f"{document.source} a été supprimé."
            st.session_state.messages = []
            st.session_state.indexing_status = "idle"
            st.session_state.chunks = []
            st.rerun()
        if action_type == "clear":
            clear_library(store)
            st.session_state.library_notice = "La bibliothèque a été vidée."
            st.session_state.messages = []
            st.session_state.indexing_status = "idle"
            st.session_state.chunks = []
            st.rerun()
        if action_type == "reindex":
            document = library_action["document"]
            try:
                candidate = load_saved_upload(document)
            except FileNotFoundError as error:
                st.error(str(error))
            else:
                run_indexing(store, [candidate], replace_document_ids={document.document_id})
                st.session_state.library_notice = f"{document.source} a été réindexé."
                st.rerun()
    if st.session_state.library_notice:
        st.success(st.session_state.library_notice)
        st.session_state.library_notice = ""
    if index_requested:
        run_indexing(store, selected_files)
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
        render_welcome(len(library))
    handle_question(store)


if __name__ == "__main__":
    main()

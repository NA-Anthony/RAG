"""Écrans d'accueil et de conversation."""

from __future__ import annotations

import streamlit as st

from core.retrieval import semantic_search
from core.rag import OllamaUnavailableError, stream_rag_answer
from core.vector_store import VectorStore
from ui.sources import render_sources
from ui.states import add_message


def render_welcome(document_count: int = 0) -> None:
    st.markdown('<span class="rag-eyebrow">100 % local</span>', unsafe_allow_html=True)
    title = (
        "Votre bibliothèque locale est prête à répondre."
        if document_count
        else "Interrogez vos documents sans les envoyer ailleurs."
    )
    st.markdown(f'<h1 class="rag-hero">{title}</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="rag-subtitle">'
        + (
            f"{document_count} document(s) disponible(s). Posez une question ou ajoutez d'autres sources."
            if document_count
            else "Ajoutez vos sources, indexez-les, puis choisissez entre les extraits bruts et une réponse rédigée par Ollama."
        )
        + "</p>",
        unsafe_allow_html=True,
    )

    columns = st.columns(3)
    steps = [
        ("1", "Ajoutez", "Importez des documents PDF, TXT ou Markdown."),
        ("2", "Indexez", "Créez localement les chunks et leurs embeddings."),
        ("3", "Questionnez", "Obtenez une réponse accompagnée de ses sources."),
    ]
    for column, (number, title, description) in zip(columns, steps, strict=True):
        with column:
            st.markdown(
                '<div class="rag-step">'
                f'<div class="rag-step-number">{number}</div>'
                f"<strong>{title}</strong><p>{description}</p>"
                "</div>",
                unsafe_allow_html=True,
            )


def render_history() -> None:
    """Réaffiche l'historique conservé dans la session."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            sources = message.get("sources", [])
            render_sources(sources, collapsed=message.get("mode") == "rag")


def handle_question(store: VectorStore) -> None:
    """Répond dans le mode actif ; la recherche pure reste sans LLM."""
    empty_library = store.count() == 0
    question = st.chat_input(
        "Posez une question sur vos documents",
        disabled=empty_library,
    )
    if not question:
        return
    add_message("user", question)
    if st.session_state.mode == "rag":
        with st.spinner("Recherche des extraits pertinents…"):
            results = semantic_search(store, question)
        if not results:
            add_message(
                "assistant",
                "Les documents fournis ne permettent pas de répondre.",
            )
        else:
            try:
                with st.chat_message("assistant"):
                    response = st.write_stream(stream_rag_answer(question, results))
            except OllamaUnavailableError as error:
                add_message("assistant", str(error))
            else:
                add_message(
                    "assistant",
                    response,
                    sources=[result.as_source() for result in results],
                    mode="rag",
                )
    else:
        with st.spinner("Recherche sémantique locale…"):
            results = semantic_search(store, question)
        if results:
            add_message(
                "assistant",
                f"{len(results)} passage(s) pertinent(s) trouvé(s), sans génération de texte.",
                sources=[result.as_source() for result in results],
                mode="search",
            )
        else:
            add_message(
                "assistant",
                "Aucun passage suffisamment pertinent n'a été trouvé dans la bibliothèque.",
            )
    st.rerun()

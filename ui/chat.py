"""Écrans d'accueil et de conversation."""

from __future__ import annotations

import streamlit as st

from core.retrieval import semantic_search
from core.vector_store import VectorStore
from ui.sources import render_mock_sources, render_source
from ui.states import add_message


def render_welcome() -> None:
    st.markdown('<span class="rag-eyebrow">100 % local</span>', unsafe_allow_html=True)
    st.markdown(
        '<h1 class="rag-hero">Interrogez vos documents sans les envoyer ailleurs.</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="rag-subtitle">Ajoutez vos sources, indexez-les, puis choisissez '
        "entre les extraits bruts et une réponse rédigée par Ollama.</p>",
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


def render_mock_conversation() -> None:
    st.divider()
    st.caption("Aperçu de la conversation finale avec données fictives")
    with st.chat_message("user"):
        st.write("Quels sont les objectifs principaux du projet ?")
    with st.chat_message("assistant"):
        st.write(
            "Le projet vise à indexer les documents localement et à rendre chaque "
            "réponse vérifiable grâce aux extraits d'origine."
        )
        render_mock_sources()


def render_history() -> None:
    """Réaffiche l'historique conservé dans la session."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            for source in message.get("sources", []):
                render_source(**source)


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
        add_message(
            "assistant",
            "Le mode RAG sera connecté à Ollama dans une prochaine étape. Passez en Recherche sémantique pour consulter les extraits.",
        )
    else:
        results = semantic_search(store, question)
        if results:
            add_message(
                "assistant",
                f"{len(results)} passage(s) pertinent(s) trouvé(s), sans génération de texte.",
                sources=[result.as_source() for result in results],
            )
        else:
            add_message(
                "assistant",
                "Aucun passage suffisamment pertinent n'a été trouvé dans la bibliothèque.",
            )
    st.rerun()

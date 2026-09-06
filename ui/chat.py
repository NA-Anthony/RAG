"""Écrans d'accueil et de conversation."""

from __future__ import annotations

import streamlit as st

from ui.sources import render_mock_sources


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

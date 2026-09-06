"""Présentation des preuves documentaires."""

from __future__ import annotations

import html
import streamlit as st


def render_mock_sources() -> None:
    """Affiche des sources fictives pour valider le design."""
    with st.expander("Voir les 2 sources fictives"):
        render_source(
            "guide-projet.pdf",
            "Le projet indexe les documents localement et conserve chaque source.",
            page=3,
            chunk_index=4,
            relevance="élevée",
        )
        render_source(
            "notes.md",
            "La recherche sémantique fonctionne sans appeler le modèle génératif.",
            chunk_index=2,
            relevance="moyenne",
        )


def render_source(
    source: str,
    content: str,
    *,
    page: int | None = None,
    chunk_index: int | None = None,
    relevance: str | None = None,
    number: int | None = None,
) -> None:
    location = f" · page {page}" if page else ""
    chunk = f"chunk {chunk_index}" if chunk_index is not None else ""
    score = f"pertinence {relevance}" if relevance else ""
    details = " · ".join(part for part in (chunk, score) if part)
    citation = f"[Source {number}] · " if number is not None else ""
    st.markdown(
        '<div class="rag-source">'
        f"<strong>{citation}{html.escape(source)}{location}</strong>"
        f"<p>{html.escape(content)}</p>"
        f'<span class="rag-meta">{details}</span>'
        "</div>",
        unsafe_allow_html=True,
    )


def unique_sources(sources: list[dict]) -> list[dict]:
    """Déduplique sans modifier l'ordre de pertinence."""
    seen: set[tuple] = set()
    unique: list[dict] = []
    for source in sources:
        key = (
            source.get("source"),
            source.get("page"),
            source.get("chunk_index"),
        )
        if key not in seen:
            seen.add(key)
            unique.append(source)
    return unique


def render_sources(sources: list[dict], *, collapsed: bool) -> None:
    cleaned = unique_sources(sources)
    if not cleaned:
        return

    def content() -> None:
        for number, source in enumerate(cleaned, start=1):
            render_source(**source, number=number)

    if collapsed:
        with st.expander(f"Voir les {len(cleaned)} source(s) utilisée(s)"):
            content()
    else:
        content()

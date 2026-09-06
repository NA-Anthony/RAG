"""État de session centralisé pour résister aux réexécutions Streamlit."""

from __future__ import annotations

from typing import Any

import streamlit as st


DEFAULT_STATE: dict[str, Any] = {
    "messages": None,
    "mode": "search",
    "selected_files": None,
    "extracted_documents": None,
    "chunks": None,
    "chunk_embeddings": None,
    "indexed_documents": None,
    "indexing_status": "idle",
    "indexing_report": None,
    "errors": None,
}


def init_session_state() -> None:
    """Initialise chaque clé une seule fois."""
    for key, default in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = [] if default is None else default


def reset_conversation() -> None:
    st.session_state.messages = []


def add_message(
    role: str,
    content: str,
    *,
    sources: list[dict] | None = None,
    mode: str | None = None,
) -> None:
    st.session_state.messages.append(
        {
            "role": role,
            "content": content,
            "sources": sources or [],
            "mode": mode,
        }
    )

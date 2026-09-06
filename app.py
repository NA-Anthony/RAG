"""Point d'entrée Streamlit du RAG local."""

from __future__ import annotations

import streamlit as st

from config.settings import settings
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
    render_sidebar()
    if st.session_state.messages:
        render_history()
    else:
        render_welcome()
    handle_mock_question()


if __name__ == "__main__":
    main()

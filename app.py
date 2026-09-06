"""Point d'entrée Streamlit du RAG local."""

from __future__ import annotations

import streamlit as st

from config.settings import settings
from ui.chat import render_mock_conversation, render_welcome
from ui.sidebar import render_sidebar_mock


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
    render_sidebar_mock()
    render_welcome()
    render_mock_conversation()
    st.chat_input("Indexez un document pour poser une question", disabled=True)


if __name__ == "__main__":
    main()

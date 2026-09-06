from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_empty_application_renders_without_exception() -> None:
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py")
    app.run(timeout=20)
    assert not app.exception
    assert app.chat_input[0].disabled

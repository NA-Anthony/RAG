from types import SimpleNamespace

import core.rag as rag
from core.retrieval import SearchResult


class FakeChatModel:
    def stream(self, _messages):
        yield SimpleNamespace(content="Réponse ")
        yield SimpleNamespace(content="locale [Source 1].")


def test_rag_streams_model_response(monkeypatch) -> None:
    monkeypatch.setattr(rag, "ensure_ollama_ready", lambda: None)
    monkeypatch.setattr(rag, "get_chat_model", lambda: FakeChatModel())
    source = SearchResult("Contexte", {"source": "a.txt", "chunk_index": 0}, 0.1)
    assert "".join(rag.stream_rag_answer("Question", [source])) == "Réponse locale [Source 1]."


def test_rag_refuses_without_context() -> None:
    assert "".join(rag.stream_rag_answer("Question", [])) == (
        "Les documents fournis ne permettent pas de répondre."
    )

"""Génération locale fondée exclusivement sur les résultats récupérés."""

from __future__ import annotations

from functools import lru_cache
import json
from typing import Iterator
from urllib.error import URLError
from urllib.request import Request, urlopen

from langchain_ollama import ChatOllama

from config.settings import settings
from core.prompt import build_rag_messages
from core.retrieval import SearchResult


class OllamaUnavailableError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_chat_model() -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0,
        num_ctx=4096,
    )


def installed_ollama_models() -> list[str]:
    request = Request(f"{settings.ollama_base_url}/api/tags", method="GET")
    try:
        with urlopen(request, timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise OllamaUnavailableError(
            "Ollama ne répond pas. Démarrez-le avec `scripts/ollama-local.sh serve`."
        ) from error
    return [str(model.get("name", "")) for model in payload.get("models", [])]


def ensure_ollama_ready() -> None:
    models = installed_ollama_models()
    if settings.ollama_model not in models:
        raise OllamaUnavailableError(
            f"Le modèle `{settings.ollama_model}` est absent. Installez-le avec "
            f"`scripts/ollama-local.sh pull {settings.ollama_model}`."
        )


def _text_content(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "".join(parts)
    return str(content or "")


def stream_rag_answer(question: str, results: list[SearchResult]) -> Iterator[str]:
    if not results:
        yield "Les documents fournis ne permettent pas de répondre."
        return
    ensure_ollama_ready()
    produced = False
    try:
        for chunk in get_chat_model().stream(build_rag_messages(question, results)):
            text = _text_content(chunk.content)
            if text:
                produced = True
                yield text
    except OllamaUnavailableError:
        raise
    except Exception as error:
        raise OllamaUnavailableError(f"La génération locale a échoué : {error}") from error
    if not produced:
        raise OllamaUnavailableError("Ollama a renvoyé une réponse vide.")

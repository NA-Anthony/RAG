#!/usr/bin/env python3
"""Vérifie l'environnement local nécessaire au projet RAG."""

from __future__ import annotations

import argparse
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.error import URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "qwen2.5:3b-instruct"
REQUIRED_IMPORTS = {
    "streamlit": "Streamlit",
    "langchain": "LangChain",
    "langchain_community": "LangChain Community",
    "langchain_text_splitters": "LangChain Text Splitters",
    "langchain_chroma": "LangChain Chroma",
    "langchain_huggingface": "LangChain Hugging Face",
    "langchain_ollama": "LangChain Ollama",
    "chromadb": "ChromaDB",
    "sentence_transformers": "Sentence Transformers",
    "fitz": "PyMuPDF",
}


def print_result(ok: bool, label: str, detail: str = "") -> None:
    marker = "OK" if ok else "ERREUR"
    suffix = f" - {detail}" if detail else ""
    print(f"[{marker}] {label}{suffix}")


def find_ollama() -> Path | None:
    configured = os.environ.get("OLLAMA_BINARY")
    candidates = [
        Path(configured) if configured else None,
        Path(PROJECT_ROOT / ".tools/ollama/bin/ollama"),
    ]
    system_binary = shutil.which("ollama")
    if system_binary:
        candidates.append(Path(system_binary))

    for candidate in candidates:
        if candidate and candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def read_ollama_tags() -> dict:
    request = Request("http://127.0.0.1:11434/api/tags", method="GET")
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def generate_test_response(model: str) -> str:
    payload = json.dumps(
        {
            "model": model,
            "prompt": "Réponds exactement par : environnement local prêt",
            "stream": False,
            "options": {"temperature": 0},
        }
    ).encode("utf-8")
    request = Request(
        "http://127.0.0.1:11434/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=180) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data.get("response", "")).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--test-generation",
        action="store_true",
        help="Envoie aussi une courte requête au modèle local.",
    )
    args = parser.parse_args()

    failed = False
    supported_python = sys.version_info[:2] == (3, 12)
    print_result(
        supported_python,
        "Python 3.12",
        f"version active : {sys.version.split()[0]}",
    )
    failed |= not supported_python

    in_project_venv = Path(sys.prefix).resolve() == (PROJECT_ROOT / ".venv").resolve()
    print_result(in_project_venv, "Environnement virtuel du projet", sys.prefix)
    failed |= not in_project_venv

    for import_name, label in REQUIRED_IMPORTS.items():
        try:
            importlib.import_module(import_name)
        except Exception as error:  # noqa: BLE001 - diagnostic exhaustif voulu
            print_result(False, f"Import {label}", str(error))
            failed = True
        else:
            print_result(True, f"Import {label}")

    ollama_binary = find_ollama()
    if ollama_binary is None:
        print_result(False, "Binaire Ollama", "introuvable")
        return 1

    version = subprocess.run(
        [str(ollama_binary), "--version"],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    version_text = (version.stdout or version.stderr).strip()
    print_result(version.returncode == 0, "Binaire Ollama", version_text)
    failed |= version.returncode != 0

    try:
        tags = read_ollama_tags()
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        print_result(False, "Service Ollama", str(error))
        print("Démarrez-le avec : scripts/ollama-local.sh serve")
        return 1

    print_result(True, "Service Ollama", "http://127.0.0.1:11434")
    model_names = [item.get("name", "") for item in tags.get("models", [])]
    model_available = args.model in model_names or any(
        name.startswith(f"{args.model}:") for name in model_names
    )
    print_result(
        model_available,
        f"Modèle {args.model}",
        ", ".join(model_names) if model_names else "aucun modèle installé",
    )
    failed |= not model_available

    if args.test_generation and model_available:
        try:
            response = generate_test_response(args.model)
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            print_result(False, "Génération Ollama", str(error))
            failed = True
        else:
            print_result(bool(response), "Génération Ollama", response)
            failed |= not bool(response)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

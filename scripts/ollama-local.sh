#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
OLLAMA_BIN="${OLLAMA_BINARY:-${PROJECT_ROOT}/.tools/ollama/bin/ollama}"
OLLAMA_MODELS_DIR="${OLLAMA_MODELS:-${PROJECT_ROOT}/data/ollama_models}"

if [[ ! -x "${OLLAMA_BIN}" ]]; then
    echo "Ollama local est introuvable : ${OLLAMA_BIN}" >&2
    echo "Lancez d'abord scripts/install_ollama_local.sh." >&2
    exit 1
fi

mkdir -p "${OLLAMA_MODELS_DIR}"
export OLLAMA_MODELS="${OLLAMA_MODELS_DIR}"

exec "${OLLAMA_BIN}" "$@"

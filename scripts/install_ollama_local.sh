#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
TOOLS_DIR="${PROJECT_ROOT}/.tools"
INSTALL_DIR="${TOOLS_DIR}/ollama"
DOWNLOAD_URL="https://ollama.com/download/ollama-linux-amd64.tar.zst"

if [[ "$(uname -s)" != "Linux" || "$(uname -m)" != "x86_64" ]]; then
    echo "Ce script local cible uniquement Linux x86_64." >&2
    exit 1
fi

for command_name in curl zstd tar; do
    if ! command -v "${command_name}" >/dev/null 2>&1; then
        echo "Commande requise absente : ${command_name}" >&2
        exit 1
    fi
done

if [[ -x "${INSTALL_DIR}/bin/ollama" ]]; then
    echo "Ollama est déjà installé dans ${INSTALL_DIR}."
    "${INSTALL_DIR}/bin/ollama" --version
    exit 0
fi

mkdir -p "${TOOLS_DIR}"
STAGING_DIR="$(mktemp -d "${TOOLS_DIR}/ollama-stage.XXXXXX")"
ARCHIVE_PATH="${STAGING_DIR}/ollama-linux-amd64.tar.zst"
cleanup() {
    rm -rf -- "${STAGING_DIR}"
}
trap cleanup EXIT

echo "Téléchargement d'Ollama depuis la distribution officielle..."
curl --fail --location --progress-bar --continue-at - \
    --output "${ARCHIVE_PATH}" "${DOWNLOAD_URL}"

echo "Extraction locale dans ${INSTALL_DIR}..."
mkdir -p "${STAGING_DIR}/extracted"
tar --zstd -xf "${ARCHIVE_PATH}" -C "${STAGING_DIR}/extracted"
mv "${STAGING_DIR}/extracted" "${INSTALL_DIR}"

echo "Ollama local installé."
"${INSTALL_DIR}/bin/ollama" --version

"""Validation pure des fichiers avant extraction ou indexation."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Iterable


ALLOWED_EXTENSIONS = {
    ".pdf": "PDF",
    ".txt": "TXT",
    ".md": "Markdown",
    ".markdown": "Markdown",
}


@dataclass(frozen=True)
class FileCandidate:
    name: str
    data: bytes
    extension: str
    file_type: str
    size_bytes: int
    file_hash: str
    status: str
    error: str | None = None

    @property
    def is_valid(self) -> bool:
        return self.status == "accepted"

    @property
    def document_id(self) -> str:
        return self.file_hash[:24]


def validate_file(
    name: str,
    data: bytes,
    *,
    known_hashes: Iterable[str] = (),
    max_size_mb: int = 25,
) -> FileCandidate:
    safe_name = Path(name).name.strip() or "document_sans_nom"
    extension = Path(safe_name).suffix.lower()
    file_type = ALLOWED_EXTENSIONS.get(extension, "Inconnu")
    file_hash = hashlib.sha256(data).hexdigest()
    base = dict(
        name=safe_name,
        data=data,
        extension=extension,
        file_type=file_type,
        size_bytes=len(data),
        file_hash=file_hash,
    )

    if extension not in ALLOWED_EXTENSIONS:
        return FileCandidate(
            **base,
            status="rejected",
            error="Format non autorisé. Utilisez PDF, TXT ou Markdown.",
        )
    if not data:
        return FileCandidate(**base, status="rejected", error="Le fichier est vide.")
    if len(data) > max_size_mb * 1024 * 1024:
        return FileCandidate(
            **base,
            status="rejected",
            error=f"Le fichier dépasse la limite de {max_size_mb} Mo.",
        )
    if file_hash in set(known_hashes):
        return FileCandidate(
            **base,
            status="duplicate",
            error="Ce contenu est déjà sélectionné ou indexé.",
        )
    return FileCandidate(**base, status="accepted")


def validate_files(
    uploads: Iterable[tuple[str, bytes]],
    *,
    indexed_hashes: Iterable[str] = (),
    max_size_mb: int = 25,
) -> list[FileCandidate]:
    known = set(indexed_hashes)
    candidates: list[FileCandidate] = []
    for name, data in uploads:
        candidate = validate_file(
            name,
            data,
            known_hashes=known,
            max_size_mb=max_size_mb,
        )
        candidates.append(candidate)
        if candidate.is_valid:
            known.add(candidate.file_hash)
    return candidates


def human_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} o"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} Ko"
    return f"{size_bytes / (1024 * 1024):.1f} Mo"

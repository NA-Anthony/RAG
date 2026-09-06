"""Extraction locale du texte des formats acceptés."""

from __future__ import annotations

from dataclasses import dataclass
import re

from langchain_core.documents import Document
import pymupdf

from core.file_validation import FileCandidate


class DocumentLoadError(ValueError):
    """Erreur présentable à l'utilisateur pour un document donné."""


@dataclass(frozen=True)
class ExtractionResult:
    documents: list[Document]
    errors: list[str]


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _metadata(candidate: FileCandidate) -> dict[str, str | int]:
    return {
        "source": candidate.name,
        "file_type": candidate.file_type,
        "document_id": candidate.document_id,
        "file_hash": candidate.file_hash,
        "size_bytes": candidate.size_bytes,
    }


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise DocumentLoadError("Encodage texte non reconnu (UTF-8 ou Windows-1252 attendu).")


def _load_pdf(candidate: FileCandidate) -> list[Document]:
    try:
        pdf = pymupdf.open(stream=candidate.data, filetype="pdf")
    except Exception as error:
        raise DocumentLoadError(f"PDF illisible ou corrompu : {error}") from error

    try:
        if pdf.needs_pass:
            raise DocumentLoadError("Le PDF est protégé par un mot de passe.")
        documents: list[Document] = []
        for page_index, page in enumerate(pdf, start=1):
            try:
                content = normalize_text(page.get_text("text"))
            except Exception as error:
                raise DocumentLoadError(
                    f"Impossible d'extraire la page {page_index} : {error}"
                ) from error
            if content:
                documents.append(
                    Document(
                        page_content=content,
                        metadata={**_metadata(candidate), "page": page_index},
                    )
                )
        if not documents:
            raise DocumentLoadError(
                "Aucun texte détecté. Le PDF est peut-être scanné ; l'OCR n'est pas pris en charge."
            )
        return documents
    finally:
        pdf.close()


def load_candidate(candidate: FileCandidate) -> list[Document]:
    if not candidate.is_valid:
        raise DocumentLoadError(candidate.error or "Fichier non valide.")
    if candidate.extension == ".pdf":
        return _load_pdf(candidate)

    content = normalize_text(_decode_text(candidate.data))
    if not content:
        raise DocumentLoadError("Le fichier ne contient aucun texte exploitable.")
    return [Document(page_content=content, metadata=_metadata(candidate))]


def load_candidates(candidates: list[FileCandidate]) -> ExtractionResult:
    documents: list[Document] = []
    errors: list[str] = []
    for candidate in candidates:
        try:
            documents.extend(load_candidate(candidate))
        except DocumentLoadError as error:
            errors.append(f"{candidate.name} : {error}")
    return ExtractionResult(documents=documents, errors=errors)

"""Découpage reproductible des documents avec conservation des sources."""

from __future__ import annotations

from collections import defaultdict
import hashlib

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def make_splitter(*, chunk_size: int = 900, chunk_overlap: int = 150) -> RecursiveCharacterTextSplitter:
    if chunk_size <= 0:
        raise ValueError("La taille des chunks doit être positive.")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("Le chevauchement doit être positif et inférieur à la taille.")
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True,
        separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""],
    )


def split_documents(
    documents: list[Document],
    *,
    chunk_size: int = 900,
    chunk_overlap: int = 150,
) -> list[Document]:
    splitter = make_splitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    counters: defaultdict[str, int] = defaultdict(int)
    chunks: list[Document] = []

    for document in documents:
        document_id = str(document.metadata["document_id"])
        for chunk in splitter.split_documents([document]):
            content = chunk.page_content.strip()
            if not content:
                continue
            chunk_index = counters[document_id]
            counters[document_id] += 1
            page = chunk.metadata.get("page", "")
            identity = f"{document_id}|{page}|{chunk_index}|{content}".encode("utf-8")
            chunk_id = hashlib.sha256(identity).hexdigest()
            chunks.append(
                Document(
                    page_content=content,
                    metadata={
                        **chunk.metadata,
                        "chunk_index": chunk_index,
                        "chunk_id": chunk_id,
                    },
                )
            )
    return chunks

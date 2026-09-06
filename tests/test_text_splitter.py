from langchain_core.documents import Document
import pytest

from core.text_splitter import make_splitter, split_documents


def test_split_preserves_metadata_and_stable_order() -> None:
    document = Document(
        page_content=("Phrase riche en contexte. " * 80).strip(),
        metadata={
            "source": "cours.txt",
            "file_type": "TXT",
            "file_hash": "hash",
            "document_id": "doc",
        },
    )
    chunks = split_documents([document], chunk_size=180, chunk_overlap=40)
    assert len(chunks) > 1
    assert [chunk.metadata["chunk_index"] for chunk in chunks] == list(range(len(chunks)))
    assert all(chunk.metadata["source"] == "cours.txt" for chunk in chunks)
    assert len({chunk.metadata["chunk_id"] for chunk in chunks}) == len(chunks)


def test_invalid_overlap_is_rejected() -> None:
    with pytest.raises(ValueError):
        make_splitter(chunk_size=100, chunk_overlap=100)

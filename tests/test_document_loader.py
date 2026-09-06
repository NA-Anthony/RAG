import pymupdf
import pytest

from core.document_loader import DocumentLoadError, load_candidate
from core.file_validation import validate_file


def test_loads_utf8_markdown_and_normalizes_lines() -> None:
    candidate = validate_file("lecon.md", "Titre\r\n\r\n\r\nTexte accentué".encode())
    documents = load_candidate(candidate)
    assert documents[0].page_content == "Titre\n\nTexte accentué"
    assert documents[0].metadata["source"] == "lecon.md"


def test_loads_pdf_page_by_page() -> None:
    pdf = pymupdf.open()
    for text in ("Première page", "Deuxième page"):
        page = pdf.new_page()
        page.insert_text((72, 72), text)
    candidate = validate_file("cours.pdf", pdf.tobytes())
    pdf.close()
    documents = load_candidate(candidate)
    assert [document.metadata["page"] for document in documents] == [1, 2]
    assert "Première" in documents[0].page_content


def test_reports_scanned_or_empty_pdf() -> None:
    pdf = pymupdf.open()
    pdf.new_page()
    candidate = validate_file("scan.pdf", pdf.tobytes())
    pdf.close()
    with pytest.raises(DocumentLoadError, match="OCR"):
        load_candidate(candidate)

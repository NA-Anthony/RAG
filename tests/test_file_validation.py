from core.file_validation import human_size, validate_file, validate_files


def test_accepts_supported_text_file() -> None:
    candidate = validate_file("cours.md", "Texte en français".encode())
    assert candidate.is_valid
    assert candidate.file_type == "Markdown"
    assert len(candidate.document_id) == 24


def test_rejects_empty_unsupported_and_oversized_files() -> None:
    assert validate_file("vide.txt", b"").status == "rejected"
    assert validate_file("image.png", b"data").status == "rejected"
    assert validate_file("gros.pdf", b"ab", max_size_mb=0).status == "rejected"


def test_detects_duplicate_content_in_batch_and_library() -> None:
    payload = b"contenu identique"
    first_hash = validate_file("original.txt", payload).file_hash
    candidates = validate_files(
        [("copie.txt", payload), ("nouveau.txt", b"autre")],
        indexed_hashes={first_hash},
    )
    assert [candidate.status for candidate in candidates] == ["duplicate", "accepted"]


def test_human_size() -> None:
    assert human_size(12) == "12 o"
    assert human_size(2048) == "2.0 Ko"

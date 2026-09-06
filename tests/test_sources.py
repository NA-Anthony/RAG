from ui.sources import unique_sources


def test_sources_are_deduplicated_by_origin() -> None:
    source = {"source": "a.pdf", "page": 1, "chunk_index": 2, "content": "Texte"}
    assert unique_sources([source, dict(source)]) == [source]

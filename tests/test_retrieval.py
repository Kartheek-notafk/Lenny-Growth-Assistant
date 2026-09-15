import pathlib
import backend.app.retrieval as retrieval

FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "transcripts"


def _use_fixture_dir(monkeypatch):
    monkeypatch.setattr(retrieval, "DATA_DIR", FIXTURES)
    retrieval.load_chunks.cache_clear()


def test_frontmatter_is_parsed_into_source_metadata(monkeypatch):
    _use_fixture_dir(monkeypatch)
    chunks = retrieval.load_chunks()
    assert len(chunks) >= 1
    c = chunks[0]
    assert c.guest == "Sample Guest"
    assert c.title == "How to price a subscription product"
    assert c.url == "https://www.youtube.com/watch?v=example"


def test_retrieve_finds_relevant_chunk_by_keyword_overlap(monkeypatch):
    _use_fixture_dir(monkeypatch)
    results = retrieval.retrieve("how should I price a subscription", k=3)
    assert len(results) >= 1
    assert "pric" in results[0].text.lower() or "price" in results[0].text.lower()


def test_retrieve_returns_empty_for_unrelated_query(monkeypatch):
    _use_fixture_dir(monkeypatch)
    results = retrieval.retrieve("xylophone zeppelin quokka", k=3)
    assert results == []


def test_readme_file_is_excluded_from_ingestion(tmp_path, monkeypatch):
    (tmp_path / "README.md").write_text("This folder holds transcripts.")
    (tmp_path / "guest.md").write_text("---\nguest: G\ntitle: T\n---\n\nActual transcript body words here.")
    monkeypatch.setattr(retrieval, "DATA_DIR", tmp_path)
    retrieval.load_chunks.cache_clear()
    chunks = retrieval.load_chunks()
    assert all(c.source != "README.md" for c in chunks)

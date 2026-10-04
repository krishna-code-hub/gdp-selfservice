
import pytest
import yaml
from conftest import write_doc

from gdp_support.cli import parser, run
from gdp_support.corpus import KnowledgeError, load_corpus
from gdp_support.references import fetch_reference, headings, load_reference
from gdp_support.store import Store


def linked_card(corpus, source="large.md"):
    folder = corpus / "references"
    folder.mkdir(exist_ok=True)
    card = write_doc(folder, id_="REF-001", body="schema migration reference")
    text = card.read_text()
    metadata = yaml.safe_load(text.split("---", 2)[1])
    metadata["source_file"] = source
    card.write_text("---\n" + yaml.safe_dump(metadata) + "---\n# Schema migration reference")
    sources = corpus.parent / "reference_documents"
    sources.mkdir(exist_ok=True)
    full = sources / "large.md"
    full.write_text("# Guide\n\n## Overview\n" + "schema " * 2000 + "\n## Check\nVerify schema.\n")
    return sources, full


def test_one_card_embedding_and_explicit_section(tmp_path, corpus, embedder):
    sources, full = linked_card(corpus)
    store = Store(tmp_path / "db", embedder)
    assert store.ingest(corpus)["embedded"] == 1
    assert len(load_corpus(corpus)) == 1
    hit = store.search("schema", kind="reference")["matches"][0]
    assert hit["source_file"] == "large.md"
    assert fetch_reference(store, sources, "REF-001")["markdown"] == full.read_text()
    section = fetch_reference(store, sources, "REF-001", section="Check")
    assert section["partial"] is True
    assert section["markdown"] == "## Check\nVerify schema.\n"
    assert [s["heading"] for s in fetch_reference(
        store, sources, "REF-001", list_sections=True
    )["sections"]] == ["Guide", "Overview", "Check"]
    full.write_text(full.read_text() + "New verification.\n")
    with pytest.raises(KnowledgeError, match="changed after ingestion"):
        fetch_reference(store, sources, "REF-001")
    assert store.ingest(corpus)["embedded"] == 0
    assert "New verification" in fetch_reference(store, sources, "REF-001", section="Check")[
        "markdown"
    ]


def test_cli_budget_requires_explicit_selection(tmp_path, corpus, embedder, monkeypatch):
    import gdp_support.embedding

    sources, _ = linked_card(corpus)
    monkeypatch.setattr(gdp_support.embedding, "RemoteEmbedder", lambda config=None: embedder)
    args = ["--db", str(tmp_path / "db"), "--corpus", str(corpus), "--sources", str(sources)]
    run(parser().parse_args(args + ["ingest"]))
    with pytest.raises(KnowledgeError, match="list-sections"):
        run(parser().parse_args(args + ["read-reference", "REF-001", "--budget", "128"]))
    result = run(parser().parse_args(args + ["read-reference", "REF-001", "--section", "Check"]))
    assert result["partial"] is True
    assert "Verify schema" in result["markdown"]


@pytest.mark.parametrize("path", ["../secret.md", "/secret.md", "dir\\secret.md", "bad.txt", ""])
def test_reference_paths_are_confined(tmp_path, path):
    with pytest.raises(KnowledgeError, match="relative .md"):
        load_reference(tmp_path, path)


def test_missing_link_prevents_index_replacement(tmp_path, corpus, embedder):
    sources, full = linked_card(corpus)
    store = Store(tmp_path / "db", embedder)
    store.ingest(corpus)
    before = store.status()["collection"]
    full.unlink()
    with pytest.raises(KnowledgeError, match="missing"):
        store.ingest(corpus)
    assert store.status()["collection"] == before
    with pytest.raises(KnowledgeError, match="missing"):
        fetch_reference(store, sources, "REF-001")


def test_section_parser_ignores_frontmatter_and_fences():
    text = "---\n# metadata comment\n---\n# Top\n```md\n## Fake\n```\n## Real\n### Child\n"
    _, sections = headings(text)
    assert [s["heading"] for s in sections] == ["Top", "Real", "Child"]


def test_duplicate_section_names_require_clarification(tmp_path, corpus, embedder):
    sources, full = linked_card(corpus)
    full.write_text("# Guide\n## Check\nOne\n## Check\nTwo\n")
    store = Store(tmp_path / "db", embedder)
    store.ingest(corpus)
    with pytest.raises(KnowledgeError, match="exactly one"):
        fetch_reference(store, sources, "REF-001", section="Check")


def test_linked_symlink_rejected(tmp_path):
    outside = tmp_path / "outside.md"
    outside.write_text("Private")
    sources = tmp_path / "sources"
    sources.mkdir()
    try:
        (sources / "link.md").symlink_to(outside)
    except OSError:
        pytest.skip("Symlinks unavailable")
    with pytest.raises(KnowledgeError, match="symlinks"):
        load_reference(sources, "link.md")

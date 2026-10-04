from pathlib import Path

import pytest
from conftest import write_doc

from gdp_support.corpus import KnowledgeError, load_corpus


def test_complete_original_markdown_is_one_document(corpus):
    path = write_doc(corpus, body="auth\n## Diagnostics\ncheck\n## Resolve\nrotate")
    documents = load_corpus(corpus)
    assert len(documents) == 1
    assert documents[0].text == path.read_text()
    assert documents[0].metadata["source"] == "ING-001.md"


def test_duplicate_ids_rejected(corpus):
    write_doc(corpus)
    write_doc(corpus, name="duplicate.md")
    with pytest.raises(KnowledgeError, match="duplicate"):
        load_corpus(corpus)


@pytest.mark.parametrize("text", ["no frontmatter", "---\n[]\n---\nbody", "---\n: :\n---\nbody"])
def test_bad_frontmatter(corpus, text):
    (corpus / "bad.md").write_text(text)
    with pytest.raises(KnowledgeError):
        load_corpus(corpus)


def test_empty_corpus_is_not_destructive(corpus):
    with pytest.raises(KnowledgeError, match="No Markdown"):
        load_corpus(corpus)


def test_external_symlink_rejected(corpus, tmp_path):
    external = write_doc(tmp_path)
    try:
        (corpus / "link.md").symlink_to(external)
    except OSError:
        pytest.skip("Symlink creation not available on this Windows runner")
    with pytest.raises(KnowledgeError, match="Symlinks"):
        load_corpus(corpus)


def test_shipped_corpus_has_valid_metadata():
    documents = load_corpus(Path(__file__).resolve().parents[1] / "knowledge")
    assert len(documents) >= 10
    assert all(d.metadata["status"] in {"example", "draft", "approved"} for d in documents)


def test_yaml_separator_in_value_does_not_end_frontmatter(corpus):
    path = write_doc(corpus)
    path.write_text(path.read_text().replace("framework-team", "team---support"))
    assert load_corpus(corpus)[0].metadata["owner"] == "team---support"

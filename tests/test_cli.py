import json

import pytest
from conftest import write_doc

from gdp_support.cli import bounded, main, parser, redact, run, token_count
from gdp_support.corpus import KnowledgeError


def test_budget_never_truncates_document():
    value = {"markdown": "diagnostic rollback verification " * 500}
    with pytest.raises(KnowledgeError, match="budget"):
        bounded(value, 128)
    assert bounded(value, 8000) == value


def test_redacts_common_credentials():
    redacted = redact("Bearer abc.def secret=hidden api_key:abc password=xyz schema mismatch")
    assert "hidden" not in redacted
    assert "abc" not in redacted
    assert "xyz" not in redacted
    assert "schema mismatch" in redacted


def test_validate_does_not_load_embedding_model(corpus, capsys):
    write_doc(corpus)
    assert main(["--corpus", str(corpus), "validate"]) == 0
    assert json.loads(capsys.readouterr().out)["documents"] == 1


def test_cli_context_omits_whole_documents_for_budget(tmp_path, corpus, embedder, monkeypatch):
    import gdp_support.embedding

    monkeypatch.setattr(gdp_support.embedding, "RemoteEmbedder", lambda config=None: embedder)
    write_doc(corpus, body="auth " * 800)
    arguments = ["--db", str(tmp_path / "db"), "--corpus", str(corpus)]
    run(parser().parse_args(arguments + ["ingest"]))
    result = run(parser().parse_args(arguments + ["context", "--query", "auth", "--budget", "128"]))
    assert result["documents"] == []
    assert result["omitted_for_budget"] == 1
    assert token_count(result) <= 128
    result = run(
        parser().parse_args(arguments + ["context", "--query", "auth", "--budget", "3000"])
    )
    assert len(result["documents"]) == 1
    assert result["documents"][0]["markdown"].endswith("auth " * 800)


def test_actual_embedder_length_guard_without_download():
    from dataclasses import replace

    from gdp_support.config import load_config
    from gdp_support.embedding import RemoteEmbedder

    embedding = RemoteEmbedder(replace(load_config().embedding, max_tokens=3))
    assert embedding.validate("one two three") == 3
    with pytest.raises(KnowledgeError, match="silently truncated"):
        embedding.validate("one two three four")

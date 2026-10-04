import json

import pytest
import yaml
from conftest import write_doc

from gdp_support.cli import main
from gdp_support.corpus import KnowledgeError
from gdp_support.evaluation import evaluate, load_dataset, render_table
from gdp_support.store import Store


def test_scoring_budget_and_missing_expected_id(tmp_path, corpus, embedder):
    write_doc(corpus, body="auth credential")
    write_doc(corpus, id_="ING-002", body="schema mismatch")
    store = Store(tmp_path / "db", embedder)
    store.ingest(corpus)
    result = evaluate(store, [
        {"id": "hit", "query": "schema", "expected_id": "ING-002", "top_k": 1},
        {"id": "miss", "query": "auth", "expected_id": "ING-002", "top_k": 1},
        {"id": "negative", "query": "violin", "expect_no_match": True},
        {"id": "false-positive", "query": "auth", "expect_no_match": True},
        {"id": "budget", "query": "schema", "expected_id": "ING-002", "budget": 128},
    ])
    assert result["passed"] == 2
    assert result["failed"] == 3
    assert result["positive_hit_rate"] == pytest.approx(1 / 3)
    assert result["positive_mean_reciprocal_rank"] == pytest.approx(1 / 3)
    assert result["negative_pass_rate"] == 0.5
    assert result["results"][-1]["matches"] == []
    with pytest.raises(KnowledgeError, match="Unknown document"):
        evaluate(store, [{"id": "bad", "query": "auth", "expected_id": "MISSING"}])


@pytest.mark.parametrize("case", [
    {"id": "x", "query": "q"},
    {"id": "x", "query": "q", "expected_id": "A", "expect_no_match": True},
    {"id": "x", "query": "q", "expected_id": "A", "top_k": True},
    {"id": "x", "query": "q", "expected_id": "A", "max_distance": float("nan")},
    {"id": "x", "query": "q", "expected_id": "A", "component": ["ingestion"]},
])
def test_invalid_dataset(tmp_path, case):
    path = tmp_path / "cases.yaml"
    path.write_text(yaml.safe_dump({"version": 1, "cases": [case]}))
    with pytest.raises(KnowledgeError):
        load_dataset(path)


def test_cli_exit_codes(tmp_path, corpus, embedder, monkeypatch, capsys):
    import gdp_support.embedding

    monkeypatch.setattr(gdp_support.embedding, "RemoteEmbedder", lambda config=None: embedder)
    write_doc(corpus)
    write_doc(corpus, id_="ING-002", body="schema")
    Store(tmp_path / "db", embedder).ingest(corpus)
    path = tmp_path / "cases.yaml"
    args = ["--db", str(tmp_path / "db"), "evaluate", "--dataset", str(path)]
    for expected, code in (("ING-001", 0), ("ING-002", 1), ("MISSING", 2)):
        path.write_text(yaml.safe_dump({"version": 1, "cases": [
            {"id": "x", "query": "auth", "expected_id": expected, "top_k": 1}
        ]}))
        assert main(args) == code
        captured = capsys.readouterr()
        if code != 2:
            assert json.loads(captured.out)["failed"] == code
    path.write_text(yaml.safe_dump({"version": 1, "cases": [
        {"id": "x", "query": "auth", "expected_id": "ING-002", "top_k": 1}
    ]}))
    assert main(args + ["--format", "table"]) == 1
    assert "Review guide wording" in capsys.readouterr().out


def test_table_distinguishes_negative_failures_and_lower_rank():
    report = {"passed": 1, "cases": 2, "failed": 1, "snapshot": "test", "results": [
        {"id": "negative|case", "expected_id": None, "expect_no_match": True,
         "passed": False, "rank": None, "matches": [{"id": "A", "distance": 0.6}]},
        {"id": "positive", "expected_id": "B", "expect_no_match": False,
         "passed": True, "rank": 2, "matches": [{"id": "B", "distance": 0.3}]},
    ]}
    output = render_table(report)
    assert "negative\\|case" in output
    assert "Refine rejection" in output
    assert "review ranking" in output
    assert "A (0.6)" in output


def test_evaluation_rejects_snapshot_changes():
    class ChangingStore:
        def status(self):
            return {"collection": "old", "embedding": "test"}

        def search(self, *args):
            return {"snapshot": "new", "matches": []}

    with pytest.raises(KnowledgeError, match="changed during evaluation"):
        evaluate(ChangingStore(), [{"id": "x", "query": "q", "expect_no_match": True}])

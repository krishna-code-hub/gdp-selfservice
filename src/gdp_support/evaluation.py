"""Evaluate budgeted retrieval against human-reviewed YAML expectations."""

import math
from pathlib import Path

import yaml

from .corpus import COMPONENTS, KINDS, STATUSES, KnowledgeError


def render_table(report):
    """Readable Markdown table; preserve JSON as the default tool contract."""
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")

    lines = [
        f"Results: {report['passed']}/{report['cases']} passed; {report['failed']} failed.",
        f"Snapshot: {report['snapshot']}",
        "",
        "| Case | Expected | Returned IDs (distance) | Rank | Result | Follow-up |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for result in report["results"]:
        if not result["passed"]:
            action = (
                "Refine rejection; unrelated guides should not appear"
                if result["expect_no_match"] else
                "Review guide wording, filters, cutoff and output budget"
            )
        elif result["rank"] and result["rank"] > 1:
            action = "Passes; review ranking if the intended guide should be first"
        else:
            action = "No refinement indicated by this case"
        values = [
            result["id"], result["expected_id"] or "No matches",
            ", ".join(f"{m['id']} ({m['distance']})" for m in result["matches"]) or "None",
            result["rank"] or "—", "PASS" if result["passed"] else "FAIL", action,
        ]
        lines.append("| " + " | ".join(cell(v) for v in values) + " |")
    return "\n".join(lines)


def load_dataset(path: Path):
    if path.stat().st_size > 1_000_000:
        raise KnowledgeError("Evaluation dataset exceeds 1MB")
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise KnowledgeError("Invalid evaluation YAML") from exc
    if not isinstance(value, dict) or set(value) != {"version", "cases"}:
        raise KnowledgeError("Dataset requires only version and cases")
    cases = value["cases"]
    if type(value["version"]) is not int or value["version"] != 1:
        raise KnowledgeError("Dataset version must be 1")
    if not isinstance(cases, list) or not 1 <= len(cases) <= 1000:
        raise KnowledgeError("Dataset requires 1..1000 cases")
    seen = set()
    allowed = {"id", "query", "expected_id", "expect_no_match", "component", "framework",
               "status", "top_k", "max_distance", "budget"}
    allowed.add("kind")
    for case in cases:
        if not isinstance(case, dict) or set(case) - allowed:
            raise KnowledgeError("Invalid case or unknown evaluation field")
        for key in ("id", "query"):
            if not isinstance(case.get(key), str) or not case[key].strip():
                raise KnowledgeError(f"Each case requires a nonempty {key}")
        if case["id"] in seen:
            raise KnowledgeError("Duplicate evaluation case ID")
        seen.add(case["id"])
        if len(case["query"].encode()) > 64_000:
            raise KnowledgeError("Evaluation query exceeds 64KB")
        positive = isinstance(case.get("expected_id"), str) and bool(case["expected_id"].strip())
        negative = case.get("expect_no_match") is True
        if positive == negative or ("expected_id" in case and not positive):
            raise KnowledgeError("Use expected_id OR expect_no_match: true")
        if "expect_no_match" in case and not negative:
            raise KnowledgeError("expect_no_match must be true")
        for key, choices in (("component", COMPONENTS), ("status", STATUSES), ("kind", KINDS)):
            if key in case and (not isinstance(case[key], str) or case[key] not in choices):
                raise KnowledgeError(f"Invalid evaluation {key}")
        if "framework" in case and (
            not isinstance(case["framework"], str) or not case["framework"].strip()
        ):
            raise KnowledgeError("framework must be a nonempty string")
        for key, default, low, high in (("top_k", 3, 1, 10), ("budget", 1200, 128, 8000)):
            number = case.get(key, default)
            if type(number) is not int or not low <= number <= high:
                raise KnowledgeError(f"Invalid evaluation {key}")
        distance = case.get("max_distance", 0.65)
        if type(distance) not in (int, float) or not math.isfinite(distance) or not 0 <= distance <= 2:
            raise KnowledgeError("Invalid evaluation max_distance")
    return cases


def evaluate(store, cases):
    # Share the CLI's redaction, output formatting and budget behavior.
    from .cli import bounded, redact, token_count

    manifest = store.status()
    snapshot = manifest["collection"]
    for id_ in sorted({c["expected_id"] for c in cases if "expected_id" in c}):
        store.read([id_], snapshot)  # Fail configuration errors before scoring.
    results = []
    for case in cases:
        budget = case.get("budget", 1200)
        found = store.search(
            redact(case["query"]), case.get("top_k", 3), case.get("component"),
            case.get("framework"), case.get("status"), case.get("max_distance", 0.65),
            case.get("kind"),
        )
        if found["snapshot"] != snapshot:
            raise KnowledgeError("Index changed during evaluation; rerun on a stable index")
        while found["matches"] and token_count(found) > budget:
            found["matches"].pop()
        bounded(found, budget)
        ids = [m["id"] for m in found["matches"]]
        expected = case.get("expected_id")
        rank = ids.index(expected) + 1 if expected in ids else None
        passed = rank is not None if expected else not ids
        results.append({
            "id": case["id"], "expected_id": expected,
            "expect_no_match": case.get("expect_no_match", False),
            "passed": passed, "rank": rank, "top_k": case.get("top_k", 3),
            "budget": budget,
            "kind": case.get("kind"),
            "matches": [{"id": m["id"], "distance": m["distance"]} for m in found["matches"]],
        })
    if store.status()["collection"] != snapshot:
        raise KnowledgeError("Index changed during evaluation; rerun on a stable index")
    positives = [r for r in results if r["expected_id"]]
    negatives = [r for r in results if r["expect_no_match"]]
    return {
        "snapshot": snapshot, "model_signature": manifest["embedding"],
        "cases": len(results), "passed": sum(r["passed"] for r in results),
        "failed": sum(not r["passed"] for r in results),
        "positive_hit_rate": sum(r["passed"] for r in positives) / len(positives)
        if positives else None,
        "positive_mean_reciprocal_rank": sum(1 / r["rank"] if r["rank"] else 0
                                             for r in positives) / len(positives)
        if positives else None,
        "negative_pass_rate": sum(r["passed"] for r in negatives) / len(negatives)
        if negatives else None,
        "results": results,
    }

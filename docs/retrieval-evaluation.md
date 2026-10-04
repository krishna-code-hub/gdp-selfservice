# Validate retrieval after ingestion

Platform and framework owners maintain [evaluation/retrieval.yaml](../evaluation/retrieval.yaml).
It contains sanitized questions phrased in different ways and the guide each
question should retrieve. It lives outside `knowledge/`, so test questions are
not embedded into the knowledge index and cannot improve results by leaking answers.

## Run the checks

Run from the repository root after setup and after every knowledge update.

macOS/Linux:

```sh
.venv/bin/python scripts/ingest.py
.venv/bin/python scripts/query.py evaluate
```

Windows PowerShell:

```powershell
.venv\Scripts\python.exe scripts\ingest.py
.venv\Scripts\python.exe scripts\query.py evaluate
```

Evaluation uses the existing index and configured remote embedding API. It does not
re-ingest in default persistent mode. Set the configured API key before running.
To use another dataset:

```sh
.venv/bin/python scripts/query.py evaluate --dataset evaluation/retrieval.yaml
```

The JSON report identifies the index snapshot and embedding model, lists each
case's returned IDs and distances, and shows the expected guide's rank. It does
not include question text or full documents. Exit codes are **0** for all cases
passing, **1** for retrieval failures, **2** for invalid dataset/index configuration
or filesystem errors, and **3** for dependency/model/database errors.

Add `--format table` to display a Markdown table with ranks, returned IDs and
distances, pass/fail and follow-up suggestions. JSON remains the default.
After editing only `evaluation/retrieval.yaml`, rerun evaluation directly;
re-ingestion is needed when the knowledge Markdown changes.

## Add a case

```yaml
version: 1
cases:
  - id: schema-type-change
    query: "Source column changed from integer to string"
    expected_id: ING-002
    component: ingestion
    top_k: 3
    budget: 1200
    max_distance: 0.65
  - id: unrelated-question
    query: "How do I bake a chocolate cake?"
    expect_no_match: true
```

Each case needs a unique `id`, a nonempty sanitized `query`, and either one
`expected_id` or `expect_no_match: true`. Positive cases pass when the expected
ID is among returned matches; negative cases pass only when no matches remain.
Expected IDs must exist in the ingested index; missing IDs are configuration
errors. Optional filters are `component`, `framework`, `status` and `kind`.
Use `kind: reference` for clarification cases and `kind: troubleshooting` for
incident cases. The four category-specific starter cases use these filters;
the older cases remain unfiltered to measure broader retrieval behavior. Defaults are
`top_k: 3`, `budget: 1200` and `max_distance: 0.65`. These match a typical agent
search and use the same redaction and JSON budgeting as the search CLI.

A case can fail because the expected guide ranks too low, falls outside the
distance cutoff, is excluded by a filter, or is removed by the output budget.
The dataset allows one expected guide per case; choose a clear owner-reviewed
question with one intended source. An ambiguous question may need clarification
rather than a rigid expected answer.

## Read the metrics

- `positive_hit_rate`: fraction of positive questions returning the expected guide.
- `positive_mean_reciprocal_rank`: average of 1/rank for positives, with misses
  counted as zero. Rank 1 scores 1; rank 3 scores 1/3.
- `negative_pass_rate`: fraction of no-match questions returning no evidence.

Metrics for absent case types are `null`. Every case must pass for exit code 0.
An index replacement during evaluation aborts the run rather than mixing results
from different snapshots. Evaluation output is a report, not subject to one
search's output budget; each evaluated search is budgeted independently.

### Historical sample baseline

The current thirteen-document corpus and seventeen-case dataset pass all fifteen
positive cases, including the four category-filtered examples at rank 1. Both
unrelated-query cases still fail, so evaluation exits with code 1 (15/17).
REF-003 now links to the full supplied CDP mapping; retrieval checks locate its
card, not the source's correctness. REF-004 still documents missing SQL/PySpark
evidence. Manually verify linked-source fetching and applicability in Copilot.

These historical results used the previous local embedding model. They do not
validate the configured remote model; rerun evaluation after re-ingesting.

The initial local run on the ten sample guides with the pinned model returned
the expected guide for all **11 positive cases**, with ten ranked first and one
ranked second. Both **negative cases failed**: unrelated cake/violin questions
returned matches under the current `0.65` distance cutoff. The overall result
was 11/13, so the starter dataset currently exits with code 1. This is an
intentional visible regression signal, not a setup error. This baseline predates
the three new documents and four category cases; rerun for current results. Negative cases remain
in the dataset rather than being removed to produce a green report.

Owners should calibrate rejection using a larger representative dataset and
apply any chosen cutoff consistently in actual searches and evaluations.
Per-case overrides alone do not change agent defaults. Embedding similarity
alone does not guarantee that unrelated questions will be rejected.

## Maintain useful tests

Add actual sanitized tenant phrasing, exact error messages, short paraphrases,
questions without component filters, and irrelevant questions. Add cases before
editing guides where possible. Preserve representative questions instead of
rewriting them to make a failing model pass. Keep queries short enough for the
embedding model, and never commit secrets or customer payloads.

Investigate failures by running the question through `search` and reading the
selected guides. Improve focused titles, summaries and symptom descriptions
using verified terminology, then re-ingest and rerun. Review distance/budget
changes against both positive and negative cases. Do not raise cutoffs simply
to force a pass. Extend this starter dataset for your real platform; passing it
measures documented retrieval behavior, not the correctness of Copilot's diagnosis.

The optional real-model GitHub Actions job runs this dataset after ingestion.
Its checks require access and credentials for the remote embedding API; ordinary
unit tests use deterministic vectors and mocked HTTP responses.

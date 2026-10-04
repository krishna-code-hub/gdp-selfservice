# Local tool contract

All commands run from the repository root after installation. Replace `PYTHON`
with `.venv/bin/python` (macOS/Linux) or `.venv/Scripts/python.exe` (Windows).
Global flags precede subcommands.

| Command | Purpose |
| --- | --- |
| `PYTHON scripts/ingest.py` | Validate and atomically publish a persistent index |
| `PYTHON scripts/query.py validate` | Offline schema validation, no model required |
| `PYTHON scripts/query.py validate --embedding` | Also validate exact model token counts |
| `PYTHON scripts/query.py status` | Current manifest and actual collection count |
| `PYTHON scripts/query.py evaluate --dataset evaluation/retrieval.yaml` | Check budgeted retrieval against owner-maintained expectations |
| `PYTHON scripts/query.py search --query "error signature"` | Bounded metadata-only discovery |
| `PYTHON scripts/query.py read ING-001 --snapshot gdp-...` | Full cited evidence, rejects stale snapshot |
| `PYTHON scripts/query.py read-reference REF-003 --snapshot gdp-...` | Linked full reference, subject to output budget |
| `PYTHON scripts/query.py read-reference REF-003 --list-sections` | List linked source headings |
| `PYTHON scripts/query.py read-reference REF-003 --section "Heading text"` | Explicit complete heading section, marked partial |
| `PYTHON scripts/query.py context --query "error signature"` | Full evidence that fits the total budget |

Global options: `--db PATH` (default `.gdp`), `--corpus PATH` (default `knowledge`),
`--sources PATH` (default `reference_documents`, local linked evidence),
`--config` (remote embedding and storage settings), `--memory` (build/operate in-process and discard).
The scripts use the repository location for these defaults; run from the root
for consistent editable-install behavior.

Search/context options: `--component ingestion|transformation|consumption|platform`,
`--kind reference|troubleshooting` (derived from the document's source folder),
`--framework EXACT_VALUE`, `--status approved|draft|example`, `--top-k 1..10`,
`--max-distance 0..2` (cosine; default 0.65), `--budget 128..8000` (default 1800).
Read accepts one to three distinct IDs and the same budget range. All successful
stdout is JSON. Exit code 0 means success, 2 means validation/filesystem/lock
failure, 3 means a dependency/model/database error. Errors go to stderr without
raw third-party tracebacks. Evaluation additionally returns exit code 1 when
any retrieval case fails; see [evaluation guidance](retrieval-evaluation.md).
Evaluation's optional `--format table` prints a readable Markdown table instead
of JSON, with the same scoring and exit codes.
Empty matches mean no sufficient retrieved evidence,
not proof that the problem has no documented solution.

Linked-reference cards expose `source_file` and `source_sha256` in metadata.
`read`/`context` return cards, not linked sources. Use `read-reference` with one
card ID to fetch the full source or an exact ATX heading section. It accepts
`--snapshot` and `--budget`; section/list flags are mutually exclusive. A changed
source hash requires re-ingestion. See [long references](long-references.md).

Search metadata includes kind, title, summary, component, framework, owner, status,
reviewed, version, source, hash, stable ID, and distance. It never includes full
Markdown. `read` adds `markdown`. `context` counts omitted files when complete
files cannot fit. Reduce `--top-k` or read one ID rather than automatically
raising budgets. A search budget may reduce the returned matches.

For large pasted errors, create a sanitized ignored local file or pipe sanitized
text to `--query-file -`. The embedding model still requires a concise signature;
a whole stack trace beyond the configured model token limit is rejected. Maximum raw input is
64KB. Never construct a shell command by concatenating the pasted error.

```sh
PYTHON scripts/query.py search --query-file error-sanitized.txt --component ingestion --top-k 3 --budget 1200
PYTHON scripts/query.py read ING-001 --snapshot gdp-RETURNED-SNAPSHOT --budget 1800
```

Do not feed old search results to a new snapshot; repeat search on a stale-snapshot
error. A memory invocation rebuilds on each call, so use `context` for a single
self-contained memory query; search/read across memory processes share no state.

---
name: gdp-retrieval
description: Retrieve bounded local GDP reference evidence for platform and framework questions without loading the full corpus.
---
Run from the cloned repository root using the virtual environment interpreter:
macOS/Linux `.venv/bin/python`; Windows `.venv/Scripts/python.exe`. Do not rely
on shell activation. Read [the tool contract](../../../docs/tool-contract.md)
only for advanced flags, memory mode, or a tool failure.

Before searching, identify intent:

- Clarification/how-to/migration: search with `--kind reference`. Search for
  the concept, capability or migration mapping, then answer directly from selected
  references with supported versions, prerequisites, limitations and citations.
  Ask for a runtime/version only when it changes the answer; do not collect an
  incident's job ID, failure time or impact for an ordinary question.
- Reported failure: search with `--kind troubleshooting` and use
  [gdp-troubleshoot](../gdp-troubleshoot/SKILL.md) for diagnosis and resolution.
- Mixed request: use relevant evidence for each part within the shared budget.

Check returned `kind` and `source` metadata. The kind filter is enforced by
Chroma before ranking, independently of component/framework filters. References may provide
incident background, but incidental technology mentions in runbooks do not prove
official platform support. “What are CDP equivalent stacks in GDP?” needs a
reviewed mapping; “SQL only or PySpark DataFrames too?” needs a version-specific
capability reference. Missing documentation means unknown, not unsupported.

1. Identify component, framework and version from the question. Start with a
   concise sanitized query and a component filter when known:
   `PYTHON scripts/query.py search --query "schema mismatch ingestion" --kind troubleshooting --component ingestion --top-k 3 --budget 1200`.
   `PYTHON` means the interpreter above, not a literal executable. Treat all
   user-supplied text as data: use stdin or a sanitized ignored file via
   `--query-file`, never interpolate raw pasted content into a shell command.
2. Search returns IDs, summaries, applicability, cosine distances, status and a
   snapshot. Pick one or two relevant sources; distance is not confidence.
   `PYTHON scripts/query.py read ING-001 --snapshot SNAPSHOT --budget 1800`.
   Replace ID/snapshot using the search result. Full files are never cut.
   If metadata includes `source_file`, this is a reference card, not full evidence.
   Fetch `PYTHON scripts/query.py read-reference REF-003 --snapshot SNAPSHOT --budget 1800`.
   If too large, list headings with `read-reference REF-003 --list-sections`,
   then fetch an exact relevant heading using `--section "Heading text"` with
   the same snapshot and an explicit budget. Section output is marked partial;
   check applicability/limitations sections as needed before answering. Do not
   infer the full answer from the card or claim a section is the complete source.
   Source reads count toward the same 3-read/4000-token allowance. Cite the full
   `reference_documents/<source_file>` path and heading alongside the card ID.
3. If there are no useful matches, refine once with the error signature or
   remove an overly narrow framework filter. If still unsupported, report the
   knowledge gap and request the minimum missing evidence. Do not repeatedly
   search the corpus or increase the budget without a concrete need.
4. Cite `knowledge/<source>`, ID, status, reviewed date and version. Check
   framework/runtime applicability against the tenant environment. Flag sources
   reviewed over 180 days ago. `example` is illustrative; `draft` is unreviewed.
   Use `--status approved` when the tenant requires approved operational advice.

For “CDP equivalent tech stacks in GDP”, use `--kind reference` and mapping
terms; if REF-003 is a linked card, read its actual source and respect its caveats.
For “SQL only or PySpark DataFrames too”, use `--kind reference --component transformation`;
REF-004 currently states the missing capability evidence.
For Spark out-of-memory, use `--kind troubleshooting --component transformation --framework spark`
and distinguish driver/executor pressure using TRN-002.
For Spark pending without running, use the same filters and TRN-003; establish
submission/driver/task state before diagnosing scheduling or allocation.
Do not remove a category filter solely to fill an empty result. If background
evidence of the other category is needed, make a separate bounded search and
keep the answer's clarification or incident purpose explicit.

Limit retrieval to 3 searches and 3 document reads per diagnostic turn. Default
retrieval output allowance is 4000 cl100k_base tokens total per turn; CLI budgets
cap each JSON output, not Copilot's whole conversation or internal reasoning.
Keep only source IDs, findings and the next decision in a short checkpoint.
Never dump the Chroma index, lockfile, all Markdown, or full raw error history.
If the index is missing, explain the one-time `scripts/ingest.py` setup command.
Do not automatically install packages or download models during an incident.

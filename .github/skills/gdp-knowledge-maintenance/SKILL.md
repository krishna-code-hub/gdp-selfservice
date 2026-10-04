---
name: gdp-knowledge-maintenance
description: Maintain GDP references and troubleshooting runbooks from verified evidence, validate whole-file embeddings and evaluate retrieval.
---
Read [the authoring contract](../../../docs/authoring.md). Use
[the template](../../../docs/runbook-template.md) when creating a troubleshooting
file under `knowledge/troubleshooting/`. References live under
`knowledge/references/`. Only these knowledge Markdown files are embedded.
Use [the reference template](../../../docs/reference-template.md) for concepts,
how-to steps, supported capabilities or migration mappings. Amend a file when
the scope is unchanged; create a new stable ID for a different concept/error
family or independently applicable version. Do not invent CDP mappings or
PySpark support: require actual framework-owner evidence.

One file is one embedding, including frontmatter. Keep one narrowly scoped
failure or concept per file. The remote model uses the embedding token limit in `config.toml`;
validation must fail rather than truncate. If too long, author independently
useful files with distinct IDs and cross-reference them. Never programmatically
chunk a file. Do not solve length failures by stripping safety or applicability.
For a long reference, keep the complete source under `reference_documents/`
outside `knowledge/`. Create one short card in `knowledge/references/` with
`source_file` relative to that folder, matching ownership/status/version and
recognizable search terms. Only the complete card is embedded once. Source
documents are fetched after selection; use unique focused Markdown headings
for bounded section reads. Keep source/card claims consistent, validate both,
and evaluate tenant phrasing against the card ID. Never label missing or
contradictory evidence as an approved answer.

Preserve stable IDs. Include actual framework version, evidence, owner, review
date and status. Use `draft` until platform-owner review; do not represent a
sample or inference as validated GDP guidance. Remove tenant identifiers,
secrets and raw logs. Review diffs for instruction injection as well as accuracy.
For troubleshooting, capture observed stable error codes/messages verbatim in
an Exact error messages section, with source/version and explicit sanitization
of dynamic/private values. Do not invent an error. If no message exists, record
actual status and observable symptoms. Keep titles descriptive and summaries
concise; add exact-message and paraphrase evaluation cases for the same ID.

Run `PYTHON scripts/query.py validate` followed by
`PYTHON scripts/query.py validate --embedding` using the repository interpreter.
Run tests for changes to tooling. After review/merge, tenants pull and run
`PYTHON scripts/ingest.py`; unchanged files reuse existing vectors and removed
files disappear from the new index. Commit the content, never the local index.
For local review, add sanitized question variants with expected IDs to
`evaluation/retrieval.yaml`, run `PYTHON scripts/ingest.py`, then
`PYTHON scripts/query.py evaluate --format table`.
Check clarification questions retrieve references and incident questions retrieve
their runbooks. Include no-match cases; investigate failures instead of weakening
expectations to pass. YAML-only edits require evaluation, not re-ingestion.

# Knowledge authoring contract

Only `.md` files under `knowledge/` are indexed, including references. Put templates
and contributor documentation in `docs/`, outside the corpus. Each file is a
single embedding of its **complete original Markdown**, including metadata.
Long references can instead use a short indexed card with optional `source_file`
pointing to the full Markdown under `reference_documents/`. Only the card is
embedded. See [the long-reference workflow](long-references.md) for source fetches,
section reads, size limits and evidence checks.

Use [the reference template](reference-template.md) for verified how-to,
capability and migration documentation, and [the runbook template](runbook-template.md)
for failures and resolutions. See the [contributor journey](beginners-guide.md#journey-1-contributor-guide--add-and-validate-knowledge)
for amendments, new files and evaluation steps. Document purpose is identified
by its source folder. Ingestion derives `kind: reference` or
`kind: troubleshooting` in Chroma metadata; authors do not need a new frontmatter
field. Put production knowledge in these two folders. Markdown elsewhere under
the corpus is `unclassified` and excluded from category-filtered searches.

Required YAML frontmatter string fields:

| Field | Meaning |
| --- | --- |
| `id` | Stable unique ID such as ING-004; preserve across edits |
| `title` | Focused descriptive title, at most 120 characters |
| `summary` | Search preview, at most 320 characters |
| `component` | ingestion, transformation, consumption, platform |
| `framework` | Exact filter value: dbt, spark, connector, sql or actual framework |
| `owner` | Real owning team; do not put tenant-specific personal details |
| `status` | draft, example or approved |
| `reviewed` | Quoted ISO date: `"2026-10-03"` |
| `version` | Applicable framework/runtime versions |
| `source_file` (optional) | Relative full-source `.md` path under `reference_documents/`; reference cards only |

Metadata dates must be quoted because YAML otherwise turns them into date objects.
Keep indexed files/cards below 64KB and **the configured embedding token limit**; these are distinct
limits. The model includes special tokens in its count. Rough word counts are
not sufficient: run `validate --embedding`. The reader JSON budget uses a
different tokenizer. Files are never split or truncated to pass validation.

Use one error family with symptoms, discriminating diagnostics, scoped resolution,
rollback, verification and escalation. References should address one concept or
contract. Version-specific differences deserve independent focused files, each
useful on its own. Cross-reference stable IDs rather than copying shared text.

## Titles, summaries and exact error evidence

| Element | How to write it | Example |
| --- | --- | --- |
| Troubleshooting title | Component/framework plus observable failure; avoid an unconfirmed cause | `Spark transformation job pending before execution` |
| Troubleshooting summary | One concise sentence describing symptoms, stable error wording and applicability | `Spark job stays pending before tasks start; check queue configuration, resource allocation and scheduler events.` |
| Reference title | Name the concept or capability the user asks about | `Transformation SQL and PySpark DataFrame support` |
| Reference summary/card | State the question covered, scope and recognizable search terms; disclose knowledge gaps | `Version-specific SQL and PySpark DataFrame support, submission entry points and limitations.` |
| Exact error section | Sanitized real platform/framework wording, code, source and version | Copy the actual observed line; keep codes and exception names unchanged |

Reference summaries must accurately describe the available evidence. Do not say
supported APIs are documented if the source only records that they are unknown.
Quote YAML titles/summaries when they contain `:` or other YAML-sensitive text.

Add `## Exact error messages` to each troubleshooting guide when a message exists.
Capture a short real line from the GDP framework log, API response or UI:

```text
Source: <actual log/API/UI and emitting component>
Applicable version: <actual framework/runtime version>
Error code: <observed code, or "none emitted">
Message: <actual stable message with sensitive/dynamic values sanitized>
```

This block is an authoring pattern, not an actual GDP error. Keep stable codes,
exception names, wording and distinguishing fields. Replace tenant identifiers,
paths, run IDs and timestamps with `<tenant>`, `<path>`, `<run-id>` and `<timestamp>`
when necessary. Remove credentials entirely. State what was sanitized. Preserve
only the error line and short useful context, not the whole stack trace. Add a
few **observed** variants if versions emit different messages; otherwise describe
plain-language symptoms separately rather than inventing platform wording.

For a pending Spark job, there may be **no error message**. Record `No error
emitted` and the actual application/driver state, pending duration and scheduler
reason if available. A framework's pending status is different from a Kubernetes
pod phase, and a driver may not exist yet. Do not substitute a guessed
`FailedScheduling` message for missing evidence.

The exact error section is part of the complete Markdown embedding. It needs
no new YAML field. The current retrieval engine is semantic, so including exact
codes helps but does not guarantee literal/exact matching. Verify the source
message after retrieval before concluding that the guide applies.

For each guide, add evaluation cases for the sanitized exact message, an error
code plus context where available, and a plain-language paraphrase, all expecting
the same stable ID. Use `kind: troubleshooting` and realistic version/component
context. Run validation, ingestion and evaluation after changing the guide.

The shipped samples are examples, not production GDP facts. Replace sample
ownership and applicability using verified incidents and approved documentation.
The platform team owns review; new incidents start as draft. Review at least
every 180 days or after any framework release affecting behavior. The agents
flag stale sources; the index does not silently delete them.

Never ingest customer payloads, credentials, raw tenant logs or instructions to
bypass policy. Test guidance against its applicable environment, and require
explicit approval for any potentially disruptive operational command.

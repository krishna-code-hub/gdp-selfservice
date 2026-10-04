# Long references: index a card, fetch the source

The remote embedding model must respect the input token limit in `config.toml`. A document with
1,218 embedding tokens cannot be encoded whole by that model. Raising a CLI
output budget or Chroma storage limit does not change this input limit.

For long reference material, use two files:

| File | Purpose | Embedded? |
| --- | --- | --- |
| `knowledge/references/cdp-gdp-equivalence.md` | Concise retrieval card: title, summary, metadata, topic terms and a source link | Yes, exactly one embedding of the complete card |
| `reference_documents/cdp-gdp-equivalence.md` | Original full mapping or manual | No; fetched only after the card is selected |

The CDP reference has been migrated to this layout. The full source was preserved
byte-for-byte, including its metadata, mapping table and earlier caveats. The
card keeps the stable ID `REF-003`. The source includes earlier knowledge-gap
statements alongside the added mapping: its owner should reconcile those claims
and version applicability before treating it as definitive.

This changes what “one Markdown → one embedding” applies to: each **indexed
knowledge file** still has exactly one embedding. The long source is outside
the indexed corpus and has no embedding. It is not split into embedded chunks.

## Create another linked reference

1. Put the complete Markdown under `reference_documents/`, not under `knowledge/`.
2. Create a short card under `knowledge/references/` using the normal required metadata.
3. Add `source_file` in its YAML frontmatter, relative to `reference_documents/`.
4. Include common question phrases, capabilities and terminology that identify
   the source. Keep the card focused and below the configured embedding token limit.
5. Give the source unique ATX headings (`## Heading`) for bounded reads.
6. Validate, ingest and evaluate questions against the card's stable ID.

For example, a card's frontmatter includes:

```yaml
id: REF-003
# Other required metadata fields still apply.
source_file: cdp-gdp-equivalence.md
```

The source can be much longer than the configured token limit, up to the toolkit's **2MB file
limit**. Its size is not a license to send it all to Copilot. Read selected
sections when necessary. Troubleshooting guides remain focused complete files;
`source_file` is currently supported only for reference cards.

## Validate and use the reference

Run from the repository root:

```bash
uv run scripts/query.py validate --embedding
uv run scripts/ingest.py
uv run scripts/query.py search --query "CDP equivalent tech stacks in GDP" --kind reference --top-k 3 --budget 1200
uv run scripts/query.py read-reference REF-003 --budget 1800
```

For agent use, also pass `--snapshot` with the snapshot ID returned by search.
If the full reference exceeds the output budget, list its headings and request
a relevant section explicitly:

```bash
uv run scripts/query.py read-reference REF-003 --list-sections --budget 1200
uv run scripts/query.py read-reference REF-003 --section "1. Technology Stack Comparison" --budget 1800
uv run scripts/query.py evaluate --format table
```

The selected section includes its nested subsections up to the next heading of
the same or higher level. The response includes `partial: true`, the heading and
line numbers. Whole-source reads use `partial: false`. Reads fail if the whole
requested output does not fit; they never silently trim a table or procedure.
List headings first if an exact name is unknown. Duplicate heading names cannot
be selected ambiguously. The parser supports ATX headings, not Setext underline
headings, and ignores headings inside fenced code and YAML frontmatter.

If a single section is too large, reorganize the source into narrower meaningful
headings, re-ingest and read those sections. Keep limitations and prerequisites
visible; retrieving an isolated procedure without its applicability can mislead.

## Updates, safety and retrieval quality

Ingestion checks the link exists, confines it to the source directory, rejects
symlinks and records the source's SHA-256 hash. If the full source changes, reads
fail until ingestion refreshes its metadata. Unchanged card embeddings are
reused even when only the source changes. Changes to both files should be reviewed
together. Original full-source frontmatter is preserved as text; the card's
metadata is what controls retrieval status and filters, so owners must keep them
consistent.

`read` and `context` still return the indexed card, not its linked full source.
Agents must use `read-reference` to get evidence before answering. This command
works from the local clone; it does not fetch arbitrary websites or network URLs.
`--sources PATH` can select another authorized local source directory and must
precede the command; use the same directory during validation, ingestion and reads.

Search can find only concepts represented in the card. Information buried in the
full document is not independently searchable. Test varied tenant questions in
`evaluation/retrieval.yaml` and improve the card's search terms when justified.
The evaluator checks card retrieval; manually verify source selection and answers
in Copilot. If one source covers too many unrelated topics, use focused source
documents/cards or consider a different embedding architecture.

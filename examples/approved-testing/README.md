# Approved Markdown test pack

Two reference files and two troubleshooting guides with `status: approved` for
**local testing only**. All have complete metadata and fit the embedding model.
Production authorization is not implied. The SQL/DataFrame contract is explicitly
simulated; the CDP mapping is a subset of the owner's supplied reference.
The OOM log line is a synthetic signature fixture; pending has no error message.

| ID | Category | Question |
| --- | --- | --- |
| TEST-REF-001 | Reference | What are CDP equivalent tech stacks in GDP? |
| TEST-REF-002 | Reference | SQL only or PySpark DataFrames too? |
| TEST-TRN-001 | Troubleshooting | Spark job failed with out-of-memory? |
| TEST-TRN-002 | Troubleshooting | Spark job pending without running? |

Run from the repository root using a separate index so your team's knowledge
and default index remain available:

```bash
uv run scripts/query.py --corpus examples/approved-testing/knowledge validate --embedding
uv run scripts/query.py --db .gdp/approved-testing --corpus examples/approved-testing/knowledge ingest
uv run scripts/query.py --db .gdp/approved-testing --offline evaluate --dataset examples/approved-testing/retrieval.yaml --format table
```

Try a clarification or error:

```bash
uv run scripts/query.py --db .gdp/approved-testing --offline context --query "SQL only or PySpark DataFrames too?" --kind reference --status approved --top-k 1
uv run scripts/query.py --db .gdp/approved-testing --offline context --query "java.lang.OutOfMemoryError: Java heap space" --kind troubleshooting --status approved --top-k 1
```

For a Copilot test, explicitly tell GDP Support:

> Use the local approved test pack and `.gdp/approved-testing` index for this
> conversation. Add `--db .gdp/approved-testing` to retrieval commands. These are
> test-only fixtures; disclose their scope. [Then ask your question.]

Agent defaults still use the normal `.gdp` index. A successful eight-case evaluation
tests retrieval and exact/paraphrased signatures, not production guidance or
end-to-end Copilot behavior. For troubleshooting, verify it performs relevant
checks and drafts the six-field generic ticket from actual results if unresolved.
Do not run Kubernetes commands without appropriate access and real placeholders.

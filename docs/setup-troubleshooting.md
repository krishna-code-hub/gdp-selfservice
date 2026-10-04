# Setup troubleshooting

- **Python 3.14 or older than 3.11:** install Python 3.12 and rerun bootstrap with
  that interpreter. Recreate `.venv` with the supported interpreter when needed.
- **Packages cannot install:** confirm approved registry access, proxy and TLS
  trust, architecture and supported Python. Use `uv sync --frozen --python 3.12`.
  Do not disable certificate verification. CI should reveal platform wheel issues.
- **Remote embedding API unavailable:** check `embedding.endpoint_url`, model name,
  configured API key environment variable, proxy/TLS access and timeout. HTTP errors
  expose only status codes. Re-ingest after changing the model or embedding endpoint.
- **Embedding too long:** the error names the file and actual token count. Shorten
  it or author independently useful focused files. Retain safety and applicability.
- **No index or model mismatch:** run the separate ingestion script. Memory mode
  does not survive process exit. Never query old vectors with a changed model.
- **No matches:** check component/framework/status filters and query vocabulary.
  Example files do not match `--status approved`. Refine once; disclose evidence gaps.
- **Output budget exceeded:** read one ID or fewer hits. The tool will not return
  an incomplete runbook. Inspect `omitted_for_budget` in context output.
- **Snapshot changed:** repeat search and use the new snapshot ID for `read`.
- **Lock timeout:** another build may be running. Wait for it to finish and retry.
  Do not force-unlock an active writer. Rebuilds briefly need two indexes on disk.
- **Local index corrupt:** preserve the source corpus, move the derived `.gdp`
  directory aside after all toolkit processes stop, and rebuild into a fresh path.
  Use `--db` before the subcommand. Never delete the knowledge source to repair DB.

The CLI reports dependency failure class without raw tracebacks to avoid leaking
sensitive error contents. Reproduce setup failures using a benign query and share
only sanitized environment/version information with toolkit maintainers.

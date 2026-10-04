# GDP self service kit

A clone-and-run GitHub Copilot toolkit for data engineers asking GDP platform
questions or diagnosing pasted errors. Copilot reasons from a locally indexed
Markdown corpus; Python performs deterministic, bounded retrieval. Embeddings use a configured remote API; no GDP credentials or custom LLM
service is required.

New to the repository? Read the [beginner's guide](docs/beginners-guide.md) for
a walkthrough of setup, agents, retrieval and knowledge maintenance.

**The included GDP references and runbooks are illustrative samples.** Your
platform team must supply and approve the actual architecture, versions, runtime
commands, owners and escalation routes before operational rollout. The agents
explicitly disclose this boundary.

## What is included

- Five Copilot agents: support router, ingestion, transformation, consumption,
  and knowledge maintainer in `.github/agents/`.
- Three progressively loaded skills in `.github/skills/`.
- Nine failure runbooks and four references under `knowledge/`, including explicit
  knowledge gaps for CDP equivalence and transformation API support.
- Separate cross-platform bootstrap, ingestion and query scripts.
- Local Chroma snapshot indexes, remote embedding API, embedding reuse,
  metadata filters, whole-document validation, token-bounded JSON and CI tests.

## Quick start

Install Python **3.11–3.13**, Git, VS Code and GitHub Copilot with agent mode.
Python 3.12 is the reference development runtime. Clone the platform team's
repository and run commands from its root. Replace the repository URL with the
real one; this toolkit does not assume an organization or remote.

```text
git clone <your-repository-url>
cd <your-repository-folder>
```

One setup script creates the environment and installs packages without activation:

macOS/Linux:

```sh
python3.12 scripts/bootstrap.py --ingest
.venv/bin/python scripts/query.py search --query "ingestion schema mismatch" --component ingestion
```

Windows PowerShell:

```powershell
py -3.12 scripts/bootstrap.py --ingest
.venv\Scripts\python.exe scripts\query.py search --query "ingestion schema mismatch" --component ingestion
```

## Remote embedding and storage configuration

Embedding inference runs through an OpenAI-compatible HTTP API. No embedding model
is downloaded or run locally. The default model is `text-embedding-3-small` at
`https://api.openai.com/v1/embeddings`, following the
[official embeddings API](https://developers.openai.com/api/docs/guides/embeddings).

Edit `config.toml` to set `embedding.model`, `embedding.endpoint_url` (the full POST
URL), `api_key_env`, `query_prefix`, `tokenizer_encoding`, `max_tokens`, `batch_size`
and `timeout_seconds`. Supply the bearer token through the named environment
variable, never through the config file. The default is `OPENAI_API_KEY`:

```sh
export OPENAI_API_KEY="your-api-key"
.venv/bin/python scripts/ingest.py
.venv/bin/python scripts/query.py search --query "schema mismatch"
```

In PowerShell, use `$env:OPENAI_API_KEY = "your-api-key"`. For another provider,
change the model and full endpoint URL, plus the tokenizer and token limit to match
that model. The endpoint must accept `{model, input, encoding_format: "float"}` and
return `{data: [{index, embedding}]}`. Set `api_key_env = ""` for an unauthenticated
server. Configure any model-specific search instruction through `query_prefix`.
Indexed Markdown and search queries are sent to the configured embedding service.

The embedding API and vector storage URLs are independent. `storage.endpoint_url`
remains empty for local Chroma; set it to a Chroma server origin such as
`http://localhost:8000` to store vectors remotely. Its tenant/database must exist.
The local `storage.path` still holds the snapshot manifest and lock; clients sharing
an index must share that directory. Remote cleanup removes only this index's old snapshot.

Use `--config /path/to/config.toml` or `GDP_CONFIG` for another config file:

```sh
.venv/bin/python scripts/ingest.py --config /path/to/config.toml
.venv/bin/python scripts/query.py --config /path/to/config.toml search --query "schema mismatch"
```

Relative storage paths resolve against the config file's directory. `--db` overrides
that path. `--memory` uses an in-memory vector index while still calling the remote
embedding API. Use the same config for ingestion and retrieval. Re-ingest after
switching from local embeddings or changing the model, embedding endpoint, query
prefix or tokenizer. When switching storage endpoints, use a separate storage path
(or `--db`). Remote embeddings require network access; `--offline` has been removed.

For reproducible installation, install `uv` and use the committed full lock:

```sh
uv sync --frozen --python 3.12 --extra dev
uv run --frozen python scripts/ingest.py
```

Bootstrap uses this lock when `uv` is available; otherwise it installs compatible
package ranges with pip and says so. Neither path requires shell activation.
`uv.lock` records transitive dependencies across supported platforms. CI exercises
macOS, Windows and Linux; inspect its results before publishing a release.

## Use in Copilot

Two Markdown categories are available: `knowledge/references/` for clarification,
how-to and migration questions, and `knowledge/troubleshooting/` for incidents.
Agents use `--kind reference` or `--kind troubleshooting` to filter retrieval
before ranking. Rerun ingestion after this update to add category metadata;
unchanged document embeddings are reused.

Open the cloned repository in VS Code and select **GDP Support** in the Copilot
agent picker. Ensure terminal tools are enabled so the agent can run the local
Python retrieval scripts. Ask, for example:

> What should I check for a schema contract mismatch during ingestion?

> Our Spark executor failed with an out-of-memory error. Help me diagnose it.

Sanitize logs before pasting. The agent searches brief metadata, reads selected
sources, cites applicability and proposes one diagnostic decision at a time.
Framework specialists can also be selected directly. The maintainer agent drafts
knowledge updates from sanitized verified incidents.

Custom agent discovery and skills follow [GitHub's agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
and [agent skill documentation](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills).
These profiles target local VS Code/CLI use; cloud agents need their own environment
setup and corpus access. Cloning alone does not install Python dependencies or
provide a cloud agent with your laptop's Chroma index. Python provides evidence,
not a standalone chat interface or automated Copilot SDK integration.

## One Markdown → one embedding

For a long reference, keep the complete document under `reference_documents/`
and index a short card with `source_file` under `knowledge/references/`.
Only the card is embedded; `read-reference` fetches the source after selection,
with optional explicit heading sections. See [long references](docs/long-references.md).

Each complete Markdown file under `knowledge/`, including frontmatter, is encoded once and stored
as one Chroma record. There is no chunker, averaging, sliding window or hidden
truncation. The configured tokenizer and token limit validate each input before submission.
The default limit is 8191 tokens with `cl100k_base`. Focused files are essential: long documents **fail before index mutation**.
See [authoring](docs/authoring.md) for the metadata contract.

Embeddings are generated remotely; Chroma stores the full documents and vectors.
Persistent mode is the default because separate scripts cannot share an ephemeral
in-memory database. Chroma loads/accesses its local index as needed; the complete
corpus is not inserted into Copilot's context. True in-memory mode is available:

```sh
.venv/bin/python scripts/query.py --memory context --query "schema mismatch" --component ingestion --top-k 2 --budget 1800
```

This ingests and searches in **one process** and discards the index on exit. A
separate `ingest --memory` process cannot populate a later query process.
See [architecture](docs/architecture.md) and [tool contract](docs/tool-contract.md).

## Refresh and maintain

After pulling approved knowledge updates, run:

```sh
.venv/bin/python scripts/ingest.py
```

Windows uses `.venv\Scripts\python.exe scripts\ingest.py`. Stable IDs and content
hashes allow unchanged vectors to be reused; changed files are re-embedded,
removed files disappear, and invalid updates leave the previous snapshot usable.
A single writer lock also coordinates readers. Only a completed index is published.

Keep `.gdp/`, the virtual environment, API credentials and tenant errors out of Git.
Govern corpus access through repository permissions. Local Chroma is not a shared
tenant authorization service. If per-tenant restricted runbooks are required,
use separate authorized corpora/indexes or a server enforcing tenant identity;
metadata filters are not security controls.

## Validation

After ingesting knowledge, run the owner-maintained [retrieval evaluation](docs/retrieval-evaluation.md):

```sh
.venv/bin/python scripts/query.py evaluate
```

Windows uses `.venv\Scripts\python.exe`. Edit `evaluation/retrieval.yaml` to add
sanitized tenant questions, expected guide IDs and no-match checks. The command
reports ranks and hit rates and exits nonzero if any case fails.

```sh
uv run --frozen python scripts/query.py validate --embedding
uv run --frozen pytest
uv run --frozen ruff check .
```

The unit/integration suite uses real Chroma with deterministic test vectors and
uses mocked HTTP responses and requires no API credentials. An optional remote-model
smoke test calls the configured API and requires its credentials:

```sh
uv run --frozen python scripts/smoke_test.py
uv run --frozen python scripts/ingest.py
uv run --frozen python scripts/query.py context --query "source authentication expired credential" --component ingestion --top-k 2 --budget 1800
```

See [setup troubleshooting](docs/setup-troubleshooting.md),
[contribution guidance](CONTRIBUTING.md), and the [release checklist](docs/release.md).

"""Small JSON tool surface for Copilot and humans; never invokes a hosted LLM."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import tiktoken

from .config import load_config
from .corpus import COMPONENTS, KINDS, STATUSES, KnowledgeError, load_corpus

ROOT = Path(__file__).resolve().parents[2]


def redact(text: str) -> str:
    """Best-effort common-secret masking; user must sanitize sensitive identifiers too."""
    text = re.sub(r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]+", r"\1 [REDACTED]", text)
    text = re.sub(
        r"(?i)\b(password|token|secret|api[_-]?key)\s*[:=]\s*[^\s,;]+", r"\1=[REDACTED]", text
    )
    text = re.sub(
        r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]+|AKIA[A-Z0-9]{16})\b",
        "[REDACTED]",
        text,
    )
    return text


def render(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def token_count(value) -> int:
    return len(tiktoken.get_encoding("cl100k_base").encode(render(value)))


def bounded(value, budget: int):
    if token_count(value) > budget:
        raise KnowledgeError(
            "Output exceeds token budget. Use fewer results or read one document; "
            "documents are never silently cut. Budget counts cl100k_base JSON tokens, "
            "not the entire Copilot conversation."
        )
    return value


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", type=Path, help="TOML settings (or GDP_CONFIG)")
    p.add_argument("--db", type=Path, help="override configured local index/manifest path")
    p.add_argument("--corpus", type=Path, default=ROOT / "knowledge")
    p.add_argument("--sources", type=Path, default=ROOT / "reference_documents")
    p.add_argument("--memory", action="store_true", help="ingest and query in this process only")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("ingest")
    v = sub.add_parser("validate")
    v.add_argument("--embedding", action="store_true", help="also check model tokenizer limits")
    sub.add_parser("status")
    e = sub.add_parser("evaluate", help="check budgeted search against a YAML dataset")
    e.add_argument("--dataset", type=Path, default=ROOT / "evaluation/retrieval.yaml")
    e.add_argument("--format", choices=("json", "table"), default="json")
    for name in ("search", "context"):
        q = sub.add_parser(name)
        group = q.add_mutually_exclusive_group(required=True)
        group.add_argument("--query")
        group.add_argument(
            "--query-file", type=Path, help="use - for stdin; avoid shell interpolation"
        )
        q.add_argument("--component", choices=sorted(COMPONENTS))
        q.add_argument("--framework")
        q.add_argument("--status", choices=sorted(STATUSES))
        q.add_argument("--kind", choices=sorted(KINDS), help="filter the document category")
        q.add_argument("--top-k", type=int, choices=range(1, 11), default=5)
        q.add_argument("--max-distance", type=float, default=0.65)
        q.add_argument("--budget", type=int, default=1800)
    r = sub.add_parser("read")
    r.add_argument("ids", nargs="+")
    r.add_argument("--snapshot")
    r.add_argument("--budget", type=int, default=1800)
    ref = sub.add_parser("read-reference", help="fetch linked full reference or an explicit section")
    ref.add_argument("id")
    ref.add_argument("--snapshot")
    selection = ref.add_mutually_exclusive_group()
    selection.add_argument("--section", help="exact ATX heading text, without # markers")
    selection.add_argument("--list-sections", action="store_true")
    ref.add_argument("--budget", type=int, default=1800)
    return p


def run(args):
    if args.command == "evaluate":
        from .evaluation import evaluate, load_dataset

        cases = load_dataset(args.dataset)
    if getattr(args, "budget", 1800) < 128 or getattr(args, "budget", 1800) > 8000:
        raise KnowledgeError("budget must be between 128 and 8000")
    if args.command == "validate" and not args.embedding:
        docs = load_corpus(args.corpus, args.sources)
        return {"documents": len(docs), "schema": "valid", "embedding_length": "not checked"}
    from .embedding import RemoteEmbedder

    config = load_config(args.config)
    embedder = RemoteEmbedder(config=config.embedding)
    if args.command == "validate":
        docs = load_corpus(args.corpus, args.sources)
        counts = {d.id: embedder.validate(d.text, d.metadata["source"]) for d in docs}
        return {"documents": len(docs), "embedding_tokens": counts, "limit": embedder.limit}
    from .store import Store

    store = Store(args.db or config.storage.path, embedder, args.memory, config.storage)
    if args.command == "ingest":
        return {
            **store.ingest(args.corpus, args.sources),
            "memory": args.memory,
            "note": "Memory is discarded on process exit."
            if args.memory
            else "Snapshot persisted.",
        }
    if args.memory:
        store.ingest(args.corpus, args.sources)
    if args.command == "status":
        return store.status()
    if args.command == "evaluate":
        return evaluate(store, cases)
    if args.command == "read-reference":
        from .references import fetch_reference

        evidence = fetch_reference(
            store, args.sources, args.id, args.snapshot, args.section, args.list_sections
        )
        if token_count(evidence) > args.budget:
            raise KnowledgeError(
                "Reference output exceeds budget; use read-reference --list-sections and "
                "--section with a focused heading. No reference was silently truncated."
            )
        return bounded(evidence, args.budget)
    if args.command == "read":
        if len(args.ids) > 3 or len(args.ids) != len(set(args.ids)):
            raise KnowledgeError("Read one to three distinct document IDs per step")
        return bounded({"documents": store.read(args.ids, args.snapshot)}, args.budget)
    if not 0 <= args.max_distance <= 2:
        raise KnowledgeError("Cosine max-distance must be between 0 and 2")
    if args.query_file:
        if str(args.query_file) == "-":
            query = sys.stdin.read(64_001)
        else:
            if args.query_file.stat().st_size > 64_000:
                raise KnowledgeError("Query file exceeds 64KB; extract the relevant error")
            query = args.query_file.read_text(encoding="utf-8")
    else:
        query = args.query
    if not query.strip() or len(query.encode()) > 64_000:
        raise KnowledgeError("Query must be nonempty and at most 64KB")
    result = store.search(
        redact(query), args.top_k, args.component, args.framework, args.status, args.max_distance,
        args.kind,
    )
    if args.command == "search":
        while result["matches"] and token_count(result) > args.budget:
            result["matches"].pop()
        return bounded(result, args.budget)
    output = {
        "snapshot": result["snapshot"],
        "documents": [],
        "omitted_for_budget": 0,
        "note": result["note"],
    }
    for doc in (
        store.read([m["id"] for m in result["matches"]], result["snapshot"])
        if result["matches"]
        else []
    ):
        candidate = {**output, "documents": output["documents"] + [doc]}
        if token_count(candidate) <= args.budget - 32:
            output["documents"].append(doc)
        else:
            output["omitted_for_budget"] += 1
    return bounded(output, args.budget)


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = run(args)
        if args.command == "evaluate" and args.format == "table":
            from .evaluation import render_table

            print(render_table(result))
        else:
            print(render(result))
        return 1 if args.command == "evaluate" and result["failed"] else 0
    except (KnowledgeError, OSError, TimeoutError) as exc:
        print(
            render(
                {"error": str(exc), "action": "Check configuration and retry the indicated step."}
            ),
            file=sys.stderr,
        )
        return 2
    except Exception as exc:
        # Do not expose query contents or credentials through third-party exception tracebacks.
        print(
            render(
                {
                    "error": type(exc).__name__,
                    "action": "Check embedding API/network, dependency versions, and index permissions; "
                    "use the setup troubleshooting guide.",
                }
            ),
            file=sys.stderr,
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())

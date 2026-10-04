"""Strict Markdown ingestion: a complete file is one immutable document."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml


class KnowledgeError(ValueError):
    """An actionable validation or retrieval failure."""


@dataclass(frozen=True)
class Document:
    id: str
    text: str
    metadata: dict


COMPONENTS = {"ingestion", "transformation", "consumption", "platform"}
STATUSES = {"example", "approved", "draft"}
KINDS = {"reference", "troubleshooting"}
MAX_FILE_BYTES = 64_000


def load_corpus(root: Path, reference_root: Path | None = None) -> list[Document]:
    root = root.resolve()
    reference_root = reference_root or root.parent / "reference_documents"
    if not root.is_dir():
        raise KnowledgeError(f"Knowledge directory does not exist: {root}")
    docs = []
    seen = set()
    for path in sorted(root.rglob("*.md")):
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise KnowledgeError(f"Symlinks/out-of-root references are forbidden: {path.name}")
        source = path.relative_to(root).as_posix()
        if path.stat().st_size > MAX_FILE_BYTES:
            raise KnowledgeError(f"{source}: exceeds {MAX_FILE_BYTES} bytes; author a focused file")
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if not lines or lines[0].strip() != "---" or end is None:
            raise KnowledgeError(f"{source}: requires YAML frontmatter delimited by ---")
        frontmatter = "".join(lines[1:end])
        body = "".join(lines[end + 1 :])
        try:
            data = yaml.safe_load(frontmatter)
        except yaml.YAMLError as exc:
            raise KnowledgeError(f"{source}: invalid YAML") from exc
        if not isinstance(data, dict):
            raise KnowledgeError(f"{source}: metadata must be a mapping")
        required = (
            "id",
            "title",
            "summary",
            "component",
            "framework",
            "owner",
            "status",
            "reviewed",
            "version",
        )
        for field in required:
            if not isinstance(data.get(field), str) or not data[field].strip():
                raise KnowledgeError(f"{source}: {field} must be a nonempty string (quote dates)")
        if len(data["summary"]) > 320 or len(data["title"]) > 120:
            raise KnowledgeError(f"{source}: title/summary exceeds retrieval metadata limit")
        if data["component"] not in COMPONENTS or data["status"] not in STATUSES:
            raise KnowledgeError(f"{source}: invalid component or status")
        try:
            date.fromisoformat(data["reviewed"])
        except ValueError as exc:
            raise KnowledgeError(f"{source}: reviewed must be YYYY-MM-DD") from exc
        if data["id"] in seen:
            raise KnowledgeError(f"{source}: duplicate document ID {data['id']}")
        if not body.strip():
            raise KnowledgeError(f"{source}: empty Markdown body")
        seen.add(data["id"])
        metadata = {key: data[key] for key in required if key != "id"}
        metadata.update(source=source, sha256=hashlib.sha256(text.encode()).hexdigest())
        metadata["kind"] = {"references": "reference", "troubleshooting": "troubleshooting"}.get(
            source.split("/")[0], "unclassified"
        )
        if "source_file" in data:
            if metadata["kind"] != "reference" or not isinstance(data["source_file"], str):
                raise KnowledgeError(f"{source}: source_file is only valid on reference cards")
            from .references import load_reference

            _, source_hash = load_reference(reference_root, data["source_file"])
            metadata.update(source_file=data["source_file"], source_sha256=source_hash)
        docs.append(Document(data["id"], text, metadata))
    if not docs:
        raise KnowledgeError("No Markdown documents found; refusing to replace a working index")
    return docs

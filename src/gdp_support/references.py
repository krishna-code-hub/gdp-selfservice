"""Fetch linked reference evidence without embedding or silently truncating it."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path, PurePosixPath

from .corpus import KnowledgeError

MAX_REFERENCE_BYTES = 2_000_000


def load_reference(root: Path, source_file: str):
    relative = PurePosixPath(source_file)
    if (
        not source_file or "\\" in source_file or relative.is_absolute()
        or ".." in relative.parts or relative.suffix != ".md"
    ):
        raise KnowledgeError("source_file must be a relative .md path inside reference_documents")
    root = root.resolve()
    path = root
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise KnowledgeError("Linked reference symlinks are forbidden")
    if not path.resolve().is_relative_to(root) or not path.is_file():
        raise KnowledgeError(f"Linked reference missing or outside source directory: {source_file}")
    if path.stat().st_size > MAX_REFERENCE_BYTES:
        raise KnowledgeError(f"{source_file}: linked reference exceeds 2MB")
    data = path.read_bytes()
    if len(data) > MAX_REFERENCE_BYTES:
        raise KnowledgeError(f"{source_file}: linked reference exceeds 2MB")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise KnowledgeError(f"{source_file}: reference must be UTF-8") from exc
    if not text.strip():
        raise KnowledgeError(f"{source_file}: linked reference is empty")
    return text, hashlib.sha256(data).hexdigest()


def headings(text):
    """Find ATX headings outside frontmatter and fenced code; line indexes are zero-based."""
    lines = text.splitlines(keepends=True)
    found = []
    frontmatter = bool(lines and lines[0].strip() == "---")
    fence = None
    for i, line in enumerate(lines):
        if frontmatter:
            if i and line.strip() == "---":
                frontmatter = False
            continue
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            value = marker[1]
            if fence is None:
                fence = value
            elif value[0] == fence[0] and len(value) >= len(fence) and not line[marker.end():].strip():
                fence = None
            continue
        if fence:
            continue
        match = re.match(r"^ {0,3}(#{1,6})[ \t]+(.+?)\s*$", line)
        if match:
            title = re.sub(r"\s+#+\s*$", "", match[2]).strip()
            found.append({"heading": title, "level": len(match[1]), "line": i + 1})
    return lines, found


def fetch_reference(store, root: Path, id_: str, snapshot=None, section=None, list_sections=False):
    card = store.read([id_], snapshot)[0]
    if card.get("kind") != "reference" or not card.get("source_file"):
        raise KnowledgeError("Document is not a reference card with source_file")
    text, digest = load_reference(root, card["source_file"])
    if digest != card.get("source_sha256"):
        raise KnowledgeError("Linked reference changed after ingestion; re-ingest before reading")
    lines, sections = headings(text)
    result = {k: card[k] for k in (
        "id", "title", "owner", "status", "reviewed", "version", "source", "source_file"
    )}
    result["source_sha256"] = digest
    if list_sections:
        return {**result, "sections": sections}
    if section:
        matches = [s for s in sections if s["heading"] == section]
        if len(matches) != 1:
            raise KnowledgeError("Section heading must match exactly one heading; list sections first")
        selected = matches[0]
        start = selected["line"] - 1
        stop = next((s["line"] - 1 for s in sections
                     if s["line"] > selected["line"] and s["level"] <= selected["level"]), len(lines))
        return {**result, "section": section, "partial": True,
                "start_line": start + 1, "end_line": stop,
                "markdown": "".join(lines[start:stop])}
    return {**result, "partial": False, "markdown": text}

"""Snapshot indexes: failed rebuilds never publish partial knowledge."""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit

import chromadb
from chromadb.config import Settings
from filelock import FileLock

from .config import StorageConfig
from .corpus import KnowledgeError, load_corpus


class Store:
    def __init__(
        self, root: Path, embedder, memory: bool = False, config: StorageConfig | None = None
    ):
        self.root = root.resolve()
        self.embedder = embedder
        self.memory = memory
        self.remote = bool(config and config.endpoint_url) and not memory
        self.storage_identity = (
            f"{config.endpoint_url.rstrip('/')}|{config.tenant}|{config.database}"
            if self.remote else "local"
        )
        self.manifest = None
        settings = Settings(anonymized_telemetry=False)
        if memory:
            self.client = chromadb.EphemeralClient(settings=settings)
        else:
            self.root.mkdir(parents=True, exist_ok=True)
            if config and config.endpoint_url:
                url = urlsplit(config.endpoint_url)
                self.client = chromadb.HttpClient(
                    host=url.hostname, port=url.port or (443 if url.scheme == "https" else 80),
                    ssl=url.scheme == "https", settings=settings,
                    tenant=config.tenant, database=config.database,
                )
                return
            self.client = chromadb.PersistentClient(
                path=str(self.root / "chroma"), settings=settings
            )

    @contextmanager
    def locked(self):
        if self.memory:
            yield
        else:
            with FileLock(str(self.root / "index.lock"), timeout=60):
                yield

    def _manifest(self):
        if self.memory:
            return self.manifest
        path = self.root / "manifest.json"
        if not path.exists():
            return None
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            raise KnowledgeError("Unreadable index manifest; rebuild using ingest") from exc
        if manifest.get("storage_identity", "local") != self.storage_identity:
            raise KnowledgeError(
                "Storage endpoint changed. Use a separate storage.path or --db directory "
                "and ingest before querying."
            )
        return manifest

    def _collection(self):
        manifest = self._manifest()
        if not manifest:
            raise KnowledgeError(
                "No index. Run scripts/ingest.py first; memory mode must ingest here."
            )
        if manifest["embedding"] != self.embedder.signature:
            raise KnowledgeError("Embedding model changed. Re-ingest before querying.")
        return self.client.get_collection(manifest["collection"], embedding_function=None), manifest

    def ingest(self, corpus: Path, reference_root: Path | None = None):
        docs = load_corpus(corpus, reference_root)
        for doc in docs:
            self.embedder.validate(doc.text, doc.metadata["source"])
        fingerprint = hashlib.sha256(
            json.dumps([
                (d.id, d.metadata)
                for d in docs
            ]).encode()
        ).hexdigest()
        with self.locked():
            old = self._manifest()
            if (
                old
                and old["embedding"] == self.embedder.signature
                and old["fingerprint"] == fingerprint
            ):
                collection, _ = self._collection()
                if collection.count() == len(docs):
                    return {"documents": len(docs), "embedded": 0, "unchanged": True}
            previous = None
            if old and old["embedding"] == self.embedder.signature:
                previous = self.client.get_collection(old["collection"], embedding_function=None)
            name = "gdp-" + uuid.uuid4().hex
            collection = self.client.create_collection(
                name, embedding_function=None, metadata={"hnsw:space": "cosine"}
            )
            embedded = 0
            temporary = None
            try:
                for offset in range(0, len(docs), 32):
                    batch = docs[offset : offset + 32]
                    cached = {}
                    if previous is not None:
                        values = previous.get(
                            ids=[d.id for d in batch], include=["embeddings", "metadatas"]
                        )
                        cached = {
                            id_: (meta["sha256"], vector.tolist())
                            for id_, meta, vector in zip(
                                values["ids"],
                                values["metadatas"],
                                values["embeddings"],
                                strict=True,
                            )
                        }
                    changed = [
                        d
                        for d in batch
                        if d.id not in cached or cached[d.id][0] != d.metadata["sha256"]
                    ]
                    vectors = self.embedder.documents([d.text for d in changed]) if changed else []
                    fresh = dict(zip([d.id for d in changed], vectors, strict=True))
                    embedded += len(changed)
                    collection.add(
                        ids=[d.id for d in batch],
                        documents=[d.text for d in batch],
                        metadatas=[d.metadata for d in batch],
                        embeddings=[
                            fresh[d.id] if d.id in fresh else cached[d.id][1] for d in batch
                        ],
                    )
                manifest = {
                    "collection": name,
                    "storage_identity": self.storage_identity,
                    "embedding": self.embedder.signature,
                    "fingerprint": fingerprint,
                    "documents": len(docs),
                    "retrieval_schema": 2,
                }
                if self.memory:
                    self.manifest = manifest
                else:
                    temporary = self.root / (name + ".json")
                    with temporary.open("w", encoding="utf-8") as stream:
                        json.dump(manifest, stream)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.replace(temporary, self.root / "manifest.json")
            except Exception:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
                self.client.delete_collection(name)
                raise
            # Readers share this lock, so old snapshots can now be removed safely.
            # A crash may leave an orphan; remove orphans on the next successful build.
            for candidate in self.client.list_collections():
                if (
                    candidate.name.startswith("gdp-")
                    and candidate.name != name
                    and (
                        (not self.memory and not self.remote)
                        or (old and candidate.name == old["collection"])
                    )
                ):
                    self.client.delete_collection(candidate.name)
            return {"documents": len(docs), "embedded": embedded, "unchanged": False}

    def search(
        self,
        query: str,
        top_k: int = 5,
        component: str | None = None,
        framework: str | None = None,
        status: str | None = None,
        max_distance: float = 0.65,
        kind: str | None = None,
    ):
        clauses = [
            {key: value}
            for key, value in (
                ("component", component),
                ("framework", framework),
                ("status", status),
                ("kind", kind),
            )
            if value
        ]
        where = clauses[0] if len(clauses) == 1 else {"$and": clauses} if clauses else None
        with self.locked():
            collection, manifest = self._collection()
            if kind and manifest.get("retrieval_schema") != 2:
                raise KnowledgeError("Category metadata missing; run scripts/ingest.py first")
            result = collection.query(
                query_embeddings=[self.embedder.query(query)],
                n_results=min(top_k, collection.count()),
                where=where,
                include=["metadatas", "distances"],
            )
            hits = []
            for id_, meta, distance in zip(
                result["ids"][0], result["metadatas"][0], result["distances"][0], strict=True
            ):
                if distance <= max_distance:
                    hits.append({"id": id_, "distance": round(distance, 4), **meta})
            return {
                "snapshot": manifest["collection"],
                "matches": hits,
                "note": "Distance ranks evidence; it is not a probability of correctness.",
            }

    def read(self, ids: list[str], snapshot: str | None = None):
        with self.locked():
            collection, manifest = self._collection()
            if snapshot and snapshot != manifest["collection"]:
                raise KnowledgeError(
                    "Index changed after search; search again before reading evidence"
                )
            result = collection.get(ids=ids, include=["documents", "metadatas"])
            found = {
                id_: {"id": id_, **meta, "markdown": text}
                for id_, text, meta in zip(
                    result["ids"], result["documents"], result["metadatas"], strict=True
                )
            }
            if set(ids) - found.keys():
                raise KnowledgeError("Unknown document ID; search before reading")
            return [found[id_] for id_ in ids]

    def status(self):
        with self.locked():
            collection, manifest = self._collection()
            return {**manifest, "actual_documents": collection.count(), "memory": self.memory}

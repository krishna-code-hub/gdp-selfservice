"""External TOML settings shared by ingestion and retrieval."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .corpus import KnowledgeError

DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config.toml"


@dataclass(frozen=True)
class EmbeddingConfig:
    model: str
    endpoint_url: str
    api_key_env: str
    query_prefix: str
    tokenizer_encoding: str
    max_tokens: int
    timeout_seconds: float
    batch_size: int


@dataclass(frozen=True)
class StorageConfig:
    path: Path
    endpoint_url: str
    tenant: str
    database: str


@dataclass(frozen=True)
class Config:
    embedding: EmbeddingConfig
    storage: StorageConfig


def load_config(path: Path | None = None) -> Config:
    path = Path(path or os.environ.get("GDP_CONFIG", DEFAULT_CONFIG)).resolve()
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        if set(data) - {"embedding", "storage"}:
            raise ValueError("unknown configuration section")
        embedding = data["embedding"]
        storage = data["storage"]
        if set(embedding) - {"model", "endpoint_url", "api_key_env", "query_prefix",
                              "tokenizer_encoding", "max_tokens", "timeout_seconds", "batch_size"}:
            raise ValueError("unknown embedding setting")
        if set(storage) - {"path", "endpoint_url", "tenant", "database"}:
            raise ValueError("unknown storage setting")
        for section, keys in ((embedding, ("model", "endpoint_url", "tokenizer_encoding")),
                              (storage, ("path", "tenant", "database"))):
            for key in keys:
                if not isinstance(section[key], str) or not section[key].strip():
                    raise ValueError(f"{key} must be a nonempty string")
        for section, key in ((embedding, "query_prefix"), (embedding, "api_key_env"),
                             (storage, "endpoint_url")):
            if not isinstance(section[key], str):
                raise ValueError(f"{key} must be a string")
        for key in ("batch_size", "max_tokens"):
            if type(embedding[key]) is not int or embedding[key] < 1:
                raise ValueError(f"{key} must be a positive integer")
        timeout = embedding["timeout_seconds"]
        if type(timeout) not in (int, float) or not 0 < timeout <= 3600:
            raise ValueError("timeout_seconds must be between 0 and 3600")
        remote = urlsplit(embedding["endpoint_url"])
        if (remote.scheme not in {"http", "https"} or not remote.hostname
                or remote.username or remote.password or remote.fragment):
            raise ValueError("embedding.endpoint_url must be an HTTP(S) URL without credentials")
        _ = remote.port
        endpoint = storage["endpoint_url"]
        if endpoint:
            url = urlsplit(endpoint)
            if (url.scheme not in {"http", "https"} or not url.hostname
                    or url.username or url.password or url.query or url.fragment
                    or url.path not in {"", "/"}):
                raise ValueError("endpoint_url must be an HTTP(S) server origin")
            _ = url.port  # Validate the port before initializing any clients.
        return Config(
            EmbeddingConfig(
                model=embedding["model"], endpoint_url=embedding["endpoint_url"],
                api_key_env=embedding["api_key_env"], query_prefix=embedding["query_prefix"],
                tokenizer_encoding=embedding["tokenizer_encoding"],
                max_tokens=embedding["max_tokens"], timeout_seconds=timeout,
                batch_size=embedding["batch_size"],
            ),
            StorageConfig((path.parent / storage["path"]).resolve(), endpoint,
                          storage["tenant"], storage["database"]),
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise KnowledgeError(f"Invalid configuration in {path}: {exc}") from exc

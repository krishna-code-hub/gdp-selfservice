"""Remote embeddings with whole-input validation and verified response ordering."""

from __future__ import annotations

import hashlib
import json
import math
import os

import httpx
import tiktoken

from .config import EmbeddingConfig, load_config
from .corpus import KnowledgeError


class RemoteEmbedder:
    def __init__(self, config: EmbeddingConfig | None = None):
        self.config = config or load_config().embedding
        try:
            self.tokenizer = tiktoken.get_encoding(self.config.tokenizer_encoding)
        except ValueError as exc:
            raise KnowledgeError("Unknown embedding tokenizer_encoding") from exc
        self.limit = self.config.max_tokens
        identity = (self.config.model, self.config.endpoint_url, self.config.query_prefix,
                    self.config.tokenizer_encoding, "normalized:whole-markdown:remote:v1")
        self.signature = "remote:" + hashlib.sha256(json.dumps(identity).encode()).hexdigest()

    def validate(self, text: str, label: str = "document") -> int:
        if not text.strip():
            raise KnowledgeError(f"{label}: embedding input must be nonempty")
        count = len(self.tokenizer.encode(text, disallowed_special=()))
        if count > self.limit:
            raise KnowledgeError(
                f"{label}: {count} embedding tokens exceeds model limit {self.limit}; "
                "shorten the Markdown or use a short reference card. "
                "No embedding has been split or silently truncated."
            )
        return count

    def _request(self, texts: list[str]) -> list[list[float]]:
        headers = {}
        if self.config.api_key_env:
            key = os.environ.get(self.config.api_key_env)
            if not key:
                raise KnowledgeError(
                    f"Set {self.config.api_key_env} for the remote embedding API"
                )
            headers["Authorization"] = f"Bearer {key}"
        try:
            # Redirects are disabled to keep credentials on the configured endpoint.
            with httpx.Client(timeout=self.config.timeout_seconds, follow_redirects=False) as client:
                response = client.post(
                    self.config.endpoint_url, headers=headers,
                    json={"model": self.config.model, "input": texts, "encoding_format": "float"},
                )
                response.raise_for_status()
                data = response.json()["data"]
        except httpx.HTTPStatusError as exc:
            raise KnowledgeError(
                f"Remote embedding API returned HTTP {exc.response.status_code}; "
                "check credentials, model, input limits and endpoint configuration"
            ) from None
        except httpx.RequestError:
            raise KnowledgeError("Remote embedding API connection failed or timed out") from None
        except (ValueError, KeyError, TypeError):
            raise KnowledgeError("Invalid remote embedding response") from None
        try:
            if not isinstance(data, list) or len(data) != len(texts):
                raise ValueError
            ordered = {}
            dimension = None
            for item in data:
                index, vector = item["index"], item["embedding"]
                if (type(index) is not int or index not in range(len(texts)) or index in ordered
                        or not isinstance(vector, list) or not vector):
                    raise ValueError
                if any(type(v) not in (int, float) or not math.isfinite(v) for v in vector):
                    raise ValueError
                if dimension is not None and len(vector) != dimension:
                    raise ValueError
                dimension = len(vector)
                norm = math.hypot(*vector)
                if not norm or not math.isfinite(norm):
                    raise ValueError
                ordered[index] = [v / norm for v in vector]
            return [ordered[i] for i in range(len(texts))]
        except (ValueError, KeyError, TypeError, OverflowError):
            raise KnowledgeError("Invalid remote embedding vectors or response indices") from None

    def documents(self, texts: list[str]) -> list[list[float]]:
        for text in texts:
            self.validate(text)
        vectors = []
        for offset in range(0, len(texts), self.config.batch_size):
            vectors.extend(self._request(texts[offset:offset + self.config.batch_size]))
        if vectors and any(len(v) != len(vectors[0]) for v in vectors):
            raise KnowledgeError("Remote embedding dimensions changed between batches")
        return vectors

    def query(self, text: str) -> list[float]:
        value = self.config.query_prefix + text
        self.validate(value, "query; extract the relevant error and component")
        return self._request([value])[0]

import math
import re

import pytest
import yaml

from gdp_support.corpus import KnowledgeError


class TestEmbedder:
    """Deterministic vectors for real DB tests, not a production embedding alternative."""

    signature = "test-vector-v1"
    words = ("auth", "schema", "spark", "freshness", "network", "dbt")

    def __init__(self):
        self.embedded = 0
        self.fail = False

    def validate(self, text, label="document"):
        if "OVERSIZED" in text:
            raise KnowledgeError(f"{label}: too long")
        return len(text.split())

    def vector(self, text):
        words = re.findall(r"\w+", text.lower())
        values = [float(words.count(word)) for word in self.words] + [0.1]
        norm = math.sqrt(sum(v * v for v in values))
        return [v / norm for v in values]

    def documents(self, texts):
        if self.fail:
            raise RuntimeError("simulated embedding failure")
        self.embedded += len(texts)
        return [self.vector(text) for text in texts]

    def query(self, text):
        return self.vector(text)


@pytest.fixture
def embedder():
    return TestEmbedder()


@pytest.fixture
def corpus(tmp_path):
    root = tmp_path / "knowledge"
    root.mkdir()
    return root


def write_doc(
    root,
    id_="ING-001",
    body="auth credential failed",
    component="ingestion",
    status="approved",
    name=None,
):
    meta = dict(
        id=id_,
        title=id_,
        summary=body[:60],
        component=component,
        framework="test",
        owner="framework-team",
        status=status,
        reviewed="2026-10-03",
        version="1.0",
    )
    path = root / (name or f"{id_}.md")
    path.write_text("---\n" + yaml.safe_dump(meta) + "---\n# Runbook\n" + body, encoding="utf-8")
    return path

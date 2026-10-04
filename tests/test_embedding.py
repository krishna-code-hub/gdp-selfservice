import json
from dataclasses import replace

import httpx
import pytest
from conftest import write_doc

from gdp_support.config import load_config
from gdp_support.corpus import KnowledgeError
from gdp_support.embedding import RemoteEmbedder
from gdp_support.store import Store


def transport(monkeypatch, handler):
    original = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: original(
        transport=httpx.MockTransport(handler), **kwargs
    ))


def settings(**kwargs):
    return replace(load_config().embedding, **kwargs)


def test_requests_auth_batching_prefix_and_order(monkeypatch):
    calls = []
    monkeypatch.setenv("TEST_EMBEDDING_KEY", "test-key")

    def handle(request):
        calls.append(request)
        body = json.loads(request.content)
        return httpx.Response(200, json={"data": [
            {"index": i, "embedding": [3, 4]} for i in reversed(range(len(body["input"])))
        ]})

    transport(monkeypatch, handle)
    embedding = RemoteEmbedder(settings(endpoint_url="https://embedding.example/v1/embeddings",
                                        model="remote-model", api_key_env="TEST_EMBEDDING_KEY",
                                        query_prefix="query: ", batch_size=2))
    assert embedding.documents(["one", "two", "three"]) == [[0.6, 0.8]] * 3
    assert [json.loads(r.content)["input"] for r in calls] == [["one", "two"], ["three"]]
    assert calls[0].headers["Authorization"] == "Bearer test-key"
    assert str(calls[0].url) == "https://embedding.example/v1/embeddings"
    assert json.loads(calls[0].content)["model"] == "remote-model"
    embedding.query("hello")
    assert json.loads(calls[-1].content)["input"] == ["query: hello"]


def test_missing_key_and_length_fail_before_request(monkeypatch):
    monkeypatch.delenv("TEST_MISSING_KEY", raising=False)
    transport(monkeypatch, lambda request: pytest.fail("unexpected HTTP call"))
    embedding = RemoteEmbedder(settings(api_key_env="TEST_MISSING_KEY", max_tokens=2))
    with pytest.raises(KnowledgeError, match="Set TEST_MISSING_KEY"):
        embedding.query("hello")
    with pytest.raises(KnowledgeError, match="exceeds model limit"):
        embedding.documents(["short", "one two three"])
    assert embedding.documents([]) == []


@pytest.mark.parametrize("data", [
    [], [{"index": 1, "embedding": [1, 2]}],
    [{"index": 0, "embedding": []}], [{"index": 0, "embedding": [0, 0]}],
    [{"index": 0, "embedding": [float("nan")]}],
    [{"index": 0, "embedding": ["value"]}],
])
def test_invalid_remote_vectors(monkeypatch, data):
    transport(monkeypatch, lambda r: httpx.Response(
        200, content=json.dumps({"data": data}).encode()
    ))
    with pytest.raises(KnowledgeError, match="Invalid remote embedding"):
        RemoteEmbedder(settings(api_key_env="")).query("hello")


def test_response_order_is_restored(monkeypatch):
    transport(monkeypatch, lambda r: httpx.Response(200, json={"data": [
        {"index": 1, "embedding": [0, 1]}, {"index": 0, "embedding": [1, 0]}
    ]}))
    assert RemoteEmbedder(settings(api_key_env="")).documents(["a", "b"]) == [[1, 0], [0, 1]]


@pytest.mark.parametrize("status", [302, 401, 429, 500])
def test_http_failure_preserves_snapshot_and_masks_body(tmp_path, corpus, monkeypatch, status):
    failed = False

    def handle(request):
        if failed:
            return httpx.Response(status, text="secret=do-not-print query-private")
        return httpx.Response(200, json={"data": [{"index": 0, "embedding": [1, 0]}]})

    transport(monkeypatch, handle)
    embedding = RemoteEmbedder(settings(api_key_env=""))
    write_doc(corpus)
    store = Store(tmp_path / "db", embedding)
    store.ingest(corpus)
    old = store.status()["collection"]
    write_doc(corpus, body="changed document")
    failed = True
    with pytest.raises(KnowledgeError, match=f"HTTP {status}") as error:
        store.ingest(corpus)
    assert "do-not-print" not in str(error.value)
    assert store.status()["collection"] == old


def test_timeout_is_actionable(monkeypatch):
    def handle(request):
        raise httpx.ReadTimeout("sensitive server content", request=request)

    transport(monkeypatch, handle)
    with pytest.raises(KnowledgeError, match="connection failed or timed out"):
        RemoteEmbedder(settings(api_key_env="")).query("hello")


def test_model_endpoint_prefix_changes_require_rebuild():
    config = settings(api_key_env="")
    signature = RemoteEmbedder(config).signature
    for changed in (replace(config, model="other"), replace(config, query_prefix="query: "),
                    replace(config, endpoint_url="https://other.example/embeddings")):
        assert RemoteEmbedder(changed).signature != signature

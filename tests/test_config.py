from dataclasses import replace

import pytest

from gdp_support.config import DEFAULT_CONFIG, load_config
from gdp_support.corpus import KnowledgeError
from gdp_support.store import Store


def test_config_relative_path_environment_and_explicit_precedence(tmp_path, monkeypatch):
    config = tmp_path / "settings.toml"
    config.write_text(DEFAULT_CONFIG.read_text().replace('path = ".gdp"', 'path = "vectors"'))
    monkeypatch.setenv("GDP_CONFIG", str(config))
    assert load_config().storage.path == tmp_path / "vectors"
    assert load_config(DEFAULT_CONFIG).storage.path == DEFAULT_CONFIG.parent / ".gdp"


@pytest.mark.parametrize("old,new", [
    ('batch_size = 16', 'batch_size = 0'),
    ('batch_size = 16', 'batch_size = true'),
    ('endpoint_url = ""', 'endpoint_url = "ftp://localhost"'),
    ('endpoint_url = ""', 'endpoint_url = "https://localhost/api"'),
    ('endpoint_url = ""', 'endpoint_url = "http://localhost:invalid"'),
    ('model = "text-embedding-3-small"', 'model = ""'),
    ('max_tokens = 8191', 'max_token = 8191'),
])
def test_invalid_configuration(tmp_path, old, new):
    path = tmp_path / "bad.toml"
    path.write_text(DEFAULT_CONFIG.read_text().replace(old, new))
    with pytest.raises(KnowledgeError, match="Invalid configuration"):
        load_config(path)


def test_remote_client_and_memory_override(tmp_path, embedder, monkeypatch):
    import chromadb

    calls = []
    monkeypatch.setattr(chromadb, "HttpClient", lambda **kwargs: calls.append(kwargs))
    settings = replace(load_config().storage, endpoint_url="https://vectors.example:8443",
                       tenant="team", database="knowledge")
    Store(tmp_path, embedder, config=settings)
    assert calls[0]["host"] == "vectors.example"
    assert calls[0]["port"] == 8443
    assert calls[0]["ssl"] is True
    assert calls[0]["tenant"] == "team"
    assert calls[0]["database"] == "knowledge"
    Store(tmp_path, embedder, memory=True, config=settings)
    assert len(calls) == 1


def test_remote_cleanup_preserves_other_indexes(tmp_path, corpus, embedder, monkeypatch):
    import chromadb
    from conftest import write_doc

    # Exercise the full remote storage path using a real isolated local Chroma client.
    client = chromadb.PersistentClient(path=str(tmp_path / "server"))
    foreign = client.create_collection("gdp-other-index")
    monkeypatch.setattr(chromadb, "HttpClient", lambda **kwargs: client)
    settings = replace(load_config().storage, endpoint_url="http://localhost:8000")
    write_doc(corpus)
    store = Store(tmp_path / "manifest", embedder, config=settings)
    store.ingest(corpus)
    previous = store.status()["collection"]
    write_doc(corpus, body="changed auth document")
    store.ingest(corpus)
    names = [collection.name for collection in client.list_collections()]
    assert foreign.name in names
    assert previous not in names
    assert store.status()["actual_documents"] == 1
    other = Store(tmp_path / "manifest", embedder,
                  config=replace(settings, endpoint_url="http://localhost:9000"))
    with pytest.raises(KnowledgeError, match="Storage endpoint changed"):
        other.status()

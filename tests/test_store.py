import pytest
from conftest import write_doc

from gdp_support.corpus import KnowledgeError
from gdp_support.store import Store


def test_incremental_rebuild_update_and_delete(tmp_path, corpus, embedder):
    a = write_doc(corpus)
    b = write_doc(corpus, "TRN-001", "spark memory", "transformation")
    store = Store(tmp_path / "db", embedder)
    assert store.ingest(corpus)["embedded"] == 2
    assert store.ingest(corpus)["unchanged"]
    assert embedder.embedded == 2
    write_doc(corpus, body="auth expiry new resolution")
    assert store.ingest(corpus)["embedded"] == 1
    b.unlink()
    assert store.ingest(corpus)["embedded"] == 0
    assert store.status()["actual_documents"] == 1
    assert store.read(["ING-001"])[0]["markdown"] == a.read_text()
    # Persistent clients reopen the same published snapshot.
    assert Store(tmp_path / "db", embedder).status()["actual_documents"] == 1


def test_embedding_failure_preserves_snapshot(tmp_path, corpus, embedder):
    write_doc(corpus)
    store = Store(tmp_path / "db", embedder)
    store.ingest(corpus)
    old = store.status()["collection"]
    write_doc(corpus, body="auth changed")
    embedder.fail = True
    with pytest.raises(RuntimeError):
        store.ingest(corpus)
    assert store.status()["collection"] == old
    assert "auth changed" not in store.read(["ING-001"])[0]["markdown"]


def test_length_failure_before_mutation(tmp_path, corpus, embedder):
    write_doc(corpus)
    store = Store(tmp_path / "db", embedder)
    store.ingest(corpus)
    snapshot = store.status()
    write_doc(corpus, body="OVERSIZED")
    with pytest.raises(KnowledgeError, match="too long"):
        store.ingest(corpus)
    assert store.status() == snapshot
    assert embedder.embedded == 1


def test_filter_relevance_no_match_and_stale_snapshot(tmp_path, corpus, embedder):
    write_doc(corpus)
    write_doc(corpus, "TRN-001", "spark memory", "transformation", status="draft")
    store = Store(tmp_path / "db", embedder)
    store.ingest(corpus)
    result = store.search("auth", component="ingestion", status="approved")
    assert [m["id"] for m in result["matches"]] == ["ING-001"]
    assert "markdown" not in result["matches"][0]
    assert store.search("auth", component="consumption")["matches"] == []
    assert store.search("network", max_distance=0.1)["matches"] == []
    write_doc(corpus, body="auth changed")
    store.ingest(corpus)
    with pytest.raises(KnowledgeError, match="changed"):
        store.read(["ING-001"], result["snapshot"])
    with pytest.raises(KnowledgeError, match="Unknown"):
        store.read(["missing"])


def test_model_mismatch_requires_rebuild(tmp_path, corpus, embedder):
    write_doc(corpus)
    store = Store(tmp_path / "db", embedder)
    store.ingest(corpus)
    embedder.signature = "different-model"
    with pytest.raises(KnowledgeError, match="changed"):
        store.search("auth")
    assert store.ingest(corpus)["embedded"] == 1


def test_memory_mode_and_empty_update(tmp_path, corpus, embedder):
    path = write_doc(corpus)
    store = Store(tmp_path / "unused", embedder, memory=True)
    store.ingest(corpus)
    assert store.status()["memory"]
    assert not (tmp_path / "unused").exists()
    path.unlink()
    with pytest.raises(KnowledgeError):
        store.ingest(corpus)
    assert store.status()["actual_documents"] == 1


def test_source_rename_updates_citations_without_embedding(tmp_path, corpus, embedder):
    path = write_doc(corpus)
    store = Store(tmp_path / "db", embedder)
    store.ingest(corpus)
    path.rename(corpus / "renamed.md")
    assert store.ingest(corpus)["embedded"] == 0
    assert store.read(["ING-001"])[0]["source"] == "renamed.md"


def test_independent_memory_stores_do_not_delete_each_other(tmp_path, corpus, embedder):
    write_doc(corpus)
    a = Store(tmp_path / "a", embedder, memory=True)
    b = Store(tmp_path / "b", embedder, memory=True)
    a.ingest(corpus)
    b.ingest(corpus)
    write_doc(corpus, body="auth updated")
    b.ingest(corpus)
    assert a.status()["actual_documents"] == 1
    assert "auth updated" not in a.read(["ING-001"])[0]["markdown"]


def test_publish_failure_preserves_previous_manifest(tmp_path, corpus, embedder, monkeypatch):
    import gdp_support.store

    write_doc(corpus)
    store = Store(tmp_path / "db", embedder)
    store.ingest(corpus)
    snapshot = store.status()["collection"]
    write_doc(corpus, body="auth changed")

    def failed_replace(*args):
        raise OSError("simulated disk error")

    monkeypatch.setattr(gdp_support.store.os, "replace", failed_replace)
    with pytest.raises(OSError):
        store.ingest(corpus)
    assert store.status()["collection"] == snapshot
    assert len(store.client.list_collections()) == 1


def test_multiple_batches_reuse_and_add_new_records(tmp_path, corpus, embedder):
    for i in range(35):
        write_doc(corpus, id_=f"DOC-{i:03}")
    store = Store(tmp_path / "db", embedder)
    assert store.ingest(corpus)["embedded"] == 35
    for i in range(35, 70):
        write_doc(corpus, id_=f"DOC-{i:03}", body="schema new")
    assert store.ingest(corpus)["embedded"] == 35
    assert store.status()["actual_documents"] == 70


def test_reader_times_out_when_another_writer_owns_lock(tmp_path, corpus, embedder, monkeypatch):
    from filelock import FileLock, Timeout

    import gdp_support.store

    write_doc(corpus)
    store = Store(tmp_path / "db", embedder)
    store.ingest(corpus)
    monkeypatch.setattr(
        gdp_support.store, "FileLock", lambda path, timeout: FileLock(path, timeout=0)
    )
    with FileLock(str(store.root / "index.lock")):
        with pytest.raises(Timeout):
            store.status()


def test_category_filter_and_folder_move_reuses_embedding(tmp_path, corpus, embedder):
    references = corpus / "references"
    runbooks = corpus / "troubleshooting"
    references.mkdir()
    runbooks.mkdir()
    ref = write_doc(references, id_="REF-001", body="spark schema", component="transformation")
    write_doc(runbooks, id_="TRN-001", body="spark schema", component="transformation")
    store = Store(tmp_path / "db", embedder)
    store.ingest(corpus)
    hits = store.search("spark schema", kind="reference", component="transformation")
    assert [m["id"] for m in hits["matches"]] == ["REF-001"]
    assert hits["matches"][0]["kind"] == "reference"
    assert [m["id"] for m in store.search("spark", kind="troubleshooting")["matches"]] == [
        "TRN-001"
    ]
    ref.rename(runbooks / ref.name)
    assert store.ingest(corpus)["embedded"] == 0
    assert store.search("spark", kind="reference")["matches"] == []
    assert len(store.search("spark", kind="troubleshooting")["matches"]) == 2


def test_old_category_schema_requires_reingestion(tmp_path, corpus, embedder):
    import json

    write_doc(corpus)
    store = Store(tmp_path / "db", embedder)
    store.ingest(corpus)
    path = store.root / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest.pop("retrieval_schema")
    manifest["fingerprint"] = "old-fingerprint"
    path.write_text(json.dumps(manifest))
    with pytest.raises(KnowledgeError, match="Category metadata missing"):
        store.search("auth", kind="reference")
    assert store.ingest(corpus)["embedded"] == 0

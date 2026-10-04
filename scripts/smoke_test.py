"""Release smoke check using the configured remote model and an isolated in-memory index."""

import argparse
from pathlib import Path

from gdp_support.config import load_config
from gdp_support.embedding import RemoteEmbedder
from gdp_support.store import Store


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    corpus = Path(__file__).resolve().parents[1] / "knowledge"
    embedder = RemoteEmbedder(config=load_config(args.config).embedding)
    store = Store(Path("."), embedder, memory=True)
    report = store.ingest(corpus)
    assert report["documents"] == store.status()["actual_documents"]
    assert report["embedded"] == report["documents"]
    assert store.ingest(corpus)["embedded"] == 0
    for query, component, expected in (
        ("source authentication expired credential", "ingestion", "ING-001"),
        ("ingestion schema contract mismatch incompatible column type", "ingestion", "ING-002"),
        ("Spark executor memory out of memory skew", "transformation", "TRN-002"),
        ("consumer SQL permission access denied", "consumption", "CON-001"),
    ):
        hits = store.search(query, top_k=1, component=component)
        assert hits["matches"] and hits["matches"][0]["id"] == expected, hits
        doc = store.read([expected], hits["snapshot"])[0]
        assert doc["markdown"] == (corpus / doc["source"]).read_text(encoding="utf-8")
    assert all(
        m["status"] == "approved"
        for m in store.search("schema mismatch", status="approved")["matches"]
    )
    print(
        "Real-model smoke passed: 1 vector/file, unchanged reuse, 4 relevance checks, full evidence."
    )


if __name__ == "__main__":
    main()

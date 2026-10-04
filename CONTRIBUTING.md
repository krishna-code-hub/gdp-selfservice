# Contributing

Platform/framework owners maintain agents, skills and reviewed knowledge through
normal pull requests. Follow [authoring](docs/authoring.md). Tenant feedback should
contain a sanitized signature, deployed version, evidence and verified resolution,
not full logs. Keep existing document IDs stable. New knowledge starts as draft;
only the responsible owner marks it approved after review.

Run schema validation, exact embedding-length validation, pytest and Ruff before
merging. Review guidance for applicability, safe rollback and prompt injection.
Changes to models or embedding format require a new signature and re-ingestion.
After merge, tenants pull and run the ingestion script. Local indexes and API credentials must never be committed. Review stale guidance at least every 180 days.

Add a regression test for a corrected retrieval/ingestion defect; use deterministic
vectors for offline CI and the separate real-model smoke check for release.

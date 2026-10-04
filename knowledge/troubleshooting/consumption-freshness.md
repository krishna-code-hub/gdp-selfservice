---
id: CON-002
title: Published data is stale
summary: Data freshness breach, stale dashboard or delayed publication.
component: consumption
framework: sql
owner: platform-team (replace before approval)
status: example
reviewed: '2026-10-03'
version: illustrative; validate deployed version
---
# Published data freshness breach
Applicability: sample for scheduled publication; actual GDP freshness SLAs must be supplied.

## Diagnose
Compare latest source, ingestion, transformation and publication timestamps in one timezone. Find the first boundary whose timestamp stopped advancing. Check orchestrator status, dependencies, data-quality gates and consumer cache separately. A successful job alone does not prove fresh data.

## Resolve
Propose correction at the failing boundary. Replay/backfill requires an approved range, idempotency check and downstream impact review. Cache invalidation requires consumer-owner authorization. Do not fabricate an SLA or bypass quality gates.

## Rollback and verify
Revert changed scheduling/configuration if required. Verify end-to-end watermark, expected counts, quality checks and the consumer-visible timestamp against the tenant's agreed SLA.

## Escalate
Unknown publication contract or a widespread breach: provide the boundary timeline and redacted run IDs to owners.

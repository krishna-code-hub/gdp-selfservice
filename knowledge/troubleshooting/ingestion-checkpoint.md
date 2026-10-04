---
id: ING-003
title: Incremental ingestion checkpoint or replay failure
summary: Invalid offset, stale checkpoint, missing source history, or duplicate replay.
component: ingestion
framework: connector
owner: platform-team (replace before approval)
status: example
reviewed: '2026-10-03'
version: illustrative; validate deployed version
---
# Incremental checkpoint failure
Applicability: sample for offset-based ingestion; source retention and commit semantics vary.

## Diagnose
Capture the redacted offset error and run ID. Read the last committed checkpoint, source retention boundary and sink commit status through approved tooling. Establish whether the prior attempt wrote data before failing. A failed job does not imply an uncommitted sink.

## Resolve
Pause automatic retries if duplication or loss is possible. The owner must define a bounded replay range, deduplication key and retention prerequisites. Never delete or reset checkpoints to "start fresh" without an approved recovery plan.

## Rollback and verify
Snapshot the original checkpoint/configuration using the platform-approved method before a change. Restore only when consistent with sink state. Verify unique-key counts, gap coverage, expected offset and consumer freshness.

## Escalate
If source history has expired or commit state is unknown, escalate to ingestion and data owners; do not promise recovery.

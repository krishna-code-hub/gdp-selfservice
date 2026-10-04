---
id: ING-002
title: Ingestion schema contract mismatch
summary: Schema drift, incompatible type or missing source field.
component: ingestion
framework: connector
owner: platform-team (replace before approval)
status: example
reviewed: '2026-10-03'
version: illustrative; validate deployed version
---
# Schema contract mismatch
Applicability: sample for schema-controlled ingestion; confirm the deployed connector version.

## Symptoms
Schema mismatch, incompatible column type or missing required field.

## Diagnose
Compare sanitized source schema with the configured contract and last successful run. Identify added, removed, renamed or type-changed columns. Check whether failure happened before or after records were committed.

## Resolve
Propose a versioned contract or compatible source correction through the framework owner. Evaluate consumers and historical records before deployment. Do not enable automatic schema evolution without approval.

## Rollback and verify
Revert the reviewed contract/configuration revision if incompatible. Confirm replay deduplication and the committed offset before retry. Validate types, required fields, rejected-record counts and downstream contracts.

## Escalate
Breaking type changes, unknown commit state or possible data loss require owner review. Record the differing schema fields without sample tenant data.

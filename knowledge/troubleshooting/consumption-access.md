---
id: CON-001
title: Consumer query access denied
summary: Permission denied, unauthorized view access or denied storage access.
component: consumption
framework: sql
owner: platform-team (replace before approval)
status: example
reviewed: '2026-10-03'
version: illustrative; validate deployed version
---
# Consumer access denied
Applicability: sample for SQL consumption; warehouse-specific authorization varies.

## Diagnose
Confirm the effective user/role, tenant, environment and referenced published object. Distinguish catalog, schema, view, underlying table and storage authorization. Compare with the approved access contract using read-only metadata.

## Resolve
Route a least-privilege access request to the data owner. Check whether a published view is intended rather than direct underlying-table access. Never suggest broad grants, policy bypasses or another tenant's identity.

## Rollback and verify
If an authorized grant is wrong, use the owner's approved revocation process. Verify the exact permitted query and that unrelated objects remain inaccessible. Do not expose row-level restricted data in chat.

## Escalate
Unclear ownership, cross-tenant resources or policy ambiguity requires security/data-owner review. Provide sanitized object scope and request time, not credentials or query results.

---
id: ING-001
title: Source authentication fails
summary: 401, 403, AccessDenied or expired credential during ingestion.
component: ingestion
framework: connector
owner: platform-team (replace before approval)
status: example
reviewed: '2026-10-03'
version: illustrative; validate deployed version
---
# Source authentication failure
Applicability: sample for connectors using managed identities or secrets; GDP owner must validate.

## Symptoms
401, 403, AccessDenied, expired credential. These signatures do not prove one cause.

## Diagnose
1. Confirm the failed request stage, identity, environment and target resource from sanitized logs.
2. Compare identity scope and credential expiry with the last successful run using approved read-only tooling.
3. Distinguish invalid credentials (authentication) from denied resource access (authorization). Check network policy separately.

## Resolve
Have the credential owner rotate an expired secret through the approved secret manager, or request narrowly scoped resource access. Require owner approval; never paste secrets or grant administrator access.

## Rollback and verify
Use the approved credential rollback procedure if rotation breaks dependents. Retry one bounded run only after confirming replay safety. Verify source access, row counts and downstream freshness.

## Escalate
Unknown identity, cross-tenant access, or a continuing denial: send redacted request ID, time and scope to the platform owner.

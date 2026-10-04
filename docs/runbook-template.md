---
id: "ASSIGN-STABLE-ID"
title: "Component/framework plus observable failure"
summary: "Failure symptom, stable error signature and distinguishing context"
component: "ingestion"
framework: "actual-framework"
owner: "actual-owning-team"
status: "draft"
reviewed: "2026-10-03"
version: "actual-tested-versions"
---
# Focused failure
Applicability: supported runtime, scope and exclusions.

## Exact error messages
Source: actual framework log, API response or UI; affected version.
Copy the observed stable error code/message verbatim except for sanitized values.
Replace IDs, timestamps, paths or secrets with explicit placeholders; do not invent messages.
```text
<sanitized observed error line or short exception>
```
If no error is emitted, state that and record the actual UI/API status instead.

## Symptoms and diagnose
Explain the visible behavior in plain language. Give a read-only check that
distinguishes causes; an error string alone does not prove the root cause.

## Resolve
Smallest reviewed change, prerequisites, scope and authorization.

## Rollback and verify
Rollback condition and procedure. Execution and data correctness checks.

## Escalate
Stop condition and actual owning team. Supply only sanitized evidence.

---
id: TRN-004
title: Spark transformation fails with Java heap out-of-memory
summary: Spark driver or executor reports java.lang.OutOfMemoryError; distinguish heap pressure, skew and container memory limits.
component: transformation
framework: spark
owner: framework-team
status: approved
reviewed: '2026-10-04'
version: Local retrieval test fixture v1; Spark JVM heap failure scenario
---
# Spark out-of-memory
Applicability: approved for local troubleshooting tests only; confirm deployed runtime.

## Exact error messages
Source: synthetic driver/executor log fixture, not a captured GDP incident.
```text
java.lang.OutOfMemoryError: Java heap space
```
No tenant data or identifiers are included. Container OOMKilled is a different
signal; do not infer heap exhaustion from executor loss alone.

## Diagnose
Identify the failing driver/executor and stage. Check authorized task metrics,
partition sizes, skew, JVM heap configuration and container termination reason.
Ask for one discriminating observation at a time.

## Resolve
For confirmed skew, propose a tested partition/join correction. For driver
collection pressure, avoid collecting the full dataset locally. For confirmed
resource shortage, request an authorized bounded configuration change.

## Rollback and verify
Revert the reviewed code/configuration if ineffective. Confirm task progress,
retry behavior, output counts, contracts and absence of duplicate writes.

## Escalate
If unresolved or checks are blocked, populate the repository's generic
docs/escalation-template.md from observed results for framework/platform support.
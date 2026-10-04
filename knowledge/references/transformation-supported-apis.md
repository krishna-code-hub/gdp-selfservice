---
id: REF-004
title: Transformation SQL and PySpark DataFrame support evidence
summary: Whether GDP transformation supports only SQL or also PySpark DataFrame operations.
component: transformation
framework: capabilities
owner: framework-team (replace before approval)
status: example
reviewed: '2026-10-04'
version: illustrative; deployed framework version required
---
# Transformation supported APIs
Applicability: knowledge-gap reference, not a confirmed capability specification.

## Clarification
Question: Does transformation support only SQL or PySpark DataFrame operations also?
Neither SQL-only nor combined API support is established by the supplied GDP evidence.
Confirm the deployed framework/runtime version with its owner.

## Evidence required
The owner must document supported SQL entry points and whether PySpark DataFrame
jobs are supported, including submission interface, dependencies, security,
testing, publication contracts and version-specific restrictions.
Include a reviewed usage example for each supported API.

## Answer boundary
Spark itself supports DataFrames, but a GDP Spark failure runbook does not prove
that the GDP transformation framework exposes those APIs. Missing documentation
means unknown, not unsupported. Cite this gap and request the capability contract.

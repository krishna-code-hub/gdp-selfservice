---
id: TRN-001
title: dbt compilation or relation missing
summary: Compilation Error, undefined ref/source, or relation does not exist.
component: transformation
framework: dbt
owner: platform-team (replace before approval)
status: example
reviewed: '2026-10-03'
version: illustrative; validate deployed version
---
# dbt compilation or missing relation
Applicability: sample for dbt projects; confirm adapter and dbt versions.

## Diagnose
Separate compile-time reference errors from runtime warehouse errors. Inspect the named model, ref/source definition, dependency versions and selected target. For a runtime missing relation, confirm upstream publication, database/schema resolution and identity access through approved read-only checks.

## Resolve
Propose the smallest project correction or approved upstream build. Verify the intended target first. A missing relation may be an access problem; do not create replacement tables blindly. Deployment or warehouse builds require authorization.

## Rollback and verify
Revert the project/configuration revision if necessary. Validate compilation, intended dependency lineage, model tests and downstream row counts. Building a model can mutate data; explain scope before execution.

## Escalate
Unclear target mapping or an upstream contract change requires the framework owner. Provide sanitized model name, adapter version and error signature.

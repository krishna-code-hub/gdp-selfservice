---
id: REF-001
title: GDP framework responsibility map
summary: Illustrative ingestion, transformation and consumption responsibilities;
  actual GDP topology is not supplied.
component: platform
framework: overview
owner: platform-team (replace before approval)
status: example
reviewed: '2026-10-03'
version: illustrative; validate deployed version
---
# Framework responsibilities
This is an illustrative operating model, not a description of your deployed GDP.

Ingestion moves source data under connectivity, identity, schema and incremental-state contracts. Transformation applies business logic with dependencies, execution resources and quality contracts. Consumption exposes approved data products with authorization, freshness and performance contracts.

Shared platform dependencies can include orchestration, identity, networking, catalog and observability. Actual tools, cloud services, ownership, SLAs and release versions must be documented by the platform team.

For a failure, find the first broken contract using a redacted error signature and timeline. Trace only the immediate upstream dependency before broadening. Verify both execution and data correctness.

Use REF-002 for the minimum framework documentation required before tenant rollout. GDP here denotes the user's platform; it does not imply Google Cloud Platform.

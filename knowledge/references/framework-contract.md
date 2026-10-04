---
id: REF-002
title: Framework onboarding contract
summary: Required GDP-specific ownership, version, supported operations and escalation
  evidence.
component: platform
framework: overview
owner: platform-team (replace before approval)
status: example
reviewed: '2026-10-03'
version: illustrative; validate deployed version
---
# Framework onboarding contract
Before approving GDP-specific guidance, each framework owner should document:

- Supported runtime/framework versions and configuration schema.
- Tenant isolation and effective identity; secrets stay in the approved secret manager.
- Source/sink semantics, schema evolution, checkpoint commit and replay idempotency.
- Data-quality gates, publication contracts and freshness objectives.
- Approved read-only diagnostic tools, relevant sanitized metrics and request IDs.
- Mutation permissions, scoped approval, rollback and post-change verification.
- Named team ownership and actual escalation destination.

Create focused reference files rather than one long manual. Link from each relevant runbook by stable ID. The toolkit has no credentials and executes no GDP runtime calls itself. Copilot suggestions must be checked against the documented deployed version.

These requirements are illustrative until adopted by your platform team; do not invent missing values.

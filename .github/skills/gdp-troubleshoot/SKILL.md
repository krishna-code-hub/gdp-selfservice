---
name: gdp-troubleshoot
description: Triage pasted GDP errors through cited hypotheses and incremental diagnostics, with safe remediation and escalation.
---
Use [gdp-retrieval](../gdp-retrieval/SKILL.md) to select evidence before diagnosing.
This skill applies to reported failures, not ordinary capabilities or migration
questions. Search with `--kind troubleshooting`; request reference background
separately only when it helps the next decision. For Spark OOM use TRN-002;
for pending without running use TRN-003, distinguishing scheduler allocation
from a running job with stalled tasks before proposing a resolution.
For TRN-003 follow its ordered queue/configuration, workload/capacity and
escalation checks. Running driver counts do not establish scheduler headroom.
Use the same generic support ticket for this and all other issues; do not create
a separate Spark-specific form.

Collect the redacted error signature, component/framework/version, environment,
first failure time with timezone, job/run ID, tenant scope, impact and recent
change. Ask only for missing fields that change the next decision. Never ask
for raw tokens, credentials or full datasets; recommend sanitizing before paste.

Separate observed symptoms from candidate causes. Cite a selected runbook.
Compare its Exact error messages/source/version with the sanitized reported
signature when available. Semantic retrieval is candidate evidence, not an exact
string match or a confirmed diagnosis. For pending/no-error cases, compare actual
states and scheduler evidence instead of inventing an error message.
Check applicability. Give the cheapest read-only check that distinguishes the
top hypotheses, explain expected outcomes, and wait for the engineer's result.
Do not issue long speculative command sequences. Sample runbooks require GDP
owner validation before operational use.

For a confirmed cause propose the smallest remediation: exact scope, access
prerequisites, data loss/duplicate risk, approval, rollback and verification.
Do not execute production changes without explicit scoped authorization. Never
reset checkpoints, drop tables, grant broad access, disable policies, or replay
blindly. Guidance must respect current tenant permissions and approved processes.

Verify both execution and data correctness: status, freshness, row counts,
contracts and downstream impact as applicable. Escalate when blast radius is
unknown, data integrity is threatened, two diagnostics fail to discriminate,
or no approved applicable evidence exists. Use
[the escalation template](../../../docs/escalation-template.md) without attaching
raw logs. After applicable checks are completed or blocked and support is still
needed, automatically draft the ticket in chat with exactly these fields:
Environment; Application name; Component; Issue name; Issue Summary;
Steps performed already. Populate them from known facts and actual results,
including check outcomes and why platform/framework support is required.
Distinguish user-reported from tool-observed results; preserve unknowns as
Not provided. Ask only for missing details needed for routing/investigation.
Do not label suggested steps as completed or guess a root cause. Drafting is
not authorization to submit an external ticket.
Save a short conversational checkpoint, not an incident file unless
requested. Offer sanitized feedback for the maintainer after verification.

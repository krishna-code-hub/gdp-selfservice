---
id: TRN-003
title: "Spark transformation pending: queue checks and escalation"
summary: Spark job pending without running; check application.yaml queue, running jobs and capacity, then raise a platform ticket.
component: transformation
framework: spark
owner: platform-team
status: approved
reviewed: '2026-10-04'
version: GDP Spark on Kubernetes; queue-based scheduling; confirm deployed versions
---
# Spark transformation pending
Applicability: queued before execution; confirm context, namespace, scheduler and versions.

## 1. Check application.yaml queue
Compare the configured queue with the tenant-approved queue and effective submitted
queue. Confirm the framework's actual field path; do not guess a YAML key.
If incorrect, propose an authorized correction before continuing.

## 2. Check running jobs and resources
Replace placeholders; verify the queue label and spark-role=driver exist.
List running drivers, not executors; count returned names as observed active applications.
```sh
kubectl --context "<context>" -n "<namespace>" get pods -l "<queue-label>=<queue-name>,spark-role=driver" --field-selector=status.phase=Running -o name
kubectl --context "<context>" -n "<namespace>" describe resourcequota
```
Job count alone does not prove capacity. Compare queue allocation/max and namespace
quota with driver/executor requests, concurrency limits and scheduler events.
Missing permissions or labels mean unknown, not zero usage.

## 3. Escalate
If sufficient headroom is confirmed but pending persists, create a platform ticket
using [the generic ticket](../../docs/escalation-template.md), populated from observed results.
Detailed checks: [queue diagnostics](../../docs/spark-pending-ticket.md).
If capacity cannot be verified, record that uncertainty and request owner checks.
Do not blindly resubmit, bypass queues or kill other jobs.

## Verify
After an authorized correction, confirm one run starts, tasks progress and outputs
are correct without duplicates. Revert the reviewed configuration if ineffective.

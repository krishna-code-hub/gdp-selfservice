---
id: TEST-TRN-002
title: Spark transformation pending before execution
summary: Spark job stays pending without tasks; verify application.yaml queue, running applications and allocation headroom before escalation.
component: transformation
framework: spark
owner: platform-team
status: approved
reviewed: '2026-10-04'
version: Local retrieval test fixture v1; queue-based Spark on Kubernetes
---
# Spark pending
Applicability: approved local test procedure; replace command placeholders for the actual deployment.

## Exact error messages
No error message is emitted in this fixture. Observed application state: pending;
no tasks started. This is not an asserted Kubernetes pod phase or scheduler error.

## 1. Verify application.yaml
Compare the effective configured queue with the tenant-approved queue. Confirm the
actual framework field path; propose an authorized correction if mismatched.

## 2. Check workload and headroom
Verify queue labels and spark-role=driver before using this read-only command:
```sh
kubectl --context "<context>" -n "<namespace>" get pods -l "<queue-label>=<queue-name>,spark-role=driver" --field-selector=status.phase=Running -o name
```
Count observed drivers, not executors. Compare queue allocation/max, concurrency,
namespace quotas and driver/executor requests. A count alone does not prove
capacity; missing access means unknown, not zero usage.

## 3. Escalate and verify
If pending persists despite confirmed headroom, or checks are blocked, populate
docs/escalation-template.md from actual findings. Do not kill jobs or resubmit blindly.
After authorized correction, verify one run starts and outputs pass contracts;
revert ineffective configuration changes.

# Generic platform/framework support ticket

Use this template for all ingestion, transformation, consumption and shared
platform issues. After applicable troubleshooting steps have been performed and
support is still needed, the agent populates it from the conversation and observed
results. Users copy the draft into their existing ticket system; platform/framework
engineers use the same draft for triage.

```text
Environment: <environment reported by the user>
Application name: <affected application>
Component: <Ingestion / Transformation / Consumption / Platform>
Issue name: <short descriptive title>
Issue Summary: <symptoms, relevant scope/impact, what remains unresolved,
                and why platform/framework support is required>
Steps performed already:
1. <check or authorized action actually performed> — <observed result>
2. <next check or authorized action actually performed> — <observed result>
```

## How the agent populates the ticket

- Fill known fields automatically. Ask only for missing details needed for
  routing/investigation; otherwise write `Not provided`.
- Include completed steps and observed outcomes. Distinguish user-reported results
  from tool-observed results; proposed checks are not completed steps.
- Record blocked checks and reasons instead of claiming success. Do not delay
  escalation for unsafe or unauthorized checks.
- Include available version, run ID, duration, impact and cited runbook ID in the
  summary without introducing issue-specific mandatory fields.
- State capacity is sufficient only when applicable evidence confirms it.
  Running-job count alone does not establish resource headroom.
- Keep unconfirmed causes tentative and explain the remaining support need.
- Remove secrets, customer payloads and complete raw logs; use sanitized excerpts.
- Draft the populated ticket in chat. External submission or saving an incident
  file requires a user request.

## Example populated draft

This is a fictional formatting example, not an actual incident or measured result:

```text
Environment: Test
Application name: orders-transform
Component: Transformation
Issue name: Spark transformation pending without starting
Issue Summary: The job remains pending. The user reports that the configured
queue matches the tenant-approved queue. Capacity is unverified because scheduler
metrics are inaccessible. Platform support is needed to investigate allocation/
admission; involve the framework team if submission or queue translation is
incorrect. Guidance: TRN-003.
Steps performed already:
1. User checked the application.yaml queue — reported it matches the approved queue.
2. User listed running driver pods — reported two drivers in the authorized namespace.
3. User attempted a scheduler capacity check — blocked by missing access;
   sufficient headroom remains unverified.
```

Platform/framework engineers use these observations to select the next check,
verify reported conclusions and respond through the normal support workflow with
confirmed cause, scoped remediation, rollback and verification. No separate
issue-specific ticket form is required.

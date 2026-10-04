---
id: PLT-001
title: Platform timeout or DNS failure
summary: Connection timed out, name resolution failure or TLS verification error.
component: platform
framework: network
owner: platform-team (replace before approval)
status: example
reviewed: '2026-10-03'
version: illustrative; validate deployed version
---
# Connectivity failure
Applicability: sample for managed runtime network paths; do not assume a cloud provider.

## Diagnose
Identify the failing runtime, target hostname and error stage without disclosing private tenant details. Distinguish DNS lookup, TCP timeout and TLS validation. Compare approved runtime connectivity, recent policy changes and certificate validity using read-only checks. Laptop reachability does not prove runtime reachability.

## Resolve
Ask the network/platform owner for the narrowly scoped route, DNS or certificate correction supported by evidence. Do not disable TLS verification, open unrestricted egress or change firewall policy directly.

## Rollback and verify
Use the approved network/certificate revision rollback. Verify the affected connection from the actual runtime, then one safe job run and data correctness.

## Escalate
Multiple tenants affected or unknown network ownership: supply redacted hostname scope, timestamp, error stage and request ID.

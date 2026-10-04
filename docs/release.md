# Production rollout acceptance

This codebase supplies a tested local retrieval mechanism and agent scaffolding.
Production readiness for a particular GDP deployment additionally requires:

1. Replace illustrative examples with approved actual GDP contracts, framework
   versions, diagnostic procedures, owning teams and escalation routes.
2. Confirm supported-runtime CI on macOS, Windows and Linux using `uv.lock`, and
   run exact-model corpus validation plus the real-model ingest/query smoke test.
3. Verify VS Code discovers all agents and skills, terminal tools use the correct
   interpreter, and an engineer can complete a cited question and staged incident.
4. Evaluate representative sanitized incidents for retrieval quality, unsupported
   query abstention, runtime applicability and safe replay guidance. Calibrate the
   distance threshold from these results, not from a claimed confidence score.
5. Confirm repository corpus access, workstation storage controls and approved
   Copilot data handling. Restricted tenant knowledge needs separate authorized
   indexes or a service enforcing authorization, not metadata filtering.
6. Measure index size, rebuild latency and peak disk use on the intended corpus.
   Record toolkit/dependency/model revisions in the release and provide tenants
   with pull/re-ingest instructions and the rollback-to-source-revision procedure.

Do not call sample-runbook correctness validated against GDP: no actual platform
architecture or live tenant runtime was supplied with this repository.

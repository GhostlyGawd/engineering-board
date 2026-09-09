---
id: F002
type: feature
status: resolved
needs: tdd
priority: P2
title: Score explicit memory evaluation before local correction in D.1
affects: evaluation/harness.py
discovered: 2026-09-09
discovered_at: 2026-09-09T05:07:44Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:49c9453ac4ac9ee2]
---

# Score explicit memory evaluation before local correction in D.1

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> Q001 resolved that the primary memory-use gate should require an explicit apply/hold/reject disposition before a local correction, while retaining systemic-before-local as a secondary signal. Priority: P2. Done when a versioned response contract records memory id/status, current and prior incidents, disposition, evidence or information gap, and ordering before the first local correction; the harness reports this rate separately from systemic-first-cause adoption; negative-memory and epistemic-status safeguards remain enforced; historical schemas and frozen evidence remain reproducible; tests and current-truth documentation cover the new contract.

## Comments

- **codex-f002-memory-evaluation-20260909** 2026-09-09T05:08:04Z: Claimed after Q001 resolution. Implement a versioned additive memory-evaluation contract while preserving historical schema and frozen-evidence reproducibility.
- **codex-f002-memory-evaluation-20260909** 2026-09-09T05:14:51Z: Resolved after additive v2 contract, boundary/status safeguards, separate reporting, current-truth docs, 26/26 evaluation tests, and 21/21 repository suites passed.

## Resolution evidence

Added `evaluation/operator-instructions-v2.md` and `evaluation/memory-evaluation-response.schema.json` with structured memory id/status, current/prior incidents, `apply`/`hold`/`reject`, and evidence-or-gap fields. The harness accepts additive attempt schema version 2, binds evaluations to surfaced memory status and version-4 incident boundaries, and reports the before-local rate separately without changing historical product-effect gates.

Historical response schema version 1 and frozen evidence remain unchanged. Tests cover schema fields, disposition values, mixed v1/v2 reporting, surfaced-status rejection, and incident-boundary rejection. `bash tests/evaluation/automated.sh` passed 26 tests and `bash tests/run-all.sh` passed all 21 suites.

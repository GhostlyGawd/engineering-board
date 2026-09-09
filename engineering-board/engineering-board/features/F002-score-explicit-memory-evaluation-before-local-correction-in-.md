---
id: F002
type: feature
status: resolved
needs: validate
priority: P2
title: Score explicit memory evaluation before local correction in D.1
affects: evaluation/harness.py
discovered: 2026-09-09
discovered_at: 2026-09-09T05:07:44Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:49c9453ac4ac9ee2]
---

# Score explicit memory evaluation before local correction in D.1

## Done when

- [ ] Versioned response records memory id/status, current/prior incidents, disposition, evidence or gap, and reviewable ordering evidence.
- [ ] Harness reports the planned before-local rate separately from systemic-first-cause adoption with truthful completeness.
- [ ] V2 negative-memory safeguards and epistemic-status checks are exposed without rewriting historical gates.
- [ ] Historical schemas and v1 evidence remain reproducible.
- [ ] Independent review, regression tests and current-truth documentation cover the contract; live outcomes remain separate.

## Evidence

> Q001 resolved that the primary memory-use gate should require an explicit apply/hold/reject disposition before a local correction, while retaining systemic-before-local as a secondary signal. Priority: P2. Done when a versioned response contract records memory id/status, current and prior incidents, disposition, evidence or information gap, and ordering before the first local correction; the harness reports this rate separately from systemic-first-cause adoption; negative-memory and epistemic-status safeguards remain enforced; historical schemas and frozen evidence remain reproducible; tests and current-truth documentation cover the new contract.

## Comments

- **codex-f002-memory-evaluation-20260909** 2026-09-09T05:08:04Z: Claimed after Q001 resolution. Implement a versioned additive memory-evaluation contract while preserving historical schema and frozen-evidence reproducibility.
- **codex-f002-memory-evaluation-20260909** 2026-09-09T05:14:51Z: Resolved after additive v2 contract, boundary/status safeguards, separate reporting, current-truth docs, 26/26 evaluation tests, and 21/21 repository suites passed.
- **independent-audit-triage** 2026-09-09T13:18:18Z: Reopened after independent audit at 151a356 found unmet completion criteria: B004 absent-memory incompatibility, B005 unsupported ordering claim, B006 negative-memory safeguard bypass, B007 selective denominator. Hold live v2 evaluation and release-readiness claims until correction and independent verification. Existing D.1 product-effect gates remain unchanged.
- **lead-f002-source-acceptance-20260909** 2026-09-09T14:08:33Z: Source reassessment after independent B004 and combined B005-B007 verification. Normalizing existing criteria from Evidence into canonical Done when; no target changes. Live study/release decision is tracked separately as F004. Integrated suite running.

## Resolution evidence

Added `evaluation/operator-instructions-v2.md` and `evaluation/memory-evaluation-response.schema.json` with structured memory id/status, current/prior incidents, `apply`/`hold`/`reject`, and evidence-or-gap fields. The harness accepts additive attempt schema version 2, binds evaluations to surfaced memory status and version-4 incident boundaries, and reports the before-local rate separately without changing historical product-effect gates.

Historical response schema version 1 and frozen evidence remain unchanged. Tests cover schema fields, disposition values, mixed v1/v2 reporting, surfaced-status rejection, and incident-boundary rejection. `bash tests/evaluation/automated.sh` passed 26 tests and `bash tests/run-all.sh` passed all 21 suites.

## Independent audit release hold

B004-B007 are mandatory corrective dependencies from docs/evidence/2026-09-09-development-team-pilot.md. This feature is not ready for a new live metric evaluation or release-readiness claim. Historical closure remains in ARCHIVE as evidence of the earlier premature decision; current status is authoritative.

## Independent source reassessment

B004 independently verified at 19edddc in the prior pilot; B005-B007 independently passed at final72ebeea after two corrective review rounds. Integrated full suite21/21 includes39 evaluation tests. Canonical Done when now reflects existing Evidence criteria. Source implementation accepted; historical closure evidence remains preserved, and live pilot/release decision is tracked separately in F004. See docs/evidence/2026-09-09-d1-measurement-corrections.md. No scored baseline, corpus lock or product effect established.

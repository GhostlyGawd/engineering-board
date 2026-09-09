---
id: B006
type: bug
status: resolved
needs: validate
priority: P1
title: D.1 v2 rejected-memory application passes reported safeguards
affects: evaluation/harness.py
discovered: 2026-09-09
discovered_at: 2026-09-09T13:18:18Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:25bbb3f91adfbb02]
---

# D.1 v2 rejected-memory application passes reported safeguards

## Done when

- [ ] A separate v2 safeguard exposes rejected-memory application and lexical-decoy use.
- [ ] Complete-run adversarial regressions prevent those actions from passing v2 safeguards.
- [ ] Historical v1 gate results remain reproducible.

## Evidence

> Independent audit at 151a356: six lexical-decoy v2 attempts using memory_status rejected, disposition apply, rejected_memory_treatment used and lexical_decoy_treatment used still yield overall_pass true when durable_systemic_conclusion is false. Complete when separate v2 safeguards expose invalid rejected/decoy-memory use without rewriting v1 gates and include adversarial complete-run tests.

## Comments

- **independent-audit-triage** 2026-09-09T13:18:18Z: Release blocker for the D.1 v2 contract. Independent audit reproduced failure despite the prior passing test suite.
- **builder-d1-b006-20260909** 2026-09-09T13:47:24Z: Lead claims on behalf of same measurement builder for separate v2 rejected-memory/decoy safeguards. Preserve failed response evidence and historical v1 gate results.
- **builder-d1-b006-20260909** 2026-09-09T13:50:30Z: Builder commit edbfb07; 32 evaluation tests passed with complete-run rejected/decoy contradictory-annotation controls. Independent review pending.

## Independent verification

/root/verify_measurement passed edbfb07901ee45b5577dfeee0e784f1801c11c21. Complete 48-arm paired adversarial runs retained failures, reported exact rejected/decoy trial keys under contradictory annotations and durable=false; v1 gate comparison identical. B007 must still prevent observed-only pass from implying complete-run readiness.

## Final source acceptance

Separate v2 safeguards expose rejected-memory application and lexical-decoy use under contradictory annotations and durable=false while retaining scored failures. Observed results and complete-population clearance are distinct. Historical v1 gates preserved; independent complete-run verification at edbfb07 and combined72ebeea pass; integrated21 suites pass.

Evidence: docs/evidence/2026-09-09-d1-measurement-corrections.md. Live pilot and release decision are separate F004 follow-up; no product-effect claim.

---
id: B006
type: bug
status: open
needs: tdd
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

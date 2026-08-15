---
id: B075
type: bug
status: resolved
needs: validate
priority: P2
title: Authoritative current-behavior table describes superseded graph context and outcome limitations
affects: docs/PRODUCT_EVOLUTION_SPEC.md
discovered: 2026-08-15
discovered_at: 2026-08-15T03:54:52Z
promoted_from: [mcp:_sessions/mcp-2026-08-15.md:f44c98e116cd5a32]
---

# Authoritative current-behavior table describes superseded graph context and outcome limitations

## Done when

- [ ] Section 5 describes the shipped shared graph, stable pattern identity, deterministic ranking, context contract version 3, and explicit outcome feedback.
- [ ] The table preserves honest limitations, including structural eligibility, explicit mutation authority, and the failed D.1 product-effect gate.
- [ ] Current implementation claims cite the applicable tests or accepted contract sections.
- [ ] Documentation coherence and semantic review pass.

## Evidence

> docs/PRODUCT_EVOLUTION_SPEC.md section 5 says the graph is a command procedure, retrieval is path-centric, and resolution records no fix outcome, while the same authoritative spec and v1.13.1 implementation ship a shared graph core, context contract v3, and board_outcomes.

## Comments

- **goal-hooks-20260815** 2026-08-15T03:58:52Z: Claimed after semantic review confirmed that the authoritative current-behavior table contradicted shipped graph, context, and outcome behavior.
- **goal-hooks-20260815** 2026-08-15T04:05:39Z: Focused checks and the settled complete suite pass. Advanced from TDD to independent review; merged-main and installed-artifact gates remain open.
- **goal-hooks-20260815** 2026-08-15T04:07:31Z: Independent read-only review found no remaining release blocker after patch and minor release-path coverage. Advanced to validation; installed and merged-main gates remain open.

## Release validation — 2026-08-15

The released specification and coherence gates now describe shipped graph memory, context contract v3, ranking v2, structured outcomes, and the failed D.1 claim boundary. See docs/evidence/2026-08-15-v1.13.2-release-and-installed-validation.md.

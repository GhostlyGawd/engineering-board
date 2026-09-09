---
id: F005
type: feature
status: blocked
needs: validate
priority: P2
title: Expose a read-only hypothesis-detail route from retrieved H records
affects: mcp-server/engineering_board_mcp.py
discovered: 2026-09-09
discovered_at: 2026-09-09T15:39:59Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:a2370914218122c4]
parent: F004
blocked_by: [B009]
---

# Expose a read-only hypothesis-detail route from retrieved H records

## Done when

- [ ] A retrieved canonical H id has a discoverable read-only path to its full claim, status, provenance, alternatives and falsifier.
- [ ] Existing B/F/Q/O/L entry reads retain their contracts; missing or malformed H records return clear, tested errors.
- [ ] Successful and failed reads leave board, archive, graph and runtime state unchanged; no implicit hypothesis confirmation or outcome write occurs.
- [ ] Independent tests and an installed retrieve-to-detail workflow verify the route; release state and observed usefulness are reported separately.

## Evidence

> F004 retained pilot TRACE-REVIEW: a3fdbe22065a4868 and c33139a00c714707 retrieved proposed H101/H102 summaries but did not receive full alternatives/falsifiers. Released1.13.5 board_get_entry(H-id) returns not found; board_hypotheses list returns metadata and source references, not full body. Local Markdown remains supported. Candidate bounded improvement: inspect one canonical H with status/provenance/alternatives/falsifier, discoverable from context; no state mutation, auto-confirmation, or success-counter change. Completion should verify H and legacy entry reads, malformed/missing handling, read-only byte invariance and installed workflow; assess actual usefulness separately.

## Comments

- **lead-workflow-pilot-20260909** 2026-09-09T15:43:06Z: Next bounded product task from the completed synthetic pilot, not implemented here. Local Markdown remains supported; add a discoverable read-only detail route without implicit causal confirmation. Future value validation must test normal installed activation and less-obvious real tasks rather than reusing these synthetic outcomes as efficacy proof.
- **lead-hypothesis-details-20260909** 2026-09-09T15:54:08Z: Lead owns this claim on behalf of build_hypothesis_details, working in /private/tmp/eb-hypothesis-details-20260909 on build/hypothesis-details from cad55eb. Builder owns MCP implementation/tests only; lead owns docs, retained smoke and release integration. A fresh independent verifier will review correctness, read-only security and discoverability before delivery. Release target is compatible-feature batch 1.14.0, not a D.1 pass or product-value claim.
- **lead-hypothesis-details-20260909** 2026-09-09T16:06:21Z: Source and read-only evidence passed, but unpacked MCP bundle initialize reports0.0.0 rather than1.14.0. Release held on B009 before tag/publication. Retain failed bundle-smoke.json; a separately claimed identity correction will be reviewed, followed by coordinated checksum refresh, all gates and installed verification.

## Approved implementation scope

Owner approved F005 after the retained workflow pilot. Extend a read-only detail route for canonical H records, preserving full claim/status/provenance/alternatives/falsifier, legacy entry-read contracts, clear missing/malformed errors, and no write or confirmation side effects. Lead session lead-hypothesis-details-20260909 owns implementation coordination and bounded builder assignment. Evidence and independent correctness/security/UX review precede closeout. No evaluation threshold, outcome counter, or agent-organization expansion.

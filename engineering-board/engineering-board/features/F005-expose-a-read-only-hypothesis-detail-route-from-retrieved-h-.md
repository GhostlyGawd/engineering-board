---
id: F005
type: feature
status: open
needs: tdd
priority: P2
title: Expose a read-only hypothesis-detail route from retrieved H records
affects: mcp-server/engineering_board_mcp.py
discovered: 2026-09-09
discovered_at: 2026-09-09T15:39:59Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:a2370914218122c4]
parent: F004
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

---
id: B008
type: bug
status: open
needs: tdd
priority: P2
title: Workflow-pilot hypothesis fixtures pass local checks but fail released Board retrieval validation
affects: evaluation/workflow-pilot/cases/
discovered: 2026-09-09
discovered_at: 2026-09-09T15:39:59Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:4462d8a4672add9c]
---

# Workflow-pilot hypothesis fixtures pass local checks but fail released Board retrieval validation

## Done when

- [x] Correct both hypothesis fixtures to the canonical fingerprint and body-section contract.
- [x] Validate all four memories through actual Board retrieval on source and installed 1.13.5, without stale flags or errors.
- [x] Preserve rejected prepared bytes and independently accept a fresh corrected inventory before live execution.

## Evidence

> Independent final prelaunch review of prepared manifest dfd906090616c296b95ec545f5caefa21ea8549fb2b42ef618a044849c6ca5f5 called installed 1.13.5 board_context for H101 and received isError:true invalid claim_fingerprint 'synthetic-h101'. No live model trial launched. Existing fixture validation did not exercise canonical hypothesis parser/retrieval. Designer assigned correction and all-four-case retrieval regressions under F004; rejected preparation preserved in Git c1d5f91.

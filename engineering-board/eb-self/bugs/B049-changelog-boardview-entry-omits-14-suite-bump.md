---
id: B049
type: bug
title: CHANGELOG never records run-all reaching 14 suites; a "13 suites" line is stale
discovered: 2026-07-04
status: resolved
priority: P3
affects: CHANGELOG.md
needs: tdd
pattern: [stale-count, coherence]
---

## Done when
- The CHANGELOG accurately reflects run-all's real suite count (14); no line claims a stale lower total that contradicts README/ARCHITECTURE (which correctly say 14).

## Observed behavior (C6 Track D — P3; lineage B031/B032/B045)
The `/board-view` (F001) entry added the 14th run-all suite but omits the "now 14 suites" phrasing that every prior suite-adding entry states, so the CHANGELOG's max stated total stays 13. Compounding: an [Unreleased] line says "ARCHITECTURE §10 rebuilt to the 13 real run-all suites" while ARCHITECTURE now correctly says 14.

## Fix direction
Add "; tests/run-all.sh now 14 suites" to the board-view entry and reconcile the stale "13 suites" line.

## Resolution (C6, PR C6c)
Added "registered in tests/run-all.sh (now 14 suites)" to the /board-view entry; softened the stale "13 real run-all suites" line to the bounds form (no brittle absolute) per the B045 lesson. Also added the C6a (B048) and C6b (B046/B047) CHANGELOG entries.

---
id: B018
type: bug
title: board-resolve contradicts itself on which steps are mandatory
discovered: 2026-07-04
status: resolved
priority: P3
affects: skills/board-resolve/SKILL.md
needs: tdd
pattern: [doc-inconsistency]
---

## Done when
- `board-resolve/SKILL.md` states one consistent set of mandatory steps.

## Observed behavior (Track B F9)
`:9` says "Steps 6-9 mandatory"; `:57` says "Steps 1, 6, 7, and 8 are mandatory."

## Resolution (C1, PR C1d — docs coherence sweep)
board-resolve/SKILL.md intro reconciled with the detailed :57 statement: the question-closing sequence is a 9-step order-sensitive protocol whose mandatory steps are 1, 6, 7, 8 (removed the contradictory 'Steps 6-9').

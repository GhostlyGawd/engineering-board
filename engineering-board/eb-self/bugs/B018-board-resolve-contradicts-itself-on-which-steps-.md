---
id: B018
type: bug
title: board-resolve contradicts itself on which steps are mandatory
discovered: 2026-07-04
status: open
priority: P3
affects: skills/board-resolve/SKILL.md
needs: tdd
pattern: [doc-inconsistency]
---

## Done when
- `board-resolve/SKILL.md` states one consistent set of mandatory steps.

## Observed behavior (Track B F9)
`:9` says "Steps 6-9 mandatory"; `:57` says "Steps 1, 6, 7, and 8 are mandatory."

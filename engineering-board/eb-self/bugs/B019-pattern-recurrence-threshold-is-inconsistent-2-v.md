---
id: B019
type: bug
title: pattern recurrence threshold is inconsistent (2+ vs >=3) across three surfaces
discovered: 2026-07-04
status: open
priority: P3
affects: skills/board-intake/SKILL.md
needs: tdd
pattern: [doc-inconsistency]
---

## Done when
- A single recurrence threshold for pattern->Learning promotion is stated consistently, or the two thresholds (cluster-surfacing vs L### promotion) are explicitly distinguished so they no longer read as a contradiction.

## Observed behavior (Track B F10)
`board-intake/SKILL.md:137` and `board-triage/SKILL.md:68` use "2+"; `learnings-curator.md:47` uses ">=3."

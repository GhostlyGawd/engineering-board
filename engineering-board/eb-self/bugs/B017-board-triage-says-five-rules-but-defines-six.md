---
id: B017
type: bug
title: board-triage says 'five rules' but defines six
discovered: 2026-07-04
status: resolved
priority: P3
affects: skills/board-triage/SKILL.md
needs: tdd
pattern: [doc-inconsistency]
---

## Done when
- The rule count in `board-triage/SKILL.md` matches the number of rules actually defined.

## Observed behavior (Track B F8)
`:9` and `:38` say five rules; `:55` adds "Rule 6 — Surface systemic pattern clusters."

## Resolution (C1, PR C1d — docs coherence sweep)
board-triage/SKILL.md 'five' -> 'six' rules in both the description and Step 2 (six rules are defined).

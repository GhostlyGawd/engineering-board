---
id: B007
type: bug
title: Validator success is a dead end the board does not reflect
discovered: 2026-07-04
status: resolved
priority: P2
affects: agents/validator.md
needs: done
pattern: [ux-affordance]
---

## Done when
- A clean validation leaves a visible marker on the entry (e.g. "validated — run /board-resolve to close") OR the orchestrator flips status on a clean validate.
- The board no longer shows a validated-and-done entry as indistinguishable from a stalled `needs: validate` entry.

## Observed behavior
`validator.md:70-75` emits `suggested_next_needs: "resolved"` but the status flip is human-driven and nothing on the board tells the user to run `/board-resolve`. The entry sits at `needs: validate` looking stuck.

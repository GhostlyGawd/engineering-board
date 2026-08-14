---
id: B022
type: bug
title: nothing_to_test / nothing_to_review still advance the entry forward
discovered: 2026-07-04
status: in_progress
priority: P3
affects: agents/tdd-builder.md
needs: validate
pattern: [counterintuitive-behavior]
---

## Done when

- [x] `nothing_to_test` and `nothing_to_review` are defined as completed
  applicability decisions, not incomplete work, and require an evidence-based
  reason in `notes`.
- [x] Their pass-through transitions remain intentional and explain that a
  hold would repeatedly redispatch the same inapplicable discipline.
- [x] Worker Stop-hook, `/board-run`, architecture, and agent contracts agree;
  `cannot_proceed` with a null transition remains the hold path.
- [x] Maintained contract tests and a superseding product-review note prevent
  the rationale from becoming implicit again.

## Observed behavior (Track B F13)
`tdd-builder.md:60` and `code-reviewer.md:60`: an entry with nothing to test is still pushed into review/validate. A first-timer expects "nothing to do" to hold, not advance.

## Comments

- **codex** 2026-08-14T15:14:54Z: Claimed for dogfood after B067. Scope: define and test compatible state semantics for nothing_to_test and nothing_to_review outcomes.
- **codex** 2026-08-14T15:23:53Z: Behavior-preserving no-op semantics are documented and contract-tested. Red: 7 mode and 1 board-run checks failed. Green: focused mode 6/6 groups, board-run 19/19, maintained suite 21/21. Implementation pull request and merged-main evidence remain pending.

---
id: B022
type: bug
title: nothing_to_test / nothing_to_review still advance the entry forward
discovered: 2026-07-04
status: open
priority: P3
affects: agents/tdd-builder.md
needs: tdd
pattern: [counterintuitive-behavior]
---

## Done when
- An entry with nothing to test/review either holds with a clear status, or the forward-advance on an empty result is documented as intentional with rationale.

## Observed behavior (Track B F13)
`tdd-builder.md:60` and `code-reviewer.md:60`: an entry with nothing to test is still pushed into review/validate. A first-timer expects "nothing to do" to hold, not advance.

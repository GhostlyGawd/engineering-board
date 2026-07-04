---
id: L002
type: learning
subtype: principle
title: Board health invariants must respect the open-vs-resolved entry lifecycle
discovered: 2026-07-04
confidence: medium
recurrence: 2
derived_from: [B023, B010]
applies_to: [hooks/scripts/board-index-check.sh, hooks/scripts/board-session-start.sh]
pattern_tag: invariant-mismatch
---

## Takeaway
Checks and displays over the board must model the same lifecycle the board
itself uses. `board-index-check` compared BOARD.md rows (open only) to a full
file count (open + resolved-in-place), so its invariant was defeated the moment
anything was resolved — and the smoke fixture never caught it because it had no
resolved entries. The empty-board count glitch was the same class: a display
that didn't handle the empty edge of the lifecycle. Test fixtures must include
the resolved/blocked/empty states, not just the happy all-open path.

## Sources
- B023 — index-check counted resolved-in-place files; now counts open only.
- B010 — empty board double-printed the open-count.

## When this applies
When writing any invariant or banner that counts or renders board entries.
Enumerate the lifecycle states (open, blocked, in_progress, resolved, empty) and
make the fixture exercise each, especially resolved-in-place and empty — the
states the happy-path fixture omits.

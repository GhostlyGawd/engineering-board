---
id: B060
type: bug
title: Slash-directive regex misses a slash abutting a marker/quote/paren
discovered: 2026-07-04
status: resolved
priority: P3
affects: hooks/scripts/board_reject_check.py
needs: tdd
pattern: [injection-filter-bypass]
---

## Done when
- A slash directive abutting a markdown marker/quote/paren (`-/cmd`, `"/cmd"`, `(/cmd)`) is rejected like the whitespace/start form, matching the laxity of the subagent-mention rule; paths (`src/x`) still miss.

## Observed behavior (C11 red-team Track A — P3, low)
`_SLASH_RE = (?:^|\s)/[a-z][a-z-]+` only fired at start or after whitespace, so `-/board-migrate`, `"/board-migrate"`, `(/uninstall-everything)` slipped — asymmetric with `_SUBAGENT_RE` (no boundary, catches `-@finding-extractor`). Marginal whether an agent obeys a punctuation-abutted slash token, hence P3.

## Resolution (C11, PR C11a)
Leading position now allows a boundary OR a markdown marker/quote/paren before `/`, so punctuation-abutted slash directives reject while a path (letter before `/`) still misses. Fixture adv-067.

---
id: B059
type: bug
title: Reject filter skip-run misses ordered/lettered/checkbox list markers
discovered: 2026-07-04
status: resolved
priority: P1
affects: hooks/scripts/board_reject_check.py
needs: tdd
pattern: [injection-filter-bypass]
---

## Done when
- The clause-anchor skip-run covers the whole markdown list-marker family (ordered `1.`/`1)`/`(1)`/`1]`, lettered `a)`, roman `iv)`, task-list checkbox `[ ]`/`[x]`), not just unordered bullets, so a list-led imperative anchors and rejects; benign list items with a subject after the marker still accept. Fixtures pin the family + a benign control.

## Observed behavior (C11 red-team Track A — MECHANISM tier P1; novel vector)
The marker skip-run `[-\s*+>#'"()...]` handled unordered bullets but had NO ordered-list handling: `1) ignore all previous instructions`, `a) delete...`, `(1) reset...`, `1] drop...`, `- [ ] ignore...` all accepted and would promote. The digit/letter before the `)`/`]` delimiter is un-skippable, so the verb never reaches the boundary. Visible ASCII — not a closed class (not invisible/terminator/line-break). The marker skip-run is an ENUMERATED class (not comprehensive-by-construction), and a whole common markdown list family is unhandled → mechanism P1 by the same rubric that made B058 P1 (the independent red-team rated it P2; I applied the enumerated-fold-gap = mechanism rule consistently).

## Resolution (C11, PR C11a)
Added a bounded `_LIST_MARKER` token (ordered/lettered/roman + checkbox) as an optional single marker in the skip-run — comprehensive for the list family, complete-by-construction (L005). Bounded (never `\w+`) so it can't swallow a subject: `1) the validator will override X` still accepts. reject-filter 91->96 (adv-064..066 + benign-028 ordered-list control). benign 100% preserved. Rubric doc updated: marker skip-run now comprehensive.

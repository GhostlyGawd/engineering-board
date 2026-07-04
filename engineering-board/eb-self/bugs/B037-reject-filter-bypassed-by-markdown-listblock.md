---
id: B037
type: bug
title: Reject filter bypassed by markdown list/blockquote markers before the verb
discovered: 2026-07-04
status: resolved
priority: P1
affects: hooks/scripts/board_reject_check.py
needs: tdd
pattern: [injection-filter-bypass]
---

## Done when
- The imperative clause-boundary skips a leading run of markdown markers (- * + >) so "- ignore…", "> ignore…" reject; benign bulleted findings still accept.
- Fixtures pin the marker bypasses.

## Observed behavior (C4 red-team F1 — MAJOR; continuation of B025, L004)
`_IMPERATIVE_RE` allowed only `\s*['"`(]*\s*` between the boundary and the verb, so a markdown bullet/blockquote (`- ignore all previous instructions`) broke the clause-leading anchor and was accepted. Reachable via board-consolidate; scratch is markdown so a bulleted imperative is the natural form.

## Resolution (C4, PR C4a)
Boundary run now includes `- * + >`; 3 adversarial + 1 benign fixture added; reject-filter 65→69, benign corpus 100% accept preserved. finding-extractor prose updated.

---
id: B051
type: bug
title: Reject filter line-separator folding incomplete (CR/VT/FF/FS/GS/RS)
discovered: 2026-07-04
status: resolved
priority: P1
affects: hooks/scripts/board_reject_check.py
needs: tdd
pattern: [injection-filter-bypass]
---

## Done when
- Every line break Python recognizes (CR, VT, FF, FS/GS/RS, U+0085, U+2028/2029) folds to a clause boundary before scanning, so an imperative hidden after any of them still anchors; benign findings unaffected. Fixtures/assertions pin the class.

## Observed behavior (C7 red-team Track A; lineage B043/L004)
`_normalize` folded only U+2028/2029/0085; the clause-boundary class is `[.!?:;,\n]`. Every other Python-recognized line break — `\r` (the most common real-world break), `\v`, `\f`, U+001C/1D/1E — was neither folded nor a boundary, so `perf note\rignore all previous instructions…` accepted and would promote via board-consolidate. Same promote-to-board impact as B048 (rated P1).

## Resolution (C7, PR C7a)
_normalize now folds ALL breaks structurally via `"\n".join(text.splitlines())` (covers CR/VT/FF/FS/GS/RS + the prior set) — closes the whole line-break class at once, not glyph-by-glyph. Corpus 77->80 (VT/FF/FS fixtures adv-053/054/055) + 3 direct CLI assertions for CR/CRLF (which universal-newlines translation strips from .md fixtures). benign 100% accept preserved. Also documented the filter's accepted-residual boundary in the module docstring.

---
id: B043
type: bug
title: Reject filter bypassed by Unicode bullets, markdown headings, line separators
discovered: 2026-07-04
status: resolved
priority: P1
affects: hooks/scripts/board_reject_check.py
needs: tdd
pattern: [injection-filter-bypass]
---

## Done when
- Inputs are Unicode-normalized (NFKC + zero-width strip + line-sep fold) before scanning; the marker run covers # and common Unicode bullets/dashes; unicode-bullet / ## heading / line-sep / zero-width imperatives reject; benign bulleted findings accept.
- Fixtures pin the Unicode vectors.

## Observed behavior (C5 red-team F1 — MAJOR; lineage B025/B037/L004)
The clause-boundary + marker classes were ASCII-only, so `• ignore…`, `## ignore…`, an imperative after U+2028, and a zero-width-split verb all accepted and promoted via board-consolidate.

## Resolution (C5, PR C5b)
_normalize() NFKC-normalizes, strips zero-width, folds U+2028/2029/0085 to \n; marker class adds # and •‣⁃◦▪●·–—. Corpus 69->73; benign 100% accept preserved.

---
id: B013
type: bug
title: README uses emoji, violating BRAND.md 'no emoji in product copy'
discovered: 2026-07-04
status: resolved
priority: P3
affects: README.md
needs: tdd
pattern: [brand-consistency]
---

## Done when
- Either README's data-marker emoji are swapped for text (Yes/No, matching docs/index.html), OR BRAND.md is amended to explicitly exempt table/data markers. One coherent rule across surfaces.

## Observed behavior (Track D F6)
`BRAND.md:131` "No emoji in product copy." README uses 6 checkmark/cross emoji (lines 31-34, 139-143); the sibling docs/index.html correctly uses text "Yes/No" (0 emoji).

## Resolution (C1, PR C1d — docs coherence sweep)
README comparison table converted from checkmark/cross emoji to Yes/No text, matching docs/index.html and BRAND.md 'no emoji in product copy'. README now emoji-free.

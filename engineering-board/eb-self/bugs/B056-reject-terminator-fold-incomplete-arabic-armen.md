---
id: B056
type: bug
title: Reject terminator fold incomplete (Arabic comma/semicolon, Armenian, Tibetan, Khmer, Mongolian, ...)
discovered: 2026-07-04
status: resolved
priority: P2
affects: hooks/scripts/board_reject_check.py
needs: tdd
pattern: [injection-filter-bypass]
---

## Done when
- The non-Latin sentence/clause terminator fold spans the major living scripts (not a hand-picked few), so a bare imperative after any common-script terminator anchors and rejects; benign findings that merely contain such marks still accept. Fixtures pin representative marks.

## Observed behavior (C9 red-team Track A — P2, coverage gap not mechanism gap)
B053 shipped the terminator-fold MECHANISM but its set was incomplete: Arabic comma U+060C (the standard clause separator of Arabic/Persian/Urdu), Arabic semicolon U+061B, Armenian full stop U+0589, Ethiopic comma, Tibetan shad, Khmer khan, Mongolian/Myanmar/Sinhala/Georgian/Syriac terminators all bypassed — proven by internal inconsistency (CJK comma U+3001 folded, Arabic comma not). Verb stays pristine ASCII, so in-scope. Rated P2 per the mechanism-vs-coverage rubric: a shipped mechanism's data set one entry short (defense-in-depth, found only by Unicode enumeration), not a missing mechanism (B053 was P1).

## Resolution (C9, PR C9a)
Replaced the curated set with a comprehensive common-living-script terminator fold (Arabic/Armenian/Ethiopic/Devanagari/CJK/Tibetan/Khmer/Mongolian/Myanmar/Sinhala/Georgian/Syriac) to ASCII "." — complete-by-construction (L005). reject-filter 86->89 (adv-059 Arabic comma / 060 Armenian / 061 Khmer). Documented the mechanism-vs-coverage severity rubric in the module docstring: a further missing terminator is P3 corpus-growth, not a mechanism defect.

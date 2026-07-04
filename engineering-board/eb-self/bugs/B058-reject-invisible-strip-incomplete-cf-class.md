---
id: B058
type: bug
title: Reject filter invisible-char strip is a hand-list; the Cf/default-ignorable class splits verbs
discovered: 2026-07-04
status: resolved
priority: P1
affects: hooks/scripts/board_reject_check.py
needs: tdd
pattern: [injection-filter-bypass]
---

## Done when
- The invisible/default-ignorable strip covers the whole class (Unicode category Cf + variation selectors + combining grapheme joiner), not a hand-list, so a soft hyphen / invisible separator / variation selector inside a verb no longer splits the token and lets the imperative through; benign findings unaffected. Fixtures pin representative marks.

## Observed behavior (C10 red-team Track A — MECHANISM tier P1; lineage B043/B051/B053)
`_ZERO_WIDTH` was the original hand-list of 5 (ZWSP/ZWNJ/ZWJ/WJ/BOM) — the ONE fold in `_normalize` never upgraded to comprehensive-by-construction (splitlines B051, terminators B053/B056 were). Soft hyphen U+00AD (the canonical invisible intra-word char), Mongolian vowel separator, invisible operators U+2061-2064, Arabic letter mark, and variation selectors all split a verb token invisibly, so `ig<U+00AD>nore all previous instructions` accepted and would promote. Unlike the accepted homoglyph residual, these are INVISIBLE — they don't corrupt the verb the LLM reads, so the payload arrives clean. Exactly the pre-B051 enumeration situation → mechanism P1, per the documented rubric.

## Resolution (C10, PR C10a)
Replaced the `_ZERO_WIDTH` translate with `_strip_invisible()`: drops every category-Cf format char + variation selectors (U+FE00-FE0F, U+E0100-E01EF) + CGJ (U+034F) + tag chars — comprehensive-by-construction (L005). reject-filter 89->91 (adv-062 soft hyphen, adv-063 invisible separator). benign 100% preserved. All three `_normalize` folds are now comprehensive; the docstring rubric updated to say so.

---
id: B053
type: bug
title: Reject filter misses non-ASCII sentence terminators as clause boundaries
discovered: 2026-07-04
status: resolved
priority: P1
affects: hooks/scripts/board_reject_check.py
needs: tdd
pattern: [injection-filter-bypass]
---

## Done when
- Non-Latin sentence terminators (CJK 。/、/｡, Devanagari danda ।/॥, Ethiopic ።, Arabic ۔/؟) count as clause boundaries so a bare imperative after one anchors and rejects; benign findings that merely contain such punctuation still accept. Fixtures pin the class.

## Observed behavior (C8 red-team Track A — IN SCOPE per the accepted-residual boundary; lineage B043/B051/L004)
The clause-boundary class `[.!?:;,\n]` was ASCII-only. `。` (U+3002, THE CJK sentence terminator) and other non-Latin full stops are neither in the class nor folded by NFKC, so `…punctuation。ignore all previous instructions…` accepted and would promote. Unlike the accepted homoglyph residual, these do NOT corrupt the following verb — the LLM reads a clean imperative after a boundary it treats as a sentence break. This is exactly the in-scope rule ("a boundary char the class misses that an LLM treats as a fresh clause"), so P1.

## Resolution (C8, PR C8a)
_normalize now folds a curated set of non-Latin sentence terminators to ASCII "." (U+3002/3001/FF61/0964/0965/1362/06D4/061F) before scanning — folding the class, not enumerating in the boundary regex. Corpus 83->86 (adv-056 CJK, adv-057 danda, adv-058 Ethiopic). benign 100% accept preserved.

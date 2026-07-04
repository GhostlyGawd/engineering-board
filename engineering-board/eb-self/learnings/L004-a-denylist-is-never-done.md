---
id: L004
type: learning
subtype: principle
title: A denylist heuristic is never done — assume every pattern has an adjacent bypass
discovered: 2026-07-04
confidence: high
recurrence: 7
derived_from: [B002, B025, B037, B043, B048, B051, B053]
applies_to: [hooks/scripts/board_reject_check.py, tests/security/]
pattern_tag: filter-completeness
---

## Takeaway
The injection reject filter was hardened in C1 (B002: unanchored, broadened
verbs, all fields) and still had an adjacent bypass in C2 (B025: a politeness
lead-in before the verb — "Please ignore…"). Denylist heuristics leak at their
edges by nature; each fix reveals the next adjacent form. The durable defenses
are (a) the pinned framing that scratch is untrusted data, not instructions, and
(b) a growing adversarial fixture corpus that captures each newly-found bypass so
it can never regress. Treat every filter finding as "grow the corpus," not "the
filter is now complete."

## When this applies
Any time a denylist/heuristic filter is touched. Add a fixture for the exact
bypass, and resist claiming completeness — expect the next cycle to find the
adjacent case. Prefer allowlist shapes or non-filter defenses (framing,
capability limits) where the denylist's leakage would be dangerous. C5's fix
normalizes inputs (NFKC + zero-width strip + line-sep fold) BEFORE the denylist
runs — folding a whole look-alike class to its ASCII intent is more durable than
adding glyphs one at a time; the primary defense remains the untrusted-data framing.
C6 confirmed the treadmill again (B048: a fronted adverb knocks the verb off the
clause boundary the anchor relies on) — five straight cycles, every one a bypass
of the *same* filter. The fix that DID hold across all of them is the one at the
grammatical layer: the verbs are matched only in their bare imperative form (the
trailing word-boundary rejects inflected "drops"/"removes"), so descriptive prose
is preserved no matter what prefix an attacker fronts. Confidence raised to high:
this filter WILL yield again; budget for it, and keep leaning on the framing +
corpus rather than believing any single patch closes the class.

## Sources
- B002 — C1 injection filter hardening (unanchored, broadened, all-fields).
- B025 — C2 politeness/modal-prefixed bypass of that same filter.
- B037 — C4 markdown list/blockquote-marker bypass of that same filter.
- B043 — C5 Unicode-bullet/heading/line-separator bypass of that same filter.
- B048 — C6 adverb-fronted imperative bypass of that same filter.
- B051 — C7 incomplete line-break folding (CR/VT/FF/FS-GS-RS) of that same filter.
- B053 — C8 non-Latin sentence terminators (CJK/danda/Ethiopic/Arabic) missed by
  the ASCII boundary class of that same filter.

## Boundary surface after C8
NFKC already folds most punctuation look-alikes to their ASCII boundary form
(ellipsis→"...", fullwidth→"!"/"?"/".", double-marks→"!!"/"??"), and B053 folds
the major non-Latin sentence terminators. So the common clause-terminator surface
is now covered; the remaining tail is exotic marks (pilcrow ¶, section §) that an
LLM does NOT reliably treat as a fresh clause reset — accepted residuals, not P1s,
under the same in-scope test the docstring draws ("does an LLM read this as a
fresh clause"). A new *common*-script terminator would still be an in-scope defect.

## Boundary drawn (C7)
After six recurrences, C7 documented the filter's **accepted-residual boundary**
in `board_reject_check.py` (the "Out of scope" docstring section): a denylist leak
is a *defect* only if it defeats an IN-SCOPE rule (an imperative-mood `_VERBS` verb
leading a clause through any obfuscation normalization folds). Deliberately-excluded
verbs, non-imperative moods, and NFKC-irreducible homoglyphs are accepted residuals,
not bugs to re-file each cycle. This converts an open-ended P1 generator into a
bounded spec — the practical form of "the durable defense is the framing, not the
denylist." B051 was still a genuine in-scope defect (a real line break the anchor
missed); the fix folds the whole line-break class structurally via `splitlines()`.

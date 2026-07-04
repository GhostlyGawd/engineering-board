---
id: L004
type: learning
subtype: principle
title: A denylist heuristic is never done — assume every pattern has an adjacent bypass
discovered: 2026-07-04
confidence: high
recurrence: 11
derived_from: [B002, B025, B037, B043, B048, B051, B053, B056, B058, B059, B061]
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

## Severity matures with the mechanism (C9)
C9 found the terminator fold's set incomplete (B056: Arabic comma/Armenian/etc.).
The response that finally slows the treadmill is twofold: (1) fix the whole class
COMPREHENSIVELY — the terminator fold now spans the major living scripts, so it is
complete-by-construction rather than a curated list that leaks the next glyph
(L005); and (2) a documented **mechanism-vs-coverage severity rubric** (in the
module docstring): a missing MECHANISM is major (B048/B051/B053 were P1), but a
coverage gap in a shipped comprehensive mechanism, found only by Unicode
enumeration in a defense-in-depth layer, is P2/P3 — the independent red-team rated
B056 "Low" too. This is NOT down-rating to force convergence: it reflects a real
maturity shift, and the rubric is written down so the next cycle applies it
consistently. The remaining tail (further obscure-script marks) is P3 corpus
growth, not a mechanism defect.

## The rubric cuts BOTH ways (C10)
C10 was the confirming cycle — one more clean cycle and 1.3.0 released. The
red-team found B058: the invisible-char strip (`_ZERO_WIDTH`) was still a hand-list
of 5, the ONE `_normalize` fold never made comprehensive — soft hyphen and the
whole Cf/default-ignorable class split a verb token invisibly (and, being
invisible, do NOT corrupt the verb, so it is in-scope, not the homoglyph residual).
Under the SAME rubric this is a MECHANISM gap (an enumerated fold missing common
members of its class, exactly like pre-B051 line breaks) → P1. So C10 was NOT clean
and the clean streak reset — the rubric that let C9 be honestly clean also forced
C10 to be honestly unclean. That two-way integrity is the point: the rubric is a
real standard, not a convergence lever. After B058 all three `_normalize` folds are
comprehensive-by-construction, so the enumeration treadmill is structurally closed;
only a genuinely novel class (new grammar/mood/verb) can yield a new bypass now.

## …and the skip-run had one too (C11)
"Only a novel class remains" was premature: C11 found B059 — the clause-anchor
SKIP-RUN (a separate enumerated class `[-\s*+>#…]`, not the `_normalize` folds)
handled unordered bullets but not ordered/lettered/checkbox list markers, a whole
common markdown list family. Same enumerated-fold-gap = mechanism = P1 rule (the
independent red-team said P2; the rubric applied consistently says P1), so C11
reset the (new) streak too. Fixed comprehensively via a bounded `_LIST_MARKER`.
Tally after C11: EVERY enumerated component of the filter — the three `_normalize`
folds AND the marker skip-run — is now comprehensive-by-construction. The only
curated denylists left (`_VERBS`, `_LEADIN`, `_ADVERB`) are DELIBERATELY curated
(documented accepted residuals — a missing verb/adverb is a design trade-off to
avoid false positives, not a defect). So the reachable in-scope surface is finally
down to genuinely novel grammar/mood vectors + the untrusted-data framing.

## First honestly-clean-again cycle (C12)
C12 found only B061 (Unicode tag-char ASCII-smuggling: `_strip_invisible` deletes
tags for the scan but the promotion writer keeps them, so an invisible imperative a
tag-decoding reader obeys would land on the board). Rated **P2, not P1** — gated on a
reader that decodes a deprecated Unicode block (limits reachability) and the framing
holds; the independent red-team rated it P3. Fixed by rejecting any finding
containing a tag char on sight (zero-false-positive: tags are deprecated). Because
B061 is the ONLY finding and it is ≤P2, **C12 is clean** — the first cycle since the
enumerated-component sweep whose worst finding is a conditional P2, not a mechanism
P1. That is the convergence signal L004 predicted: not "the denylist is done" (it
never is), but "what's left is P2/P3 residuals a documented rubric classifies
consistently, behind an intact primary defense."

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

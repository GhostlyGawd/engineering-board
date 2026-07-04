---
id: L004
type: learning
subtype: principle
title: A denylist heuristic is never done — assume every pattern has an adjacent bypass
discovered: 2026-07-04
confidence: medium
recurrence: 4
derived_from: [B002, B025, B037, B043]
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

## Sources
- B002 — C1 injection filter hardening (unanchored, broadened, all-fields).
- B025 — C2 politeness/modal-prefixed bypass of that same filter.
- B037 — C4 markdown list/blockquote-marker bypass of that same filter.
- B043 — C5 Unicode-bullet/heading/line-separator bypass of that same filter.

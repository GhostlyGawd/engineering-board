---
id: B061
type: bug
title: Reject filter strips Unicode tag chars for its scan but promotes them raw (ASCII smuggling)
discovered: 2026-07-04
status: resolved
priority: P2
affects: hooks/scripts/board_reject_check.py
needs: tdd
pattern: [injection-filter-bypass]
---

## Done when
- A finding containing Unicode Tag characters (U+E0000-E007F) is rejected on sight (they are deprecated with no legitimate use in a finding), closing the strip-for-scan-but-promote-raw asymmetry; benign findings (incl. normal Unicode/emoji) still accept. Fixture pins the vector.

## Observed behavior (C12 red-team Track A — P2, conditional/niche)
`_strip_invisible` DELETES tag chars before scanning (correct when they SPLIT a visible verb — the B058 win), but when tag chars ENCODE the whole command, deletion makes the scan see empty text -> accept, while `flatten()`/`_oneline` keep the raw tag chars, so the invisible imperative is promoted verbatim into the entry title/heading. A downstream model that decodes Unicode tag chars reads a clean listed-verb imperative; a human sees only the benign remainder. Rated P2 not P1: gated on a reader that decodes a deprecated Unicode block (limits reachability), and the untrusted-data framing (primary defense) holds — but it's a real strip-and-promote inconsistency defeating an in-scope directive, so worth a clean fix. Independent red-team rated it P3.

## Resolution (C12, PR C12a)
Added `_TAG_RE`; `_scan` now rejects (reason `invisible_tag`) when the RAW text (before normalization strips tags) contains any U+E0000-E007F char. Zero false-positive (tags are deprecated). Catches both the encode-whole and split-verb tag shapes. reject-filter 96->97 (adv-068). benign 100% preserved.

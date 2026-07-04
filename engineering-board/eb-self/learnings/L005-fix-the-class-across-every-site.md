---
id: L005
type: learning
subtype: principle
title: Fix an input-handling class across every site at once, not one site per cycle
discovered: 2026-07-04
confidence: high
recurrence: 4
derived_from: [B051, B052, B053, B054]
applies_to: [hooks/scripts/board_reject_check.py, hooks/scripts/board-consolidate.sh, mcp-server/engineering_board_mcp.py]
pattern_tag: whole-class-sweep
---

## Takeaway
The same defect class — incomplete line-break / separator handling of untrusted
text — surfaced at FOUR different sites across two cycles: the reject filter's
line-break fold (B051), the consolidate promotion writer's field flatten (B052),
the reject filter's boundary class for non-Latin terminators (B053), and the MCP
capture evidence blockquote (B054). Each earlier fix patched only the ONE site the
red-team happened to hit, so the next cycle found the identical class at the next
writer/reader. The cost was real: two extra cycles of P1/P2 findings that a single
codebase-wide sweep would have closed at once.

The lesson: when you fix an input-normalization/escaping bug, treat it as a CLASS,
not an instance. Grep every writer and reader of the same untrusted field for the
same primitive (`split("\n")` vs `splitlines()`, a partial control-char regex, an
ASCII-only boundary set), fix them all in the same PR, and add a regression at each
site. A fix that closes one call-site while leaving siblings open is a fix that
schedules its own recurrence.

## When this applies
Any time a deterministic guard over untrusted input is touched (normalization,
flattening, boundary detection, escaping). Before closing the PR, enumerate every
site that consumes the same field or uses the same primitive and confirm each is
covered — this is L001 ("guards need tests at real call-sites") extended from one
call-site to the whole class of call-sites.

## Sources
- B051 — C7 reject filter folded only some line breaks (missed CR/VT/FF/FS-GS-RS).
- B052 — C7 consolidate promotion writer flattened only evidence_quote.
- B053 — C8 reject filter boundary class was ASCII-only (missed non-Latin terminators).
- B054 — C8 MCP capture evidence split on `\n` only (CR/FF/NEL forged a header).

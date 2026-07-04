---
id: B041
type: bug
title: RFC 0002 stale command count + missing /board-view verdict
discovered: 2026-07-04
status: resolved
priority: P3
affects: docs/rfcs/0002-surface-product-review.md
needs: tdd
pattern: [doc-drift]
---

## Done when
- RFC 0002 says 11 commands and includes a /board-view keep/simplify/merge/deprecate verdict.

## Observed behavior (C4 Track D)
RFC 0002 said "10 commands" (×2) and lacked a row for the newly-shipped /board-view (F001), the one count disagreeing with ls commands/ across audited files.

## Resolution (C4, PR C4b)
Count -> 11; added /board-view (keep) row; cycle range C1-C2 -> C1-C4; MCP-tools hardening note updated with C3/C4 fixes.

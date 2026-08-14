---
id: B062
type: bug
title: Promotion reuses resolved canonical entry identifiers
discovered: 2026-08-14
status: resolved
priority: P2
affects: mcp-server/engineering_board_core.py
needs: validate
pattern: [invariant-mismatch, dogfooding-pain]
---

## Done when

- [x] Promotion deduplication, provenance lookup, and identifier allocation include open and resolved canonical entries.
- [x] A regression fixture with resolved B023 makes the next promoted bug B024 and never creates a duplicate identifier.
- [x] Graph construction continues to rank only open graphable entries.
- [x] The complete repository test suite passes.

## Comments

- **codex** 2026-08-14T04:37:38Z: Dogfood reproduction confirmed. Promotion preview proposed resolved B023. Context retrieval surfaced L002, which identifies the shared open-versus-resolved lifecycle defect.
- **codex** 2026-08-14T04:53:14Z: Verified with the resolved-ID promotion fixture and the complete 19-suite repository run.

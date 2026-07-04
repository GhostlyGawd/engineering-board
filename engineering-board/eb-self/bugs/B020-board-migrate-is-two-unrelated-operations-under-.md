---
id: B020
type: bug
title: board-migrate is two unrelated operations under one verb
discovered: 2026-07-04
status: open
priority: P3
affects: commands/board-migrate.md
needs: tdd
pattern: [surface-overload]
---

## Done when
- The data-migration (`--apply/--rollback/--status`) and folder-relocation (`--relocate`) operations are either split into two clearly-named surfaces or the one command clearly documents that it is two modes.

## Observed behavior (Track B F11)
`board-migrate.md` bundles v0.3.0 data migration and the 1.1.0 folder move; the body even branches "skip Steps 2-4" for relocate. Confusing for both.

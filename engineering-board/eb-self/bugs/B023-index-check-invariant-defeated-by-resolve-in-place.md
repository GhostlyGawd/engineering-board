---
id: B023
type: bug
title: board-index-check invariant is defeated by the resolve-in-place convention
discovered: 2026-07-04
status: open
priority: P2
affects: hooks/scripts/board-index-check.sh
needs: tdd
pattern: [invariant-mismatch, dogfooding-pain]
---

## Done when
- `board-index-check.sh` counts only NON-resolved entry files (`status: resolved` excluded) so its file-count matches BOARD.md's open-only rows, OR the resolve convention is changed to move resolved files out of the entry subdirs (decide which).
- A test plants a resolved-in-place entry and asserts `board-index-check.sh` exits 0 (currently it exits 2).
- Running `board-index-check.sh` on the `eb-self` board (which has resolved-in-place entries) exits 0.

## Observed behavior (dogfooding, C1)
The canonical resolve flow (`skills/board-resolve/SKILL.md` Steps 2-4) sets
`status: resolved` in the entry file **in place** (file stays in `bugs/`), appends
provenance to ARCHIVE.md, and `/board-rebuild` omits it from BOARD.md. But
`board-index-check.sh:45` counts **all** `*.md` files in each subdir with no
status filter, while `:48` counts BOARD.md rows (open only). So the moment any
entry is resolved, `file_count > row_count` → MISMATCH (exit 2), permanently.
Reproduced on `eb-self` after C1 resolutions: `MISMATCH [eb-self/bugs] files=22 board_rows=10`.

## Impact
The invariant is silently defeated on every mature board: it can no longer
distinguish a healthy board (with resolved entries) from an actually-desynced
one, and the tidier (`agents/tidier.md:66,145`) does a spurious rebuild on every
run. No data loss (BOARD.md itself stays correct via rebuild) — hence P2, not P1.

## Fix direction
Filter `find` in `board-index-check.sh` to entries whose frontmatter lacks
`status: resolved` (a small python3 pass, crosscompat-safe), matching BOARD.md's
open-only semantics. The smoke test never caught this because its fixture board
has zero resolved entries.

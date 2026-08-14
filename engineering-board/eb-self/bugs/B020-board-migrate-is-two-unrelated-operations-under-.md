---
id: B020
type: bug
title: board-migrate is two unrelated operations under one verb
discovered: 2026-07-04
status: in_progress
priority: P3
affects: commands/board-migrate.md
needs: validate
pattern: [surface-overload]
---

## Done when

- [x] `/board-migrate` names data migration and folder relocation as two
  independent workflows before it gives execution steps.
- [x] Data flags resolve project board directories and run
  `board-migrate.sh`; `--relocate` runs `board-relocate.sh` once at repository
  scope.
- [x] The command contains no cross-workflow skip instruction and preserves all
  existing flags and safety boundaries.
- [x] The real command-file contract, architecture summary, changelog, and
  dated evidence agree.

## Observed behavior (Track B F11)
`board-migrate.md` bundles v0.3.0 data migration and the 1.1.0 folder move; the body even branches "skip Steps 2-4" for relocate. Confusing for both.

## Comments

- **codex** 2026-08-14T17:44:48Z: Claimed after B069 closeout. Direction: preserve the existing /board-migrate compatibility surface, but make data migration and folder relocation two independent named workflows with immediate mode dispatch and no skip-step branch. Add a real command-file contract to the existing board-migrate test; align architecture, changelog, and dated evidence.
- **codex** 2026-08-14T17:49:09Z: Implementation validation complete. Red: the existing migration behavior passed 8 checks while all 4 real command-contract checks failed. Green: the focused test passes 12 checks; documentation coherence passes; all 25 orchestration sub-suites pass; the maintained suite passes 21 of 21. Existing flags, scripts, snapshots, rollback behavior, command count, and release state remain unchanged.

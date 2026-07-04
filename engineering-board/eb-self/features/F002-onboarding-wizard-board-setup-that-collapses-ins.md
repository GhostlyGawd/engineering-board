---
id: F002
type: feature
title: Onboarding wizard (/board-setup) that collapses install->value to one step
discovered: 2026-07-04
status: open
priority: P2
affects: commands/board-setup.md
needs: tdd
pattern: [onboarding]
---

## Done when
- `/board-setup [project]` (mirror `board_setup` MCP tool) infers the project name from the repo dir, runs board-init with defaults, runs the permission self-check (prints the paste block only if perms missing — no silent settings edits), leaves mode at Passive, and prints a 3-line "you're ready + next action" summary.
- Time-to-first-value from install to first captured finding is measured at <=5 min following only this path.

## Motivation
Rank-2 opportunity (Track C) + directly moves Convergence Criterion 3. Today onboarding is 4 manual commands + interactive permissions + mode-learning before any visible value. Composes existing scripts; new surface is a thin orchestrator + a good final print.

## Kill criteria
If the manual `claude config add` permission step is irreducible, demote to a `board-init` epilogue rather than a new command. Fold into board-init if it just duplicates Step 7.

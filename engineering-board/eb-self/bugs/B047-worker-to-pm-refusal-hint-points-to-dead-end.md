---
id: B047
type: bug
title: worker->pm refusal hint points to a dead-end (/board-resume no-ops from worker mode)
discovered: 2026-07-04
status: open
priority: P3
affects: hooks/scripts/board-mode-guard.sh
needs: tdd
pattern: [error-message, wrong-recovery-hint]
---

## Done when
- The worker->pm refusal message no longer suggests `/board-resume` (which only acts on `paused` and no-ops from worker mode); it matches the symmetric pm->worker message (restart-only).

## Observed behavior (C6 Track B — P3)
`board-mode-guard.sh` (worker current, pm target) prints "Run /board-resume or restart the session…". But `/board-resume` returns NOOP for null|pm|worker (only acts on `paused`), so a user following the hint gets a no-op. The symmetric pm->worker refusal correctly says restart-only, confirming the slip.

## Fix direction
Drop "Run /board-resume or" from the worker->pm refusal message; update the mode-routing test assertion in lockstep.

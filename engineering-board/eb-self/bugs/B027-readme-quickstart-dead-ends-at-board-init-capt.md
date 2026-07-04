---
id: B027
type: bug
title: README Quickstart dead-ends at board-init; capture-promote-fix path is undiscoverable
discovered: 2026-07-04
status: open
priority: P1
affects: README.md
needs: tdd
pattern: [onboarding, time-to-first-value]
---

## Done when
- The README Quickstart continues past `/board-init` with a short "first value" block: (1) findings are captured automatically when a turn ends, and where they land (`_sessions/`); (2) run `/pm-start` then end a turn to promote them; (3) run `/board-install-permissions` to stop per-script prompts.
- The README documents the honest time-to-first-value expectation (from the C2 measurement).

## Observed behavior (C2 Track B — new P1)
The Quickstart (README.md:48-89) contains only `marketplace add` → `install` → `/board-init` and stops. `/pm-start`, `/worker-start`, the passive-capture behavior, and the `_sessions/` location appear ONLY in the reference Modes table (README.md:98-107), never as onboarding steps. A user following only the Quickstart cannot reach first-promotion or first-fix, and cannot even confirm first-capture (invisible, B005). This is the dominant time-to-first-value cliff (measured: ≤5min capture and ≤15min promote are NOT met following public docs). Distinct from B005 (invisibility) and B006 (discipline restart).

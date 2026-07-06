---
id: B006
type: bug
title: Advancing one entry through tdd->review->validate requires two session restarts
discovered: 2026-07-04
status: resolved
priority: P2
affects: commands/worker-start.md
needs: done
pattern: [ux-friction]
---

## Done when
- Either a worker session can rotate disciplines (or `--discipline auto` advances whatever the entry `needs:`), OR the docs explicitly frame worker mode as a primitive and the Conductor as the intended end-to-end driver.
- The friction is measured/documented in the time-to-first-value analysis.

## Observed behavior
`worker-start.md:44-46` + `board-mode-guard.sh` REFUSE an in-session discipline switch, so one entry reaching `resolved` costs three worker sessions + restarts + a manual `/board-resolve`. Biggest friction against VP4 "autonomous build pipeline." Likely resolved by the Conductor (RFC 0001) — decide build-vs-document.

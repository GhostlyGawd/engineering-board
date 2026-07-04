---
id: B005
type: bug
title: First captured finding is invisible — buried in _sessions/, only a count shown
discovered: 2026-07-04
status: open
priority: P2
affects: hooks/stop-hook-procedure.md
needs: tdd
pattern: [invisible-feedback, ux-affordance]
---

## Done when
- After a passive capture, the Stop-hook output includes a one-line human summary of what was captured (e.g. "Captured: <title> — run /pm-start to promote"), not just a scratch-file count at the NEXT SessionStart.
- A walkthrough transcript shows the capture is observable on the turn it happens.

## Observed behavior
Passive path writes to `engineering-board/<p>/_sessions/<id>.md`; the user never sees it. First "value" surfaces only as a count at the next SessionStart (`board-session-start.sh:94`). For persona Sam this reads as "nothing happened." Highest-leverage day-one UX fix.

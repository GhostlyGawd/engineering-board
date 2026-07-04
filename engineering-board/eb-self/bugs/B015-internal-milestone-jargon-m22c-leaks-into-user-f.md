---
id: B015
type: bug
title: Internal milestone jargon (M2.2.c) leaks into user-facing command output
discovered: 2026-07-04
status: resolved
priority: P3
affects: commands/board-install-permissions.md
needs: tdd
pattern: [jargon-leak]
---

## Done when
- No internal milestone identifiers (M2.2.c, M2.2.b, etc.) appear in user-facing command prints; replaced with plain language or the public version.

## Observed behavior (Track B F6)
`board-install-permissions.md:23` prints "All M2.2.c permissions installed."; same jargon in `pm-start.md:8,87` and `worker-start.md:100`.

## Resolution (C1, PR C1b)
Internal milestone jargon (M2.2.b/M2.2.c) removed from user-facing command
copy: board-install-permissions.md ("All engineering-board permissions
installed"), pm-start.md (:8 description + :87 note), worker-start.md (:100).

---
id: B015
type: bug
title: Internal milestone jargon (M2.2.c) leaks into user-facing command output
discovered: 2026-07-04
status: open
priority: P3
affects: commands/board-install-permissions.md
needs: tdd
pattern: [jargon-leak]
---

## Done when
- No internal milestone identifiers (M2.2.c, M2.2.b, etc.) appear in user-facing command prints; replaced with plain language or the public version.

## Observed behavior (Track B F6)
`board-install-permissions.md:23` prints "All M2.2.c permissions installed."; same jargon in `pm-start.md:8,87` and `worker-start.md:100`.

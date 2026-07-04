---
id: B010
type: bug
title: Empty board renders a broken two-line open-count (0 then 0)
discovered: 2026-07-04
status: open
priority: P3
affects: hooks/scripts/board-session-start.sh
needs: tdd
pattern: [cosmetic]
---

## Done when
- An empty board prints a single clean "0 open item(s)" line.
- Test asserts the header shape on an empty board.

## Observed behavior (confirmed, Track A + D6)
`board-session-start.sh:37`: `open_count=$(echo "${open_items}" | grep -c "^- " || echo "0")` — on an empty board `grep -c` prints `0` AND exits 1, so `|| echo "0"` also fires → `open_count="0\n0"`, garbling the header. Fix: `|| true` (drop the `echo "0"`) or `printf` without the fallback.

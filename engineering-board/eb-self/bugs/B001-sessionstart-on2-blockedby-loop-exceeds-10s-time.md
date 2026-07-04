---
id: B001
type: bug
title: SessionStart O(n^2) blocked_by loop exceeds 10s timeout on large boards
discovered: 2026-07-04
status: resolved
priority: P1
affects: hooks/scripts/board-session-start.sh
needs: tdd
pattern: [o-n-squared, hook-latency]
---

## Done when
- The "Blocking relationships" section is computed in a single `python3` pass over frontmatter (like the learnings block), not a shell loop of `grep -rl` per unique blocker.
- A board of 1200 entries with distinct `blocked_by` relationships renders SessionStart well under the 10s `hooks.json` timeout.
- A perf regression test (or documented measurement in `.goal/evidence/loop/`) records the before/after wall time.

## Observed behavior
Measured (Track A red-team): 300 entries=2.15s, 800=7.97s, **1200=15.05s → exceeds the 10s SessionStart timeout**; control (1200 entries, no `blocked_by`)=0.06s. The board summary is silently truncated/lost past ~900-1000 entries — exactly the "mature board" the product targets.

## Root cause
`board-session-start.sh:61-72` runs `grep -rl "${line}" "${BOARD_DIR}"` once per unique `blocked_by:` line → O(unique_blockers × files).

## Resolution (C1, PR C1c)
The blocked_by dependency map now computes in a single python3 pass over entry
frontmatter (walks the board once, skips _sessions/_archive/_claims), replacing
the per-blocker `grep -rl` full-tree scan. Measured: 1200 entries 15.05s -> 0.10s;
2000 entries = 0.14s (linear). Evidence: .goal/evidence/loop/C1c-session-start-perf.txt.
New suite tests/session-start/automated.sh (T4) fails if a 1200-entry board takes
>= 10s. Also fixes the prior head -1 quirk that mis-attributed identical blocked_by lines.

---
id: B009
type: bug
title: Consolidator silently no-ops (findings lost) when python3 is broken/absent
discovered: 2026-07-04
status: resolved
priority: P2
affects: hooks/scripts/board-consolidate.sh
needs: done
pattern: [silent-failure]
---

## Done when
- A shared python3 preflight (`command -v python3`) fails loudly with one actionable line when python3 is missing, instead of exiting 0 having promoted nothing.
- Applied to the hooks that depend on python3 (consolidate, session-start, stop-gate).
- Test covers a shimmed broken python3.

## Observed behavior (confirmed, Track A)
With `python3` exiting 127, `board-consolidate.sh` exits 0 and promotes nothing; the Stop-hook path swallows it, so captured scratch findings are silently dropped with a success exit.

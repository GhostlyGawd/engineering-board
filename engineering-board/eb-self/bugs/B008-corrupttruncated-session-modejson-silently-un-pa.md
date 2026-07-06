---
id: B008
type: bug
title: Corrupt/truncated session-mode.json silently un-pauses a paused session
discovered: 2026-07-04
status: resolved
priority: P2
affects: hooks/scripts/board-stop-gate.sh
needs: done
pattern: [fail-open, silent-failure]
---

## Done when
- `board-stop-gate.sh` distinguishes "file present but unparseable" from "absent": an unparseable mode fails CLOSED (treated as paused / no-op) and emits a loud diagnostic.
- Same fix applied to `board-mode-guard.sh` `read_state` (corrupt → REFUSE, not ALLOW).
- Tests cover: valid paused (suppress), truncated JSON (fail closed), broken/absent python3 (fail closed).

## Observed behavior (confirmed, Track A)
`{"mode":"paused"}` → suppressed correctly. Truncate to `{"mode":"pau` → stop-gate emits nothing, exit 0 → autonomous prompt hook runs. Same with python3 exiting 127. `board-mode-guard.sh` with a truncated file returns ALLOW instead of REFUSE. This is defect D4 from PRODUCT_FACTS, confirmed reproducible.

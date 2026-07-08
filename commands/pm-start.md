---
description: Start a PM (project manager) session for the engineering board. Writes session-mode=pm to .engineering-board/session-mode.json so the Stop hook routes through the PM continuation path on each subsequent assistant turn. Idempotent.
argument-hint: (no arguments)
---

# /pm-start — start PM mode

Mark the current session as the engineering-board PM session. While `session-mode=pm`, the Stop hook runs the PM continuation procedure — the passive extractor plus the full consolidator + tidier + learnings-curator dispatch chain. Use this to designate a long-running session whose job is consolidating scratch into the live board.

## What to do

You are writing a small JSON state file that the Stop hook reads. Be precise about path and shape.

### Step 1 — Resolve paths

- State directory: `${CLAUDE_PROJECT_DIR}/.engineering-board/`
- State file: `${CLAUDE_PROJECT_DIR}/.engineering-board/session-mode.json`

Create the state directory if it does not exist (`mkdir -p` semantics).

### Step 2 — Run the mode-transition guard

Delegate the refusal-matrix decision to the deterministic guard (single source of truth for ARCHITECTURE.md §11.5):

```
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-mode-guard.sh" pm
```

Inspect the exit code:

- **0 (ALLOW)** — continue to Step 3. The guard's stdout contains `CURRENT_MODE=null` (only `null` reaches here; pm/worker/paused all short-circuit at exit 2 or 3).
- **2 (NOOP)** — print the guard's stdout verbatim and stop. The canonical message for this branch is `Engineering board: already in PM mode. No action taken.`
- **3 (REFUSE)** — print the guard's stdout verbatim and stop. The canonical messages for this branch are either:
  - `Engineering board: currently in worker mode (discipline=<value>). Restart the session to switch to PM mode. No action taken.`
  - `Engineering board: currently paused. Run /board-resume first, then /pm-start. No action taken.`

The four canonical messages live in `hooks/scripts/board-mode-guard.sh` so the same matrix is enforced identically by `/pm-start`, `/worker-start`, `/board-pause`, and `/board-resume`. Do not re-implement the matrix in this file.

### Step 3 — Determine current session_id

Read `${CLAUDE_PROJECT_DIR}/.engineering-board/last-stop-stdin.json` if it exists and extract the `session_id` field. If that file does not exist or has no `session_id`, use an empty string `""`. (The hook will populate it on the next Stop turn anyway.)

### Step 4 — Write the pm state

Write `${CLAUDE_PROJECT_DIR}/.engineering-board/session-mode.json` with content:

```json
{
  "mode": "pm",
  "previous_mode": null,
  "started_at": "<ISO-8601 now, UTC, e.g. 2026-05-11T19:32:07Z>",
  "session_id": "<value from step 3>"
}
```

Field rules:
- `mode` is always the JSON string `"pm"`.
- `previous_mode` is always JSON `null` for a fresh /pm-start (this field is reserved for /board-pause restore semantics).
- `started_at` is a JSON string; compute the current UTC time at second precision (e.g. via Bash: `python3 -c "import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"`). Do not stub the time.
- `session_id` is a JSON string (possibly empty).

### Step 5 — Register in the active-workers registry (v0.2.3)

After writing `session-mode.json`, invoke the registry helper so PM-fallback heartbeat and stale-session GC can see this session:

```
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-active-workers-register.sh" "<session_id from step 3>" "pm" "" "<started_at from step 4>"
```

Pass the empty string `""` for the discipline argument (PM has no discipline). If the script exits non-zero, print its stderr and continue — registry-write failures are not fatal to PM mode (the next register attempt on subsequent turns will retry). See `references/active-workers-registry.md` for the full contract.

### Step 6 — Confirm

Print exactly:

```
Engineering board: PM mode is on. Nothing promotes yet — findings become real board cards when you END YOUR NEXT TURN (just finish your next reply). Keep working normally; each turn you end, new findings consolidate onto the board. Run /board-pause to suspend.
```

Then stop.

## Notes

- This command is idempotent in the "already pm" sense (Step 2 NOOP short-circuit via the guard).
- The Stop hook reads `session-mode.json` at the start of its procedure; the next Stop-hook turn after this command will emit `<<EB-PM-CONTINUE>>` instead of `<<EB-PASSIVE-DONE>>`.
- `/board-pause` and `/board-resume` continue to work — pause sets `mode=paused` with `previous_mode=pm`, resume restores `mode=pm`.
- PM mode dispatches the full continuation chain: the passive extractor, then the consolidator + tidier + learnings-curator subagents that promote scratch into the live board and keep the index tidy.

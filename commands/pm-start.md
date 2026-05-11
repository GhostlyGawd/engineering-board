---
description: Start a PM (project manager) session for the engineering board. Writes session-mode=pm to .engineering-board/session-mode.json so the Stop hook routes through the PM continuation path on each subsequent assistant turn. Idempotent.
argument-hint: (no arguments)
---

# /pm-start — start PM mode

Mark the current session as the engineering-board PM session. While `session-mode=pm`, the Stop hook runs the PM continuation procedure (passive extractor + PM-CONTINUE sentinel in v0.2.2 M2.2.b; full consolidator+tidier dispatch in v0.2.2 M2.2.c). Use this to designate a long-running session whose job is consolidating scratch into the live board.

## What to do

You are writing a small JSON state file that the Stop hook reads. Be precise about path and shape.

### Step 1 — Resolve paths

- State directory: `${CLAUDE_PROJECT_DIR}/.engineering-board/`
- State file: `${CLAUDE_PROJECT_DIR}/.engineering-board/session-mode.json`

Create the state directory if it does not exist (`mkdir -p` semantics).

### Step 2 — Read current mode (if any)

If `session-mode.json` already exists:
- Parse it as JSON.
- Read the existing `mode` field.
- If `mode` is already `"pm"`, print `Engineering board: already in PM mode. No action taken.` and stop.
- If `mode` is `"worker"`, print `Engineering board: currently in worker mode (discipline=<value>). Run /board-resume or restart the session to switch to PM mode. No action taken.` and stop.
- If `mode` is `"paused"`, print `Engineering board: currently paused. Run /board-resume first, then /pm-start. No action taken.` and stop.
- Otherwise (mode is null, missing, or unrecognized), continue to Step 3 — switching to PM mode is allowed.

If the file does not exist, continue to Step 3.

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

### Step 5 — Confirm

Print exactly:

```
Engineering board: PM mode active. Stop hook will route through PM continuation each turn. Run /board-pause to suspend, or end the session normally to consolidate.
```

Then stop.

## Notes

- This command is idempotent in the "already pm" sense (Step 2 short-circuit).
- The Stop hook reads `session-mode.json` at the start of its procedure; the next Stop-hook turn after this command will emit `<<EB-PM-CONTINUE>>` instead of `<<EB-PASSIVE-DONE>>`.
- `/board-pause` and `/board-resume` continue to work — pause sets `mode=paused` with `previous_mode=pm`, resume restores `mode=pm`.
- v0.2.2 M2.2.b ships the mode switch and the PM continuation sentinel. v0.2.2 M2.2.c will extend the PM continuation procedure with consolidator + tidier subagent dispatch and board-state tidying.

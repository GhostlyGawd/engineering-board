---
description: Start a Worker session for the engineering board with a specific discipline (M2.2.b ships discipline=tdd only). Writes session-mode=worker + discipline to .engineering-board/session-mode.json so the Stop hook dispatches the matching worker subagent each turn. Idempotent.
argument-hint: --discipline <tdd>
---

# /worker-start — start Worker mode

Mark the current session as an engineering-board Worker session for a specific discipline. While `session-mode=worker`, the Stop hook runs the Worker continuation procedure: search the live board for `needs:<discipline>` entries, claim one via the atomic mkdir primitive, dispatch the matching worker subagent, release the claim, and emit a continuation sentinel.

## What to do

You are writing a small JSON state file that the Stop hook reads. Be precise about path, shape, and discipline validation.

### Step 1 — Parse the --discipline argument

The argument list is `$ARGUMENTS`. Look for `--discipline <value>` (one-token value, kebab-case). Accept the long form `--discipline=value` as well.

- If `--discipline` is missing, print `Usage: /worker-start --discipline <tdd>. No action taken.` and stop.
- If `<value>` is empty, print the same usage message and stop.
- If `<value>` is anything other than `tdd`, print `Engineering board: unsupported discipline "<value>". v0.2.2 M2.2.b ships only "tdd"; "review" and "validate" land in v0.2.2 M2.2.c. No action taken.` and stop.

The supported-discipline set for this milestone is exactly `{"tdd"}`. Do not silently coerce or accept aliases.

### Step 2 — Resolve paths

- State directory: `${CLAUDE_PROJECT_DIR}/.engineering-board/`
- State file: `${CLAUDE_PROJECT_DIR}/.engineering-board/session-mode.json`

Create the state directory if it does not exist (`mkdir -p` semantics).

### Step 3 — Read current mode (if any)

If `session-mode.json` already exists:
- Parse it as JSON.
- Read the existing `mode` and `discipline` fields.
- If `mode` is already `"worker"` AND the existing `discipline` matches the requested one, print `Engineering board: already in worker mode (discipline=<value>). No action taken.` and stop.
- If `mode` is `"worker"` with a DIFFERENT discipline, print `Engineering board: currently in worker mode (discipline=<existing>). Restart the session to switch to discipline=<requested>. No action taken.` and stop.
- If `mode` is `"pm"`, print `Engineering board: currently in PM mode. Restart the session to switch to worker mode. No action taken.` and stop.
- If `mode` is `"paused"`, print `Engineering board: currently paused. Run /board-resume first, then /worker-start --discipline <value>. No action taken.` and stop.
- Otherwise (mode is null, missing, or unrecognized), continue to Step 4 — switching to worker mode is allowed.

If the file does not exist, continue to Step 4.

### Step 4 — Determine current session_id

Read `${CLAUDE_PROJECT_DIR}/.engineering-board/last-stop-stdin.json` if it exists and extract the `session_id` field. If that file does not exist or has no `session_id`, use an empty string `""`.

### Step 5 — Write the worker state

Write `${CLAUDE_PROJECT_DIR}/.engineering-board/session-mode.json` with content:

```json
{
  "mode": "worker",
  "discipline": "<value from step 1>",
  "previous_mode": null,
  "started_at": "<ISO-8601 now, UTC, e.g. 2026-05-11T19:32:07Z>",
  "session_id": "<value from step 4>"
}
```

Field rules:
- `mode` is always the JSON string `"worker"`.
- `discipline` is the validated value from Step 1 (currently only `"tdd"`).
- `previous_mode` is always JSON `null` for a fresh /worker-start.
- `started_at` is a JSON string; compute the current UTC time at second precision (e.g. via Bash: `python3 -c "import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"`). Do not stub the time.
- `session_id` is a JSON string (possibly empty).

### Step 6 — Confirm

Print exactly:

```
Engineering board: Worker mode active (discipline=<value>). Stop hook will dispatch <value>-builder each turn until no needs:<value> entries remain, then emit <<EB-WORKER-NOTHING-TO-DO>>. Run /board-pause to suspend.
```

Then stop.

## Notes

- This command is idempotent in the "already worker with same discipline" sense (Step 3 short-circuit).
- The Stop hook reads `session-mode.json` at the start of its procedure; the next Stop-hook turn after this command will execute the Worker continuation procedure for the configured discipline.
- The Worker continuation in M2.2.b matches the locked-plan AC A2: "Within 10 continuations, worker claims `needs:`-matching task OR emits `nothing-to-do`."
- v0.2.2 M2.2.b ships discipline=`tdd` only. v0.2.2 M2.2.c will add disciplines `review` (code-reviewer subagent) and `validate` (validator subagent), wired through the `needs: tdd → review → validate → resolved` state machine.
- `/board-pause` and `/board-resume` continue to work — pause sets `mode=paused` with `previous_mode=worker`, resume restores `mode=worker` with the original `discipline`.

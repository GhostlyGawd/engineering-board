---
description: Pause passive listening in this session. The Stop hook will bypass the finding-extractor and return decision:approve. Use when you need a quiet session (planning, drafting, brainstorming) without scratch-board capture.
argument-hint: (no arguments)
---

# /board-pause — suspend passive listening

Pause the engineering-board passive listener for the current session. While paused, the Stop hook short-circuits with `<<EB-PASSIVE-PAUSED>>` and does NOT invoke the finding-extractor subagent or write to the scratch board. Use this when you want a quiet session for planning, drafting, or brainstorming without capture overhead.

## What to do

You are writing a small JSON state file that the Stop hook reads. Be precise about path and shape.

### Step 1 — Resolve paths

- State directory: `${CLAUDE_PROJECT_DIR}/.engineering-board/`
- State file: `${CLAUDE_PROJECT_DIR}/.engineering-board/session-mode.json`

Create the state directory if it does not exist (`mkdir -p` semantics).

### Step 2 — Read current mode (if any)

If `session-mode.json` already exists:
- Parse it as JSON.
- Read the existing `mode` field — this becomes the `previous_mode` value below.
- If the existing `mode` is already `"paused"`, print `Engineering board: already paused. No action taken.` and stop.

If the file does not exist, `previous_mode` is `null`.

### Step 3 — Determine current session_id

Read `${CLAUDE_PROJECT_DIR}/.engineering-board/last-stop-stdin.json` if it exists and extract the `session_id` field. If that file does not exist or has no `session_id`, use an empty string `""`.

### Step 4 — Write the paused state

Write `${CLAUDE_PROJECT_DIR}/.engineering-board/session-mode.json` with content:

```json
{
  "mode": "paused",
  "previous_mode": "<value from step 2, or null>",
  "paused_at": "<ISO-8601 now, UTC, e.g. 2026-05-11T14:32:07Z>",
  "session_id": "<value from step 3>"
}
```

The `previous_mode` field is a JSON string (or JSON `null` if no prior mode was set). `paused_at` is a JSON string. `session_id` is a JSON string (possibly empty).

### Step 5 — Confirm

Print exactly:

```
Engineering board: passive listening paused. Run /board-resume to re-enable.
```

Then stop.

## Notes

- This command is idempotent in the "already paused" sense (Step 2 short-circuit).
- The Stop hook reads `session-mode.json` at the start of its procedure; the next Stop-hook turn after this command will emit `<<EB-PASSIVE-PAUSED>>` and skip extraction.
- `/board-resume` reverses this state.

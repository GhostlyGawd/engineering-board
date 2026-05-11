---
description: Resume passive listening after /board-pause. Restores prior session mode and clears the paused_at timestamp.
argument-hint: (no arguments)
---

# /board-resume — re-enable passive listening

Resume the engineering-board passive listener after a `/board-pause`. Restores the prior `mode` value (or `null` if there was none) and clears the `paused_at` timestamp. The next Stop-hook turn will resume invoking the finding-extractor.

## What to do

### Step 1 — Resolve state file

State file: `${CLAUDE_PROJECT_DIR}/.engineering-board/session-mode.json`

### Step 2 — Read current state

If the state file does not exist, print exactly:

```
Engineering board: not currently paused. No action taken.
```

and stop.

Otherwise, parse the file as JSON and inspect the `mode` field. If `mode` is not `"paused"` (e.g., it is `null`, `"pm"`, `"worker"`, or missing), print exactly:

```
Engineering board: not currently paused. No action taken.
```

and stop.

### Step 3 — Determine current session_id

Read `${CLAUDE_PROJECT_DIR}/.engineering-board/last-stop-stdin.json` if it exists and extract the `session_id` field. If that file does not exist or has no `session_id`, use an empty string `""`.

### Step 4 — Rewrite the state file

Read the `previous_mode` field from the parsed JSON in Step 2. Rewrite `session-mode.json` with content:

```json
{
  "mode": "<previous_mode value from step 2; if it was JSON null, write JSON null (not the string \"null\")>",
  "previous_mode": null,
  "paused_at": null,
  "session_id": "<value from step 3>"
}
```

Important: if the prior `previous_mode` was JSON `null`, the new `mode` must also be JSON `null` (not the string `"null"`). If it was a string like `"pm"` or `"worker"`, the new `mode` is that string.

### Step 5 — Confirm

Print exactly:

```
Engineering board: passive listening resumed.
```

Then stop.

## Notes

- This command is safe to run when not paused — it prints a no-op message and exits.
- After resume, the Stop hook resumes normal scratch capture on the next assistant turn.

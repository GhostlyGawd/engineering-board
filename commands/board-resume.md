---
description: Resume passive listening after /board-pause. Restores prior session mode and clears the paused_at timestamp.
argument-hint: (no arguments)
---

# /board-resume — re-enable passive listening

Resume the engineering-board passive listener after a `/board-pause`. Restores the prior `mode` value (or `null` if there was none) and clears the `paused_at` timestamp. The next Stop-hook turn will resume invoking the finding-extractor.

## What to do

### Step 1 — Resolve state file

State file: `${CLAUDE_PROJECT_DIR}/.engineering-board/session-mode.json`

### Step 2 — Run the mode-transition guard

Delegate the refusal-matrix decision to the deterministic guard (single source of truth for ARCHITECTURE.md §11.5):

```
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-mode-guard.sh" resumed
```

Inspect the exit code:

- **0 (ALLOW)** — parse the guard's stdout. It emits key=value lines including `RESTORE_MODE=<pm|worker|null>` and `RESTORE_DISCIPLINE=<tdd|review|validate|null>`. Use these in Step 4 below. Then continue to Step 3.
- **2 (NOOP)** — print the guard's stdout verbatim and stop. The canonical message for this branch is `Engineering board: not currently paused. No action taken.` (Fires when no state file exists OR `mode` is anything other than `"paused"`.)

`/board-resume` has no REFUSE branch — every state either ALLOWs (paused) or NOOPs (not paused).

### Step 3 — Determine current session_id

Read `${CLAUDE_PROJECT_DIR}/.engineering-board/last-stop-stdin.json` if it exists and extract the `session_id` field. If that file does not exist or has no `session_id`, use an empty string `""`.

### Step 4 — Rewrite the state file

Rewrite `session-mode.json` with content:

```json
{
  "mode": "<RESTORE_MODE from the guard's stdout; JSON null if null>",
  "discipline": "<RESTORE_DISCIPLINE from the guard's stdout; only present when RESTORE_MODE == 'worker'; JSON null otherwise>",
  "previous_mode": null,
  "previous_discipline": null,
  "paused_at": null,
  "session_id": "<value from step 3>"
}
```

Field rules:
- If `RESTORE_MODE == null`: write the literal JSON `null` (not the string `"null"`) for `mode`, and JSON `null` for `discipline`.
- If `RESTORE_MODE == "pm"`: write `"mode": "pm"`, `"discipline": null`.
- If `RESTORE_MODE == "worker"`: write `"mode": "worker"`, `"discipline": "<RESTORE_DISCIPLINE>"`. The discipline MUST match the one captured at `/board-pause` time so the (mode, discipline) round-trip is bit-exact per ARCHITECTURE.md §11.5.
- `previous_mode` and `previous_discipline` reset to JSON `null` — the pause/resume cycle has completed.
- `paused_at` resets to JSON `null`.
- `session_id` is a JSON string (possibly empty).

### Step 5 — Flip the registry paused field (v0.2.3)

After rewriting `session-mode.json`, clear the paused flag in the active-workers registry:

```
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-active-workers-bump.sh" "<session_id from step 3>" --paused false
```

If the session is not registered, the bump script no-ops silently. Continue regardless of its exit status.

### Step 6 — Confirm

Print exactly:

```
Engineering board: passive listening resumed.
```

Then stop.

## Notes

- This command is safe to run when not paused — it prints a no-op message and exits via the guard's NOOP branch.
- After resume, the Stop hook resumes normal scratch capture on the next assistant turn. If the prior mode was `worker`, the Stop hook dispatches the matching worker subagent because `discipline` is restored too.

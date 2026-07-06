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

### Step 2 — Run the mode-transition guard

Delegate the refusal-matrix decision to the deterministic guard (single source of truth for ARCHITECTURE.md §11.5):

```
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-mode-guard.sh" paused
```

Inspect the exit code:

- **0 (ALLOW)** — parse the guard's stdout. It emits key=value lines including `PREVIOUS_MODE=<pm|worker|null>` and `PREVIOUS_DISCIPLINE=<tdd|review|validate|null>`. Use these values in Step 4 below. Then continue to Step 3.
- **2 (NOOP)** — print the guard's stdout verbatim and stop. The canonical message for this branch is `Engineering board: already paused. No action taken.`

`/board-pause` has no REFUSE branch — every non-paused state allows the transition. The matrix in ARCHITECTURE.md §11.5 lists `/board-pause` as the in-session escape hatch.

### Step 3 — Determine current session_id

Read `${CLAUDE_PROJECT_DIR}/.engineering-board/last-stop-stdin.json` if it exists and extract the `session_id` field. If that file does not exist or has no `session_id`, use an empty string `""`.

### Step 4 — Write the paused state

Write `${CLAUDE_PROJECT_DIR}/.engineering-board/session-mode.json` with content:

```json
{
  "mode": "paused",
  "previous_mode": "<PREVIOUS_MODE from the guard's stdout; JSON null if null>",
  "previous_discipline": "<PREVIOUS_DISCIPLINE from the guard's stdout; JSON null if null>",
  "paused_at": "<ISO-8601 now, UTC, e.g. 2026-05-11T14:32:07Z>",
  "session_id": "<value from step 3>"
}
```

Field rules:
- `previous_mode` is a JSON string (`"pm"` or `"worker"`) or JSON `null`. The guard's stdout key is the source of truth.
- `previous_discipline` is a JSON string (`"tdd"` / `"review"` / `"validate"`) only when `previous_mode == "worker"`; otherwise JSON `null`. Preserving this lets `/board-resume` restore the exact (mode, discipline) tuple per ARCHITECTURE.md §11.5.
- `paused_at` is a JSON string at second precision.
- `session_id` is a JSON string (possibly empty).

### Step 5 — Flip the registry paused field (v0.2.3)

After writing `session-mode.json`, mark the session as paused in the active-workers registry so PM-fallback heartbeat skips its claims:

```
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-active-workers-bump.sh" "<session_id from step 3>" --paused true
```

If the session is not registered (e.g. passive-only mode that never ran `/pm-start` or `/worker-start`), the bump script no-ops silently. Continue regardless of its exit status.

### Step 6 — Confirm

Print exactly:

```
Engineering board: passive listening paused. Run /board-resume to re-enable.
```

Then stop.

## Notes

- This command is idempotent in the "already paused" sense (Step 2 NOOP short-circuit via the guard).
- The Stop hook reads `session-mode.json` at the start of its procedure; the next Stop-hook turn after this command will emit `<<EB-PASSIVE-PAUSED>>` (paired with the plain line "Board capture is paused — run /board-resume to restore.") and skip extraction.
- `/board-resume` reverses this state and restores the prior (mode, discipline) tuple from `previous_mode` + `previous_discipline`.

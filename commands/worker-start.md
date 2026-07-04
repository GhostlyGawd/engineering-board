---
description: Start a Worker session for the engineering board with a specific discipline (tdd, review, or validate). Writes session-mode=worker + discipline to .engineering-board/session-mode.json so the Stop hook dispatches the matching worker subagent each turn. Idempotent.
argument-hint: --discipline <tdd|review|validate>
---

# /worker-start — start Worker mode

Mark the current session as an engineering-board Worker session for a specific discipline. While `session-mode=worker`, the Stop hook runs the Worker continuation procedure: search the live board for `needs:<discipline>` entries, claim one via the atomic mkdir primitive, dispatch the matching worker subagent, release the claim, and emit a continuation sentinel.

## What to do

You are writing a small JSON state file that the Stop hook reads. Be precise about path, shape, and discipline validation.

### Step 1 — Parse the --discipline argument

The argument list is `$ARGUMENTS`. Look for `--discipline <value>` (one-token value, kebab-case). Accept the long form `--discipline=value` as well.

- If `--discipline` is missing, print `Usage: /worker-start --discipline <tdd|review|validate>. No action taken.` and stop.
- If `<value>` is empty, print the same usage message and stop.
- If `<value>` is anything other than `tdd`, `review`, or `validate`, print `Engineering board: unsupported discipline "<value>". supported disciplines: tdd, review, validate. No action taken.` and stop.

The supported-discipline set for this milestone is exactly `{"tdd","review","validate"}`. Do not silently coerce or accept aliases.

### Step 2 — Resolve paths

- State directory: `${CLAUDE_PROJECT_DIR}/.engineering-board/`
- State file: `${CLAUDE_PROJECT_DIR}/.engineering-board/session-mode.json`

Create the state directory if it does not exist (`mkdir -p` semantics).

### Step 3 — Run the mode-transition guard

Delegate the refusal-matrix decision to the deterministic guard (single source of truth for ARCHITECTURE.md §11.5):

```
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-mode-guard.sh" worker --discipline <value from step 1>
```

Inspect the exit code:

- **0 (ALLOW)** — continue to Step 4.
- **2 (NOOP)** — print the guard's stdout verbatim and stop. The canonical message for this branch is `Engineering board: already in worker mode (discipline=<value>). No action taken.`
- **3 (REFUSE)** — print the guard's stdout verbatim and stop. The canonical messages for this branch are:
  - `Engineering board: currently in PM mode. Restart the session to switch to worker mode. No action taken.`
  - `Engineering board: currently in worker mode (discipline=<existing>). Restart the session to switch to discipline=<requested>. No action taken.`
  - `Engineering board: currently paused. Run /board-resume first, then /worker-start --discipline <value>. No action taken.`

The four canonical messages live in `hooks/scripts/board-mode-guard.sh` so the same matrix is enforced identically by `/pm-start`, `/worker-start`, `/board-pause`, and `/board-resume`. Do not re-implement the matrix in this file.

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
- `discipline` is the validated value from Step 1 (`"tdd"`, `"review"`, or `"validate"`).
- `previous_mode` is always JSON `null` for a fresh /worker-start.
- `started_at` is a JSON string; compute the current UTC time at second precision (e.g. via Bash: `python3 -c "import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))"`). Do not stub the time.
- `session_id` is a JSON string (possibly empty).

### Step 6 — Register in the active-workers registry (v0.2.3)

After writing `session-mode.json`, invoke the registry helper so PM-fallback heartbeat and stale-session GC can see this session:

```
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-active-workers-register.sh" "<session_id from step 4>" "worker" "<discipline from step 1>" "<started_at from step 5>"
```

If the script exits non-zero, print its stderr and continue — registry-write failures are not fatal to Worker mode (the next register attempt on subsequent turns will retry). See `references/active-workers-registry.md` for the full contract.

### Step 7 — Confirm

Print exactly:

```
Engineering board: Worker mode active (discipline=<value>). Stop hook will dispatch the <value> worker subagent each turn until no needs:<value> entries remain, then emit <<EB-WORKER-NOTHING-TO-DO>>. Run /board-pause to suspend.
```

Then stop.

## Notes

- This command is idempotent in the "already worker with same discipline" sense (Step 3 NOOP short-circuit via the guard).
- The Stop hook reads `session-mode.json` at the start of its procedure; the next Stop-hook turn after this command will execute the Worker continuation procedure for the configured discipline.
- The Worker continuation matches the locked-plan AC A2: "Within 10 continuations, worker claims `needs:`-matching task OR emits `nothing-to-do`."
- All three disciplines (tdd, review, validate) are wired through the `needs: tdd -> review -> validate -> resolved` state machine.
- `/board-pause` and `/board-resume` continue to work -- pause sets `mode=paused` with `previous_mode=worker` and `previous_discipline=<value>`, resume restores `mode=worker` with the original `discipline`.

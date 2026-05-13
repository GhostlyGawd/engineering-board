---
description: Manually release a claim on an engineering-board entry. Useful when a worker session has gone offline or an entry is stuck in_progress. Reads the claim owner from _claims/<entry-id>/owner.txt and verifies session ownership before releasing. Use --force to override a mismatched owner (breaks the active worker's lock).
argument-hint: <entry-id>
---

# /board-claim-release — manual claim release

Release a stuck or orphaned claim so another worker (or the same user) can re-acquire it. The Stop hook's worker-mode procedure releases claims automatically each turn; this command is the manual fallback for when a worker session has gone offline or a claim is visibly stuck.

## What to do

### Step 1 — Parse arguments

Extract `<entry-id>` from `$ARGUMENTS`. The entry-id must match `^[A-Z][0-9]+$` (e.g. B017, F003, Q012).

Also check whether `--force` appears in `$ARGUMENTS`.

If no entry-id is found or the pattern does not match, print:

```
Usage: /board-claim-release <entry-id> (e.g. B017). No action taken.
```

Then stop.

### Step 2 — Resolve board directory

Read `${CLAUDE_PROJECT_DIR}/docs/boards/BOARD-ROUTER.md` if it exists and extract the board path for the current project. If that file does not exist, fall back to `${CLAUDE_PROJECT_DIR}/docs/board/`.

### Step 3 — Check claim existence

Check whether `<board-dir>/_claims/<entry-id>/` exists.

If not, print:

```
No claim found for <entry-id>. Nothing to release.
```

Then stop.

### Step 4 — Read claim owner and current session

Read `<board-dir>/_claims/<entry-id>/owner.txt`. Extract the `session_id:` line value (second whitespace-separated token).

Read `${CLAUDE_PROJECT_DIR}/.engineering-board/last-stop-stdin.json` if it exists. Extract the `session_id` field. If the file does not exist or has no `session_id`, use an empty string `""` as the current session_id.

### Step 5 — Run the release script

Run:

```bash
bash $CLAUDE_PLUGIN_ROOT/hooks/scripts/board-claim-release.sh <board-dir> <entry-id> <session-id>
```

Where `<session-id>` is:
- Without `--force`: the current session_id from Step 4.
- With `--force`: the owner session_id read from `owner.txt` in Step 4 (so the script's owner-check passes regardless of who is calling).

Handle exit codes:

- **Exit 0**: print `Released claim on <entry-id>.` and stop.
- **Exit 3 (owner mismatch, no --force)**: print:
  ```
  Claim is held by a different session (<owner-session-id>). Use /board-claim-release <entry-id> --force to override.
  ```
  Then stop.
- **Exit 4 (retries exhausted)**: print `Failed to release claim on <entry-id> after retries. The filesystem may be locked. Try again shortly.` and stop.

If `--force` was used, prefix the success message with a warning:

```
Warning: force-release used. Any active worker holding this claim will encounter an error on its next turn.
Released claim on <entry-id>.
```

## Notes

- The Stop hook's worker-mode procedure calls `board-claim-release.sh` automatically at the end of each worker turn. Manual release is only needed when a worker session has gone offline mid-turn or a claim appears stuck.
- `--force` bypasses the session-id owner check by passing the claim's own owner session_id to the release script. This is intentional and documented — forcing release of an active worker's claim will cause that worker to error on its next attempt to release or heartbeat.
- Entry-id validation (`^[A-Z][0-9]+$`) catches common typos like lowercase ids or missing prefix.

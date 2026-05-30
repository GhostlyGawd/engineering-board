# Active workers registry (v0.2.3)

Contract for `.engineering-board/active-workers.json` — the source of truth for which PM/Worker sessions are currently live.

This file documents the registry. The implementation lives in three scripts:

- `hooks/scripts/board-active-workers-register.sh` — append-or-update.
- `hooks/scripts/board-active-workers-cleanup.sh` — remove a session entry.
- `hooks/scripts/board-active-workers-bump.sh` — refresh `last_seen` and `claim_ids_held`.

## Purpose

v0.2.2 ships PM and Worker orchestration, but the system has no central record of which sessions are alive at any moment. Two consequences leak from that gap:

1. **A PM session that crashes mid-consolidation** leaves scratch un-promoted. The next PM session can't tell whether the prior PM is still running and won't run catch-up consolidation.
2. **A Worker session whose claim heartbeat falls behind** (slow Bash op, OS pause) has its claim reclaimed by another worker — but there's no signal that the original worker is still alive and about to refresh.

The registry plus a PM-fallback heartbeat (`board-pm-fallback-heartbeat.sh`, separate doc) closes both gaps: the PM observes "this session is still alive per the registry" and refreshes its claim heartbeats on its behalf.

## File location

`${CLAUDE_PROJECT_DIR}/.engineering-board/active-workers.json`

Same directory as `session-mode.json` and `last-stop-stdin.json`. Not committed to the repo (gitignored under `.engineering-board/`).

## Schema

A JSON array of session entries. Each entry:

```json
{
  "session_id": "<uuid string>",
  "started_at": "<ISO 8601 UTC, second precision>",
  "last_seen":  "<ISO 8601 UTC, second precision>",
  "mode":       "pm | worker",
  "discipline": "tdd | review | validate | null",
  "cwd":        "<absolute path>",
  "claim_ids_held": ["<entry-id>", ...],
  "paused": false
}
```

Field rules:

- `session_id` is the value from `last-stop-stdin.json`'s `session_id` field. Empty string allowed for the brief window before the first Stop event fires.
- `started_at` is set once on first register; never updated.
- `last_seen` is bumped on every register, every bump, and (per consensus plan §v0.2.3) every Nth worker heartbeat where `N = ceil(staleClaimSec / 4 / heartbeatIntervalSec)`.
- `mode` is `"pm"` for PM sessions, `"worker"` for Worker sessions.
- `discipline` is JSON `null` for PM mode; one of `"tdd"` / `"review"` / `"validate"` for Worker mode.
- `cwd` records where the session was launched (informational; the registry is `CLAUDE_PROJECT_DIR`-scoped already).
- `claim_ids_held` is the union of entry IDs the session currently holds a claim on. Updated by `board-active-workers-bump.sh` on claim acquire / release.
- `paused` is `true` while `/board-pause` is in effect; `false` otherwise. PM-fallback heartbeat skips paused entries.

## Concurrency

All writes serialized through `<state_dir>/active-workers.json.lock`, a `mkdir`-based lockfile (same atomic primitive as `_claims/<entry-id>/`).

Write protocol:

1. `mkdir <state_dir>/active-workers.json.lock` — retry up to 5× with 100ms backoff on `EEXIST`.
2. Read `active-workers.json` if it exists; else treat as `[]`.
3. Modify the array in-memory (append / update / remove).
4. Write to `active-workers.json.tmp` in the same dir.
5. `mv active-workers.json.tmp active-workers.json` (atomic-rename within volume; on NTFS, retry 3× with 250ms jitter on `EBUSY`).
6. `rmdir <state_dir>/active-workers.json.lock`.

Reads are not lock-guarded — they read whatever shape exists. Atomic-rename guarantees the file is always either the pre- or post-write version, never a partial.

## Liveness

A session entry is **alive** if `(now - last_seen) < 2 * staleClaimSec` (default `2 * 180 = 360s`; cloud-sync `2 * 300 = 600s`).

There is no OS introspection. Liveness is exclusively recorded by `last_seen` bumps from:

- `/pm-start` and `/worker-start` (initial register).
- `/board-resume` (resume from pause).
- `board-active-workers-bump.sh` (called by worker subagents on claim acquire / release / Nth heartbeat).
- PM-tidier observing the session writing claims or scratch (v0.2.3 PM-fallback path).

The `2x` multiplier vs. `staleClaimSec` is intentional: it gives a registered session one full stale-window of grace before peer sessions stop trusting it.

## Cleanup

Three paths reach cleanup:

1. **Explicit:** `board-active-workers-cleanup.sh <session_id>` invoked on intentional session end.
2. **Manual:** a user may invoke `/board-pause` (sets `paused: true`) when stepping away; the entry stays in the registry but its claims are skipped by the fallback heartbeat.
3. **Lazy / GC:** `board-active-workers-register.sh` does a sweep on every invocation — entries whose `last_seen` is older than `2 * staleClaimSec` are removed before the new entry is written. This is the only path that runs automatically on the timescale of session ends.

Cleanup never deletes a still-held claim. Claims are owned by the claim filesystem (`_claims/<entry-id>/`) and reclaimed by `board-claim-reclaim-stale.sh` against the heartbeat timestamp, not the registry.

## Invariants

- The file always parses as a JSON array (possibly empty).
- No two entries share a `session_id`.
- An entry with `mode: "worker"` always has a non-null `discipline`.
- An entry with `mode: "pm"` always has `discipline: null`.
- `claim_ids_held` is sorted ASCII-ascending (canonical form for diff cleanliness).

These invariants are enforced by the three scripts; readers may rely on them.

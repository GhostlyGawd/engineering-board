---
description: Apply or roll back the v0.2.x -> v0.3.0 board migration. --apply creates a learnings/ subdir, back-fills needs:tdd on open bugs/features that lack it, and snapshots the pre-migration state. --rollback restores the snapshot. Both are SHA256-idempotent.
argument-hint: --apply|--rollback|--status [project]
---

# /board-migrate — v0.2.x → v0.3.0 migration

Apply or roll back the v0.3.0 migration on one or all project boards in this repo. The actual work is done by `hooks/scripts/board-migrate.sh`; this command is a thin dispatcher that resolves board paths from the router and reports per-project status.

## What the migration does

**`--apply`:**
1. Snapshots the entire `<board-dir>/` to `<board-dir>/_migrate-snapshot/pre-migrate/` (only on first apply).
2. Creates `<board-dir>/learnings/` with a `.gitkeep` if missing.
3. Back-fills `needs: tdd` on bug/feature entries with `status: open` (or `in_progress`, `blocked`) that don't already have a `needs:` field. Resolved entries are left alone.
4. Writes `<board-dir>/.migration-state.json` with the apply timestamp and post-apply SHA.

Idempotent: re-running on an already-migrated board produces a byte-identical tree (same SHA).

**`--rollback`:**
1. Verifies the pre-migrate snapshot exists.
2. Removes files added by the migrate (e.g. `learnings/.gitkeep`).
3. Restores files from the snapshot, overwriting any drift.
4. Records `rolled_back_at` and `sha_after_rollback` in `.migration-state.json`.

After rollback, the live tree SHA equals the pre-migrate SHA.

**`--status`:**
Reports whether each project has a snapshot, the current live SHA, and the state file contents.

## What to do

### Step 1 — Parse arguments

The argument list is `$ARGUMENTS`. Expect:
- `--apply [project]` or `--rollback [project]` or `--status [project]`.
- If `project` is omitted, operate on every board listed in `docs/boards/BOARD-ROUTER.md` (or the legacy `docs/board/` if no router exists).
- If `project` is given, operate only on that project's board directory.

If the first argument is missing or not one of the three flags, print:

```
Usage: /board-migrate --apply [project] | --rollback [project] | --status [project]
```

and stop.

### Step 2 — Resolve target board directories

If `BOARD-ROUTER.md` exists in `$CLAUDE_PROJECT_DIR/docs/boards/`, read its table rows. Each row has columns `project | path | affects-prefix`.

- If `project` was given on the command line, filter to that row.
- Otherwise include all rows.

If no router exists, target the legacy `$CLAUDE_PROJECT_DIR/docs/board/` if it exists; otherwise print `No board layout found at docs/boards/ or docs/board/.` and stop.

### Step 3 — Dispatch the migrate script

For each resolved board directory, run:

```
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-migrate.sh" <mode> "<absolute board dir>"
```

where `<mode>` is `--apply`, `--rollback`, or `--status` per the user's command.

Capture the script's stdout per project. If the script exits non-zero, capture its stderr and continue to the next project (do not abort the whole pass).

### Step 4 — Confirm

After all projects complete, print a summary:

```
/board-migrate <mode> summary:
  <project>: <ok | failed: <reason>>
```

Include the script's reported `sha_after` (or `sha_after_rollback`) per project.

## Notes

- The migration is reversible by design — `--apply` always snapshots first. `--rollback` works as long as the snapshot exists.
- `--apply` may be re-run safely at any time. Subsequent runs touch nothing (SHA stable).
- `--rollback` is destructive of post-apply changes: any user edits made to migrated entries after `--apply` will be overwritten by the snapshot. Re-edit after rollback.
- The snapshot directory `<board-dir>/_migrate-snapshot/` is excluded from BOARD.md indexing and from `board-index-check.sh` (subdirs starting with `_` are runtime state).
- After a successful `--apply`, run `/board-rebuild` to refresh `BOARD.md` and `GRAPH.yml` if you want the index to reflect post-migration entry counts (the back-fill changes `needs:` fields but not entry counts).

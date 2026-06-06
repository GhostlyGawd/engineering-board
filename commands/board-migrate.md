---
description: Apply or roll back the v0.2.x -> v0.3.0 board migration, or relocate boards onto the 1.1.0 engineering-board/ default. --apply creates a learnings/ subdir, back-fills needs:tdd on open bugs/features that lack it, and snapshots the pre-migration state. --rollback restores the snapshot. --relocate moves docs/boards/ content to engineering-board/ and rewrites the router. --apply/--rollback are SHA256-idempotent; --relocate is move-idempotent.
argument-hint: --apply|--rollback|--status|--relocate [project]
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

**`--relocate` (1.1.0):**
Relocates committed board content from the compat `docs/boards/` location to the visible `engineering-board/` default:
1. Snapshots the whole `docs/boards/` tree first into the gitignored `.engineering-board/relocate-snapshot/<iso>/`.
2. Moves `docs/boards/<project>/` → `engineering-board/<project>/` (prefers `git mv` inside a work tree, so the move is history-preserving and reversible; falls back to plain `mv`).
3. Moves + rewrites the router to `engineering-board/BOARD-ROUTER.md`, rewriting each `docs/boards/<p>` path column to `engineering-board/<p>` (affects-prefix column untouched).
4. Reports per project (moved / already-relocated / skipped).

Idempotent: re-running on an already-relocated board is a no-op, and old `docs/boards/` + legacy `docs/board/` keep resolving (so a half-migrated repo still works). Legacy single-board `docs/board/` is **not** auto-relocated (that would mean synthesizing a router); it keeps resolving via the fallback.

## What to do

### Step 1 — Parse arguments

The argument list is `$ARGUMENTS`. Expect:
- `--apply [project]`, `--rollback [project]`, `--status [project]`, or `--relocate [project]`.
- **If the mode is `--relocate`:** skip Steps 2–4 and follow the **Relocate (1.1.0)** section at the end — relocation is a repo-level move dispatched to a separate script, not a per-board loop.
- If `project` is omitted, operate on every board listed in `docs/boards/BOARD-ROUTER.md` (or the legacy `docs/board/` if no router exists).
- If `project` is given, operate only on that project's board directory.

If the first argument is missing or not one of the four flags, print:

```
Usage: /board-migrate --apply [project] | --rollback [project] | --status [project] | --relocate [project]
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

## Relocate (1.1.0): docs/boards/ → engineering-board/

For `--relocate`, do **not** loop per board dir. Run the relocation script once for the whole repo — it resolves the router and moves every project (or just `[project]` when given):

```
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-relocate.sh" "$CLAUDE_PROJECT_DIR" [project]
```

Print the script's stdout — the per-project moved/already-relocated/skipped lines, the snapshot path, and the summary — back to the user. The script is idempotent and safe to re-run.

After a successful relocate, run `/board-rebuild` so `BOARD.md`/`GRAPH.yml` reflect the new paths, and remind the user to add the `engineering-board/` runtime stanza to `.gitignore` (printed by `/board-init`) if they haven't already.

## Notes

- The migration is reversible by design — `--apply` always snapshots first. `--rollback` works as long as the snapshot exists.
- `--apply` may be re-run safely at any time. Subsequent runs touch nothing (SHA stable).
- `--rollback` is destructive of post-apply changes: any user edits made to migrated entries after `--apply` will be overwritten by the snapshot. Re-edit after rollback.
- The snapshot directory `<board-dir>/_migrate-snapshot/` is excluded from BOARD.md indexing and from `board-index-check.sh` (subdirs starting with `_` are runtime state).
- After a successful `--apply`, run `/board-rebuild` to refresh `BOARD.md` and `GRAPH.yml` if you want the index to reflect post-migration entry counts (the back-fill changes `needs:` fields but not entry counts).
- `--relocate` is reversible: in a work tree it uses `git mv` (undo via git) and snapshots `docs/boards/` to `.engineering-board/relocate-snapshot/` first. It does not auto-relocate legacy `docs/board/`.

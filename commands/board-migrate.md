---
description: Run one of two independent board maintenance workflows. Use --apply, --rollback, or --status for the v0.2.x to v0.3.0 data migration. Use --relocate to move committed boards from docs/boards/ to engineering-board/. The modes use separate scripts and safety boundaries.
argument-hint: --apply|--rollback|--status|--relocate [project]
---


# /board-migrate: choose one migration mode

This compatibility command dispatches one of two independent workflows. Select
the mode before you resolve targets or run a script. Do not combine mode flags.

## Choose a migration mode

### Data migration mode

Use `--apply`, `--rollback`, or `--status` to manage the v0.2.x to v0.3.0
board-data migration. This workflow operates on one or more resolved project
board directories and runs `hooks/scripts/board-migrate.sh` once for each
target.

### Folder relocation mode

Use `--relocate` to move committed board folders from the compatible
`docs/boards/` layout to the `engineering-board/` default. This workflow
operates at the repository level and runs `hooks/scripts/board-relocate.sh`
once.

The two workflows share the `/board-migrate` command name for compatibility.
They do not share execution steps.

```text
Usage:
  /board-migrate --apply [project]
  /board-migrate --rollback [project]
  /board-migrate --status [project]
  /board-migrate --relocate [project]
```

## Data migration workflow

### Step 1: Validate the data mode

Accept `--apply`, `--rollback`, or `--status` as the first argument. Accept an
optional project name as the second argument. Stop with the usage text if an
argument is invalid.

### Step 2: Resolve project board directories

Source `hooks/scripts/board-paths.sh` and use `eb_board_rows`. This applies the
current location order: `engineering-board/`, then `docs/boards/`, then the
legacy single-board `docs/board/` fallback.

- If the user supplied a project, select only its row.
- If the user omitted a project, select every returned row.
- If no row exists, report that there is no board layout and suggest
  `/board-init <project>` for a new board. Then stop.

### Step 3: Run the data migration script

For each selected board directory, run:

```bash
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-migrate.sh" <mode> "<absolute-board-dir>"
```

Use `--apply`, `--rollback`, or `--status` as `<mode>`. Capture standard output
for each project. If one project fails, capture its standard error and continue
with the other selected projects.

### Step 4: Report the data result

Print one result for each project:

```text
/board-migrate <mode> data migration summary:
  <project>: <ok | failed: reason>
```

Include the script's `sha_after` or `sha_after_rollback` value when it is
available.

### Data migration behavior

`--apply` does these actions:

1. On the first apply, snapshot the complete board directory to
   `<board-dir>/_migrate-snapshot/pre-migrate/`.
2. Create `<board-dir>/learnings/.gitkeep` if it is absent.
3. Add `needs: tdd` to open, in-progress, or blocked bug and feature entries
   that do not have a `needs:` field. Leave resolved entries unchanged.
4. Write `<board-dir>/.migration-state.json` with the apply time and resulting
   SHA.

Reapplying an already migrated board produces a byte-identical live tree.

`--rollback` verifies the snapshot, removes files added by apply, restores the
snapshot over the live board, and records `rolled_back_at` and
`sha_after_rollback`. The restored live-tree SHA must equal the pre-migration
SHA.

`--status` reports the snapshot state, current live-tree SHA, and migration
state file for each selected project.

### Data migration safety

- Rollback overwrites user changes made after apply. Restore those changes
  manually if they are still required.
- The `_migrate-snapshot/` directory is runtime state. BOARD.md generation and
  `board-index-check.sh` exclude directories whose names start with `_`.
- After apply, run `/board-rebuild [project]` if the index must show the new
  `needs:` values.

## Folder relocation workflow

### Step 1: Validate the relocation mode

Accept `--relocate` as the first argument. Accept an optional project name as
the second argument. Stop with the usage text if an argument is invalid.

### Step 2: Run the relocation script once

Run this command once for the repository:

```bash
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-relocate.sh" "$CLAUDE_PROJECT_DIR" [project]
```

The script resolves the compatible router and moves every project, or only the
selected project. Do not run it once for each board directory.

### Step 3: Rebuild and report the relocation result

Print the script's per-project `moved`, `already-relocated`, or `skipped`
results and its snapshot path. After a successful move, run
`/board-rebuild [project]`. Remind the user to add the `engineering-board/`
runtime stanza printed by `/board-init` to `.gitignore` if it is absent.

### Folder relocation behavior and safety

1. Snapshot `docs/boards/` to
   `.engineering-board/relocate-snapshot/<iso>/` before a move.
2. Move `docs/boards/<project>/` to `engineering-board/<project>/`. Prefer
   `git mv` in a work tree and use `mv` only as the fallback.
3. Move the router to `engineering-board/BOARD-ROUTER.md` and rewrite only its
   path column from `docs/boards/<project>` to
   `engineering-board/<project>`. Keep the affects-prefix column unchanged.
4. Treat an already relocated project as a no-op.

The relocation keeps both `docs/boards/` and legacy `docs/board/` resolution
compatible with partially moved repositories. It does not automatically move a
legacy single-board `docs/board/` layout because that operation would require a
new router and affects prefix.

---
description: Prepare the board, check permissions, and print a short readiness summary. This command can also run the optional pattern-intelligence demonstration. It uses /board-init and the permission self-check. It leaves the session in passive capture mode. Repeated use has the same result.
argument-hint: [project-name]
---


# /board-setup: one command from install to a working board

Collapse the install to value path (previously: `/board-init` + `/board-install-permissions` + mode-learning) into one idempotent step (eb-self F002). This command composes existing pieces: it introduces no new state.

## What to do

### Step 1: Infer the project name

Use `$1` if given. Otherwise default to the basename of `$CLAUDE_PROJECT_DIR`, lowercased with any character outside `[a-z0-9-]` replaced by `-`. If the sanitized name is empty, ask the user for a project name and stop.

### Step 2: Scaffold (or detect an existing board)

Check whether the resolver already finds a board for this project (source `hooks/scripts/board-paths.sh`. if `engineering-board/BOARD-ROUTER.md` lists the project, the board exists).

- **Board exists:** skip scaffolding: say so in the Step 4 summary ("board already set up"). Never re-scaffold or clobber.
- **No board:** execute the `/board-init` procedure (Read `commands/board-init.md` and follow its Steps 1-7) with the inferred project name and default affects-prefix. Keep its `.gitignore` guidance print-only, as that command specifies.

### Step 3: Permission self-check (print the paste block only if needed)

Run:

```bash
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-permission-self-check.sh"
```

- Exit `0` (all installed): note "pipeline permissions: installed" for the summary.
- Exit `1` (some missing): print the missing-rule paste block exactly as `/board-install-permissions` would (the self-check output lists the missing patterns), preceded by one line: `To let the pipeline run without prompts, paste the block below into a terminal (interactive by design — this command never edits your settings).` Note "pipeline permissions: N missing (paste block above)" for the summary.

Do NOT edit any settings file yourself: permission installation is interactive by design.

### Step 4: Report (three readiness lines + one optional first-win line)

Print:

```
Board ready: engineering-board/<project>/ (<scaffolded fresh | already set up>).
Capture is on: findings land in _sessions/ automatically — run /board-promote <project> to preview them, or /pm-start for advanced batch mode.
Pipeline permissions: <installed | N missing — paste block above>.
Try the pattern-intelligence sample: /board-demo
```

The session stays in **passive** mode (no mode file is written). Do not start PM or Worker mode from this command.

## Notes

- Idempotent: re-running detects the existing board and re-checks permissions. nothing is clobbered.
- This is the Quickstart's first command. `/board-init` remains available for explicit control (multiple projects, custom affects-prefixes, `--private`).
- `/board-demo` is optional and writes only to the hidden run-scoped `.engineering-board/demo/` area. setup never starts it automatically.

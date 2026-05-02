---
description: Initialize the docs/boards/ scaffold for a project. Creates BOARD-ROUTER.md (or appends to it), the project board directory, BOARD.md, ARCHIVE.md, and the four entry-type subdirectories with starter templates.
argument-hint: <project-name> [affects-prefix]
---

# /board-init — scaffold a project board

Initialize the engineering-board layout for project: **$1**
Affects prefix(es): **${2:-$1/}** (defaults to `<project-name>/` when omitted)

## What to do

You are creating the `docs/boards/` scaffold this plugin's hooks and skills expect. Be precise about file paths and idempotent — never clobber an existing file.

### Step 1 — Validate inputs

- If `$1` (project name) is empty, ask the user for one and stop. Project names should be kebab-case (e.g. `navigator`, `retail-workflow`).
- Confirm you're in the project root: there should be a `docs/` directory or it's safe to create one. If the current working directory looks wrong (e.g. a home dir), confirm with the user before creating files.

### Step 2 — Create or update `docs/boards/BOARD-ROUTER.md`

If `docs/boards/BOARD-ROUTER.md` does **not** exist, create it with this content:

```markdown
# Board Router

Maps each project to its board directory. The `affects:` prefix on entry frontmatter determines which board the entry belongs to.

| project | path | affects prefix |
|---------|------|----------------|
| $1 | docs/boards/$1 | ${2:-$1/} |
```

If it **does** exist, append a new row to the table for this project. Skip the append if a row for `$1` is already present (idempotent).

### Step 3 — Create the project board directory

Create:
- `docs/boards/$1/`
- `docs/boards/$1/bugs/`
- `docs/boards/$1/features/`
- `docs/boards/$1/questions/`
- `docs/boards/$1/observations/`

Add a `.gitkeep` file in each of the four entry-type subdirectories so they survive an empty git commit.

### Step 4 — Create `docs/boards/$1/BOARD.md`

Only create if it does not already exist. Content:

```markdown
# $1 — Board

Live index of open items. Resolved items move to ARCHIVE.md.

## Open

(none)

## Conventions

- Bug/Feature lines: `- B### P# | [title](bugs/filename.md)` (append `⊘ Q###` when blocked)
- Question lines: `- Q### | [title](questions/filename.md)`
- Observation lines: `- O### | [title](observations/filename.md)`
- Order within each section: P0 → P1 → P2 → P3 → unranked
```

### Step 5 — Create `docs/boards/$1/ARCHIVE.md`

Only create if it does not already exist. Content:

```markdown
# $1 — Archive

Resolved entries. Newest at the top.
```

### Step 6 — Report

Print a short confirmation listing what was created vs. what already existed. Example:

```
Initialized board for "$1":
  ✓ docs/boards/BOARD-ROUTER.md (added row)
  ✓ docs/boards/$1/BOARD.md
  ✓ docs/boards/$1/ARCHIVE.md
  ✓ docs/boards/$1/{bugs,features,questions,observations}/

The board-manager agent will now route findings affecting `${2:-$1/}` to this board automatically.
Restart Claude Code (or open a new session) so the SessionStart hook picks up the new layout.
```

## Notes

- This command is idempotent — running it twice on the same project should not corrupt files or duplicate router rows.
- If the user wants multiple `affects:` prefixes for one board (e.g. `navigator/, src/, scripts/`), they can edit the router row by hand after init, or pass them as `$2` comma-separated.

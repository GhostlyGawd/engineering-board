---
description: Initialize the engineering-board/ scaffold for a project. Creates BOARD-ROUTER.md (or appends to it), the project board directory, BOARD.md, ARCHIVE.md, and the five entry-type subdirectories with starter templates. Prints the recommended .gitignore stanza (pass --private for a fully untracked board).
argument-hint: <project-name> [affects-prefix] [--private]
---

# /board-init — scaffold a project board

Initialize the engineering-board layout for project: **$1**
Affects prefix(es): **${2:-$1/}** (defaults to `<project-name>/` when omitted)

## What to do

You are creating the `engineering-board/` scaffold this plugin's hooks and skills expect — a **visible, committed-by-default** top-level directory (the new default since 1.1.0). Be precise about file paths and idempotent — never clobber an existing file.

> **Backward compatibility.** Existing boards under `docs/boards/` (and the legacy single-board `docs/board/`) keep resolving with no action — the resolver checks `engineering-board/` first, then `docs/boards/`, then `docs/board/`. This command always scaffolds *new* boards at the `engineering-board/` default. To move an existing board onto the new path, use `/board-migrate --relocate` — do **not** re-scaffold it here.

### Step 1 — Validate inputs

- If `$1` (project name) is empty, ask the user for one and stop. Project names should be kebab-case (e.g. `navigator`, `retail-workflow`).
- Confirm you're in the project root — the directory where `engineering-board/` should live (typically the repo root, alongside `.git/`). If the current working directory looks wrong (e.g. a home dir), confirm with the user before creating files.
- Check whether `--private` appears in `$ARGUMENTS`; it is a flag (not the project name or affects-prefix) that changes the `.gitignore` guidance in Step 6.

### Step 2 — Create or update `engineering-board/BOARD-ROUTER.md`

If `engineering-board/BOARD-ROUTER.md` does **not** exist, create it with this content:

```markdown
# Board Router

Maps each project to its board directory. The `affects:` prefix on entry frontmatter determines which board the entry belongs to.

| project | path | affects prefix |
|---------|------|----------------|
| $1 | engineering-board/$1 | ${2:-$1/} |
```

If it **does** exist, append a new row to the table for this project. Skip the append if a row for `$1` is already present (idempotent).

### Step 3 — Create the project board directory

Create:
- `engineering-board/$1/`
- `engineering-board/$1/bugs/`
- `engineering-board/$1/features/`
- `engineering-board/$1/questions/`
- `engineering-board/$1/observations/`
- `engineering-board/$1/learnings/` (v0.3.0 — populated by the `learnings-curator` PM subagent)

Add a `.gitkeep` file in each of the five entry-type subdirectories so they survive an empty git commit.

### Step 4 — Create `engineering-board/$1/BOARD.md`

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
- Learning lines: `- L### | [title](learnings/filename.md)` (v0.3.0)
- Order within each section: P0 → P1 → P2 → P3 → unranked
```

### Step 5 — Create `engineering-board/$1/ARCHIVE.md`

Only create if it does not already exist. Content:

```markdown
# $1 — Archive

Resolved entries. Newest at the top.
```

### Step 6 — Print the recommended `.gitignore` stanza

Board content under `engineering-board/` is **committed by default** — that is the point of the layout (the board is meant to be browsed on GitHub and version-controlled). Only the ephemeral runtime subdirs should be ignored. Print this additive stanza for the user to add to their `.gitignore` — **do not edit `.gitignore` automatically**:

```gitignore
# engineering-board runtime (ephemeral — do not commit)
.engineering-board/
engineering-board/*/_sessions/
engineering-board/*/_claims/
engineering-board/*/_migrate-snapshot/
```

These are all **additive** patterns — they work precisely because the board content lives in a non-ignored folder, so no negation is needed. `consolidation.log` is deliberately *not* ignored: it is the committed audit trail.

**If `--private` was passed** (e.g. a public repo that should not expose internal triage), recommend the full-privacy opt-out instead — ignore the whole tree with one clean line, and tell the user the board content will **not** be committed:

```gitignore
# engineering-board (private — whole board untracked)
.engineering-board/
engineering-board/
```

One line over the content tree, no negation, and no clash with the differently-named runtime folder `.engineering-board/`.

### Step 7 — Report

Print a short confirmation listing what was created vs. what already existed. Example:

```
Initialized board for "$1":
  ✓ engineering-board/BOARD-ROUTER.md (added row)
  ✓ engineering-board/$1/BOARD.md
  ✓ engineering-board/$1/ARCHIVE.md
  ✓ engineering-board/$1/{bugs,features,questions,observations,learnings}/

Next: add the printed .gitignore stanza so runtime state stays out of git (board content itself is committed by default).
The board-manager agent will now route findings affecting `${2:-$1/}` to this board automatically.
Restart Claude Code (or open a new session) so the SessionStart hook picks up the new layout.
```

## Notes

- This command is idempotent — running it twice on the same project should not corrupt files or duplicate router rows.
- New boards scaffold at `engineering-board/` (1.1.0 default). Older boards under `docs/boards/` or legacy `docs/board/` keep working untouched; relocate them on demand with `/board-migrate --relocate`.
- If the user wants multiple `affects:` prefixes for one board (e.g. `navigator/, src/, scripts/`), they can edit the router row by hand after init, or pass them as `$2` comma-separated.

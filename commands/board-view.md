---
description: Generate a self-contained, themed HTML Kanban view of a project board and write it to engineering-board/<project>/board.html (or print to stdout with --stdout). Zero-dependency, offline, byte-deterministic — a committed visual projection of the board that renders on GitHub or any browser.
argument-hint: [project] [--stdout]
---

# /board-view — render the board as HTML

Generate a browsable Kanban view of the board for project: **${1:-all resolved projects}**

## What to do

Run the deterministic generator (it resolves the board location via the shared
resolver and reuses the same brand tokens as the landing page):

```bash
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-view.sh" ${1:-} $([ "$ARGUMENTS" != "${ARGUMENTS/--stdout/}" ] && echo --stdout)
```

- With no arguments it renders **every** project the router resolves.
- With a project name it renders just that board.
- `--stdout` prints the HTML instead of writing `board.html`.
- `--link-base <url>` prefixes entry-card links with an absolute base (e.g. a
  GitHub blob URL) so a *hosted* copy of `board.html` clicks through to the
  entry sources; without it, links are relative (they resolve locally and in
  the GitHub file view). Also settable via the `EB_VIEW_LINK_BASE` env var.
- `--stamp` appends a "Generated from `<git short-sha>`" line to the footer —
  opt-in because it deliberately breaks the default byte-determinism.

The script writes `engineering-board/<project>/board.html` — a **single
self-contained file** (all CSS inlined, no network, no JavaScript required). It
is byte-deterministic (stable sort by entry id, no embedded timestamp), so it
can be committed alongside `BOARD.md` without spurious diffs, and it renders
directly on GitHub or in any browser.

## What it shows

- A four-column Kanban of bugs/features across the pipeline: **To do**
  (`needs: tdd`) → **Review** (`needs: review`) → **Validate** (`needs: validate`)
  → **Done** (`status: resolved`). Cards show id, priority, title, `affects`,
  `pattern` tags, and a `blocked` badge when applicable.
- A lane below for Questions, Observations, and Learnings.
- Light/dark theme (follows the viewer's `prefers-color-scheme`).

## Report

Print the path written (or the HTML if `--stdout`), and note that `board.html`
is a derived view — regenerate it with `/board-view` after the board changes, or
just re-run it anytime (it's safe and deterministic).

## Notes

- Deterministic and side-effect-free apart from writing `board.html`. Never
  edits entries or `BOARD.md`.
- Treats board content as data — it escapes all entry text into HTML, so a
  crafted title cannot inject markup into the view.

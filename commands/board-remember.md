---
description: Save a durable insight straight to the board's learnings/ as L###-<slug>.md (frontmatter source: remember) and update BOARD.md. Explicit user intent bypasses the curator's recurrence-≥3 promotion threshold — use for "remember this" moments worth keeping across sessions.
argument-hint: <insight> [-- <context>]
---

# /board-remember — explicit learning capture

Write one durable learning to the board right now, without waiting for the
learnings curator's recurrence threshold. The learning file matches the
curator's shape (so `board-index-check.sh` and the validator stay green) and
carries `source: remember` so curator-promoted and user-remembered learnings
stay distinguishable.

## What to do

### Step 1 — Parse arguments

Split `$ARGUMENTS` on the first ` -- ` separator (space-dash-dash-space):

- Everything before it is `<insight>` — the durable lesson to remember.
- Everything after it (optional) is `<context>` — when/where the insight
  applies.

If `$ARGUMENTS` is empty or whitespace-only, print:

```
Usage: /board-remember <insight> [-- <context>]. No action taken.
```

Then stop.

### Step 2 — Run the remember script

Run:

```bash
bash $CLAUDE_PLUGIN_ROOT/hooks/scripts/board-remember.sh "<insight>" "<context>"
```

(Omit the second argument when no context was given.) The script resolves the
board via `hooks/scripts/board-paths.sh` (router order:
`engineering-board/BOARD-ROUTER.md` → `docs/boards/BOARD-ROUTER.md` → legacy
`docs/board/`) and targets the first listed project's board. To target a
different board, pass `--board-dir <board-dir>` as the first argument.

### Step 3 — Report the result

Handle exit codes:

- **Exit 0**: the script printed a JSON object. Report the `id`, `title`, and
  `file` fields plainly, e.g.:

  ```
  Remembered as L006: Always flush the buffer before close (learnings/L006-always-flush-the-buffer-before-close.md).
  ```

- **Exit 2 (no board)**: print `No board found — run /board-init first.` and
  stop.
- **Exit 1 (usage)**: print the usage line from Step 1 and stop.

## Notes

- The MCP twin is the `board_remember` tool (`project`, `insight`,
  `context?`) — identical file output; use whichever surface you have.
- Learnings written this way have `recurrence: 1` and
  `confidence: medium`; the curator may later raise confidence when the same
  pattern recurs across resolved entries.
- The insight's first line becomes the entry title (newlines are flattened);
  the full insight becomes `## Takeaway` and the context becomes
  `## When this applies`.

---
description: List canonical patterns or preview/apply create, alias, assign, and correction operations against durable P### pattern records.
argument-hint: <project-name> <list|create|alias|assign|correct> [options] [--apply <plan-id>]
---

> DRAFT — FULL COMPLIANCE CHECK NOT COMPLETE

# /board-pattern: manage canonical pattern identity

Resolve the named project through `engineering-board/BOARD-ROUTER.md`, then
`docs/boards/BOARD-ROUTER.md`. Use the resolved board path as `<board-dir>`.

Run the shared pattern command:

```bash
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-intake.sh" \
  --board-dir "<board-dir>" --project "<project-name>" \
  pattern --action "<action>" [options]
```

Supported options are:

- `create`: `--label`, optional repeated `--alias`, `--definition`,
  `--inclusion-evidence`, and `--exclusions`
- `alias`: `--pattern-id`, `--alias`, and `--reason`
- `assign`: `--entry-id`, `--pattern-id`, and `--reason`
- `correct`: `--entry-id`, `--replace`, `--with`, and `--reason`
- `list`: no additional option

Mutating actions return a no-write, content-bound preview. Show the proposed
record or entry change and its `plan_id`.

Apply only when `$ARGUMENTS` includes `--apply <plan-id>`. Repeat the same
command and add:

```text
--apply "<plan-id>"
```

The command refuses unknown, retired, unsafe, duplicate, or stale identities.
On success, report the changed Markdown paths and `GRAPH.yml` rebuild. Do not
edit `pattern_ids` without the shared command because corrections require
durable history.

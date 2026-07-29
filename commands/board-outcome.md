---
description: Preview or apply one explicit fix result against a durable root-cause hypothesis and review the resulting Learning feedback.
argument-hint: <project-name> <preview|apply|apply-learning|report> [--token <plan-token>]
---


# /board-outcome: connect fix results to later memory

Resolve the named project through `engineering-board/BOARD-ROUTER.md`, then
`docs/boards/BOARD-ROUTER.md`. Use the resolved project path as `<board-dir>`.

For `preview`, construct one JSON object with:

- `entry_id` and `hypothesis_id`
- `fix_result`: `held`, `failed`, `partial`, or `inconclusive`
- `hypothesis_disposition`: an explicitly compatible value
- `fix_summary`, `evidence_ids`, `observed_until`, and `actor`
- optional `context_token`
- `context_used`, set to `true` only when the surfaced memory affected the fix

Pass the object on standard input:

```bash
printf '%s' '<validated-json>' | \
  bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-outcome.sh" \
  --board-dir "<board-dir>" \
  --project "<project-name>" \
  preview
```

Preview does not write a file. Apply only with the unchanged token returned by
preview:

```bash
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-outcome.sh" \
  --board-dir "<board-dir>" \
  --project "<project-name>" \
  apply --token "<outcome-plan-token>"
```

Outcome apply changes at most one H### file. It returns zero or more Learning
feedback previews. It does not apply them. Review one returned plan, then
apply it explicitly:

```bash
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-outcome.sh" \
  --board-dir "<board-dir>" \
  --project "<project-name>" \
  apply-learning --token "<learning-plan-token>"
```

Use `report` to read the canonical outcome-value report. Never infer that a
passing test confirms a cause. Record the fix result and choose the hypothesis
disposition separately.

---
description: Rank deterministic finding clusters for root-cause investigation and show linked hypothesis and negative-memory records.
argument-hint: <project-name> [--cluster <fingerprint>] [--limit <1-100>]
---

> DRAFT — FULL COMPLIANCE CHECK NOT COMPLETE

# /board-insights: rank systemic investigations

Resolve the named project through `engineering-board/BOARD-ROUTER.md`, then
`docs/boards/BOARD-ROUTER.md`. Use the resolved project path as `<board-dir>`.

Run the shared deterministic adapter:

```bash
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-insights.sh" \
  --board-dir "<board-dir>" --project "<project-name>" \
  rank [--cluster "<cluster-fingerprint>"] [--limit "<count>"]
```

Report each cluster's 0-100 investigation-priority score, score components,
members, member source paths, pattern IDs, domains, hypothesis references, and
negative-memory references. State that the score prioritizes investigation. It
does not measure causal confidence and cannot confirm a root cause.

Do not edit `GRAPH.yml`, cache files, entries, patterns, or hypotheses. Use
`/board-hypothesis` for an explicit proposal or evaluation.

---
id: F001
type: feature
title: Zero-dep HTML board viewer (/board-view -> committed board.html)
discovered: 2026-07-04
status: open
priority: P2
affects: commands/board-view.md
needs: tdd
pattern: [board-visibility]
---

## Done when
- `/board-view [project]` (and/or a `board_render` MCP tool sharing the generator) parses existing entry frontmatter, buckets cards by `needs:`/`status:` into columns, and writes a single self-contained `engineering-board/<project>/board.html` (python3 stdlib only, no network, inlining the landing page's `.cols/.col/.card` CSS — already WCAG-AA, theme-aware, reduced-motion).
- Output is byte-deterministic enough to commit without churn (stable sort, no timestamps) OR offered as an on-demand `--stdout`/gitignored artifact.
- Cards show id, priority, title, blocked-by, pattern.

## Motivation
Rank-1 opportunity (Track C). The #1 conceded competitive gap: Backlog.md (Kanban TUI, ~5.9k*) and Agent-MCP (dashboard) beat us on visualization; ours is markdown-only. The generated HTML is simultaneously the missing feature, a real-data hero asset for README/landing, and the host for F003's Learnings panel. Reuses the frontmatter parse loop already written in board-session-start.sh / the MCP server.

## Kill criteria
Kill the committed-file framing if it produces noisy diffs on every board change (fall back to on-demand). Kill the MCP variant if it duplicates rather than shares the command's generator.

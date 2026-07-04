---
id: B040
type: bug
title: MCP board_capture_finding title/kind not flattened (scratch header injection + count spoof)
discovered: 2026-07-04
status: resolved
priority: P3
affects: mcp-server/engineering_board_mcp.py
needs: tdd
pattern: [input-hygiene, mcp-security]
---

## Done when
- `board_capture_finding` flattens newlines in title/kind (and affects) so a crafted title can't inject a second `## ` scratch header.

## Observed behavior (C4 red-team F4 — MINOR)
title/kind were written into the `## <ts> — <kind>: <title>` header unflattened. A title with an embedded `\n## FAKE …` injected a second header; count_scratch_findings counts `## ` lines so board_status.unpromoted_scratch was inflated/spoofed.

## Resolution (C4, PR C4a)
title/kind/affects run through _oneline before building the block. Pinned by an MCP test (single header).

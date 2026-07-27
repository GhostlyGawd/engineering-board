---
id: B057
type: bug
title: count_scratch_findings undercounts multi-finding scratch-append blocks
discovered: 2026-07-04
status: resolved
priority: P3
affects: mcp-server/engineering_board_mcp.py
needs: done
pattern: [status-accuracy]
---

## Done when
- board_status unpromoted_scratch reflects the true number of un-promoted findings, counting each finding inside a board-scratch-append.sh `<!-- ts -->` JSON block (its `findings` array may hold several), not one per block.

## Observed behavior (C9 red-team Track A — P3, non-security correctness note)
count_scratch_findings counts each `<!-- ts -->` comment block as 1, but a plugin scratch-append block is `{"schema_version":..., "findings":[...]}` and can hold multiple findings. So the board_status unpromoted count is a lower bound for multi-finding blocks. Cosmetic status inaccuracy only; consolidation promotes each finding correctly.

## Fix direction
Parse the JSON block and count len(findings) instead of 1 per block (keep the `## ` MCP-capture header count as-is). Update any status-count test fixtures in lockstep.

## Resolution (2026-07-26)
`count_scratch_findings` now parses each plugin scratch block's JSON payload and
counts the exact length of its `findings` array. MCP-style `## ` captures remain
additive, empty arrays count as zero, and malformed blocks retain the historical
fallback count of one so `board_status` remains available and conservative.
Lifecycle coverage pins all four cases.

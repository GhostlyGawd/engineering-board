---
id: B044
type: bug
title: MCP board_capture_finding evidence field injects scratch headers (count spoof)
discovered: 2026-07-04
status: resolved
priority: P3
affects: mcp-server/engineering_board_mcp.py
needs: tdd
pattern: [input-hygiene, mcp-security]
---

## Done when
- evidence is blockquoted (or structurally counted) so an embedded ## can't inject a second scratch header / spoof unpromoted_scratch.

## Observed behavior (C5 red-team F2 — MINOR; B040 left evidence)
B040 flattened title/kind/affects but evidence was appended raw, so a multi-line evidence with `## <ts> — <kind>:` injected a second header counted by count_scratch_findings.

## Resolution (C5, PR C5b)
Each evidence line is blockquoted (`> `) on write, so an embedded ## becomes `> ##` (not a header). Legit multi-line evidence stays readable. Pinned by an MCP test.

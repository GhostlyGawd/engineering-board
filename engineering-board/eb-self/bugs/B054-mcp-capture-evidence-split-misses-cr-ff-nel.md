---
id: B054
type: bug
title: MCP board_capture_finding evidence blockquote splits on \n only (CR/FF/NEL forge a header)
discovered: 2026-07-04
status: resolved
priority: P2
affects: mcp-server/engineering_board_mcp.py
needs: tdd
pattern: [frontmatter-injection]
---

## Done when
- Evidence blockquoting splits on every line separator (CR/CRLF/FF/VT/C0-seps/NEL/LS/PS) so no embedded `## …` can escape the `> ` prefix and forge a scratch header; count_scratch_findings and board_status report the true finding count. A regression drives the real tool with CR/FF/NEL evidence.

## Observed behavior (C8 red-team Track A — P2; re-opens B040)
board_capture_finding blockquoted evidence with `.split("\n")`, missing CR/FF/NEL/LS/PS. Downstream readers (count_scratch_findings, agents) use universal-newline semantics, so a bare `\r` before `## …` escaped the blockquote and forged a second scratch header — one captured finding reported as two (spoofed unpromoted count). Same class B051 fixed in the reject filter; the MCP-only B040 flatten never covered the evidence split.

## Resolution (C8, PR C8a)
`.split("\n")` -> `.splitlines()` in the evidence blockquote. Also proactively hardened `_oneline` (title/kind/affects/heading flatten) to the full separator class `[\r\n\t\f\v\x1c-\x1f\x85  ]`. New MCP regression (B054) drives capture with CR/FF/NEL evidence + asserts one header and count==1. MCP suite 82->88.

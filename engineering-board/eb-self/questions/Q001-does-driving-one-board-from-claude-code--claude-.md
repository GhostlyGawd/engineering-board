---
id: Q001
type: question
title: Does driving one board from Claude Code + Claude Desktop simultaneously work, and what breaks?
discovered: 2026-07-04
status: open
source: C1 DISCOVER Track C
affects: mcp-server/engineering_board_mcp.py
---

## Done when
- Two clients (Claude Code + Claude Desktop) are exercised against one board concurrently; any breakage is captured as a bug entry; if it works, it is documented as a differentiator with a walkthrough.

## Why it matters
Track C reclassified "multi-client story" from a feature to a validation+doc task: both clients speak the same on-disk format and claim-locking is mkdir-atomic on a shared filesystem, so they are already coordinated by design — but the claim is unproven. Note: fully exercising two live clients may be human-gated (BLOCKERS B1-class limitation).

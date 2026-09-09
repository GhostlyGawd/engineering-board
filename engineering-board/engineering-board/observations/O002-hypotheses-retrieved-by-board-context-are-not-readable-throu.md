---
id: O002
type: observation
title: Hypotheses retrieved by board_context are not readable through board_get_entry in installed 1.13.5
affects: mcp-server/engineering_board_mcp.py
discovered: 2026-09-09
discovered_at: 2026-09-09T15:39:59Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:13cfbd3fc1a1351b]
---

# Hypotheses retrieved by board_context are not readable through board_get_entry in installed 1.13.5

## Evidence

> F004 independent prelaunch review: corrected prepared H102 is returned successfully by installed1.13.5 board_context, but board_get_entry(entry_id='H102') returns not found. Supporting B entries and local Markdown are separate routes; no claim yet that this violates documented get_entry contract. Potential read-navigation/expectation gap, not proof of incremental memory benefit. No live model trial yet.

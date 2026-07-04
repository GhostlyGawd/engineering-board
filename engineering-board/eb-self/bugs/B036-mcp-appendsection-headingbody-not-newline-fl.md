---
id: B036
type: bug
title: MCP append_section heading/body not newline-flattened
discovered: 2026-07-04
status: resolved
priority: P3
affects: mcp-server/engineering_board_mcp.py
needs: tdd
pattern: [input-hygiene]
---

## Done when
- `tool_board_update_entry` flattens newlines in `append_section.heading` (and considers the body) for hygiene.

## Observed behavior (C3 red-team #3 — MINOR)
Unlike frontmatter values, `append_section.heading`/`body` (:739-748) skip
`_oneline`, so a heading `"H\n---\ninjected: yes"` writes a `---` into the entry
BODY. Not a frontmatter injection (body `---` is inert markdown) — cosmetic
corruption only. Flatten the heading for hygiene.

## Resolution (C3, PR C3b)
tool_board_update_entry now runs append_section.heading through _oneline so a
newline in the heading can't inject extra lines into the entry body. Pinned by
an MCP test.

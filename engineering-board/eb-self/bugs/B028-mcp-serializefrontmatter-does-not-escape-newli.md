---
id: B028
type: bug
title: MCP serialize_frontmatter does not escape newlines; field values can inject keys
discovered: 2026-07-04
status: resolved
priority: P2
affects: mcp-server/engineering_board_mcp.py
needs: tdd
pattern: [frontmatter-injection, untrusted-input]
---

## Done when
- `serialize_frontmatter` rejects or replaces `\n`/`\r` in scalar field values (or validation at the tool boundary rejects them).
- A test asserts `board_create_entry(title="pwn\nstatus: resolved")` does not produce an injected `status:` line.

## Observed behavior (C2 red-team, F4 — MINOR)
`serialize_frontmatter` emits `"%s: %s" % (key, val)` with no newline escaping. A newline in `title` (or any string field) injects arbitrary frontmatter keys or closes the `---` block early. Since entry text is often copied from untrusted finding text, crafted input can flip an entry to `resolved` (hiding it) or break the parser.

## Resolution (C2, PR C2a)
`serialize_frontmatter` now flattens CR/LF/control chars in scalar and list
values to spaces (`_oneline`), so a newline in a field value can no longer
inject frontmatter keys or close the `---` block. Pinned by an MCP test.

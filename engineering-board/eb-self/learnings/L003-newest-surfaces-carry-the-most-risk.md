---
id: L003
type: learning
subtype: principle
title: The newest surface carries the most risk — red-team it hardest
discovered: 2026-07-04
confidence: high
recurrence: 3
derived_from: [B024, B026, B028]
applies_to: [mcp-server/]
pattern_tag: new-surface-risk
---

## Takeaway
Cycle C2's blocker and both other MCP defects (path traversal, frontmatter
injection, silent findings-loss on consolidate) were all in the MCP server — the
newest surface, added in 1.2.0 — while the older plugin substrate, hardened over
many cycles, held up. New code has had the fewest adversarial eyes on it. When a
release adds a surface, direct the next red-team pass primarily at that surface,
and give it the same input-validation + cross-component-integration scrutiny the
mature code already survived (untrusted names → filesystem, untrusted text →
serialized files, one component's output → another's parser).

## Sources
- B024 — MCP path traversal via project name (blocker).
- B026 — MCP-captured findings silently destroyed by the plugin consolidator.
- B028 — MCP frontmatter injection via unescaped newlines.

## When this applies
Immediately after shipping any net-new surface (a server, a tool, a new hook).
Prioritize red-team coverage of it over re-scanning battle-tested code, and pay
special attention to the SEAMS where it hands data to older components.

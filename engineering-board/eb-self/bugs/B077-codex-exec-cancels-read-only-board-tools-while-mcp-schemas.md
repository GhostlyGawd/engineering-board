---
id: B077
type: bug
status: open
needs: tdd
priority: P2
title: Codex exec cancels read-only board tools while MCP schemas omit approval annotations
affects: mcp-server/engineering_board_mcp.py
discovered: 2026-08-15
discovered_at: 2026-08-15T04:33:09Z
promoted_from: [mcp:_sessions/mcp-2026-08-15.md:98906d9b28aa48d8]
---

# Codex exec cancels read-only board tools while MCP schemas omit approval annotations

## Done when

- [ ] A controlled Codex host test compares otherwise equivalent annotated and unannotated read-only tools and determines whether annotations or plugin policy change the cancellation behavior.
- [ ] If the hypothesis survives, all 19 tools expose accurate read-only, destructive, idempotent, and open-world annotations where those properties apply; if it fails, record the host limitation and do not ship an unrelated annotation change as the fix.
- [ ] A fresh installed Codex process completes `board_status` and `board_context` without a per-call prompt, while a mutating control remains approval-gated or denied.
- [ ] Focused tests, the complete suite, release publication, and installed-host evidence pass without a dangerous approval bypass.

## Hypothesis

Missing tool annotations or plugin approval policy may cause Codex to request
an approval that non-interactive `codex exec` cannot answer. The current
evidence establishes correlation only. The annotated-versus-unannotated host
control must falsify or support this explanation before implementation.

## Evidence

> Installed v1.13.2 on Codex 0.145.0 initialized engineering-board, but board_status and board_context returned user cancelled MCP tool call in non-interactive exec. Direct tools/list exposed 19 tools and zero annotations. Official Codex MCP policy supports writes mode based on read-only annotations; no persistent bypass was used.

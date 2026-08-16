---
id: B077
type: bug
status: in_progress
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

- [x] A controlled Codex host test compares otherwise equivalent annotated and unannotated read-only tools and determines whether annotations or plugin policy change the cancellation behavior.
- [x] If the hypothesis survives, all 19 tools expose accurate read-only, destructive, idempotent, and open-world annotations where those properties apply; if it fails, record the host limitation and do not ship an unrelated annotation change as the fix.
- [ ] A fresh installed Codex process completes `board_status` and `board_context` without a per-call prompt, while a mutating control remains approval-gated or denied.
- [ ] Focused tests, the complete suite, release publication, and installed-host evidence pass without a dangerous approval bypass.

## Hypothesis

Missing tool annotations or plugin approval policy may cause Codex to request
an approval that non-interactive `codex exec` cannot answer. The current
evidence establishes correlation only. The annotated-versus-unannotated host
control must falsify or support this explanation before implementation.

## Evidence

> Installed v1.13.2 on Codex 0.145.0 initialized engineering-board, but board_status and board_context returned user cancelled MCP tool call in non-interactive exec. Direct tools/list exposed 19 tools and zero annotations. Official Codex MCP policy supports writes mode based on read-only annotations; no persistent bypass was used.

> Controlled result: with an otherwise identical ephemeral STDIO server and writes policy, readOnlyHint true completed with CONTROL_OK; omitted and false both returned user cancelled MCP tool call. An independent annotated Auto-policy cell also completed. Local tools/list now exposes the exact 19-tool maximum-capability matrix; installed release proof remains pending.

> Matched policy result: the missing auto plus omitted-annotation cell also returned user cancelled MCP tool call. Under both auto and writes, the annotated read completed while the otherwise equivalent omitted annotation cancelled. This isolates the missing annotation, not the policy value, as the read-call cause.

> Source-host result: a fresh Codex process completed the real board_status tool under writes. A valid board_update_entry call against nonexistent B999 reached the MCP call state but returned user cancelled MCP tool call before server execution. The released-plugin proof remains pending.

## Comments

- **goal-b077-20260815** 2026-08-15T04:48:48Z: Claimed for an annotated-versus-unannotated Codex host control. No causal fix is selected before the control.
- **goal-b077-20260815** 2026-08-15T05:12:00Z: The controlled comparison supported the annotation hypothesis. Added exact schema tests, conservative annotations, a Codex-specific writes default, and aligned current documentation. Release and installed negative-control gates remain open.
- **goal-b077-20260815** 2026-08-15T05:22:00Z: Fresh source-host controls completed board_status without a prompt and cancelled board_update_entry under writes. Captured the unrelated strict Claude manifest warning separately as B078.
- **goal-b077-20260815** 2026-08-15T05:24:52Z: The settled worker diff passed all 21 maintained suites in 59.99 seconds. Independent review, delivery, release, reinstall, and installed-host gates remain open.
- **goal-b077-20260815** 2026-08-16T00:19:33Z: Independent review required the missing auto plus omitted-annotation cell and a non-circular side-effect guard. The matched cell cancelled, and all six declared read handlers preserved a full paths-and-bytes snapshot while the mutation control changed it. The focused MCP suite passes 230 checks; the final complete-suite rerun remains open.

---
id: F001
type: feature
status: resolved
needs: tdd
priority: P1
title: Add exhaustive Codex dogfood capability matrix
affects: tests/codex-plugin.sh
discovered: 2026-09-08
discovered_at: 2026-09-08T23:53:48Z
promoted_from: [mcp:_sessions/mcp-2026-09-08.md:4e7f7c361ec3ef7e]
---

# Add exhaustive Codex dogfood capability matrix

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> Priority: P1.
> Done when:
> 1. All 19 MCP tools are exercised through the installed Codex plugin with recorded pass/fail evidence.
> 2. Each of the five bundled skills is triggered by a representative fresh-session prompt.
> 3. Read/write approval behavior, plugin installation/update behavior, and the Codex empty-hook boundary are verified.
> 4. Every discovered gap becomes a canonical board entry.
> 5. bash tests/run-all.sh passes on macOS.

## Done when

- [ ] All 19 MCP tools are exercised through the installed Codex plugin with recorded pass/fail evidence.
- [ ] Each of the five bundled skills is triggered by a representative fresh-session prompt.
- [ ] Read/write approval behavior, plugin installation/update behavior, and the Codex empty-hook boundary are verified.
- [ ] Every discovered gap becomes a canonical board entry.
- [ ] `bash tests/run-all.sh` passes on macOS.

## Comments

- **Codex** 2026-09-09T00:05:10Z: live MCP sweep 19/19 PASS; board-intake skill 1/5 live; full suite 20/21 with evaluation-harness blocked by B001; token-only apply gap tracked by the new bug.
- **Codex** 2026-09-09T00:11:50Z: Corrective progress: 19/19 MCP tools pass, and the confirmed apply asymmetry is patterns-only.
- **Codex** 2026-09-09T00:18:47Z: Five of five bundled skills passed fresh-session activation tests: board-intake created canonical records through capture/preview/apply; board-triage produced a read-only systemic recommendation; board-insights returned context, ranked cluster, hypothesis and learning; board-consolidate correctly completed as a no-op with zero scratch and rebuilt derived state; board-resolve closed capability-lab O001 with archive, rebuild, claim release and status verification. F001 remains open because tests/run-all.sh is 20/21 on macOS (B001) and the confirmed patterns-only apply asymmetry remains B002.
- **Codex** 2026-09-09T02:46:25Z: Closed with owner confirmation after the capability sweep reached 19/19 MCP tools, 5/5 skills, canonical gap capture, and 21/21 passing macOS suites.

## Resolution evidence

The installed Codex plugin dogfood completed all 19 MCP tool calls and all five bundled skill activations. The plugin checks verified read/write annotations and approval defaults, pinned installation/update metadata, and the empty Codex hook boundary. Discovered gaps were captured as canonical B001 and B002 entries. After resolving B001, `bash tests/run-all.sh` passed all 21 suites on macOS. The owner confirmed closure on 2026-09-08.

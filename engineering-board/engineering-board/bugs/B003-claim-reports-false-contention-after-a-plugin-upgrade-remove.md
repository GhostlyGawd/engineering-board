---
id: B003
type: bug
status: resolved
needs: tdd
priority: P1
title: Claim reports false contention after a plugin upgrade removes the server working directory
affects: mcp-server/engineering_board_mcp.py
discovered: 2026-09-09
discovered_at: 2026-09-09T04:58:46Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:5963c9811e81bd9f]
---

# Claim reports false contention after a plugin upgrade removes the server working directory

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> After upgrading the installed Engineering Board plugin from 1.13.4 to 1.13.5 within the active Codex session, two board_claim calls against an existing empty _claims directory returned exit_code 1 with '[Errno 2] No such file or directory'. The running MCP process retained the deleted 1.13.4 cache as its cwd. tool_board_claim calls os.getcwd() while writing owner.txt; that failure enters the generic claim-write exception, removes the newly created lock, and reports contention. Priority: P1 because an approved plugin upgrade makes all claims fail until restart. Done when claim acquisition succeeds with a deleted process cwd, records a stable fallback cwd, and regression coverage verifies the lock is not discarded.

## Comments

- **Codex** 2026-09-09T04:59:02Z: Raised to P1: upgrading the plugin during an active session makes every subsequent claim fail until the MCP process restarts.
- **codex-b003-deleted-cwd-20260909** 2026-09-09T04:59:22Z: Claimed through a fresh released server process after reproducing the active-session stale-cwd failure twice. Add a safe cwd fallback and regression coverage for claim acquisition from a deleted process cwd.
- **codex-b003-deleted-cwd-20260909** 2026-09-09T05:04:30Z: Resolved after deleted-cwd claim acquisition, fallback owner metadata, normal release, all 235 MCP checks, and all 21 repository suites passed.

## Resolution evidence

`tool_board_claim` now reads the process cwd through a guarded helper. If an in-session plugin upgrade removed that cwd, the helper records the caller's already-validated absolute repository root instead of discarding the new lock.

Regression coverage forces `os.getcwd()` to raise, verifies claim acquisition returns `exit_code: 0`, confirms `owner.txt` records the explicit root, and releases the claim normally. `bash mcp-server/run-tests.sh` passed 235 checks and `bash tests/run-all.sh` passed all 21 suites.

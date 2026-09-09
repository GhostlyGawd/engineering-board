---
id: B002
type: bug
status: resolved
needs: tdd
priority: P2
title: Token-only pattern and hypothesis apply falls through to list
affects: mcp-server/engineering_board_mcp.py
discovered: 2026-09-09
discovered_at: 2026-09-09T00:04:32Z
promoted_from: [mcp:_sessions/mcp-2026-09-09.md:24b9d8c9f6419eda]
---

# Token-only pattern and hypothesis apply falls through to list

## Done when

- [ ] Define and verify the completion criterion.

## Evidence

> During the installed-plugin capability-lab sweep, board_patterns and board_hypotheses preview succeeded, but an apply call containing only the exact unchanged returned plan_id or plan_token behaved like list and wrote nothing; repeating the original action payload alongside the exact unchanged token succeeded. Priority: P2. Done when: token-only apply works for both tools as documented and regression tests cover it.

## Done when

- [ ] Token-only apply works for both `board_patterns` and `board_hypotheses` as documented.
- [ ] Regression tests cover token-only apply for both tools.

## Comments

- **Codex** 2026-09-09T00:11:46Z: Correction: exact reproduction proved board_hypotheses token-only apply succeeds when the unchanged token is passed in the apply field; only board_patterns falls through to list when called with root, project, and apply alone. B002 scope is narrowed to board_patterns, and hypothesis behavior is not a defect.
- **codex-b002-20260908** 2026-09-09T02:48:51Z: Claimed for TDD implementation. Reproduce root/project/apply-only board_patterns behavior, align it with board_hypotheses token-only apply, and add regression coverage.
- **codex-b002-20260908** 2026-09-09T02:56:48Z: Resolved after apply-only parity passed for patterns and hypotheses, legacy repeated-payload apply remained compatible, the MCP suite passed 232 checks, and the full suite passed 21/21.

## Resolution evidence

`board_patterns` MCP previews now return a self-contained, content-bound identifier in `plan_id`. An apply call with only `root`, `project`, and that identifier reconstructs and revalidates the original action before writing. Existing 64-character plan IDs remain accepted when callers repeat the original action and inputs.

Regression coverage exercises apply-only follow-ups for both `board_patterns` and `board_hypotheses`. `bash mcp-server/run-tests.sh` passed 232 checks, and `bash tests/run-all.sh` passed all 21 suites.

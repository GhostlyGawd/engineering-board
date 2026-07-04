---
id: B004
type: bug
title: Permission allowlist does not cover the scripts the hooks actually invoke
discovered: 2026-07-04
status: resolved
priority: P1
affects: references/required-permissions.json
needs: tdd
pattern: [permission-mismatch, silent-failure]
---

## Done when
- `references/required-permissions.json` contains a Bash pattern for EVERY `board-*.sh` invoked by `hooks/stop-hook-procedure.md` and `commands/*.md`, using the same path form the invocation uses (`$CLAUDE_PLUGIN_ROOT/hooks/scripts/...`).
- `commands/board-install-permissions.md`'s printed list matches the JSON.
- A deterministic test asserts: allowlist ⊇ {scripts invoked in procedures/commands}, with matching path form.

## Observed behavior
Allowlist covers only 5 scripts (acquire/heartbeat/reclaim-stale/release/permission-self-check) using RELATIVE paths `bash hooks/scripts/...`. The procedures invoke ABSOLUTE `bash $CLAUDE_PLUGIN_ROOT/hooks/scripts/...` and use scripts absent from the allowlist entirely: `board-scratch-append.sh` (every passive Stop), `board-active-workers-bump/register.sh`, `board-mode-guard.sh`, `board-pm-fallback-heartbeat.sh`. Net effect: the autonomous loop hits permission prompts on its core scripts, contradicting "runs without babysitting."

## Note
Structural gap (missing scripts + inconsistent path form) is verifiable in-repo. Live permission-prompt behavior can't be exercised autonomously (BLOCKERS B1) — the fix is validated by the coverage test, not a live session.

## Resolution (C1, PR C1b)
`references/required-permissions.json` rewritten to cover all 11 board-*.sh
scripts the orchestrator invokes (was 5), using the `$CLAUDE_PLUGIN_ROOT/hooks/
scripts/...` form that matches the real invocations (was relative, mismatched).
New coverage assertions T26-T28 in `tests/permissions/automated.sh` parse every
`bash ...board-*.sh` call in stop-hook-procedure.md + commands/*.md and assert
allowlist coverage + consistent path form. `settings-*` fixtures updated.
Live permission-prompt behavior can't be exercised autonomously (BLOCKERS B1);
the structural coverage is the verifiable fix.

---
id: B004
type: bug
title: Permission allowlist does not cover the scripts the hooks actually invoke
discovered: 2026-07-04
status: open
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

---
id: B046
type: bug
title: Permission rules emitted without Tool(...) wrapper; self-check reports a false green
discovered: 2026-07-04
status: resolved
priority: P1
affects: commands/board-install-permissions.md
needs: tdd
pattern: [permissions, false-negative-selfcheck]
---

## Done when
- The install path emits Claude Code permission rules in wrapped `Tool(specifier)` form (`Bash(bash …:*)`, `SlashCommand(/pm-start)`) so they actually match, and the self-check compares against the same wrapped form so a correct install reports green and an incorrect/absent one reports missing.

## Observed behavior (C6 Track B — MAJOR)
`references/required-permissions.json` stores a bare `pattern` plus a separate `tool` field. `commands/board-install-permissions.md` emits `claude config add permissions.allow "<bare pattern>"` and `board-permission-self-check.sh` compares the bare `pattern` against `permissions.allow`. But Claude Code allow-rules must be `Tool(specifier)` strings; a bare `bash …:*` / `/pm-start` never matches the real Bash/SlashCommand tools. Net: the user installs rules that never fire (every Stop-hook script and slash command still prompts), yet re-running the self-check prints "all permissions installed" — a false green over a no-op. No `Bash(`/`SlashCommand(` wrapper appears anywhere in the repo. Distinct from B004 (coverage + path form) and B030 (delivery step-count), which left the wrapper untouched.

## Fix direction
Generate the wrapped rule from the `tool` field (or store the wrapped string) in both the printed `claude config add` lines and the self-check comparison; update the settings-all-patterns fixture + T26-T28 assertions to the wrapped form.

## Resolution (C6, PR C6b)
self-check now compares the wrapped `Tool(specifier)` rule (rule_for = f"{tool}({pattern})"); the install command emits the wrapped form; all-patterns/partial fixtures wrapped; new T05b regression fixture (settings-bare-legacy.json) asserts bare rules report all-missing, not a false green. permissions suite 28->29.

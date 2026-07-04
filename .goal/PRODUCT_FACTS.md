# PRODUCT_FACTS — engineering-board (Phase 0 audit)

_Ground-truth audit for the productization run. Derived from the repo at commit `0d6d532` (branch `claude/engineering-board-productize-fu2vvk`). All claims here are checked against code._

## 1. What it is

**engineering-board** is a **Claude Code plugin** (v1.1.0, MIT, author "Acadia") that turns a committed markdown tree — `engineering-board/<project>/` — into an **autonomous, multi-agent software-engineering board**. It runs entirely on vanilla Claude Code primitives (hooks, slash commands, subagents, `Task()` dispatch) plus `bash` + `python3`. No external services, no database, no daemon.

The board is **human-visible and git-committed** (markdown cards, a `BOARD.md` index, a `GRAPH.yml` structural graph, a `BOARD-ROUTER.md`), not a hidden database. AI agent sessions read and write it to coordinate work across sessions, with durable cross-session memory ("Learning" entries, `L###`).

- **Language / stack:** Bash scripts (`#!/usr/bin/env bash`, POSIX/Git-Bash-safe) + `python3` for date math, JSON, SHA256, atomic file ops. Orchestration logic lives in markdown prompt files interpreted by Claude Code. **Zero runtime package dependencies.**
- **Entry points:** slash commands in `commands/`, hooks wired in `hooks/hooks.json`, subagents in `agents/`, skills in `skills/`.
- **Packaging today:** Claude Code plugin — `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` (both at 1.1.0, coherence-checked). **No MCP server exists yet** (grep confirms: MCP is only referenced in research docs comparing sibling projects; the product deliberately advertises "no MCP server requirements"). MCP packaging is the primary net-new Phase 2 build.
- **Docs:** `README.md` (user-facing, thorough), `ARCHITECTURE.md` (contributor-facing, 13 sections), `state.md` (cross-session handoff), `CLAUDE.md`, `NEXT-PHASE.md` (declares design frozen at v1.0.0), `docs/` (RFCs, research, specs), `specs/board-relocation.md`.
- **License:** MIT (already present — no fallback needed).
- **CI:** `.github/workflows/test.yml` runs `bash tests/run-all.sh` on every push + PR. Toolchain: bash + python3 + coreutils, preinstalled on `ubuntu-latest`, no install step.

## 2. Who it's plausibly for

- **Solo devs running agentic Claude Code workflows** who want findings captured automatically and worked autonomously without babysitting.
- **Small-team leads** who want a shared, reviewable, git-committed board that both humans and agents read/write.
- **OSS maintainers** who want durable, auditable engineering memory (Learnings) that survives session boundaries and lives in the repo.

## 3. Build / run instructions (verified this run)

Clean checkout → run tests. No build step (interpreted plugin).

```bash
git clone <repo> && cd engineering-board
bash tests/run-all.sh      # requires bash + python3 only
```

**Result (this run):** `RUN-ALL SUMMARY: 10 pass, 0 fail (of 10 suites)` — evidence: `.goal/evidence/G0-test-suite.txt`.

Installing/using the plugin itself: add the marketplace, install the plugin, then `/board-init <project>` in a consuming repo (see README Quick start). Runtime needs the permission allowlist from `references/required-permissions.json` (installable via `/board-install-permissions`).

## 4. Feature inventory (feature → one-line → code path)

**Modes (Stop-hook routing):** `.engineering-board/session-mode.json`, read by `hooks/scripts/board-stop-gate.sh`; procedure in `hooks/stop-hook-procedure.md`.
- Passive (default) — capture findings only. `finding-extractor` agent.
- PM (`/pm-start`) — `finding-extractor → consolidator → tidier → learnings-curator`.
- Worker (`/worker-start --discipline <tdd|review|validate>`) — claim → `tdd-builder`/`code-reviewer`/`validator` → release.
- Paused (`/board-pause`, `/board-resume`) — bypass capture.

**Commands (`commands/`, 10):** `board-init`, `board-rebuild`, `board-graph`, `board-pause`, `board-resume`, `pm-start`, `worker-start`, `board-install-permissions`, `board-claim-release`, `board-migrate`.

**Agents (`agents/`, 8):** `board-manager` (router over 4 skills), `finding-extractor` (per-turn passive listener, `tools: Read`), `consolidator` (scratch→live w/ anchor verification, supersession, T2b distinct-affects safeguard), `tidier` (index rebuild, stale-claim reclaim, scratch cleanup), `learnings-curator` (promotes recurring `pattern:` tags → `learnings/L###`), `tdd-builder`, `code-reviewer`, `validator` (strictly read-only).

**Skills (`skills/`, 4):** `board-intake`, `board-triage`, `board-resolve`, `board-consolidate` — shared protocol `references/auto-resolve-pass.md`.

**Hooks (`hooks/hooks.json`, 4 events):** `SessionStart`→`board-session-start.sh` (board view), `PostToolUse(Write)`→`board-validate-entry.sh` (frontmatter + index validation), `UserPromptSubmit`→`board-prompt-guard.sh` (routing reminder on debug keywords), `Stop`→`board-stop-gate.sh` + `stop-hook-procedure.md` (mode-routed orchestrator).

**Deterministic substrate scripts (`hooks/scripts/`, 21):** claim locking (`board-claim-acquire/release/reclaim-stale/heartbeat.sh`), `board-consolidate.sh`, `board-scratch-append.sh`, `board-curate-learnings.sh`, `board-migrate.sh`, `board-relocate.sh`, `board-mode-guard.sh`, `board-paths.sh` (single-source board-location resolver), `board-session-start.sh`, active-workers registry (`register/bump/cleanup`), `board-audit-scratch.sh`, `board-index-check.sh`, `board-permission-self-check.sh`, `board-validate-entry.sh`, `board-pm-fallback-heartbeat.sh`.

## 5. Defect inventory (severity-labeled)

| # | Defect | File | Severity | Justification |
|---|---|---|---|---|
| D1 | README line 45 still calls `learnings-curator` a "v0.2.2 stub (inventory-only)"; it was fully implemented in v0.3.0 (Learning entity L###). Stale/inaccurate doc. | `README.md:45`, and README:217 | **minor** | Doc accuracy only; contradicts shipped behavior. Fix in Phase 2/4 README rewrite. |
| D2 | README §"Component" table + line 61 mark `board-claim-heartbeat.sh` "reserved; not yet wired". | `README.md:61` | **minor** | Documented intentional state; no runtime impact. Confirm whether to wire or keep documented. |
| D3 | `board-index-check.sh`, `board-claim-*.sh`, `board-consolidate.sh`, etc. are `-rw` (not executable) while others are `-rwx`. Invoked via `bash <script>` so this is harmless, but inconsistent. | `hooks/scripts/*.sh` | **minor** | Cosmetic; scripts are sourced/`bash`-invoked, not exec'd directly. |
| D4 | No MCP server. Positioning wants dual distribution (plugin + MCP). | (absent) | **major** (scope, not bug) | Required Phase 2 build item; not a regression. |
| — | `<!-- TODO — define completion criteria. -->` in `consolidator.md:146` and `board-consolidate.sh:364` | | **not a defect** | This is intentional *template text* written INTO generated board entries as a Done-when placeholder for the user. Verified by context. |

**Failing tests:** none — 10/10 suites green. **Open GitHub issues affecting scope:** none blocking (historical #3 scratch-append fidelity already shipped in v1.0.1).

**Severity summary:** 0 blocker, 1 major (MCP packaging = build item), 3 minor (doc/cosmetic).

## 6. Existing packaging state

- **Claude Code plugin:** ✅ present and versioned (`.claude-plugin/plugin.json` + `marketplace.json`, both 1.1.0, coherence-enforced by `tests/version-coherence.sh`). Structure (commands/agents/skills/hooks) follows the plugin layout. Phase 2 will verify against current official plugin docs.
- **MCP server:** ❌ absent. Net-new adapter to build in Phase 2, wrapping the deterministic board substrate (init, capture, list/get, consolidate, rebuild, claim/release, learnings) as MCP tools.

## 7. Test facts

`bash tests/run-all.sh` → **10 suites**: orchestration (15 sub-tests), claims (5), smoke, scratch, paths, modes (6), permissions (25 assertions), lint-orchestrator-prompts (10/10 framing files), version-coherence, crosscompat-lint (22 scripts). Fixtures: 20 benign + 30 adversarial-paste corpora. All green this run.

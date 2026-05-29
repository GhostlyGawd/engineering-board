# engineering-board

A Claude Code plugin that converts a markdown-based engineering board (`docs/boards/`) into an autonomous, multi-agent build system. Findings get captured passively from every session, promoted to the live board via deterministic consolidation, and worked through a `tdd → review → validate` state machine with atomic claim locking — all driven by the Stop hook.

For a full contributor-facing map of every file and how they connect, see [`ARCHITECTURE.md`](ARCHITECTURE.md).

## What it does

- **Passive finding capture** — every Stop event dispatches a `finding-extractor` subagent that scans the just-finished turn for bugs, features, questions, observations and writes them to a per-session scratch board at `docs/boards/<project>/_sessions/<session-id>.md`.
- **Deterministic consolidation** — scratch never reaches the live board until anchor-verified by the `consolidator` subagent (matched against the transcript), with supersession detection and a distinct-`affects:` safeguard.
- **Real-time routing** — when a confirmed finding surfaces during a session, the `board-manager` agent routes it via the four board-* skills (intake, triage, resolve, consolidate).
- **PM pipeline** (`/pm-start`) — every Stop event runs `finding-extractor` → `consolidator` → `tidier` → `learnings-curator`, keeping the live board promoted and tidy.
- **Worker pipeline** (`/worker-start --discipline <tdd|review|validate>`) — every Stop event picks an entry with matching `needs:`, atomically claims it, dispatches the matching worker subagent (`tdd-builder` / `code-reviewer` / `validator`), writes back `suggested_next_needs`, and releases the claim. Three workers run in parallel form a continuous build pipeline.
- **Entry validation on write** — frontmatter and `BOARD.md` indexing are checked on every Write to `docs/boards/.../*.md`. Missing fields or unindexed entries block the write.
- **Session-start board view** — every session starts with open items, in-progress warnings, blocking relationships, systemic patterns, and un-promoted scratch counts across all project boards.

## Mode-based Stop routing

The Stop hook reads `.engineering-board/session-mode.json` and routes to one of three procedures (full canonical procedure in [`hooks/stop-hook-procedure.md`](hooks/stop-hook-procedure.md)):

| Mode | Set by | Stop dispatches | Use case |
|---|---|---|---|
| **Passive** (default) | nothing | `finding-extractor` only | Any session — captures findings without disturbing the work |
| **Paused** | `/board-pause` | nothing (emits `<<EB-PASSIVE-PAUSED>>`) | Drafting / brainstorming — bypass capture |
| **PM** | `/pm-start` | `finding-extractor` → `consolidator` → `tidier` → `learnings-curator` | Long-running session promoting scratch → live |
| **Worker** | `/worker-start --discipline <d>` | claim-acquire → one of `tdd-builder` / `code-reviewer` / `validator` → claim-release | Long-running session driving `needs:` state machine |

## Components

| Type | Name | Purpose |
|------|------|---------|
| Command | `/board-init <project> [affects-prefix]` | Scaffold `docs/boards/<project>/` and append to `BOARD-ROUTER.md` |
| Command | `/board-rebuild [project]` | Deterministically regenerate `BOARD.md` + `GRAPH.yml` from entry files; runs auto-resolve terminal pass |
| Command | `/board-graph [project] [--include-archive]` | Build structural graph (`GRAPH.yml`): clusters, bridges, isolated nodes, density |
| Command | `/board-pause` | Suspend passive listening (Stop emits `<<EB-PASSIVE-PAUSED>>`) |
| Command | `/board-resume` | Restore passive listening |
| Command | `/pm-start` | Set session to PM mode — Stop runs PM pipeline every turn |
| Command | `/worker-start --discipline <tdd\|review\|validate>` | Set session to Worker mode — Stop runs worker dispatch every turn |
| Command | `/board-install-permissions` | Print copy-pasteable `claude config add` commands from `references/required-permissions.json` |
| Command | `/board-claim-release <entry-id> [--force]` | Manual fallback to release a stuck `_claims/<entry-id>/` after a worker session crashed mid-turn |
| Agent | `board-manager` | Master router for ad-hoc routing/triage/resolution; wraps the 4 board-* skills |
| Agent | `finding-extractor` | Per-turn passive listener (`model: inherit`, `tools: Read`); emits scratch JSON |
| Agent | `consolidator` | PM subagent: promote scratch → live; anchor verification, supersession, T2b distinct-affects safeguard |
| Agent | `tidier` | PM subagent: index rebuild, stale-claim reclamation, scratch cleanup |
| Agent | `learnings-curator` | PM subagent — **v0.2.2 stub** (inventory-only; full Learning entity in v0.3.0 plan) |
| Agent | `tdd-builder` | Worker subagent (`tdd` discipline): write failing test → minimal fix → re-run |
| Agent | `code-reviewer` | Worker subagent (`review` discipline): inspect tests + impl; suggest `validate` or regress to `tdd` |
| Agent | `validator` | Worker subagent (`validate` discipline, **strictly read-only**): re-run suite + verify Done-when |
| Skill | `board-intake` | Protocol for creating new board entries |
| Skill | `board-triage` | Protocol for prioritizing open items |
| Skill | `board-resolve` | Protocol for resolving questions and bugs/features |
| Skill | `board-consolidate` | Protocol for promoting scratch → live board |
| Hook | `SessionStart` → `board-session-start.sh` | Surface open items, in-progress, blocked, systemic patterns, un-promoted scratch counts |
| Hook | `PostToolUse` (Write) → `board-validate-entry.sh` | Validate frontmatter + `BOARD.md` indexing |
| Hook | `UserPromptSubmit` → `board-prompt-guard.sh` | Inject routing reminder on debug/error/bug/crash keyword prompts |
| Hook | `Stop` (command) → `board-stop-gate.sh` | Capture stdin; check mode; suppress prompt hook if paused or no board |
| Hook | `Stop` (prompt) → `stop-hook-procedure.md` | Mode-routed orchestrator: passive / PM / worker dispatch |
| Script | `board-claim-acquire.sh` | Atomic `mkdir`-based claim lock with cloud-sync detection (180s → 300s stale threshold) |
| Script | `board-claim-release.sh` | Owner-verified claim release with NTFS retry loop |
| Script | `board-claim-reclaim-stale.sh` | Scan + remove stale claims; cloud-sync detection |
| Script | `board-claim-heartbeat.sh` | Refresh heartbeat during long worker operations (reserved; not yet wired) |
| Script | `board-consolidate.sh` | Re-applies reject rules + anchor verification + supersession; promotes scratch → live |
| Script | `board-audit-scratch.sh` | Completeness audit: every scratch_id must have a `consolidation.log` disposition |
| Script | `board-index-check.sh` | Invariant: `BOARD.md` row count == entry file count |
| Script | `board-permission-self-check.sh` | Compare `required-permissions.json` against `~/.claude/settings.json` |
| Reference | `references/auto-resolve-pass.md` | Shared protocol used by all 4 skills (extract Done-when → evidence → confidence → cascade depth 2) |
| Reference | `references/required-permissions.json` | Permission allowlist manifest used by `/board-install-permissions` |

## Quick start

After installing, run this once per project that should have a board:

```
/board-init <project-name> [affects-prefix]
```

Examples:
- `/board-init navigator` — creates a board for project `navigator`, routing entries with `affects: navigator/...`
- `/board-init platform "platform/, services/, infra/"` — creates a board with multiple affects-prefixes

`/board-init` is idempotent — running it twice does not duplicate files or router rows. It creates `docs/boards/BOARD-ROUTER.md` (or appends to it), `docs/boards/<project>/BOARD.md`, `ARCHIVE.md`, and the four entry-type subdirectories.

If no board exists when a session starts, the SessionStart hook prints a one-line reminder pointing at `/board-init` instead of doing anything else — projects that should not have a board are unaffected.

## Layout

This plugin is opinionated about your repo layout. After running `/board-init`, your project will have either:

**Multi-board layout (recommended):**
```
docs/boards/
├── BOARD-ROUTER.md          # Maps `affects:` prefix → board directory
├── <project-a>/
│   ├── BOARD.md             # Live index of open items
│   ├── ARCHIVE.md           # Resolved items
│   ├── bugs/
│   ├── features/
│   ├── questions/
│   └── observations/
└── <project-b>/
    └── ...
```

**Or legacy single-board layout (auto-detected):**
```
docs/board/
├── BOARD.md
├── ARCHIVE.md
├── bugs/
├── features/
├── questions/
└── observations/
```

If neither exists, the SessionStart hook prints a one-line nudge to run `/board-init` and otherwise stays out of your way.

### `BOARD-ROUTER.md` format

The router is a markdown table with `project | path | affects-prefix` columns:

```markdown
| project    | path                       | affects prefix |
|------------|----------------------------|----------------|
| navigator  | docs/boards/navigator      | navigator/, src/, scripts/ |
| platform   | docs/boards/platform       | platform/      |
```

### Entry frontmatter

Bug/feature entries require:
```yaml
---
id: B001
type: bug
title: Short description
discovered: 2026-05-02
status: open
priority: high
affects: navigator/ranking
---

## Done when
- [ ] Specific exit criterion
```

Question entries require `id`, `type: question`, `title`, `discovered`, `status`, and a `## Done when` section.

## Requirements

- **python3** on PATH — used for date math, JSON parsing, SHA256 in board scripts. The plugin degrades to a one-line warning if python3 is missing; consolidation will not run.
- **bash** — POSIX or Git Bash (bundled with Git for Windows). All scripts use `#!/usr/bin/env bash`.
- **Cost model:** v0.2.1's Stop hook fires the finding-extractor on every turn. There is no per-session call cap and no sampling. Users on flat-rate plans (Claude Max) absorb this naturally; users on metered API billing should review the cost model before enabling.

## Install

```
/plugin marketplace add GhostlyGawd/engineering-board
/plugin install engineering-board
```

Then enable it in your Claude Code settings.

## Uninstall

```
/plugin uninstall engineering-board
/plugin marketplace remove engineering-board
```

## Changelog

### 0.3.0 — Resilience + Learning entity

Combines the v0.2.3 Resilience block (active-workers registry + PM-fallback heartbeat) with the v0.3.0 Unification block (Learning entity + `/board-migrate`). Shipped together because they were implemented in one session; the consensus plan kept them logically separate so they can still be rolled back independently via `git revert`.

**v0.2.3 Resilience additions:**
- `references/active-workers-registry.md` — contract for `.engineering-board/active-workers.json`.
- `hooks/scripts/board-active-workers-register.sh`, `board-active-workers-bump.sh`, `board-active-workers-cleanup.sh` — registry mutators with mkdir-based lockfile.
- `hooks/scripts/board-pm-fallback-heartbeat.sh` — PM pre-flight scans `_claims/`, cross-references the registry, refreshes heartbeats for claims whose owning session is alive (and not paused). Wired into `stop-hook-procedure.md` Section 3-PM step `(pre)`.
- `/pm-start`, `/worker-start` register on session start; `/board-pause`, `/board-resume` toggle `paused: true` in the registry.
- Worker self-bump on claim acquire / release (Stop hook step (f), (i)); worker subagents document heartbeat refresh for long ops.

**v0.3.0 Unification additions:**
- Learning entry type (`L###`): subtype `pattern` / `finding` / `principle`; required fields `confidence`, `recurrence`, `derived_from`; required body sections `## Takeaway` and `## Sources`. Schema in `skills/board-intake/references/frontmatter-schema.md`.
- `agents/learnings-curator.md` — full implementation (replaces the v0.2.2 stub). Dispatches `hooks/scripts/board-curate-learnings.sh`, which scans resolved bug/feature/observation entries for `pattern:` tags and promotes tags with recurrence ≥ 3 to `learnings/L###-<slug>.md`. Idempotent (re-run produces byte-identical learnings).
- `commands/board-migrate.md` + `hooks/scripts/board-migrate.sh` — `--apply` / `--rollback` / `--status`. Both apply and rollback are SHA256-idempotent (verified by `tests/orchestration/board-migrate.sh`). Apply creates `learnings/`, back-fills `needs: tdd` on open bug/feature entries without it, and snapshots pre-migrate state. Rollback restores the snapshot byte-equal.
- SessionStart surfaces top 3 medium/high-confidence learnings filtered by cwd against each learning's `applies_to` field.

**Quality-of-life additions:**
- `tests/run-all.sh` — single CI runner across all 8 suites.
- `tests/version-coherence.sh` — `plugin.json.version == marketplace.json.plugins[].version` invariant.
- `tests/crosscompat-lint.sh` — bash + python3 portability lint over `hooks/scripts/*.sh` (no `date -d`/`date -j -f`, no drive letters, no CRLF shebangs, no `jq`, shebang must be `#!/usr/bin/env bash`). Supports per-file `# crosscompat-lint-ignore: <rule>` opt-out for documented exceptions.
- `ARCHITECTURE.md` §11.5 documents the four-mode transition refusal matrix.
- 4 new integration test suites: `active-workers-registry.sh`, `pm-fallback-heartbeat.sh`, `learnings-curator.sh`, `board-migrate.sh`.

**Caught in this release:**
- `hooks/hooks.json` had silently lost its Stop `type: "prompt"` hook in commit 5a4226d. The runtime dispatch chain was inactive for ~13 days. Restored in commit 52e99a4; structural lint covers it.
- `board-prompt-guard.sh`, `board-session-start.sh`, `board-validate-entry.sh` had `#!/bin/bash` shebangs (Git Bash incompatible). Normalized to `#!/usr/bin/env bash` per the consensus plan global rules.

### 0.2.2 — PM + Worker orchestration

Adds the multi-agent orchestration layer on top of v0.2.1 scratch capture: PM pipeline that consolidates scratch into the live board on every Stop turn, and a Worker pipeline that drives a `tdd → review → validate → resolved` state machine on entries with `needs:` set. Per-entry exclusivity is enforced via atomic `mkdir`-based claim locks with cloud-sync detection.

**New commands:** `/pm-start`, `/worker-start --discipline <tdd|review|validate>`, `/board-install-permissions`, `/board-claim-release`, `/board-rebuild`, `/board-graph`.

**New PM subagents:** `consolidator` (promotes verified scratch → live), `tidier` (board hygiene), `learnings-curator` (stub; full Learning entity in v0.3.0 plan).

**New Worker subagents:** `tdd-builder`, `code-reviewer`, `validator` (validator is strictly read-only — enforced by tool list).

**New scripts:** `board-claim-acquire.sh`, `board-claim-release.sh`, `board-claim-reclaim-stale.sh`, `board-claim-heartbeat.sh` (reserved), `board-permission-self-check.sh`.

**New procedure:** `hooks/stop-hook-procedure.md` is the canonical mode-routed Stop orchestrator; `hooks.json`'s Stop entries are intentionally thin.

**New reference:** `references/required-permissions.json` is the permission allowlist manifest installed by `/board-install-permissions`.

### 0.2.1.2 — Prompt-author tightenings (2026-05-11)

Two small, non-behavioral patches surfaced during v0.2.1 live smoke testing. No new scope; both are prompt-author tightenings against existing v0.2.1 surfaces.

**Modified:**
- `hooks/hooks.json` Stop hook step (d) — timestamp instruction now explicitly forbids placeholder times and pins the canonical computation (`python3 -c "...datetime.now(timezone.utc)..."`). v0.2.1 left "ISO-8601" loose, and live testing observed the model emitting midnight stubs.
- `agents/finding-extractor.md` — opens by documenting the canonical input format (`---USER MESSAGE---` / `---ASSISTANT MESSAGE---` / `---END---`) as a first-class section, matching the v0.2.1 hook fix in commit `8e03757`. Eliminates the prior ambiguity where the agent doc said "current assistant turn" while the hook actually dispatched a user+assistant pair.
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — version 0.2.1 → 0.2.1.2.

No new files. No behavioral change to the consolidator, scratch corpus, or AC coverage. v0.2.1's 12/12 verifier and 21/21 smoke continue to pass post-patch.

### 0.2.1 — Scratch Capture (2026-05-11)

**New:**
- `agents/finding-extractor.md` — per-turn passive listener (`model: inherit`); emits JSON scratch findings.
- `hooks/hooks.json` Stop hook — replaced the v0.2.0 routing-guard prompt with a condition-shaped `type: "prompt"` hook that dispatches `finding-extractor` via `Task()` every turn, plus a `type: "command"` hook that captures stdin for the consolidator. New `<<EB-PASSIVE-PAUSED>>` sentinel emitted when `session-mode = paused`.
- `hooks/scripts/board-consolidate.sh` — deterministic anchor verification + consolidator-detected supersession + AC T2b safeguard (distinct `affects:` never archived).
- `hooks/scripts/board-audit-scratch.sh` — completeness audit; zero unaccounted scratch IDs.
- `hooks/scripts/board-index-check.sh` — BOARD.md row count == subdir file count invariant (AC T4 partial).
- `commands/board-pause.md`, `commands/board-resume.md` — passive-listening kill switch and restore.
- `skills/board-consolidate/SKILL.md` — consolidation protocol.
- `tests/fixtures/benign-findings/` (20 fixtures) + `tests/fixtures/adversarial-paste/` (30 fixtures, covering all three reject categories: imperative-prefix, slash-command, subagent-mention) — corpora for AC C6 accept-rate and Scenario 4 reject-rate.
- `tests/lint-orchestrator-prompts.sh` — verifies the canonical "untrusted data" framing string is present in all orchestrator-facing prompt files (live PASS 3/3).

**Modified:**
- `hooks/scripts/board-session-start.sh` — recognizes `_sessions/` and surfaces un-promoted scratch counts per project.
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` — version 0.2.0 → 0.2.1.

**Consistency fix:** The slash-command reject regex in `agents/finding-extractor.md` and `skills/board-consolidate/SKILL.md` is anchored at a token boundary — `(?:^|\s)/[a-z][a-z-]+` — so Unix file paths like `src/foo.py` do not produce false-positive drops. The naked `/[a-z][a-z-]+` form would have rejected every finding whose `affects:` referenced a slash-pathed file. Caught during the T2b lint test.

**Composability spike:** all 5 criteria PASS (Stop-hook type:prompt dispatches Task() from main session; JSON captured; written to disk pre-Stop; transcript accessible via stdin; orchestrator framing neutralizes mid-string imperatives). Documented in `tests/spike/`.

**Architectural finding (for v0.2.2 ADR):** Claude Code presents `type: "prompt"` Stop hook bodies as a "stop-condition judge" prompt to the model. Production hook bodies are written as condition-shaped — explicitly "if condition unmet, execute the procedure" — and reference `stop_hook_active` in stdin to skip self-triggered re-firings.

**Acceptance criteria covered:** C1 (every-turn extraction, no sampling, no caps — spec-compliant), C2 (scratch write before Stop returns), C3 (consolidation log accountability), C6 (framing-string lint + ≥95% benign-corpus accept rate), T2 (consolidator-detected supersession), T2b (distinct `affects:` never archived), partial T4 (index-check script).

**Constraints (user-stated):** Claude Max 20x subscription. No haiku locks anywhere; all subagents `model: inherit`. No per-session call caps. No cost-driven sampling.

### 0.2.0 — Multi-board layout
(previous release — see git history)

## License

MIT — see [LICENSE](LICENSE).

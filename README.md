# engineering-board

A Claude Code plugin that converts a markdown-based engineering board (`docs/boards/`) into an autonomous, event-driven system. Findings get routed to the correct project board in real-time, entries are validated on write, in-progress items are surfaced at session start, and unrouted findings are caught before session end.

## What it does

- **Real-time routing** — when a confirmed bug, regression, or noteworthy observation surfaces during a debugging or workflow session, the `board-manager` agent routes it to the correct project board immediately. No batching for end-of-session.
- **Session-start board view** — every session starts with the open items, in-progress warnings, blocking relationships, and systemic patterns across all your project boards.
- **Entry validation on write** — when you write to `docs/boards/<project>/{bugs,features,questions,observations}/*.md`, frontmatter is validated and your `BOARD.md` index is checked for the entry ID. Missing fields or unindexed entries block the write.
- **Routing-before-stop guard** — at session end, the model is prompted to review the conversation for unrouted findings and route any it missed.
- **Prompt-context priming** — when your prompt looks like a debugging or workflow-run session, a system message reminds the agent that real-time routing is active.

## v0.2.1 — Scratch Capture (new)

Every Stop event in every session now dispatches a `finding-extractor` subagent that scans the just-finished assistant turn for surface-level findings (bugs, features, questions, observations) and writes them to a per-session scratch board at `docs/boards/<project>/_sessions/<session-id>.md`. Scratch entries never reach the live board until a consolidation pass runs — by default on real session end (Stop without continuation), which promotes survivors and archives superseded entries with deterministic anchor verification against the conversation transcript.

This means: planning conversations, drafts, and brainstorms no longer pollute the live board with half-formed findings. Capture happens every turn; the live board only ever sees verified, deduplicated, anchor-matched entries.

Two new slash commands:
- `/board-pause` — bypass passive listening for the current session (useful for drafting / brainstorming). The Stop hook emits the `<<EB-PASSIVE-PAUSED>>` sentinel and skips extraction while paused.
- `/board-resume` — re-enable.

The composability spike that gated v0.2.1 (a–e) passed empirically: Stop hook `type: "prompt"` dispatches Task() from main session, JSON is captured in the assistant turn, written to disk before Stop returns, the transcript is accessible to the consolidator, and orchestrator framing neutralizes mid-string imperatives.

## Components

| Type | Name | Purpose |
|------|------|---------|
| Command | `/board-init <project-name>` | Scaffolds the `docs/boards/` layout for a project |
| Command | `/board-pause` | Suspend passive listening for the current session |
| Command | `/board-resume` | Resume passive listening |
| Agent | `board-manager` | Routes findings, resolves questions, runs triage |
| Agent | `finding-extractor` | Per-turn passive listener; emits scratch JSON |
| Skill | `board-intake` | Protocol for creating new board entries |
| Skill | `board-triage` | Protocol for prioritizing open items |
| Skill | `board-resolve` | Protocol for resolving questions and bugs/features |
| Skill | `board-consolidate` | Protocol for promoting scratch → live board |
| Hook | `SessionStart` | Loads board state at session start; surfaces un-promoted scratch |
| Hook | `PostToolUse` (Write) | Validates board entries on write |
| Hook | `UserPromptSubmit` | Primes routing context on debugging prompts |
| Hook | `Stop` (command) | Captures Stop stdin to `.engineering-board/last-stop-stdin.json` |
| Hook | `Stop` (prompt) | Condition-shaped judge that dispatches `finding-extractor` per turn |

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

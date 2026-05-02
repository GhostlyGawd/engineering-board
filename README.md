# engineering-board

A Claude Code plugin that converts a markdown-based engineering board (`docs/boards/`) into an autonomous, event-driven system. Findings get routed to the correct project board in real-time, entries are validated on write, in-progress items are surfaced at session start, and unrouted findings are caught before session end.

## What it does

- **Real-time routing** — when a confirmed bug, regression, or noteworthy observation surfaces during a debugging or workflow session, the `board-manager` agent routes it to the correct project board immediately. No batching for end-of-session.
- **Session-start board view** — every session starts with the open items, in-progress warnings, blocking relationships, and systemic patterns across all your project boards.
- **Entry validation on write** — when you write to `docs/boards/<project>/{bugs,features,questions,observations}/*.md`, frontmatter is validated and your `BOARD.md` index is checked for the entry ID. Missing fields or unindexed entries block the write.
- **Routing-before-stop guard** — at session end, the model is prompted to review the conversation for unrouted findings and route any it missed.
- **Prompt-context priming** — when your prompt looks like a debugging or workflow-run session, a system message reminds the agent that real-time routing is active.

## Components

| Type | Name | Purpose |
|------|------|---------|
| Agent | `board-manager` | Routes findings, resolves questions, runs triage |
| Skill | `board-intake` | Protocol for creating new board entries |
| Skill | `board-triage` | Protocol for prioritizing open items |
| Skill | `board-resolve` | Protocol for resolving questions and bugs/features |
| Hook | `SessionStart` | Loads board state at session start |
| Hook | `PostToolUse` (Write) | Validates board entries on write |
| Hook | `UserPromptSubmit` | Primes routing context on debugging prompts |
| Hook | `Stop` | Catches unrouted findings before session ends |

## Requirements

This plugin is opinionated about your repo layout. Before installing, your project should have either:

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

If neither exists in your project, the SessionStart hook exits silently — the plugin won't error, it just won't do anything until you create the structure.

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

## License

MIT — see [LICENSE](LICENSE).

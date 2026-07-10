# Coming from Vibe Kanban? — landing copy

_Launch asset (IMPROVEMENTS.md v4, C11): page copy for vibe-kanban users looking
for a new home after the project's sunset (announced April 2026 —
<https://www.vibekanban.com/blog/shutdown>). Tone rule: no gloating —
vibe-kanban was a good tool (~27k stars, a 195-point Show HN) and its users'
workflow deserves a straight answer, not a victory lap. This file is the copy
source; it can ship as-is in docs or be adapted into a landing section later._

---

## Vibe Kanban is winding down. Here's what maps — and what doesn't.

Vibe Kanban earned its audience: a genuinely good GUI for orchestrating coding
agents in parallel, one of the first tools to take multi-agent work seriously.
Its [shutdown post](https://www.vibekanban.com/blog/shutdown) is worth reading.
If you relied on it, you're not looking for a eulogy — you're looking for where
your workflow goes next. Here's an honest accounting of how much of it
engineering-board covers.

### What maps

| You had in Vibe Kanban | You get here |
|---|---|
| A kanban board of your agents' tasks | A board committed to your repo as markdown, rendered to a static `board.html` and republishable on every merge — no app to run, and your teammates see it in PRs |
| Parallel agents without collisions | Atomic claim-locking: workers claim a card before touching it, with heartbeats and stale-claim reclamation, so parallel agents never collide |
| Task tracking across sessions | Board entries (bugs, features, questions, observations) with priorities, dependencies, and a `tdd → review → validate` pipeline — plus findings captured passively from every session, and recurring lessons promoted into committed Learning entries |

### What does NOT map — plainly

- **No GUI orchestrator.** There is no desktop app and no live web UI. The board
  view is a static, read-only HTML page generated from the markdown; the
  orchestration runs through Claude Code hooks and agents (or MCP tools), not
  through buttons.
- **No per-task git worktrees.** Vibe Kanban isolated each task in its own
  worktree. engineering-board doesn't do that — agents work in your checkout,
  and isolation is whatever your own git habits provide.
- **No multi-executor support.** Vibe Kanban could drive multiple coding agents
  from one panel. engineering-board's autonomous pipeline is
  built for Claude Code specifically; other agents can read and write the same
  board through the zero-dependency MCP server, but the opinionated pipeline is
  a Claude Code plugin.

If those three are the core of what you loved, engineering-board is probably not
your replacement — and we'd rather you know that in the first minute than after
an install.

### Why the in-repo model survives a shutdown

The uncomfortable lesson of a sunsetting tool is that your workflow depended on
a company. engineering-board is structured so that can't happen to your board:

- **MIT licensed, zero runtime dependencies** — bash + python3, no packages to
  rot, nothing to license.
- **No server, no daemon, no database.** There is no backend to turn off.
- **The board is the database.** Every card, lock, and learning is plain
  markdown committed to your repo. If this project died tomorrow, your board
  stays exactly where it is — readable, diffable, yours — because it was never
  anywhere else.

### Where to start

- Live proof: [this repo's own board](https://ghostlygawd.github.io/engineering-board/board.html) —
  the tool is built in the open on itself.
- Install: [README quickstart](https://github.com/GhostlyGawd/engineering-board#quickstart) —
  Claude Code plugin (`/plugin marketplace add GhostlyGawd/engineering-board`) or
  the MCP server for any MCP client.
- The honest comparison table (including the things we don't do) is in the
  [README](https://github.com/GhostlyGawd/engineering-board#comparison).

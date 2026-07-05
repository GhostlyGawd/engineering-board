# POSITIONING — engineering-board (Phase 1)

_Live market research + positioning. All competitor/traction figures fetched live 2026-07-04; URLs in Citations. Traction numbers are snapshots and drift._

## 1. Landscape (≥6 competitors, cited)

The market splits into two camps that each make a trade-off engineering-board refuses:
**visible-but-dumb** git-markdown boards (no locking, no memory) vs. **smart-but-opaque** MCP coordination servers (locks + memory, but hidden in a DB, not Claude-native).

| # | Competitor | Bucket | What it does | Distribution | Traction | Gap engineering-board owns |
|---|---|---|---|---|---|---|
| 1 | **Backlog.md** (MrLesk) | git-markdown board | Markdown-native tasks (git-committed `.md`+YAML) + Kanban viz; MCP tools expose to agents | npm/Homebrew/Nix/Bun; MCP; CLI | **~5.9k★** (category leader) | Explicitly single-agent ("one task=one context=one PR"); **no claim-locking, no durable memory**; external CLI, not Claude-native |
| 2 | **Flux** (getflux.dev) | agent kanban | Kanban engine for agents; MCP + git `pull`/`push` on a side branch; JSON/SQLite | Docker/npm/source; MCP | Early | State in SQLite/JSON on a side branch (not in-tree human-readable); single-agent framing; no learnings memory |
| 3 | **Agent-MCP** (rinadelph) | MCP coordination | Multi-agent RAG knowledge-graph memory; file-level locks; dashboard | MCP (self-hosted) | **~1.3k★** | Memory is an **opaque RAG DB**, not a human-visible committed board; heavier setup; not a Claude Code plugin |
| 4 | **claude-code-workflows** (shinpr) | CC plugin | Specialized agents: requirements→design→impl→QA | **Claude Code plugin marketplace** | **~536★** | Artifacts in `docs/plans/` are **ephemeral/gitignored**; no durable board, no cross-session memory, no locking; linear not persistent |
| 5 | **kanban-mcp** (eyalzh) | MCP board | Kanban "memory" for multi-session AI; WIP limits; web UI | MCP; SQLite; web UI | **~40★** | State is a **SQLite DB** in a config dir (not git-diffable); no claim-locking; no learnings pipeline; not a plugin |
| 6 | **agent-orchestration** (madebyaris) | MCP coordination | Shared memory, turn-based queue, resource locks, agent discovery | MCP; per-project SQLite | **~12★** | Closest on *coordination primitives* but state is **SQLite**, Cursor/AGENTS.md-oriented, not Claude-native; no promoted Learnings |
| 7 | **kanban-mcp** (bradrisse) | MCP bridge | Middleware bridging LLMs to external **Planka** app | MCP (needs Planka) | Established | Depends on external Planka server; nothing lives in the repo; no memory/locking of its own |
| 8 | **taskboard** (tcarac) | local PM + MCP | Kanban UI + CLI + MCP; single binary; SQLite | Homebrew; MCP | Niche | Shared **SQLite DB**, not committed markdown; no learnings, no claim-locking; not Claude-native |

**Read of the field:** No competitor combines all four of engineering-board's traits at once — **git-committed/human-visible board + durable "Learning" memory + atomic multi-agent claim-locking + native Claude Code**. That four-way intersection is the open lane.

## 2. Distribution-channel & submission map

| Channel | How to submit | Human account / review? | Priority |
|---|---|---|---|
| **Self-hosted plugin marketplace** (`.claude-plugin/marketplace.json`) | Host in repo; users `/plugin marketplace add GhostlyGawd/engineering-board` → `/plugin install engineering-board` | None (self-serve) | **Live now** |
| **Claude community marketplace** (`anthropics/claude-plugins-community`) | Submit via claude.ai (Team/Enterprise) or Console form `platform.claude.com/plugins/submit`; run `claude plugin validate` first; review + safety screen; pinned to commit SHA | **Yes** — form + review | Prepared (needs human account) |
| **Official Anthropic directory** | Form `clau.de/plugin-directory-submission`; curated at Anthropic's discretion | **Yes** — manual | Prepared |
| **Official MCP Registry** (`registry.modelcontextprotocol.io`) | Publish package; add `mcpName`; `mcp-publisher init/login github/publish` a `server.json`; namespace `io.github.<user>/<name>`; automated validation | GitHub auth | Prepared |
| **Smithery** (`smithery.ai/new`) | `smithery mcp publish` or `.mcpb` bundle; needs `smithery.yaml`; auto-scan | Account + API key | Prepared |
| **PulseMCP / mcp.so / Glama** | Auto-crawl official registry + GitHub; claim/submit form/issue | Light/none | Auto-syndicated after registry |
| **awesome-claude-code** (hesreallyhim) | "Recommend a new resource" → issue (not PR); automated vetting | Issue | **High-signal, prepared** |
| **awesome-mcp-servers** (punkpeye) | PR adding entry per format | Manual PR review | Prepared |

## 3. Personas

1. **Solo agentic dev ("Sam").** Runs long autonomous Claude Code sessions. JTBD: *capture every bug/feature/question the agent surfaces and get them worked without me babysitting.* Reaches for it the moment a session ends with "I noticed 3 other issues" and they evaporate — engineering-board's passive finding-extractor + PM pipeline catch and promote them.
2. **Small-team lead ("Priya").** Wants a shared board humans AND agents read/write, reviewable in the same PRs as code. JTBD: *coordinate parallel agent work without collisions and keep it auditable.* Reaches for it when two agents (or an agent + a teammate) risk stepping on the same task — atomic claim-locking + a diffable board solve it.
3. **OSS maintainer ("Devon").** Wants durable, in-repo engineering memory. JTBD: *stop relearning the same lessons every session.* Reaches for it when the same class of bug recurs — Learnings (L###) promote recurring patterns into committed memory.

## 4. Positioning

- **Category:** *Agent coordination board* — "a git-committed kanban board that AI agents run themselves." (Sub-category: multi-agent memory + orchestration for Claude Code.)
- **Most defensible angle:** **The board is the database.** Coordination state, WIP locks, and durable learnings all live as committed markdown in your repo — no hidden DB, no external service, versioned and reviewable in the same PRs as your code. Structurally hard for SQLite/RAG competitors to copy without abandoning their storage model, and the thing Backlog.md deliberately doesn't do (no locking/memory).
- **One-liner (9 words ≤ 12 ✓):**
  > **A git-committed kanban board your AI agents run and remember.**
- **Tagline candidates:**
  1. *The board is the database.* ← **CHOSEN.** Shortest, most defensible, encodes the exact structural moat; works as a headline and a repo tagline.
  2. *Multi-agent engineering, in Markdown you can diff.*
  3. *Autonomous agents. Atomic locks. Durable memory. All in your repo.*
  Rationale for #1: the differentiator IS the storage model. It's a claim competitors literally cannot make. #3 is the strongest *supporting* line and is reused as the value-prop triad.

### Messaging hierarchy (each value prop → real feature or Phase-2 item)

**Headline:** The board is the database — a git-committed kanban board your AI agents run and remember.

| Value prop | Proof point | Backed by |
|---|---|---|
| **VP1 — Visible, diffable coordination state.** Your agents' board is committed markdown, reviewed in the same PRs as code. | `engineering-board/<project>/` tree + `BOARD.md` index + `GRAPH.yml` + `BOARD-ROUTER.md`; validated on every Write | **Existing** — `board-validate-entry.sh`, `board-session-start.sh`, `board-rebuild`/`board-graph` |
| **VP2 — Durable cross-session memory.** Recurring lessons promote into committed Learning entries (L###) that survive session boundaries. | `learnings-curator` promotes `pattern:` tags with recurrence ≥3 → `learnings/L###` | **Existing** — `board-curate-learnings.sh` |
| **VP3 — Collision-free parallel agents.** Atomic claim-locking lets multiple worker agents run without stepping on each other. | mkdir-based atomic lock, heartbeat, stale reclamation, cloud-sync detection | **Existing** — `board-claim-acquire/release/reclaim-stale.sh` (tested: `tests/claims/`) |
| **VP4 — Autonomous build pipeline.** Findings flow through a `tdd → review → validate` state machine, driven by the Stop hook. | Worker pipeline dispatches `tdd-builder`/`code-reviewer`/`validator` on `needs:` state | **Existing** — worker mode + `stop-hook-procedure.md` |
| **VP5 — Runs where you already are, and everywhere else.** Native Claude Code plugin **and** an MCP server for any MCP client. | Plugin (commands/agents/hooks/skills) + MCP tools over the same board format | Plugin **existing**; **MCP server existing** (shipped 1.2.0 — 11 tools over stdio) |

## 5. Name decision

**Keep `engineering-board`.** Research surfaced no naming conflict on the plugin/MCP side (competitors are Backlog.md, Flux, Agent-MCP, kanban-mcp, etc.; no "engineering-board" collision). The name is literal, SEO-legible, matches the committed `engineering-board/` directory it creates, and preserves existing links/marketplace identity (immutable once published). No rename.

## 6. SEO / discovery keywords

`claude code plugin` · `mcp server task board` · `git-committed kanban` · `multi-agent coordination` · `ai agent memory` · `autonomous software engineering` · `agent claim locking` · `cross-session agent memory` · `markdown kanban ai agents` · `claude code orchestration` · `tdd agent pipeline` · `ai code review agent` · `agent task queue mcp` · `human-visible agent state` · `persistent agent learnings`

Repo topics (set in LAUNCH): `claude-code`, `claude-code-plugin`, `mcp`, `mcp-server`, `ai-agents`, `multi-agent`, `kanban`, `agentic-workflow`, `tdd`, `developer-tools`.

## Citations (fetched live 2026-07-04)
- https://github.com/MrLesk/Backlog.md
- https://paddo.dev/blog/flux-kanban-for-ai-agents/
- https://github.com/rinadelph/Agent-MCP
- https://github.com/shinpr/claude-code-workflows
- https://github.com/eyalzh/kanban-mcp
- https://github.com/madebyaris/agent-orchestration
- https://github.com/bradrisse/kanban-mcp
- https://github.com/tcarac/taskboard
- https://github.com/anthropics/claude-plugins-official (→ https://clau.de/plugin-directory-submission)
- https://code.claude.com/docs/en/plugin-marketplaces
- https://registry.modelcontextprotocol.io/ · https://modelcontextprotocol.io/registry/quickstart
- https://smithery.ai/docs/build/publish · https://www.pulsemcp.com/use-cases/submit · https://glama.ai/mcp/servers · https://mcp.so/
- https://github.com/punkpeye/awesome-mcp-servers · https://github.com/hesreallyhim/awesome-claude-code

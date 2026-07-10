# IMPROVEMENTS — product discovery pass v4 (2026-07-10): the competitive parity audit

_Discovery only; nothing here is implemented. Every idea cites repo evidence or a
live-fetched competitor source (all competitor facts fetched 2026-07-10; traction
figures are snapshots and drift)._

## What changed since v3

v3 (2026-07-08) audited the **engine** — the coordination core under the product's
guarantees (E1–E13; headline: only claim-acquire is concurrency-safe). Those
findings stand and are *not* repeated here; E1–E4 remain the prerequisite for any
multi-agent claim this report leans on.

**This pass looks outward for the first time since 2026-07-04.** The mission:
compare engineering-board's **marketing presentation** and **product experience**
against top competitors, find the table-stakes gaps, then sharpen differentiation.
Four parallel research passes (a Backlog.md deep-dive; Task Master / Vibe Kanban /
beads; remaining rivals + new-entrant discovery; a marketing table-stakes benchmark
across category leaders) produced one overriding conclusion:

> **The field we compare ourselves against no longer exists.** Our README/landing
> comparison (built 2026-07-04) is aimed at the small end of a market whose top end
> moved: Claude Code shipped **native persistent Tasks + subagent memory**
> (commoditizing raw task CRUD), **beads** (~25k★) now ships durable memory *and*
> atomic claims as its headline, **Task Master** (~28k★, 1.5M npm downloads) became
> a company, **vibe-kanban** (~27k★) is *sunsetting*, and our table's named rivals
> (kanban-mcp 40★, Flux 92★, Agent-MCP) are dormant or stalled. Meanwhile every
> distribution/proof table-stake in the category — one-command install, download
> badges, a launch moment — is still missing on our side.

The board backlog and prior roadmaps (ROADMAP.md RM-1…17, v3's E1–E13) are
excluded except where a competitor finding *changes their priority* — noted inline.

## 1. Product snapshot

engineering-board is a git-committed markdown kanban board that Claude Code agents
fill in and work through themselves: a Stop hook passively captures findings each
turn, PM mode consolidates them into validated entries, worker mode drives each
entry through a `tdd → review → validate` state machine under an atomic claim
lock, and recurring lessons promote into durable `Learning` entries. It ships as a
Claude Code plugin (13 commands, 8 agents, 4 skills) and a zero-dependency python3
MCP server (11 tools) on the official MCP Registry, with a static, byte-deterministic
HTML board view republished to GitHub Pages on every merge. The thesis — **"the
board is the database"** — is plain markdown in the repo, reviewed in the same PRs
as code. It is v1.6.1, solo-built, dogfooded on its own live board. Its market sits
between git-markdown boards (Backlog.md), agent-memory substrates (beads,
claude-mem), AI task decomposers (Task Master), and — since January 2026 —
Claude Code's own built-in Tasks.

## 2. The field, refreshed (who actually matters now)

| Competitor | Traction (2026-07-10) | What it is | Threat to our claims |
|---|---|---|---|
| **Claude Code native Tasks + memory** (Anthropic, Jan–Feb 2026) | built into the host | Persistent tasks w/ dependencies, Ctrl+T board, `~/.claude/tasks/` cross-session; per-subagent `MEMORY.md` | Commoditizes raw task CRUD + memory-lite for our exact audience — **the** positioning question |
| **beads** (gastownhall, Yegge) | ~25k★, v1.1.0 Jul 2026, explosive | Git-versioned (Dolt) graph issue tracker as **agent memory**: `bd remember`/`bd prime`, atomic `--claim`, hash ids, `discovered-from` links, `bd ready` | Direct overlap on memory, claims, and even passive capture — our most substantive feature rival |
| **Task Master → Hamster** | ~27.8k★, 1.5M+ npm downloads | PRD→tasks decomposition, complexity analysis, research mode, TDD autopilot, 36 MCP tools, 10 editors | Owns the "structure for AI" intake lane; file-locking since Jan 2026 |
| **Backlog.md** (MrLesk) | ~6k★, v1.47.1 Jun 2026, very active | Markdown-native tasks + terminal/web kanban + MCP; milestones, comments, DoD checklists, fuzzy search, stats overview | Closest overall shape; wins on task-model richness, install channels, UI |
| **claude-mem** (thedotmack) | very large, v13 Jul 2026 | Hook-based per-session capture → compress → re-inject; Stop-hook capture like ours | The incumbent in hook-based passive memory capture |
| **vibe-kanban** (Bloop) | ~27.3k★ — **sunsetting** (Apr 2026) | GUI orchestrator, worktree-per-task | Exit validates the category's danger and frees positioning room |
| Gas Town / Claude Flow / spec-kit | 16k–119k★ | Orchestrators / spec-driven upstream | Adjacent, not board rivals — integration targets |
| Agent-MCP · Flux · kanban-mcp · claude-code-workflows | 1.3k / 92 / 40 / 628★ | Our current README comparison set | Stalled, tiny, dormant, or non-overlapping — **no longer the field** |

**Where we already meet or beat table stakes** (no action needed): acceptance
criteria (`Done when` ≈ Backlog.md AC/DoD), priorities + dependencies
(`priority`/`blocked_by`), archive/drafts (scratch inbox), local-first/offline/
zero-config (`/board-setup`), dogfooding proof (the live board — only Backlog.md
matches this), honest changelog + releases, MCP Registry listing, a security
posture (SECURITY.md + injection corpus) ahead of every rival checked.

**Marketing table stakes across category leaders** (benchmark of Backlog.md, Task
Master, vibe-kanban, Claude Flow, beads, CCPM): motion above the fold ✅ we have it;
copy-paste install blocks ✅; comparison table ✅ (rare — most leaders skip it);
**stars/downloads/version badges with real counts — we have none**; **one-command
install (npx/uvx-class) — ours needs `git clone`**; **a launch moment (Show HN
254pts for Backlog.md, 195 for vibe-kanban, Yegge's essay for beads) — we have
none**; **registry breadth (Smithery, awesome-lists) — prepared in
`.goal/LAUNCH.md` but never executed**.

## 3. Opportunity map (impact × effort)

| | **Low effort (S)** | **Medium (M)** | **Large (L)** |
|---|---|---|---|
| **High impact** | C2 native-Tasks answer · C9 proof badges | C1 comparison rebuild · C3 one-command install · C6 memory-story parity · C11 launch kit | — |
| **Med impact** | C4 board search/filter · C5 ready queue · C10 registry breadth | C7 entry-model parity pack · C8 non-Claude onboarding · C12 stats + coordination surface | — |
| **Focused** | C13 llms.txt + docs entry | — | — |

## 4. Top 5 quick wins (~a day or less each)

1. **C2 — answer "why not Claude Code's built-in Tasks?"** The single question every
   2026 visitor now asks first, and no surface answers it. One positioning block.
2. **C9 — proof badges.** Stars + release-cadence badges in README, numeric liveness
   on the landing trustband. Every leader has this; absence reads as abandonment.
3. **C4 — client-side search/filter in `board.html`.** ~60 lines of vanilla JS in
   the existing static page — parity with Backlog.md's filters without a daemon.
4. **C5 — a deterministic "ready" queue.** beads' `bd ready` is its most-loved
   command; ours is one derived filter away (we already parse `blocked_by`).
5. **C10 — execute the prepared registry submissions.** `smithery.yaml` exists;
   `.goal/LAUNCH.md` §2 lists the awesome-list/marketplace steps. Mostly human-action
   items — the report flags them as *still* undone three releases later.

## 5. Top 3 big bets

1. **Reposition for the 2026 field (C1 + C2).** Rebuild the comparison and the
   "why different" story around beads, Backlog.md, Task Master, claude-mem, and
   native Tasks — the honest-comparison franchise is the brand; today it's honest
   about a field that's gone. The surviving open lane (per the post-native-Tasks
   analyses) is exactly ours: **the repo-committed, PR-reviewable, team-visible
   board + opinionated pipeline** — but it must be claimed against the real rivals.
2. **Collapse install friction to one command and widen the funnel (C3 + C8).**
   PyPI/uvx (and optionally npm) for the MCP server, per-client setup for Codex/
   Gemini/Cursor, `AGENTS.md` emission at init. The category's gold standard is
   `npx vibe-kanban`; ours is `git clone` + an absolute path.
3. **Win the memory story on a hardened core (C6, gated on v3's E1–E4).** beads'
   tagline is literally "a memory upgrade for your coding agent." We have the more
   auditable memory design (committed markdown Learnings) — but it's gated behind
   PM-mode ceremony (ROADMAP RM-4) and has no explicit `remember` affordance. Ship
   `board_remember` + the ungated loop and the differentiation writes itself.

## 6. Full opportunity list

### C1 — Rebuild the comparison story around the real field
- **Tag/lens:** FIX · marketing / trust
- **Evidence:** `README.md:157-172` and `docs/index.html:266-286` compare against
  kanban-mcp (~40★, no activity since 2025), Flux (92★, no releases), Agent-MCP
  (stalled since Sep 2025), claude-code-workflows — while omitting beads (~25k★),
  Task Master (~27.8k★), claude-mem, and native Tasks entirely (verified: zero
  mentions repo-wide). The "durable memory: **No**" column is now false-by-omission —
  beads ships `bd remember`/`bd prime`/decay as its headline; its `bd update --claim`
  is atomic claim-locking; its `discovered-from` links are passive-capture-adjacent.
- **Proposal:** new comparison rows: beads, Backlog.md (keep), Task Master, native
  Claude Tasks, claude-mem; new columns that carve *our* ground: "state is
  PR-reviewable markdown" (beads: Dolt DB + JSONL export; native Tasks:
  `~/.claude/tasks/`, outside the repo), "opinionated tdd→review→validate pipeline",
  "published team-visible board". Keep the fairness note — it's the franchise.
- **Why it matters:** the honest-comparison table is our most distinctive marketing
  move (the benchmark found most leaders don't dare compare). Aim it at the real
  leaders or it curdles from honesty into misdirection.
- **Effort:** S-M · **Impact:** High · **Risks:** the new table concedes more cells —
  that's the point; honesty against giants reads stronger than dominance over ghosts.

### C2 — Answer "why not Claude Code's native Tasks?" everywhere positioning lives
- **Tag/lens:** NEW · marketing / positioning
- **Evidence:** Claude Code v2.1.16+ (Jan 2026) ships persistent tasks with
  dependencies, a Ctrl+T board, cross-session state in `~/.claude/tasks/`, opt-in
  shared lists; v2.1.33 adds per-subagent `MEMORY.md`. Grep of README/landing/
  BRAND/ARCHITECTURE: no mention (verified 2026-07-10). Post-native-Tasks analyses
  (paddo.dev "From Beads to Tasks") conclude raw task CRUD has no moat and
  third parties must differentiate on richer, team-visible surfaces.
- **Proposal:** a short "vs the built-in Tasks" block (README + landing FAQ): native
  Tasks are **per-user, per-machine, outside the repo** — invisible in PRs, invisible
  to teammates, no capture pipeline, no review states, no committed learnings.
  engineering-board is the **repo's** shared board. Position native Tasks as the
  on-ramp we compose with, not deny.
- **Why it matters:** it's the first objection in every 2026 evaluation; silence
  reads as either ignorance or evasion, and we have a genuinely good answer.
- **Effort:** S · **Impact:** High · **Risks:** none material; keep tone additive.

### C3 — One-command install: publish the MCP server to PyPI (uvx-able)
- **Tag/lens:** IMPROVE · reach / onboarding
- **Evidence:** the server is a single zero-dependency python3 file
  (`mcp-server/engineering_board_mcp.py`, 1457 lines) — ideally shaped for PyPI.
  Yet the documented path (`README.md:93-96`, `docs/index.html:305-310`) is
  `git clone` + an absolute path — the highest-friction install in the entire
  cohort benchmarked. Category standard: `npx vibe-kanban`, `npm i -g backlog.md`,
  `brew install beads`, Task Master's one-click MCP button.
- **Proposal:** publish `engineering-board-mcp` to PyPI; install becomes
  `claude mcp add engineering-board -- uvx engineering-board-mcp` (one line, no
  clone, no path). Wire the version into the existing release workflow
  (`release.yml`) beside the `.mcpb` asset; add the PyPI badge (feeds C9). Optional
  follow-up: an npm wrapper for `npx` parity.
- **Why it matters:** install friction is the top-of-funnel; every competitor
  audit (our own CRO.md included) has flagged it, and the field's bar is one command.
- **Effort:** M · **Impact:** High · **Risks:** version-coherence — `server.json`/
  `manifest.json`/`plugin.json` are digest-pinned in lockstep (`tests/version-coherence.sh`);
  extend the check rather than bypassing it.

### C4 — Client-side search + filters in `board.html`
- **Tag/lens:** NEW · UX / UI
- **Evidence:** `hooks/scripts/board-view.sh` renders a static, read-only page — no
  search, no filter (verified: flags are only `--stdout/--stamp/--link-base`). The
  self-hosted board already has 61+ bug cards. Backlog.md ships fuzzy search +
  label/status filters + keyboard shortcuts (web UI v1.45); its TUI filters by
  milestone; beads filters by label/assignee/status.
- **Proposal:** embed ~60 lines of vanilla JS in the generated page: a search box
  (title/id/affects/pattern) plus type/priority/status chips, all client-side —
  zero dependencies, still byte-deterministic, no daemon. The published GitHub
  Pages board gets it for free.
- **Why it matters:** the live board is our proof asset and our "richer surface"
  bet; at 60+ cards it's already past comfortable scanning.
- **Effort:** S-M · **Impact:** Med-High · **Risks:** keep the no-JS fallback (page
  currently works with JS disabled; filters should degrade gracefully).

### C5 — A deterministic "ready" work queue
- **Tag/lens:** NEW · helpfulness / smart defaults
- **Evidence:** worker selection skips only the *manual* `status: blocked`
  (`hooks/stop-hook-procedure.md:115`); nothing derives blockedness from
  `blocked_by` pointing at unresolved entries, and `board_list_entries` filters
  only `project/type/status/needs` (`mcp-server/engineering_board_mcp.py`) — no
  unblocked-work query. beads' `bd ready` (deterministic, ~10ms, offline) is its
  flagship agent affordance; Task Master added `--ready`/`--blocking` in v0.42.
- **Proposal:** a `ready` filter (entries whose `blocked_by` targets are all
  resolved) in `board_list_entries` + a `ready:` count in `board_status`, and make
  worker/`/board-run` selection consume it. SessionStart already computes the
  blocking map in one python pass (`board-session-start.sh`) — reuse that logic.
- **Why it matters:** it upgrades `blocked_by` from decoration to coordination —
  and prevents workers claiming entries that can't actually proceed.
- **Effort:** S-M · **Impact:** Med-High · **Risks:** semantics for dangling ids —
  follow the existing validator's treatment.

### C6 — Win the memory story: `board_remember` + the ungated learnings loop
- **Tag/lens:** IMPROVE · retention / differentiation
- **Evidence:** beads: `bd remember "insight"` + `bd prime` (inject into prompts) +
  semantic decay — marketed as "a memory upgrade for your coding agent"; claude-mem
  captures per-session via the same Stop-hook mechanism we use and re-injects
  automatically. Ours: Learnings promote only via PM-mode consolidation
  (RETENTION R1 / ROADMAP RM-4 — "the moat is gated behind the mode dance") and
  there is no explicit remember affordance in the 11 MCP tools or 13 commands
  (verified tool list, `engineering_board_mcp.py`).
- **Proposal:** (a) `board_remember` MCP tool + `/board-remember` command writing a
  learning-candidate directly (bypassing recurrence-≥3 for explicit user intent);
  (b) execute RM-4 (auto-consolidate outside PM mode) so the loop accrues for
  everyone; (c) say "memory" out loud in marketing — our Learnings are the *only*
  PR-reviewable, plain-markdown agent memory in the field (beads: Dolt; claude-mem:
  SQLite+Chroma).
- **Why it matters:** memory is the category's hottest claim and we hold the most
  auditable implementation of it — currently our least-accessible feature.
- **Effort:** M · **Impact:** High · **Risks:** RM-4 is architecturally hot — land
  v3's E-series hardening + RM-16 first (same gating ROADMAP already imposes).

### C7 — Entry-model parity pack: comments + parent/subtask links
- **Tag/lens:** NEW · product / collaboration
- **Evidence:** entry frontmatter supports `id/type/title/status/priority/affects/
  needs/pattern/blocked_by` (sample: `engineering-board/eb-self/bugs/*.md`) — no
  comments, no parent/child. Backlog.md added task comments with authorship
  (v1.46.0, Jun 2026) and has parent tasks; Task Master has subtasks; beads has
  hierarchical hash ids (`bd-a3f8.1`) and threaded messages.
- **Proposal:** (a) a `## Comments` body convention + `board_update_entry` comment
  append (author + timestamp — trivially diffable); (b) a `parent:` frontmatter
  field rendered as grouping in BOARD.md/board.html. Skip milestones/sprints for
  now — no evidence of need at current board scale.
- **Why it matters:** multi-agent *and* human-in-the-loop review both want a place
  to talk on the card; today the only channel is editing prose sections.
- **Effort:** M · **Impact:** Med · **Risks:** schema additions touch
  `board-validate-entry.sh` + rebuild + view — one coherent PR, per L005.

### C8 — Non-Claude agent onboarding: per-client setup + `AGENTS.md` emission
- **Tag/lens:** IMPROVE · reach
- **Evidence:** Backlog.md generates CLAUDE.md/AGENTS.md/GEMINI.md/Copilot files
  (`backlog agents --update-instructions`) and documents one-line MCP setup for
  Claude Code, Codex, Gemini CLI, Kiro; beads ships `bd setup <tool>` for 9+
  clients and auto-creates `AGENTS.md`. Our `mcp-server/README.md` documents Claude
  Code and Claude Desktop only, and `board_init` emits no agent-instruction file
  for non-hook clients (verified tool schema).
- **Proposal:** `board_init`/`board_setup` optionally emit an `AGENTS.md` stanza
  (how to capture findings, claim, and update entries via the MCP tools — the
  hook-free protocol); add Codex CLI / Gemini CLI / Cursor setup blocks to the MCP
  README and landing install card.
- **Why it matters:** VP5 ("runs everywhere else") is currently documentation-deep
  only for Claude surfaces; the MCP funnel is our only non-Claude growth channel.
- **Effort:** S-M · **Impact:** Med-High · **Risks:** keep the emitted stanza short
  and pointer-like; it must not drift from the tool schemas (add a lint).

### C9 — Proof badges + liveness counters on README and landing
- **Tag/lens:** FIX · marketing / proof
- **Evidence:** `README.md:15-20` badges: website, license, version, tests, plugin,
  MCP — **no stars, no downloads, no release cadence**; `docs/index.html:249`
  trustband has zero numbers. Benchmark: every leader shows version + downloads +
  stars (Backlog.md, Task Master, beads, Claude Flow), and leaders restate counts
  in prose ("25k+ stars, 1.5M+ downloads" — tryhamster.com).
- **Proposal:** add GitHub stars + latest-release(+date) badges now; PyPI/npm
  downloads badges after C3; trustband gains "N releases · vX.Y.Z (Mon YYYY)".
  At small absolute numbers, *cadence* is the honest proof — lead with it.
- **Why it matters:** the 30-second outsider scan currently finds no liveness
  signal at all; in this category that reads as abandonware.
- **Effort:** S · **Impact:** Med (multiplies every other marketing asset) ·
  **Risks:** none.

### C10 — Execute the prepared registry/listing breadth
- **Tag/lens:** IMPROVE · distribution
- **Evidence:** `mcp-server/smithery.yaml` has existed since v1.4.0; `.goal/LAUNCH.md`
  lists prepared submissions (Claude community marketplace, awesome-claude-code,
  awesome-mcp-servers) — none executed three releases later. Backlog.md/Task
  Master/beads each appear on 3–5 registries + multiple awesome-lists; even
  dormant kanban-mcp outranks us in directory search because of syndication.
- **Proposal:** publish to Smithery; file the awesome-claude-code issue and the
  awesome-mcp-servers PR; submit the community-marketplace form. Flag clearly:
  these are mostly **human-account actions** — the repo work is done.
- **Why it matters:** directories are where MCP users actually search; our only
  listing (MCP Registry) syndicates to some but not the highest-traffic lists.
- **Effort:** S (human) · **Impact:** Med · **Risks:** none.

### C11 — Launch kit: Show HN + the "after vibe-kanban" wedge
- **Tag/lens:** NEW · community / growth
- **Evidence:** every comparable's audience traces to one launch moment: Backlog.md
  Show HN (254 pts), vibe-kanban Show HN (195 pts), beads via Yegge's essay +
  thread. We have none (no HN/Reddit/PH footprint found). Timely wedge: vibe-kanban
  (~27k★) announced sunset Apr 2026 — "standalone agent-kanban GUIs died; the board
  that lives in your repo doesn't need a company to survive" is a true, resonant
  line (we are MIT, zero-dep, no server).
- **Proposal:** prepare the launch asset pack: the Show HN draft (lede: "the board
  is the database"), the real-screenshot + demo GIF assets (this *is* ROADMAP
  RM-10/RM-11 — competitor evidence upgrades their priority), and a short "where
  vibe-kanban users land" comparison page. Launch after C1/C2/C3/C9 so the landing
  survives the traffic's 30-second scan.
- **Why it matters:** distribution is our widest gap vs. every leader, and launch
  moments are how this category's winners all got their start.
- **Effort:** S-M (assets; the post itself is a human action) · **Impact:** High
  variance · **Risks:** launching before C1/C2 lands the traffic on a stale story.

### C12 — Stats + coordination surface (the "richer surface" bet, consolidated)
- **Tag/lens:** IMPROVE · engagement / synergy
- **Evidence:** Backlog.md ships `backlog overview` (project-health TUI dashboard);
  beads v1.1.0 added `bd metrics`. Ours: no stats surface (ROADMAP RM-6 already
  proposes `/board-stats`); coordination state is logged but invisible (v3's E12:
  `_claims/`, `_reclaimed.log`, `active-workers.json` never rendered). The
  post-native-Tasks analyses name team-visible dashboards as the surviving
  third-party lane — and our published board is already that surface.
- **Proposal:** one pass, two panels on `board.html` + `/board-view`: **Stats**
  (open/resolved by type, resolution velocity, learnings count — RM-6) and
  **Coordination** (current claims, recent reclaims, active workers — E12). Pure
  reads over data that already exists on disk.
- **Why it matters:** converts the live board from a static index into the
  observable, team-visible dashboard the field's survivors differentiate on.
- **Effort:** M · **Impact:** Med · **Risks:** low — read-only.

### C13 — `llms.txt` + a docs entry point above the fold
- **Tag/lens:** NEW · reach / friendliness
- **Evidence:** beads, vibe-kanban, and Task Master all publish `llms.txt` /
  agent-consumable docs; leaders put "Read the docs" as a hero CTA (Task Master,
  vibe-kanban). Our landing's docs links live in the footer (`docs/index.html:327-338`);
  no `llms.txt` exists (verified).
- **Proposal:** generate `docs/llms.txt` (product summary + README + MCP tool
  reference, plain text) in the pages sync; add a "Docs" link beside "Live board"
  in the landing nav. For a product whose *users are agents*, agent-readable docs
  are on-brand table stakes.
- **Effort:** S · **Impact:** Low-Med · **Risks:** none.

## 7. Ideas generated and cut (so they stay cut)

PRD parsing / task expansion (Task Master's lane — our intake thesis is *capture,
not spec*; compose, don't compete) · a live web server / drag-drop UI (contradicts
the no-daemon, committed-artifact stance that survived vibe-kanban's death) · a TUI
(large surface, off-thesis) · milestones/sprints (no evidence of need at current
scale) · Dolt/SQLite storage (the antithesis) · Discord (premature below ~2k★;
Discussions suffice — Backlog.md agrees) · Ed25519 agent identities (niche) ·
cross-branch state resolution (niche) · `onStatusChange` shell hook (generic) ·
one-click Cursor deep-link (sequenced after C3) · token-cost table (fold into docs
later).

## 8. Suggested sequence — if only three ship first

1. **C1 + C2 — tell the truth about 2026 (one PR).** The comparison rebuild and the
   native-Tasks answer are the same job: repositioning against the real field. It
   is cheap, it is urgent (every day the current table stands, the honesty
   franchise erodes), and everything else — launch, badges, funnel — lands on top
   of this story.
2. **C3 (+C9) — one-command install with proof attached.** PyPI/uvx collapses the
   worst funnel step in the cohort; the badges ride along in the same release.
3. **C11 — the launch, prepared then fired.** Assets (real screenshot, GIF — RM-10/11)
   plus the Show HN draft and the vibe-kanban-wedge page; fire only after 1 and 2
   are live so the traffic converts.

Product-depth work (C4, C5, C6, C7, C8, C12) then proceeds behind the repositioned
story — with C6 still gated on v3's E1–E4 engine hardening, exactly as ROADMAP
already sequences RM-4.

---

_Report only — no product code changed. **Which items should I build?** My
recommendation: C1+C2 immediately (one honest-repositioning PR), C9 the same day,
then C3 as the next release's headline. C11's launch kit is the highest-leverage
use of the month after that — and the engine work (v3 E1–E4) remains the
prerequisite under everything multi-agent._

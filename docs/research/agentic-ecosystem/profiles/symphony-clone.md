# Profile — symphony-clone (Symphony)

> Snapshot 2026-06-08. Source: public repo `GhostlyGawd/symphony-clone` (cloned, read directly).

**Identity:** a **Claude-Code-native orchestrator** that watches an issue tracker
and gives every open ticket its own isolated workspace + a headless `claude` agent,
running them in parallel until each leaves the active states. *"Turn an issue board
into autonomous, isolated implementation runs… You manage work, not coding agents."*
It is an explicit **independent re-implementation of OpenAI's open-source Symphony
spec** (`openai/symphony`, originally for Codex), retargeted to Claude on a
subscription — *"a clean-room implementation"* per NOTICE.

**Repo / version / lang / status:** `GhostlyGawd/symphony-clone` (public) ·
**v0.1.0** (`@ghostlygawd/symphony`) · Node.js ≥18, ESM, **zero deps** · Apache-2.0 ·
shipped/published to npm; runs as a long-lived CLI daemon or in Docker, drives the
subscription `claude` CLI (no `ANTHROPIC_API_KEY`).

## Core mental model
The **tracker is the state machine, the coding agent is the worker, the PR (or a
review state) is the output.** A polling orchestrator reconciles the board against
running work each tick and dispatches eligible issues. Crucially: **"Handoff, not
Done."** A run ends at a *review* state (e.g. `In Review`) that the agent sets on
itself — the loop stops the moment an issue leaves the active states. Reactive to
the board; it executes a planned queue, it doesn't manufacture its own work.

## State substrate
**No database — runtime state is in-memory; the tracker is the only durable store.**
`Orchestrator` holds `running` / `claimed` / `retry` / `completed` Maps + cumulative
`codexTotals` (`orchestrator.js:42-46`); *"There is no database… the tracker is the
durable state, not Symphony"* (`docs/architecture.md:53`). Recovery after a crash =
startup terminal-workspace cleanup + fresh polling + re-dispatch (no resume; durable
runtime state is open backlog **BL-9**). The **default tracker is git-native
markdown**: one issue per file under `.symphony/issues/` with YAML front matter
(`identifier/title/state/priority/labels/blocked_by`) + a markdown body; *state
transitions are just edits to the `state:` field* the agent performs (`local.js`).
Pluggable to GitHub (state ← a `status:<state>` label) or Linear (workflow states).
Per-issue **workspaces are plain directories** under `workspace.root`, gitignored.

## Components
- **CLI: 7 commands** (`cli.js`) — `init`, `start` (`--once`/`--port`/`--host`/
  `--verbose`), `status`, `validate`, `doctor`, `move <id> <state>` (handoff helper),
  `version`/`help`. Single bin `bin/symphony.js`.
- **~10 core src modules** (~4k LOC): `orchestrator.js` (scheduler), `runner.js`
  (one worker attempt), `agent/claude.js` (the Claude Code adapter), `workspace.js`,
  `workflow.js`+`defaults.js` (config), `template.js` (Liquid-ish prompt renderer),
  `yaml.js` (mini-YAML), `server.js` (dashboard), `trackers/{local,github,linear}.js`.
- **Worker model: ONE role** — a generic "autonomous engineer" `claude` process per
  issue. No subagents, no reviewer/validator panel, no MCP server, no skills.
- **Config: one file, `WORKFLOW.md`** — YAML front matter (tracker/polling/workspace/
  hooks/agent/claude/server/logging) + a markdown prompt template; **hot-reloaded** on
  change. Lifecycle hooks (`after_create`/`before_run`/`after_run`/`before_remove`).
- **Tests:** ~11 suites, `node --test`, zero deps, mock-`claude` fixture (94 tests, 1
  skipped). Gated live test behind `SYMPHONY_LIVE_TEST=1`. CI is **manual-only**
  (`workflow_dispatch`, "out of Actions minutes"); the real gate is a **pre-push hook**.

## Orchestration model
**External, always-on polling loop — and the workers are HEADLESS, not observable.**
`Orchestrator.start()` schedules `tick()` every `polling.interval_ms` (default 30s;
scaffold 10s). Each tick: (1) hot-reload `WORKFLOW.md`; (2) **reconcile** running
issues — stall-detect (`now − lastActivity > stall_timeout_ms`, default 5m → abort +
retry) and refresh tracker state (terminal → stop+clean, active → refresh snapshot);
(3) process the **retry queue** (continuations + exponential backoff); (4) validate
config (invalid → pause dispatch, keep reconciling); (5) **dispatch** eligible
candidates within concurrency. Each worker (`runner.js`) ensures a workspace, runs
`before_run`, then loops turns: spawns **`claude -p --output-format stream-json
--verbose [--resume <session>] --dangerously-skip-permissions`** (`agent/claude.js:147`),
delivers the prompt on **stdin**, parses the JSON event stream, and **re-checks tracker
state between turns** until *"the issue leaves the active states or `max_turns` is hit."*
Key facts for the EB Conductor comparison:
- **Headless `claude -p`, period.** There is **no tmux, no PTY, no `--add-dir`-attach,
  no interactive session** anywhere in `src/` (grep-confirmed). Observability is a
  **read-only fleet dashboard** (`server.js`, aggregate snapshot, auto-refresh 2s) —
  you watch *counts/turns/cost*, you cannot attach to or step into a worker.
- **No git worktrees.** Isolation is a sanitized per-issue **directory**; the shipped
  repo-seeding strategy is a full `tar` copy. First-class worktrees are **punted to
  backlog BL-17** (the engine "validates a worktree at the path" only incidentally).
- **Parallelism:** `max_concurrent_agents` (default 10) + optional per-state caps;
  atomic-ish claiming via the in-memory `claimed` Set (single process, so no FS lock).
- **"What to run next":** sort by priority↑, then `created_at`↑, then identifier;
  **blocker gating** skips an issue if any `blocked_by` is still an active candidate.
- **Human-in-loop:** the **handoff/review state IS the gate** (the agent moves the
  issue to e.g. `In Review`; the human reviews/merges). Multi-turn continuation runs
  **on one resumed Claude session** — i.e. *no* "one bounded round then die" boundary.

## Review / verification
**None built in.** There is no reviewer agent, no validator, no independent
verification, no trust calibration. Quality is delegated entirely to (a) the prompt
("run the project's tests/build and make them pass") and (b) the **human at the review
state**. The `github-pr` example pushes a branch and opens a PR via `gh` as the
artifact; the PR is the review surface.

## Falsifiability stance
**Not enforced — the weakest position of the siblings.** The LLM is never stopped
from hand-waving: "done" is detected purely by **tracker state leaving the active set**
(`runner.js:129-130`), which the agent *self-asserts* by editing `state:`. No evidence
anchor (cf. EB's transcript substring-match), no runnable-check gate (cf. AE's
`validate_spec`), no acceptance criteria in the schema. The only backstops are the
turn/stall budgets and the downstream human review gate.

## Distinctive design decisions
- **Subscription-native, API-key-free** by design — drives the same `claude` CLI you
  use interactively; the init event reports `apiKeySource: "none"`. Sets `IS_SANDBOX=1`
  for root containers so `--dangerously-skip-permissions` is honored.
- **Zero runtime/dev dependencies**; faithful, spec-mapped re-implementation (README
  ships a "How this maps to OpenAI's Symphony" table).
- **Config-as-one-markdown-file** with hot reload; prompt is a Liquid-ish template.
- **The container IS the trust boundary** — Dockerfile + compose ship the sandbox;
  `bypassPermissions` is gated on "isolated envs only."
- **Mobile-friendly tokened dashboard** (cookie login, refuses non-loopback bind
  without a token) — observability of the *fleet*, watchable through a tunnel.
- **Crash-safe-by-statelessness:** failures become retries; the tracker reconstructs.

## Strengths / gaps (for consolidation)
- **Strengths:** clean always-on reconcile loop (poll → reconcile → retry → dispatch)
  that actually ships; subscription-native headless execution; bounded concurrency +
  exponential-backoff + stall detection + dynamic reload; pluggable trackers with a
  git-native markdown default; zero-dep, readable, container-sandboxed.
- **Gaps:** **no review/verification, no falsifiability gate** (quality is all prompt +
  human); **headless black-box workers** (no attach/step-in); **no git worktrees** (only
  directory isolation; full-tar seeding doesn't scale to monorepos — BL-17); **in-memory
  state** (no mid-flight resume — BL-9); scheduler **ignores labels** (BL-14) and has no
  file-level conflict awareness; **no self-improvement loop**; v0.1.0.

## Consolidation notes
Carry forward: the **board-as-control-plane reconciliation tick** (poll → reconcile →
retry → dispatch with stall detection + backoff), the **subscription-native `claude`
adapter** (stdio prompt + `stream-json` parsing + session-resume + rate-limit capture),
**pluggable trackers** with a git-native markdown default, and the **handoff-to-review
gate** ("never auto-merge"). The `claude/stream-json` adapter is the most directly
reusable artifact.

**What it teaches the engineering-board Conductor RFC 0001:** symphony-clone is the
**most complete prior-art match** to RFC 0001 — same skeleton (external always-on loop,
tracker/board as state machine, isolated per-issue workspace, restart-on-stall, stop at
a human-review handoff) — but it makes the **opposite call on the two bets the RFC
stakes its novelty on**, so it's a precise contrast:
- **Worker model.** symphony-clone is **headless `claude -p`** with only a fleet
  dashboard for "observability." RFC 0001 explicitly rejects that black box for
  **attachable interactive tmux sessions**. symphony-clone proves the headless path is
  cheap and shippable today; it gives the RFC zero help on the hard part (the
  tmux/PTY/attach substrate it lifts from claude-squad instead). Net: it validates the
  *loop*, not the *observable-worker* thesis.
- **Round boundary.** symphony-clone has **no "one bounded round then die"** — it runs
  multi-turn on a single *resumed* Claude session until the issue leaves the active
  states, with continuity living **inside** the session. RFC 0001 wants the opposite
  (small per-round context; continuity reconstructed from durable state via pickup
  prompts). symphony-clone shows the simple alternative works but is the design the RFC
  is deliberately avoiding for context hygiene + containment.
- **Done-detection.** symphony-clone's signal is **"tracker state left the active set"**
  (agent self-edits `state:`), re-read each turn/tick — exactly the "board frontmatter
  field" option RFC 0001 lists as open, proven viable. It needs **no machine-readable
  outcome marker** because the worker mutates the durable board directly; that is a
  concrete, working answer to RFC 0001 §10's open round-outcome question — *if* you
  accept self-asserted completion with no falsifiability/evidence gate.
- **Worktrees + concurrency.** symphony-clone confirms RFC 0001's worry: per-issue
  isolation **without** worktrees and **without** file-level conflict awareness (it has
  neither) is the gap; its own BL-17 reaches for worktrees, validating the RFC's choice
  to build on worktrees from the start.
- **Crash recovery.** symphony-clone's **stateless re-poll** recovery is simpler than
  RFC 0001's supervision table; the tradeoff (cold re-dispatch from turn 1, lost
  backoff timers) is exactly what RFC 0001's durable supervision avoids.

# Profile — harness-sdd

> Snapshot 2026-06-08. Source: public repo `GhostlyGawd/harness-sdd` (cloned, read directly).

**Identity:** a **drop-in spec-driven-development (SDD) harness** — a bundle of
soft rules + hard git gates you copy into *another* repo to make an AI "build from a
written spec instead of from vibes." *"That bundle — the rules the AI reads (soft)
plus the hooks that block bad commits (hard) — is the 'harness.'"* The repo ships no
application code; **the repo *is* the machinery.**

**Repo / version / lang / status:** `GhostlyGawd/harness-sdd` (public) · no release
tag (constitution **v1.1.0**; bundled sample CLI v0.1.0) · **POSIX `sh`** machinery +
**Python 3 stdlib** hooks + a tiny **TypeScript/Node** dogfood CLI · **Apache-2.0** ·
shipped & self-hosting — all 11 specs `Status: done`, built through its own loop
(GitHub labels it "Shell"; truth = sh-dominant).

## Core mental model
The spec is the source of truth; code is a derived, regenerable artifact. A planner
**drives** PRD → SPEC → PLAN in one continuous pass (clarifying inline), stops at the
**one** hard human gate (**ALIGN**, where interfaces lock), then breaks out tasks; a
builder implements one task at a time TDD; a reviewer tries to prove it wrong.
*"Enforce with machinery, not prompts"* — anything that can be a deterministic gate
**must** be one. Directed, plan-driven build (the opposite of EB's reactive capture).

## State substrate
**Markdown files are the database — committed, git-diffable, hand-editable, zero
runtime deps.** Feature contracts live in `specs/<feature>/{spec,plan,tasks}.md`; the
`spec.md` carries a **forward-only `Status:` state machine** (`draft → clarifying →
ready → locked → building → done`) plus an `Aligned:` sign-off line. `BACKLOG.md` is a
gated table of surfaced-but-unchosen ideas (id + status). `constitution.md` is the
versioned root authority. The only typed structure is the JSONL emitted at **runtime**
and **gitignored**: per-unit run-logs at `evidence/<TID>/run-log.jsonl`, gate decision
traces under `evidence/gate*/`, and `.claude/runtime/session-baseline.json`. Anchors at
the **legible end of the markdown↔typed-DB axis**, alongside EB.

## Components
- **3 subagents** (`.claude/agents/`): `sdd-planner` (`tools: Read,Grep,Glob,Write,Edit`
  — writes only `specs/`), `sdd-builder` (+`Bash`), `sdd-reviewer` (read-only:
  `Read,Grep,Glob,Bash`). No skills directory; reuses the user's global `code-review`.
- **Hooks (4 events, `.claude/settings.json`):** SessionStart (`housekeeping.sh` +
  `record-session-baseline.sh`) · PreToolUse(Bash → `inflight-guard.py`) ·
  PreToolUse(Agent|Task → `guard-subagent-spawn.py`) · PostToolUse(Bash →
  `refresh-session-baseline.sh`) · **Stop** (`backlog-nudge.py`, advisory-only).
- **~38 scripts** (`scripts/`): `gate.sh` (full boundary gate) + `gate-fast.sh`
  (scoped inner-loop), **16 `check-*.sh`** self-eval harnesses, `run-wave.sh`
  (~925-line wave engine) + **12 `lib/*.sh`** (`worker-contract`, `wave-isolation`,
  `wave-review-loop`, `wave-consolidation`, `wave-runlog`, …), 5 Python/sh hooks.
- **1 MCP server** (`.mcp.json`): Linear (HTTP) — **optional, off by default, never a
  gate**; one-way repo→Linear mirror.
- **11 specs**, all `done`; `tests/fixtures/` = **42 pass/fail golden case dirs**.
  Only real code = the **`spec-status` CLI** (4 `.test.ts`, 68 tests) dogfooded to arm
  the language gate.

## Orchestration model
**A deterministic POSIX-sh wave engine + an observable coordinator session — NOT
headless `claude -p`.** `run-wave.sh` enforces a **locked-spec precondition** (refuses
pre-ALIGN, never advances `Status:`), computes the runnable **`[P]` wave** (parallel-safe
tasks with satisfied `depends:`), and drives a per-unit pipeline in its **own git
worktree on `wave/<slug>/<TID>`**: implement (TDD) → two-reviewer fix-loop →
commit-then-amend → visual e2e evidence → unit PR → integration branch → **one final
no-squash PR to `main` (Gate B, human merge)**. Crucially, **the shell engine cannot
spawn Claude subagents — only the coordinator (the main, attachable session) does**
(discovered mid-build: *"subagents cannot spawn subagents"*). So workers are
**observable Task/Agent subagents**, dispatched in worktrees (`isolation: worktree`),
**not** a black-box `claude -p` fleet. **v1 is single-unit** (singleton-before-fan-out);
concurrent fan-out is deferred to **B14**. Two human gates (ALIGN + final PR); deliberate
non-goal: *"NOT chasing fire-and-forget autonomy."*

## Review / verification
**Coordinator-orchestrated, anti-self-grading.** Per unit, the coordinator spawns the
implementer, then **two independent read-only reviewers that measure different things**
— `code-review` (correctness bugs) + `sdd-reviewer` (spec conformance) — which may run
concurrently; a unit is clean only when **both** pass. On findings, a fresh `sdd-builder`
**fixer amends the same commit** (gate re-runs on every amend), looping under a
**stall-guard budget** → `escalated` on exhaustion. Verification floor = `scripts/gate.sh`
must pass in every worktree (inherited via `core.hooksPath`); the visual e2e recording is
evidence on top.

## Falsifiability stance
Enforced at the **commit gate** (git pre-commit hook + CI — the same `gate.sh`), the
hardest-edged of the lifecycle: `check-specs.sh` fails any spec at `ready`+ that still
carries a `[NEEDS CLARIFICATION]` marker; `check-status.sh` fails a `Status:` that
doesn't match its artifacts (plan at `ready`+, `Aligned:` at `locked`+, tasks at
`building`+); `check-backlog.sh` fails an invalid/duplicate or dangling-pointer backlog
row. The planner's *"clarify until nothing is vague"* discipline is the soft front-end;
the gate is the deterministic backstop (*"a failing gate is backpressure: fix and redo,
never bypass"*). It is honest about the split: chat-blind behavioral rules (same-turn
capture, no-state-in-prose) stay agent contracts, not gates — *"claiming more than that
would be gate theater."*

## Distinctive design decisions
- **Harness-as-product, not engine-as-product:** the deliverable is a copy-into-your-repo
  bundle; the README is written *to be executed by an AI installer.*
- **One hard human gate (ALIGN), continuous everything else** — clarification and the
  commit gate are continuous; the lock is the single stop.
- **Determinism-over-trust** taken to a gate-of-gates: 16 `check-*.sh` + 42 golden
  fixtures prove the gates themselves still catch their failure modes (anti-gate-theater).
- **Two-profile gate** (`fast-gate-execution`/`gate-profile-split`): scoped seconds-long
  inner loop vs full boundary gate — fail-safe degrades to full on unknown git state.
- **In-flight work is sacred:** two `PreToolUse` guard hooks (`inflight-guard.py`,
  `guard-subagent-spawn.py`) deny/ask on destructive git ops and unsafe subagent spawns;
  a `deny` posture (because the session runs `bypassPermissions`, where `ask` auto-allows).
- **Observable-by-default / no black boxes:** every feature must emit a durable local
  run-log; the wave engine re-reads each unit's log post-exit to *prove* durability.
- **Custom layering lint:** `eslint.config.js` + `eslint-resolver-layering.cjs` turn
  ARCHITECTURE.md's one-directional dependency rule into an `error`-level
  `import/no-restricted-paths` gate (the tiny resolver maps NodeNext `./x.js` → `x.ts`
  so the rule fires on real TS — otherwise it would silently never trigger).
- **Self-improvement is a stated principle, not a loop:** constitution §10 *"every
  recurring agent mistake becomes a new line in a rules file or a new gate"* is **manual**
  — there is no automated retro→pattern→prompt-rewrite (the maturity-ladder doc parks
  L5/L6 as backlog aspirations, B3/B4).

## Strengths / gaps (for consolidation)
- **Strengths:** portability (drop-in for any repo, tool-agnostic via `AGENTS.md`);
  gate-of-gates rigor with golden fixtures; a *built* worktree orchestrator that is
  **observable**, not headless; commit-time falsifiability; deterministic git-safety
  guards; the singleton-before-fan-out discipline; markdown legibility + zero deps.
- **Gaps:** markdown can't *structurally* enforce invariants (no typed graph); the wave
  engine ships **single-unit only** (the wall-clock win, B14, is deferred); no closed
  self-improvement loop; no typed knowledge/memory across features; language gates are
  placeholders until a stack lands; the rich review loop is driven from RECORDED/STUB
  verdicts in the gate (real-agent dispatch is coordinator runtime, not under test).

## Consolidation notes
Carry forward: the **observable coordinator-spawns-subagents-in-worktrees** model (a
third worker point distinct from EB's RFC and AE/AEM's headless `claude -p` — it *built*
worktree orchestration without the black box), the **gate-of-gates + golden-fixture**
self-eval discipline, **commit-gate falsifiability** (`check-specs`/`check-status`), the
**deterministic git-safety guard hooks**, **singleton-before-fan-out** as a staging law,
and the **harness-installer** packaging idea. It is the cleanest worked answer to fork
#2 (worker observability) and reinforces fork #1's legible/markdown pole; its missing
pieces (typed substrate, self-improvement loop) are exactly what AE supplies.

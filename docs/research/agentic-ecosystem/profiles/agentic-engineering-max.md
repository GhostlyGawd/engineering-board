# Profile — agentic-engineering-max (AEM)

> Snapshot 2026-06-08. Source: **public** `agentic-engineering-max` repo (a
> leak-gated `git subtree split` of the private `Dev_006`). Bleeding edge in
> `Dev_006` may be ahead.

**Identity:** a *"Plan, build, review"* multi-agent **build factory** — a
scientific-method plan interviewer feeds a 3-department (PM / worker / reviewer)
execution system with atomic task claiming and an epistemic review panel, kept
honest by an auto-written **state surface** with git-level drift detection.

**Repo / version / lang / status:** `GhostlyGawd/agentic-engineering-max` (public)
· **v2.4.0** (8 releases, 2026-05-20→05-30) · PowerShell / pwsh 7 (Win + Linux) ·
MIT · the most productized of the three.

## Core mental model
The **plan→build→review loop**, run as **concurrent terminals**: plan-interviewer
(scientific method, falsify hypotheses, 100%-confidence scorecard gate) →
`prd-writer` → `spec-writer` → atomic task board → parallel workers → reviewer →
done. State surfaces auto-write; drift checks catch when they drift from reality.

## State substrate
**Markdown task files + a web HUD.** `task-NNN.md` (YAML frontmatter is
authoritative) · `task-board.md` (regenerated, never hand-edited) · `.lock`
siblings · `plan-state.md` · README mirror · append-only `plan-ledger.md`
(strikethrough versioning) · `.state-auto-log`. Plus a **Web HUD control plane**
at `http://127.0.0.1:8787` (`webui/`, vanilla HTML/CSS/JS, Loops/Board/Gates/Logs).

## Components
- **11 agents** — 8 `epistemic-*` stance agents + `prd-writer`, `spec-writer`,
  `wave-closer` (writers `model: opus`; epistemic agents Read/Grep/Glob/WebFetch).
- **10 skills** (no `commands/` dir; skills *are* the slash commands):
  `plan-interviewer`, `task-create`, `aem-init`, `aem-doctor`, `pm`, `worker`,
  `reviewer`, `launch-build`, `board`, `unblock`.
- **25 scripts** — `orchestrator-loop.ps1`, `headless-{worker,reviewer,pm,pusher}-loop.ps1`,
  `build-board`, `sweep-stale-locks`, `triage-intake`, `control-plane-web`, …
- **16 test scripts** (custom pwsh harness) · `webui/` · `assets/` · `docs/`.
- **Hooks (`hooks/hooks.json`; root `settings.json` is empty `{}`):** SessionStart
  → `claude-context-inject` + `state-writer-sweep` · SessionEnd → `state-writer` ·
  UserPromptSubmit → `state-drift-check` (**7 drift checks A–G** as
  additionalContext on every prompt) · git **pre-commit** (via `core.hooksPath`,
  blocks orphaned ledger-only commits). **No Stop hook** (orchestration is
  external). All `pwsh -NoProfile -File`, **no `-ExecutionPolicy Bypass`**.

## Orchestration model
**External deterministic adaptive controller** `orchestrator-loop.ps1` (~30s
tick): regen board → sweep stale locks → triage-intake → compute claimable queue
width → count live `.beat` heartbeats (TTL 180s) → spawn
`min(queue, cap) − live` headless agents (**max 4 workers / 2 reviewers**) → reap
dead → **dormancy on drain** (poll wake-sentinels). Workers are **headless
`claude -p --dangerously-skip-permissions`** in separate terminals; observability
via the web HUD. PM is a redundant, decoupled escalation narrator. **Atomic
claim:** `[IO.File]::Open(CreateNew)` + `FileShare.None`, body written through the
same FileStream (closes the create-vs-populate race); 5-task cap; `HANDOFF.md` +
`.stop` sentinel.

## Review / verification
**8 epistemic stance agents defined** (empiricist, skeptic, falsificationist,
bayesian, pragmatist, coherentist, hermeneut, phenomenologist), but the **live
reviewer runs a 4-lens single pass** (pragmatist + falsificationist + hermeneut +
bayesian) — no subagent fan-out, *"one review costs one Claude session, not
five."* 3-iteration loop → `escalated`. The plan-interviewer *does* fan out the
epistemic panel for hard design choices.

## Falsifiability stance
At **planning + review**. The plan-interviewer is explicit hypothesis-falsification
(*"form a hypothesis… design the question that would falsify it"*); the reviewer
applies a falsificationist lens.

## Distinctive design decisions
- Falsification as a first-class **workflow** primitive.
- Atomic single-claimant `FileStream` locking (real concurrency control).
- **State-surface honesty enforced mechanically** — drift checks every prompt +
  pre-commit blocking ledger-only commits.
- Append-only ledger with **strikethrough** versioning (decisions struck, never
  deleted).
- **Cost-discipline reversal** — 8 agents defined, 4 in-session lenses used.
- Multi-terminal concurrent model with caps + sentinels + a decoupled controller.
- **Trigger-based** (not date-based) roadmapping.
- **Leak-proof public/private split** — public repo is a subtree split of
  `Dev_006` with allow/deny/content gates.

## Strengths / gaps (for consolidation)
- **Strengths:** most productized (web HUD, `/aem-doctor`, release checklist,
  8 releases); shipped autonomous orchestration; richest planning.
- **Gaps:** headless workers are black boxes (HUD compensates); no
  self-improvement loop; cost tension (retreated from fan-out).

## Consolidation notes
Carry forward: the **web HUD control plane**, **`/aem-doctor`** health-check,
**release discipline**, the **scientific-method plan interviewer**, and
`orchestrator-loop`'s **capacity / heartbeat / dormancy** machinery. The
headless-vs-observable worker choice is an open fork.

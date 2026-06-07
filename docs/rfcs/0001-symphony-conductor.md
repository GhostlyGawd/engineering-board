# RFC 0001 — Conductor: always-on orchestrated agents over the engineering board

- **Status:** Draft (rev 3 — drops the policy precondition; the execution backend is now a plain CLI/API adapter choice. rev 2 added the execution/ownership model, concurrency/merge handling, and sequencing against the 1.1.0 board relocation.)
- **Target repo:** `GhostlyGawd/engineering-board`
- **Author:** GhostlyGawd
- **Date:** 2026-06-06
- **Depends on:** [`specs/board-relocation.md`](../../specs/board-relocation.md) (the 1.1.0 path-resolution helper — see §8)
- **Related:** OpenAI Symphony (`openai/symphony`) — prior art for board-as-control-plane orchestration

## 1. Summary

Add a **conductor**: an external, always-on orchestrator that drives the
engineering board to completion without a human in the session. The board
(already git-native) is the control plane. The conductor wakes on a trigger,
reconciles the board against running work, dispatches a headless worker per
eligible entry in an isolated git worktree, and stops each entry at a **PR**
that serves as the human-review gate.

The key structural observation that makes this cheap: **the plugin already
splits "orchestrator" from "worker."** The discipline subagents
(`tdd-builder`, `code-reviewer`, `validator`) are already pure executors — they
do **not** acquire/release claims, never edit the board entry, and return a
JSON result carrying `suggested_next_needs`. The *orchestrator* (today: the
in-session Stop hook) owns claims, heartbeats, and `needs:` transitions. The
conductor is therefore a **drop-in replacement for the orchestrator role the
disciplines already expect** — moved out of the session and made always-on. The
disciplines and the board substrate are reused unchanged; what is net-new is the
external orchestrator and its worktree/PR/trigger/governor plumbing.

This is, in effect, a git-native Symphony — with the addition that the board
*also* manufactures its own work via the existing capture/consolidation
pipeline, which Symphony leaves to humans.

## 2. Motivation

The plugin already has a durable orchestration **substrate**:

- Durable, git-tracked board (entry state in YAML frontmatter).
- Claims with leases: `board-claim-acquire/release`, heartbeats,
  `board-claim-reclaim-stale` (atomic `mkdir` lock on `_claims/<id>/`).
- Worker disciplines and a state machine: `needs: tdd → review → validate → resolved`.
- **A clean orchestrator/worker contract** (see §1): disciplines are read-only
  with respect to coordination and emit `suggested_next_needs`.
- Blocker gating (`blocked_by` / `⊘ Q###`), liveness registry
  (`active-workers.json`), auto-capture (extractor → scratch → consolidate).

What is **missing is the orchestrator running when no human is present.** Today
the only orchestrator is the Stop hook re-firing inside a live, human-attended
session; on Claude Code on the web, sessions are ephemeral containers with
nothing running between them. So entries sit at `needs:<discipline>` until a
human opens a session. The conductor closes that gap by being the orchestrator
that is always on.

**Calibrating "how much is done":** the *substrate* (format, claims, disciplines,
state model, registry) is close to complete and is genuinely reusable. The
*orchestrator that runs unattended* — supervisor, worktree lifecycle, PR/evidence
plumbing, triggers, governor, conflict-aware scheduling, crash recovery — is
greenfield, and every genuinely novel or risky part of this RFC lives there, not
in the reused substrate. "We're most of the way there" is true of the substrate
and false of the conductor; plan accordingly.

## 3. Goals / Non-goals

**Goals**
- Advance every eligible board entry through its discipline pipeline with no
  human in the session, up to the PR gate.
- **Reuse the substrate as-is**: board format, the three discipline subagents and
  their I/O contract, the claim/heartbeat/reclaim scripts, the `needs:` model, and
  the registry schema. The conductor *re-homes* the orchestrator role rather than
  rewriting any of it (§5, §7).
- Run on the author's own machine. **Backend-agnostic** at the seam: default to the
  `claude` CLI, but keep worker invocation behind an adapter so the metered
  API/Agent SDK is a drop-in fallback (§4.5).
- Be cheap when idle (event-driven wake → reconcile → sleep; fresh context per wake).
- Safe concurrency: no two agents clobbering the same tree; **no two concurrent
  workers with overlapping file blast radius** (§6); bounded blast radius and
  bounded PR volume.

**Non-goals (v1)**
- Auto-merge. The PR is the human gate; merging stays manual (the conductor *maintains*
  mergeability but does not merge — §6.3).
- Hosted/multi-tenant service. Single-user, single-machine daemon.
- Replacing the in-session passive-listening / consolidation flow.
- Giving workers any credentials or network identity. **All git-remote and GitHub
  interaction is the conductor's**; workers only edit code in a worktree (§5.1).

## 4. Design

### 4.1 Control plane (unchanged)
The board stays the source of truth. Durable state = markdown + frontmatter in
git. Runtime/coordination state (claims, registry, the conductor's supervision
table) is gitignored and lives under a **single conductor-owned runtime root**
(§5.2). The conductor `git pull`s to read board state and owns all branch pushes.

### 4.2 The conductor loop (event-driven reconciliation)

```
[trigger fires] → conductor wakes (FRESH context window)
  1. git pull --rebase                       # latest board, in the conductor's own checkout
  2. recover: load supervision table; reattach to or reap any in-flight workers
  3. reconcile running set:                  # conductor owns claim liveness
       for each in-flight claim: ensure its heartbeat companion is alive
       run board-claim-reclaim-stale for any claim whose worker is gone
  4. select eligible entries:
       status open/in_progress AND needs:<discipline> set
       AND not claimed AND not blocked_by(open)
       AND no in-flight sibling with overlapping blast radius (§6.2)
       sort P0 → P3, then age
  5. governor: clamp to MIN(MAX_CONCURRENCY, free-slots, rate-budget, open-PR-cap)
  6. for each selected entry:
       board-claim-acquire.sh <runtime-root> <id> <conductor-session>   # conductor claims
       start heartbeat companion for <id>                               # lives for the worker's lifetime
       git worktree add ../wt/<id> -b eb/<id>
       spawn CONTAINED headless worker (one discipline, Stop hook off — §5.4)
       on worker exit: parse JSON result → advance needs: per suggested_next_needs
                       conductor commits the needs: change, pushes eb/<id>,
                       opens/updates PR, posts evidence comment
       stop heartbeat companion; board-claim-release.sh; GC worktree (§6/§10)
  7. sleep
```

Each wake is a clean context window — cheap, and nothing burns tokens idle.
This mirrors Symphony's reconciliation "tick" but is event-gated instead of a hot
poll. Note steps 2–3 and 6 make the conductor the **sole owner of claim
acquisition, heartbeat, transition, and release** — the role the discipline
contracts already delegate to "the orchestrator."

### 4.3 Worker isolation & integration
- **Per-entry git worktree** (`git worktree add ../wt/<id> -b eb/<id>`), removed
  per the GC policy in §6/§10. Prevents concurrent agents from clobbering one shared
  tree.
- **PR per entry**, branch `eb/<id>`. The **conductor** pushes the branch and
  opens/updates the PR; review iterations and validation evidence are posted as
  **PR comments** (the audit trail). Workers never push and never call GitHub.
- **Merge:** entries land via their PRs; v1 = manual human merge. The conductor keeps
  branches mergeable and re-validates affected siblings on each merge (§6.3).

### 4.4 Human-review gate
Workers run `tdd → review → validate` (driven by the conductor across separate
worker invocations) and the entry **stops at the PR**. The PR — with accumulated
evidence comments — is the single human gate. Nothing is auto-closed or
auto-merged. This matches the plugin's existing "resolve is never automatic"
stance (`validator.md`: the `needs: validate → resolved` transition is
human-driven) and Symphony's `Human Review` handoff.

### 4.5 Execution backend (adapter)
Worker invocation goes through a thin **execution adapter** with one method,
`run_discipline(entry, discipline, worktree) → result_json`, so the conductor,
governor, claims, transitions, and PR plumbing stay identical regardless of how a
worker is actually run. Two backends sit behind it:

- **`cli` (default):** spawn the **`claude` CLI in headless/print mode**
  (`claude -p …`) under the machine's logged-in account.
- **`api` (fallback):** the metered API / Agent SDK.

Only the adapter differs between them; everything else in the conductor is
backend-agnostic.

**Rate/usage limits are a first-class outcome.** A limit response is not a
  failure: the adapter surfaces `rate_limited`, the governor backs off and lowers
  effective concurrency below `MAX_CONCURRENCY`, and the entry is cleanly released
  and re-queued (claim dropped, worktree GC'd or parked) rather than left holding a
  claim. Real throughput is bounded by the limit, not the concurrency cap.

### 4.6 Trigger model
- **Primary:** GitHub webhook on board commits / PR review events / CI completion
  → small local listener → one reconciliation tick.
- **Floor:** a slow cron (e.g. every N minutes) as a safety net so nothing stalls
  forever if a webhook is missed.
- **Optional:** filesystem watch (inotify) on the **resolver's board root** (not a
  hardcoded `docs/boards/**` — see §8) for local edits.

### 4.7 Cost & safety governor
- `MAX_CONCURRENCY` cap on simultaneous workers; **adaptive** down on rate limits (§4.5).
- **Bounded PR volume:** caps on open-PR count and PRs-created-per-day, so a
  self-generating board can't surface 40 PRs overnight (§6.4).
- Per-tick and per-day budget/turn ceilings; hard timeout per worker (reuses stall
  detection → reclaim).
- Allowlist of repos/branches the conductor may touch. Human gate at PR (no auto-merge).

## 5. Execution & ownership model (net-new — resolves the in-session→headless seams)

The original draft promised "reuse the claim/heartbeat/worker/state-machine code
unchanged." That holds for the **disciplines and the substrate**, but the
*orchestrator* cannot be reused unchanged: today it is the in-session Stop hook,
and three of its behaviors assume a live session. This section pins how the
conductor takes over the orchestrator role so those assumptions hold headlessly.
These are **MVP requirements**, not hardening.

### 5.1 Principle: conductor = control plane, worker = data plane
The discipline contracts already define this split; the conductor simply fills the
"orchestrator" slot:

| Concern | Owner |
|---|---|
| Claim acquire / heartbeat / release / reclaim | **Conductor** (the disciplines explicitly disown it) |
| `needs:` transitions | **Conductor** (from the worker's `suggested_next_needs`) |
| Git push, PR create/update, evidence comments, GitHub auth | **Conductor** |
| Code edits + tests inside one worktree, returning result JSON | **Worker** (no claims, no board-entry edits, no network) |

The conductor↔worker interface **already exists**: the disciplines' canonical
input format (`---ENTRY-ID--- / ---ENTRY-CONTENT--- / ---END---`) and their JSON
Output contract (`status`, `suggested_next_needs`, `test_output_excerpt`,
`impl_files_changed`, …). The conductor delivers that input and parses that output.

### 5.2 Claim & runtime location (resolves "claims don't cross worktrees")
`board-claim-acquire.sh` locks via `mkdir "${BOARD_DIR}/_claims/<id>"` — a
filesystem-atomic primitive. `_claims/` is gitignored and lives in the working
tree, and **git worktrees do not share working-tree/ignored files**, so a claim
acquired inside worktree A is invisible to worktree B and to the conductor.

Resolution: **all coordination state lives in one conductor-owned runtime root
outside every worktree**, and every claim/registry call is made by the conductor
against that root.

- Define `EB_RUNTIME_ROOT` (default: the conductor's main checkout
  `.engineering-board/`). Claims, registry, and the supervision table live here.
- The conductor passes this root explicitly to the claim scripts; workers never
  invoke claim scripts and never create a competing `_claims/`.
- This is exactly the "runtime root vs board root" split the 1.1.0 relocation
  resolver introduces — so the location is **decided as part of that resolver's
  contract**, not bolted on (§8).

### 5.3 Heartbeat ownership (resolves stale-reclaim of a live headless worker)
Today workers self-heartbeat and a PM-fallback refreshes live sessions; a
`claude -p` subprocess is neither, and the stale threshold is **180 s**. A worker
that runs longer with nobody bumping its claim would be reclaimed → double-dispatch.

Resolution: when the conductor acquires a claim and spawns the worker, it starts a
**heartbeat companion** that bumps `board-claim-heartbeat.sh` every
`HEARTBEAT_INTERVAL_SEC` (30 s) for the **entire lifetime of the subprocess**, and
stops it on exit. Per-tick "refresh" is insufficient when triggers are event-sparse;
the companion is continuous. The existing heartbeat script is reused verbatim — only
the caller moves from the in-session worker to the conductor.

### 5.4 State-machine driver & Stop-hook containment (resolves recursion / non-advancement)
The `needs:` machine advances today because the in-session Stop hook re-fires,
greps `needs:<discipline>`, and continues (`<<EB-WORKER-CONTINUE>>`). A
conductor-spawned `claude` must not inherit that behavior, or one of two failures
occurs: (a) if its Stop hook fires, the worker becomes its **own** conductor
(nested orchestration); (b) if it doesn't, nothing advances `needs:`.

Resolution — two parts:

1. **The conductor drives transitions.** After a worker exits `work_done`, the
   conductor reads `suggested_next_needs`, validates it against the legal
   transitions for that discipline, and writes the new `needs:` value to the entry
   frontmatter (a deterministic board edit it then commits/pushes). This is the
   role `code-reviewer.md`/`validator.md`/`tdd-builder.md` already delegate to "the
   orchestrator." No discipline change.
2. **Contain the worker's Stop hook** so the spawned `claude` never self-orchestrates.
   Belt-and-suspenders, consistent with the Stop hook's existing fast-path gates
   (`stop_hook_active`, loop-guard):
   - The conductor sets `EB_CONDUCTOR_MANAGED=1` in the worker's environment; the
     **command-stage** Stop gate (`board-stop-gate.sh`, which runs before the prompt
     stage and can read env) short-circuits to a terminal decision when it sees the
     flag.
   - And/or the conductor seeds the worker's `session-mode.json` to a single-shot
     mode the gate treats as "do nothing." Either alone suffices; both together make
     recursion structurally impossible.

### 5.5 Worker contract (I/O)
- **In:** entry id, discipline, verbatim entry content (canonical delimited format),
  worktree path. No claims, no creds.
- **Do:** run exactly one discipline once, in the worktree, with coordination hooks
  contained (§5.4).
- **Out (stdout):** the discipline's existing JSON object — `status`,
  `suggested_next_needs`, evidence fields. The conductor parses it; on
  `cannot_proceed`/non-JSON/timeout it treats the entry as a failed attempt
  (release claim, leave `needs:` unchanged, record on the PR).

### 5.6 Crash recovery
The conductor persists a **supervision table** in `EB_RUNTIME_ROOT`:
`{entry_id → (worktree, branch, pid, claim, last_heartbeat, discipline, started_at)}`.
On restart (loop step 2) it re-reads the board and the table, reattaches to live
PIDs, reaps dead ones (release/reclaim their claims, GC or reuse their worktrees),
and resumes — tracker-driven recovery, like Symphony.

## 6. Concurrency & merge (net-new — resolves the file-level safety gap)

Per-entry claims + per-entry worktrees give clean **isolation**, but not
**file-level** safety: two entries that edit overlapping files produce two PRs
that don't both merge. This is more likely here because the board *manufactures its
own work*.

### 6.1 Blast radius
Add an optional `touches:` frontmatter hint (a list of path globs) to bug/feature
entries. The consolidator may populate it at promotion; a worker may refine it in
its result. It is advisory, not load-bearing.

### 6.2 Conflict-aware scheduling
In loop step 4 the conductor will not start an entry concurrently with an in-flight
sibling whose `touches:` overlaps. When `touches:` is absent, the conservative
fallback is to serialize entries with unknown scope against any in-flight worker, or
(configurable) run them and resolve conflicts at merge time (§6.3). This keeps "no
two agents clobbering" honest at the *file* level, not just the worktree level.

### 6.3 Mergeability maintenance (not auto-merge)
v1 keeps human merge as the gate, but the conductor prevents the gate from becoming a
pile of stale conflicts: it keeps each `eb/<id>` rebased on `main` (or flags when a PR
no longer merges cleanly), and **on a human merge of one PR it triggers a re-validate
tick on siblings whose blast radius overlapped** (rebase their worktree, re-run
`validate`, update the PR). The human still approves and merges; the conductor keeps
the set mergeable. Without this, "no human in the session" just relocates the human to
an ever-growing merge queue.

### 6.4 Bounded PR volume
Because capture/consolidate can mint new entries, the governor caps **open-PR count**
and **PRs-created-per-day** (§4.7), so the human review surface stays bounded.

## 7. Reuse / re-home / replace / net-new

| Reused **unchanged** | Re-homed (same code, conductor is now the caller) | Replaced | Net-new |
|---|---|---|---|
| Board format + frontmatter | `board-claim-acquire/release/heartbeat/reclaim-stale` | In-session Stop-hook **orchestrator** → external conductor | Conductor supervisor + supervision table + crash recovery (§5.6) |
| The three discipline subagents (already pure executors) + their I/O contract | `active-workers` registry bumps | Stop-hook self-continue loop → **contained** in workers (§5.4) | Per-entry worktree lifecycle |
| `needs:` state model + `suggested_next_needs` output | Claim/runtime *location* → single shared runtime root (§5.2) | Worker self-heartbeat → conductor heartbeat companion (§5.3) | PR-per-entry + evidence-comment plumbing (conductor-owned) |
| Blocker gating, capture/consolidate | — | — | Trigger listener; adaptive governor; conflict-aware scheduler (§6); execution adapter (§4.5) |

The honest headline: **the substrate and disciplines are reused; the orchestrator
is rebuilt as an always-on external process.** The original two-column table
under-counted the orchestrator rebuild.

## 8. Sequencing & dependencies

This RFC has a hard upstream dependency on the **1.1.0 board relocation**
([`specs/board-relocation.md`](../../specs/board-relocation.md)), which centralizes
path resolution into a single helper returning the **board root** and (the part this
RFC needs most) a canonical **runtime root**.

- **Order:** land 1.1.0 first; build the conductor on its resolver. The conductor must
  not hardcode `docs/boards/**` or `.engineering-board/` (e.g. the §4.6 filesystem
  watch and §5.2 runtime root both come from the resolver).
- **Fold §5.2 into the resolver contract.** "Where do claims/runtime live so the
  conductor and all worktrees see one shared lock namespace?" is exactly the
  runtime-root question the relocation work is already touching. Decide it there;
  record the dependency in both docs.
- **Version targeting:** relocation = **1.1.0**; conductor = **1.2.0** (additive and
  opt-in — running the conductor is a choice; existing boards and the in-session flow
  are unaffected). Only the breaking removal of an old path or contract would force a
  2.0.0, which this RFC does not require.
- **Doc convention nit:** this is `docs/rfcs/0001`, while relocation lives at
  `specs/board-relocation.md`. Worth unifying (promote the relocation spec to
  `docs/rfcs/0000`, or keep `specs/` for locked designs and `docs/rfcs/` for
  proposals) — cosmetic, but pick one.

## 9. Phased plan

0. **Phase 0 — Execution adapter.** Stand up the execution adapter with both `cli`
   and `api` backends behind one interface (§4.5), so the rest of the conductor is
   written once against `run_discipline(...)` and the backend choice never dictates a
   rewrite.
1. **Conductor MVP (sequential) — proves the ownership seams.** One entry per tick, one
   worktree, contained headless worker, conductor-owned claim + heartbeat companion +
   `needs:` transition (§5.2–5.4), conductor pushes branch + opens PR. This phase
   exists to validate §5; the seams are the MVP, not hardening.
2. **Concurrency + scheduling.** `MAX_CONCURRENCY`, multiple worktrees, the governor,
   and conflict-aware scheduling (§6.1–6.2).
3. **Triggers.** Webhook listener + cron floor (+ optional inotify on the resolver root).
4. **Evidence & mergeability.** Structured per-stage PR comments; rebase + sibling
   re-validate on merge (§6.3); PR-volume caps (§6.4).
5. **Hardening.** Budgets, timeouts, allowlists, rate-limit adaptation, crash recovery
   (§5.6), worktree GC policy.

## 10. Open questions

**Resolved in this revision** (recorded here so reviewers can challenge the choices):
- *Worker mode / does its Stop hook fire?* → workers run contained; the conductor
  drives transitions (§5.4).
- *Where do claims live so conductor + all worktrees agree?* → one runtime root,
  conductor-owned, defined by the 1.1.0 resolver (§5.2, §8).
- *Who heartbeats an in-flight claim?* → the conductor's per-worker heartbeat companion (§5.3).
- *GitHub auth / who opens PRs?* → only the conductor; workers hold no creds (§4.3, §5.1).

**Still open:**
- **Worktree GC policy:** remove on PR open, on merge, or on a TTL? (Reuse-on-rebase for
  sibling re-validation (§6.3) argues for keep-until-merge or TTL.)
- **Blast-radius source:** is the `touches:` hint reliable enough, or should the
  conductor derive scope from the worker's `impl_files_changed` after the first attempt
  and reschedule? (Probably: schedule optimistically, learn scope from the first diff.)
- **Does capture/consolidation run headless on a tick,** or stay in-session only? If
  headless, the conductor gains a second job (mint work) feeding the first (execute it) —
  amplifying the §6.4 volume concern.
- **Discipline granularity:** one conductor driving all of tdd/review/validate vs. a
  conductor instance per discipline. (Leaning single conductor, since it already owns the
  per-entry transition.)

## 11. Prior art

OpenAI Symphony (`openai/symphony`): an orchestrator polls an issue tracker (Linear),
claims eligible issues, runs a per-issue agent in an isolated workspace, restarts
stalls, and hands off to `Human Review`. This RFC adapts the same pattern to a
git-native board, fills the orchestrator slot the plugin already defines, and adds
self-generated work items (with the bounded-volume controls that addition requires).

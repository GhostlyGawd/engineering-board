# RFC 0001 — Conductor: always-on orchestrated agents over the engineering board

- **Status:** Draft (rev 5 — adopts **claude-squad's `session/tmux` + `session/git` as the lifted spawn/worktree substrate** for the observable sessions; the conductor stays our own code (claude-squad is the hands, not the brain — it neither selects work nor opens PRs). rev 4 pivoted execution to observable interactive sessions: a deterministic orchestrator spawns one attachable `claude` session per round, the session drives discipline subagents that write their trail to the task thread and then self-terminates, and the orchestrator reads that durable state to spawn a *pickup* session. rev 3 dropped the policy precondition and pinned execution to the subscription CLI; rev 2 added the execution/ownership model, concurrency/merge, and 1.1.0 sequencing.)
- **Target repo:** `GhostlyGawd/engineering-board`
- **Author:** GhostlyGawd
- **Date:** 2026-06-06
- **Depends on:** [`specs/board-relocation.md`](../../specs/board-relocation.md) (the 1.1.0 path-resolution helper — see §8)
- **Related:** OpenAI Symphony (`openai/symphony`) — prior art for board-as-control-plane orchestration; [`smtg-ai/claude-squad`](https://github.com/smtg-ai/claude-squad) — lifted for the session/worktree substrate (§4.5, §7, §11)

## 1. Summary

Add a **conductor**: an external, always-on **deterministic** orchestrator that
drives the engineering board to completion without a human in the session. The
board (already git-native) is the control plane. The conductor wakes on a trigger,
reconciles the board against running work, and — for each eligible entry — spawns
one **observable interactive `claude` session** in an isolated git worktree. That
session does **one bounded round** of work and self-terminates; the conductor reads
the resulting durable state and, while the entry is unfinished, spawns the next
session with a **pickup prompt** that resumes where the last one left off. Each
entry stops at a **PR** that serves as the human-review gate.

Two choices define this revision:

- **Observable, not headless.** A headless `claude -p` worker is a black box — you
  cannot watch it think or step in. Workers are therefore **interactive sessions you
  can attach to and watch live.** The cost of interactive (a terminal has to be
  spawned, which is tedious by hand) is paid by the orchestrator, which spawns the
  session programmatically — e.g. a detached `tmux` session a human can `attach` to
  (§4.5). The deterministic loop stays code; only the *workers* are live sessions.
- **One round per session, then die.** To keep each session's context small and
  focused, a session advances the entry as far as one round allows and then exits.
  Continuity lives **outside** the session: progress and evidence are written to the
  task's comment thread and the board, and the deterministic orchestrator stitches
  rounds together by spawning pickup sessions.

The structural observation that keeps this cheap: **the plugin already splits
"orchestrator" from "worker."** The discipline subagents (`tdd-builder`,
`code-reviewer`, `validator`) are pure executors. Here they run as **subagents
inside the session**, and each leaves its notes, findings, surprises, and evidence
in the task thread as it works — the trail that makes a run observable *during* and
*after*. A builder builds and records as it goes, then stops; the code-reviewer
reviews and records, raising anything blocking; that review↔fix loop iterates until
the round's goal is met and "done" evidence is left. What is reused is the board
substrate and the disciplines; what is net-new is the deterministic cross-session
orchestrator and its session-spawn/pickup, worktree/PR, trigger, and governor
plumbing.

This is, in effect, a git-native Symphony — with the additions that the board
*also* manufactures its own work via the existing capture/consolidation pipeline,
and that every worker run is a live, attachable session rather than an opaque batch
job.

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

Two things are **missing: (1) an orchestrator that runs when no human is present,
and (2) a way to *see* what an unattended run is doing.** Today the only
orchestrator is the Stop hook re-firing inside a live, human-attended session; on
Claude Code on the web, sessions are ephemeral containers with nothing running
between them, so entries sit at `needs:<discipline>` until a human opens a session.
The conductor closes the first gap by being always on, and the second by running
workers as **observable sessions** (you can attach and watch) that leave a written
trail, rather than as headless batch jobs you can only inspect by their exit code.

**Calibrating "how much is done":** the *substrate* (format, claims, disciplines,
state model, registry) is close to complete and is genuinely reusable. The
*orchestrator that runs unattended* — supervisor, observable-session spawn +
pickup, worktree lifecycle, PR/evidence plumbing, triggers, governor,
conflict-aware scheduling, crash recovery — is greenfield, and every genuinely
novel or risky part of this RFC lives there, not in the reused substrate. "We're
most of the way there" is true of the substrate and false of the conductor; plan
accordingly.

## 3. Goals / Non-goals

**Goals**
- Advance every eligible board entry through its discipline pipeline with no
  human in the session, up to the PR gate.
- **Observable runs.** Every worker is a live, attachable `claude` session, and
  every round leaves a written trail (notes, findings, surprises, evidence) in the
  task's comment thread — so a human can both *watch* a run in progress and *audit*
  it afterward. Black-box headless execution is explicitly rejected (§4.5).
- **One bounded round per session, then self-terminate** — context stays small and
  focused; continuity is reconstructed from durable state (board + task thread) by
  the orchestrator's pickup mechanism (§4.2, §5.4).
- **Reuse the substrate as-is**: board format, the three discipline subagents, the
  claim/heartbeat/reclaim scripts, the `needs:` model, and the registry schema. The
  conductor *re-homes* the cross-session orchestrator role rather than rewriting any
  of it (§5, §7).
- Run on the author's own machine, on the flat-rate **subscription** `claude` CLI —
  not the metered API. Running it yourself on the subscription is the whole point.
- Be cheap when idle (event-driven wake → reconcile → sleep; a fresh, short-lived
  session per round).
- Safe concurrency: no two agents clobbering the same tree; **no two concurrent
  sessions with overlapping file blast radius** (§6); bounded blast radius and
  bounded PR volume.

**Non-goals (v1)**
- Auto-merge. The PR is the human gate; merging stays manual (the conductor *maintains*
  mergeability but does not merge — §6.3).
- Hosted/multi-tenant service. Single-user, single-machine daemon.
- Replacing the in-session passive-listening / consolidation flow.
- Giving sessions broad credentials or a network identity beyond what they need to
  leave their evidence trail. **Branch pushes, PR open/update, and merge stay the
  conductor's;** whether a session posts its own thread comments directly or routes
  them through the conductor is deferred (§10).

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
  2. recover: load supervision table; reattach to or reap any in-flight sessions
  3. reconcile running set:                  # conductor owns claim liveness
       for each in-flight claim: ensure its heartbeat companion is alive
       run board-claim-reclaim-stale for any claim whose session is gone
  4. select eligible entries:
       status open/in_progress AND needs:<discipline> set
       AND not claimed AND not blocked_by(open)
       AND no in-flight sibling with overlapping blast radius (§6.2)
       sort P0 → P3, then age
  5. governor: clamp to MIN(MAX_CONCURRENCY, free-slots, rate-budget, open-PR-cap)
  6. for each selected entry:
       board-claim-acquire.sh <runtime-root> <id> <conductor-session>   # conductor claims
       start heartbeat companion for <id>                               # lives for the session's round
       ensure worktree + task thread exist:
         git worktree add ../wt/<id> -b eb/<id>   (reused as-is on a pickup)
         a thread to write into (draft PR and/or tracker issue) so the round has a home
       build the PICKUP PROMPT from <id>'s current state (board entry + thread tail)
       spawn an OBSERVABLE interactive `claude` session in the worktree (§4.5),
         loaded with that pickup prompt
       the session runs ONE bounded round via discipline subagents (build → review →
         iterate), each appending notes/findings/surprises/evidence to the thread,
         then MARKS THE ROUND OUTCOME (board + a structured status line) and EXITS (§5.4–5.5)
       on session exit, conductor reads board + thread to classify the round:
         done            → push branch, finalize PR, release claim, GC worktree (§6/§10)
         more to do       → push branch, update PR, release claim; a later tick spawns a pickup
         stuck / errored  → release claim, flag on the thread, back off
       stop heartbeat companion; board-claim-release.sh
  7. sleep
```

Each wake is a clean context window for the *orchestrator*; each round is a clean
context window for the *worker*. Nothing burns tokens idle. This mirrors Symphony's
reconciliation "tick" but is event-gated instead of a hot poll. Steps 2–3 keep the
conductor the **sole owner of claim liveness, the spawn/pickup decision, and the
branch/PR lifecycle** — the cross-session half of the role the discipline contracts
delegate to "the orchestrator" (§5.1).

### 4.3 Worker isolation & integration
- **Per-entry git worktree** (`git worktree add ../wt/<id> -b eb/<id>`), reused
  across rounds and removed per the GC policy in §6/§10. Prevents concurrent agents
  from clobbering one shared tree.
- **PR per entry**, branch `eb/<id>`. The **conductor** pushes the branch and
  opens/updates the PR. The round's evidence (review iterations, validation results)
  is written into the **task thread** by the session as it works — that thread is
  the live, observable audit trail (§4.5, §5.5).
- **Merge:** entries land via their PRs; v1 = manual human merge. The conductor keeps
  branches mergeable and re-validates affected siblings on each merge (§6.3).

### 4.4 Human-review gate
An entry advances `tdd → review → validate` across one or more rounds — *within* a
round the session runs the disciplines as subagents; *across* rounds the conductor
spawns pickups — and the entry **stops at the PR**. The PR, with the accumulated
evidence thread, is the single human gate. Nothing is auto-closed or auto-merged.
This matches the plugin's existing "resolve is never automatic" stance
(`validator.md`: the `needs: validate → resolved` transition is human-driven) and
Symphony's `Human Review` handoff.

### 4.5 Execution: observable interactive sessions
Workers are **interactive `claude` sessions** under the machine's logged-in
subscription — not headless `claude -p`. The driver is *why*: a headless run is a
black box; an interactive session can be **attached to and watched live**, and (per
§5.5) leaves a written trail as it goes. The conductor pays the cost that makes
interactive impractical by hand — spawning and supervising a terminal — by
**lifting that layer from [claude-squad](https://github.com/smtg-ai/claude-squad)**,
whose `session/tmux` + `session/git` packages already do exactly this: spawn a
detached, attachable session in a per-task git worktree, drive it through a PTY, and
observe it with `capture-pane`. The proven shape:

```
tmux new-session -d -s eb-<id> 'claude'   # detached; drive via PTY, observe via capture-pane
#   a human or dashboard attaches with:   tmux attach -t eb-<id>   (Ctrl-Q to detach)
git worktree add ../wt/<id> -b eb/<id>    # per-task isolation
```

claude-squad is **the hands, not the brain.** We vendor its session/worktree
primitives — light surgery only: initialize its global loggers, override its
hardcoded `~/.claude-squad` root, and drop its `gh`-CLI push path — and write the
conductor on top. It does **not** select work, drive the `needs:` machine, detect
round completion, or open PRs; those are the conductor's (§5, §7). The spawn/attach
mechanism is therefore **settled** (claude-squad's tmux + PTY model), not an open
question. There is no headless/API execution path.

**Rate/usage limits are a first-class outcome.** A limit response is not a
failure: the conductor surfaces `rate_limited`, the governor backs off and lowers
effective concurrency below `MAX_CONCURRENCY`, and the entry is cleanly released
and re-queued (claim dropped, worktree parked for the next pickup) rather than left
holding a claim. Real throughput is bounded by the limit, not the concurrency cap.

### 4.6 Trigger model
- **Primary:** GitHub webhook on board commits / PR review events / CI completion
  → small local listener → one reconciliation tick.
- **Floor:** a slow cron (e.g. every N minutes) as a safety net so nothing stalls
  forever if a webhook is missed.
- **Optional:** filesystem watch (inotify) on the **resolver's board root** (not a
  hardcoded `docs/boards/**` — see §8) for local edits.

### 4.7 Cost & safety governor
- `MAX_CONCURRENCY` cap on simultaneous sessions; **adaptive** down on rate limits (§4.5).
- **Bounded PR volume:** caps on open-PR count and PRs-created-per-day, so a
  self-generating board can't surface 40 PRs overnight (§6.4).
- Per-tick and per-day budget/turn ceilings; hard timeout per session (reuses stall
  detection → reclaim).
- Allowlist of repos/branches the conductor may touch. Human gate at PR (no auto-merge).

## 5. Execution & ownership model (net-new — resolves the in-session→cross-session seams)

The original draft promised "reuse the claim/heartbeat/worker/state-machine code
unchanged." That holds for the **disciplines and the substrate**, but the
*orchestrator* cannot be reused unchanged: today it is the in-session Stop hook, and
its behaviors assume a single live session that runs forever. This section pins how
a deterministic, always-on conductor and a fleet of one-round sessions split the
orchestrator role between them. These are **MVP requirements**, not hardening.

### 5.1 Principle: two orchestrators, two altitudes
There are now two orchestrators, and the discipline subagents stay the pure data
plane beneath both:

| Concern | Owner |
|---|---|
| Claim acquire / heartbeat / release / reclaim | **Deterministic conductor** (cross-session) |
| Reading durable state → deciding done vs. spawn-a-pickup; building the pickup prompt | **Deterministic conductor** |
| Git branch push, PR create/update, merge-gate, GitHub auth | **Deterministic conductor** |
| Driving the disciplines for ONE round; collecting their trail; marking the round outcome | **Session agent** (in-session, ephemeral — lives one round) |
| Code edits + tests; recording notes/findings/surprises/evidence to the task thread | **Discipline subagents** (`tdd-builder` / `code-reviewer` / `validator`) |

The split is clean: the **deterministic conductor** owns everything *between*
sessions (liveness, the spawn/pickup decision, branch/PR/merge); the **session
agent** owns everything *within* one round; the **disciplines** do the work and
leave the trail. The conductor never reasons about code; the session never reasons
about scheduling, claims, or other entries.

The conductor↔session interface is durable state, not a return value: the conductor
delivers a **pickup prompt** (built from the board entry + the tail of the task
thread) and, after the session exits, reads the **round outcome** the session wrote
back to durable state (§5.5). This is the cross-session analogue of the disciplines'
existing `suggested_next_needs` contract.

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
- The conductor passes this root explicitly to the claim scripts; sessions never
  invoke claim scripts and never create a competing `_claims/`.
- This is exactly the "runtime root vs board root" split the 1.1.0 relocation
  resolver introduces — so the location is **decided as part of that resolver's
  contract**, not bolted on (§8).

### 5.3 Heartbeat ownership (resolves stale-reclaim of a live session)
Today workers self-heartbeat and a PM-fallback refreshes live sessions; a
conductor-spawned session is neither, and the stale threshold is **180 s**. A round
that runs longer with nobody bumping its claim would be reclaimed → double-dispatch.

Resolution: when the conductor acquires a claim and spawns the session, it starts a
**heartbeat companion** that bumps `board-claim-heartbeat.sh` every
`HEARTBEAT_INTERVAL_SEC` (30 s) for the **entire lifetime of the session**, and
stops it on exit. Per-tick "refresh" is insufficient when triggers are event-sparse;
the companion is continuous. The existing heartbeat script is reused verbatim — only
the caller moves from the in-session worker to the conductor.

### 5.4 Round boundary & no nested orchestration (resolves runaway / recursion)
The `needs:` machine advances today because the in-session Stop hook re-fires and
continues (`<<EB-WORKER-CONTINUE>>`) **indefinitely** inside one session. A
conductor-spawned session must not inherit that, or one of two failures occurs:
(a) it never stops — one session does many rounds, defeating "one bounded round, small
context"; (b) its Stop hook turns it into its **own** cross-session conductor (nested
orchestration over other entries).

Resolution — three parts:

1. **One round, then exit.** The session is scoped to a single round: drive the
   disciplines (build → review → iterate) until this round's goal is met or its
   budget is spent, write the outcome, and terminate. *How* a round's end is detected
   (task-done vs. context/turn budget vs. an explicit "round complete" signal) is an
   open question (§10).
2. **Contain the session's Stop hook** so it never self-orchestrates beyond its one
   round. Consistent with the Stop hook's existing fast-path gates (`stop_hook_active`,
   loop-guard):
   - The conductor sets `EB_CONDUCTOR_MANAGED=1` in the session's environment; the
     **command-stage** Stop gate (`board-stop-gate.sh`) short-circuits to a terminal
     decision when it sees the flag.
   - And/or the conductor seeds the session's `session-mode.json` to a single-shot
     mode the gate treats as "finish this round, then stop." Either alone suffices;
     both make a runaway structurally impossible.
3. **The session marks the round outcome** to durable state — the `needs:` value (or a
   "still on `needs:<x>`, round N done") plus a structured status line in the task
   thread — so the deterministic conductor can classify done / more-to-do / stuck on
   read, without parsing prose. Spawning the *next* round is the conductor's job, never
   the session's.

### 5.5 Session contract (I/O)
- **In:** entry id, worktree path, and a **pickup prompt** assembled by the conductor
  from durable state — the canonical entry content plus the tail of the task thread
  (what prior rounds did, what's left). No claims; only the credentials needed to
  write its trail (§3 non-goal, §10).
- **Do:** run exactly **one bounded round** in the worktree, driving the discipline
  subagents, with the Stop hook contained (§5.4). Append notes/findings/surprises/
  evidence to the task thread *as it works* — that is both the live observability
  surface and the next round's pickup context.
- **Out (durable side effects, not stdout):** the **round outcome** — updated board
  state and a structured status line in the thread — and the accumulated evidence
  trail; then self-terminate. On stuck/non-progress/error it leaves the outcome marked
  accordingly and flags the thread; the conductor releases the claim and either
  re-queues for a pickup or escalates to a human. There is no JSON return value to
  parse, because the session is gone — the conductor reads what the session *wrote*.

### 5.6 Crash recovery
The conductor persists a **supervision table** in `EB_RUNTIME_ROOT`:
`{entry_id → (worktree, branch, session-handle, pid, claim, last_heartbeat, round, started_at)}`,
where the session-handle is the spawn reference (e.g. the `tmux` session name). On
restart (loop step 2) it re-reads the board and the table, reattaches to live
sessions, reaps dead ones (release/reclaim their claims, GC or reuse their
worktrees), and resumes — tracker-driven recovery, like Symphony.

## 6. Concurrency & merge (net-new — resolves the file-level safety gap)

Per-entry claims + per-entry worktrees give clean **isolation**, but not
**file-level** safety: two entries that edit overlapping files produce two PRs
that don't both merge. This is more likely here because the board *manufactures its
own work*.

### 6.1 Blast radius
Add an optional `touches:` frontmatter hint (a list of path globs) to bug/feature
entries. The consolidator may populate it at promotion; a session may refine it in
the round outcome. It is advisory, not load-bearing.

### 6.2 Conflict-aware scheduling
In loop step 4 the conductor will not start an entry concurrently with an in-flight
sibling whose `touches:` overlaps. When `touches:` is absent, the conservative
fallback is to serialize entries with unknown scope against any in-flight session, or
(configurable) run them and resolve conflicts at merge time (§6.3). This keeps "no
two agents clobbering" honest at the *file* level, not just the worktree level.

### 6.3 Mergeability maintenance (not auto-merge)
v1 keeps human merge as the gate, but the conductor prevents the gate from becoming a
pile of stale conflicts: it keeps each `eb/<id>` rebased on `main` (or flags when a PR
no longer merges cleanly), and **on a human merge of one PR it triggers a re-validate
round on siblings whose blast radius overlapped** (rebase their worktree, spawn a
validate round, update the PR). The human still approves and merges; the conductor keeps
the set mergeable. Without this, "no human in the session" just relocates the human to
an ever-growing merge queue.

### 6.4 Bounded PR volume
Because capture/consolidate can mint new entries, the governor caps **open-PR count**
and **PRs-created-per-day** (§4.7), so the human review surface stays bounded.

## 7. Reuse / re-home / replace / net-new

| Reused **unchanged** | Re-homed (same code, conductor is now the caller) | Replaced | Net-new |
|---|---|---|---|
| Board format + frontmatter | `board-claim-acquire/release/heartbeat/reclaim-stale` | In-session Stop-hook **orchestrator** → deterministic external conductor | Conductor supervisor + supervision table + crash recovery (§5.6) |
| The three discipline subagents (pure executors) | `active-workers` registry bumps | Headless batch worker → **observable interactive session, one round** (§4.5, §5.4) | Pickup-prompt continuation loop (§4.2, §5.5); session/worktree spawn **lifted from claude-squad** (§4.5) |
| `needs:` state model | Claim/runtime *location* → single shared runtime root (§5.2) | Worker self-heartbeat → conductor heartbeat companion (§5.3) | Evidence written to the task thread by subagents as they work (§4.3, §5.5) |
| Blocker gating, capture/consolidate | — | Stop-hook self-continue loop → **one-round** containment (§5.4) | Trigger listener; adaptive governor; conflict-aware scheduler (§6) |

The honest headline: **the substrate and disciplines are reused, the session/worktree
plumbing is lifted from [claude-squad](https://github.com/smtg-ai/claude-squad)
(`session/tmux` + `session/git`), and the orchestrator brain is the only thing we
build.** claude-squad supplies the hands — spawn a detached, attachable session in a
worktree — but selects no work, drives no `needs:`, detects no round-completion, and
opens no PRs, so the deterministic conductor + pickup loop remain net-new. The
original two-column table under-counted the orchestrator rebuild.

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

0. **Phase 0 — One observable round.** Spawn a detached, attachable `claude` session
   (§4.5) in a worktree, hand it a pickup prompt, have it run one round via the
   discipline subagents, write its trail to a task thread, mark a round outcome, and
   self-terminate (§5.4–5.5). Prove a human can `attach` and watch. This is the load-
   bearing primitive; everything else builds on it.
1. **Pickup loop (sequential) — proves the cross-session seams.** Deterministic
   conductor: one entry per tick, conductor-owned claim + heartbeat companion (§5.2–5.3),
   read the round outcome, decide done vs. spawn-a-pickup, build the next pickup prompt,
   push branch + open/update PR. This phase validates §5; the seams are the MVP, not
   hardening.
2. **Concurrency + scheduling.** `MAX_CONCURRENCY`, multiple worktrees/sessions, the
   governor, and conflict-aware scheduling (§6.1–6.2).
3. **Triggers.** Webhook listener + cron floor (+ optional inotify on the resolver root).
4. **Evidence & mergeability.** Structured per-round status the conductor can read
   reliably; rebase + sibling re-validate on merge (§6.3); PR-volume caps (§6.4).
5. **Hardening.** Budgets, timeouts, allowlists, rate-limit adaptation, crash recovery
   (§5.6), worktree GC policy.

## 10. Open questions

**Resolved in this revision** (recorded here so reviewers can challenge the choices):
- *Headless or observable?* → observable interactive sessions; headless is rejected for
  its black-box opacity (§4.5).
- *How much work per session?* → one bounded round, then self-terminate; the conductor
  stitches rounds with pickup prompts (§4.2, §5.4).
- *Where do claims live so conductor + all worktrees agree?* → one runtime root,
  conductor-owned, defined by the 1.1.0 resolver (§5.2, §8).
- *Who heartbeats an in-flight claim?* → the conductor's per-session heartbeat companion (§5.3).
- *GitHub auth / who opens PRs and merges?* → only the conductor (§4.3, §5.1).
- *Spawn/attach mechanism?* → **lift claude-squad's `session/tmux` + `session/git`** (detached tmux + PTY + `capture-pane`, Ctrl-Q detach; `git worktree add/remove/prune`), confirmed by source review. Light surgery: init its global loggers, override its hardcoded `~/.claude-squad` root, drop its `gh`-CLI push path (§4.5, §7).

**Still open:**
- **Evidence-posting credentials:** does the session post its own thread comments
  directly (needs scoped PR/tracker write access — relaxes the v1 "no creds" stance), or
  does it write evidence to a local file the conductor relays? The §1 model ("subagents
  record as they work") leans toward direct posting; pin the credential scope.
- **Round-boundary signal & machine-readable outcome:** how a session knows its round is
  over (task-done vs. a context/turn budget vs. an explicit "round complete" it emits), and
  the exact shape of the outcome the conductor reads on exit (a board frontmatter field vs.
  a structured status line in the thread). claude-squad's analogue — infer "done" from "the
  tmux pane stopped changing for 500 ms" plus scraping one hard-coded prompt string per
  agent — is the **rejected baseline** (it is the cause of its flaky `-y`); our session
  emits an explicit marker instead. Open: the marker's exact format and how it stays
  reliable when an LLM writes it.
- **Task surface for the thread:** PR comments vs. a tracker issue (Linear) for the
  evidence/pickup trail, with the board still the control plane. Linear is available via
  MCP and is Symphony's own substrate (§11); a draft PR opened up front is the
  git-native alternative.
- **Streaming as an alternative to interactive:** Claude Code's headless mode can emit a
  structured event stream (e.g. `--output-format stream-json`), which is *a* form of
  observability without a terminal. This RFC favors live attachable sessions for true
  step-in/watch; verify the trade-off before locking it in.
- **Blast-radius source:** is the `touches:` hint reliable enough, or should the
  conductor derive scope from a round's diff and reschedule? (Probably: schedule
  optimistically, learn scope from the first diff.)
- **Does capture/consolidation run headless on a tick,** or stay in-session only? If on
  a tick, the conductor gains a second job (mint work) feeding the first (execute it) —
  amplifying the §6.4 volume concern.

## 11. Prior art

OpenAI Symphony (`openai/symphony`): an orchestrator polls an issue tracker (Linear),
claims eligible issues, runs a per-issue agent in an isolated workspace, restarts
stalls, and hands off to `Human Review`. This RFC adapts the same pattern to a
git-native board, fills the orchestrator slot the plugin already defines, runs each
worker as an observable one-round session rather than an opaque job, and adds
self-generated work items (with the bounded-volume controls that addition requires).

**claude-squad (`smtg-ai/claude-squad`)** — prior art *and* a lifted dependency for the
worker substrate: it runs many AI-agent sessions, each in its own detached tmux session
+ git worktree, attachable for live observation. But it is human-driven (manual title +
prompt, no tracker intake), its daemon only auto-confirms existing sessions, and it
exposes no programmatic/headless control surface — the hands, not the brain. We lift its
`session/tmux` + `session/git` packages (§4.5, §7) and build the autonomous board-driven
orchestrator it lacks. Symphony is the orchestrator prior art; claude-squad is the
session-substrate prior art.

# IMPROVEMENTS — product discovery pass v3 (2026-07-08): the engine audit

_Discovery only; nothing here is implemented. Every idea cites a file/line, an
open board entry, or a verified absence — no hypotheticals._

**Why this pass is different.** v1 (14 opportunities, all shipped as
[v1.5.0](https://github.com/GhostlyGawd/engineering-board/releases/tag/v1.5.0))
and v2, plus the 6 Experience-Optimization reports, the 6 Design reports, and
[`ROADMAP.md`](ROADMAP.md), audited **every UX, marketing, and visual surface**.
All of them named the same blind spot in the same words:

> _"Nothing audits the **engine** — the ~20 `hooks/scripts/*.sh` + `python3` + the
> MCP server — for correctness, debt, or performance… Run a BUGS / technical-debt
> audit of the shell+python engine next — it would change the technical half of
> this roadmap the most."_ — ROADMAP.md §1

**This is that audit.** It reads the coordination core the product's guarantees
rest on: the claim-locking scripts, the consolidation engine, the MCP server
(1457 lines), and the SessionStart/Stop wiring. The headline: the product markets
**"collision-free parallel agents"** (VP3) and **"two servers, one board"** (Q001),
but only *one* path — acquiring a claim — is actually concurrency-safe. **Creating,
mutating, and reclaiming** board state are unsynchronized, non-atomic, or use the
wrong staleness signal. And the product's own five committed Learnings (L001–L005)
each have fresh violations in the engine.

The known board backlog (B016/B020/B021/B022/B057/F003) is **excluded** — every
item below is new.

## 1. Product snapshot

engineering-board is a git-committed markdown kanban board that Claude Code agents
fill in and work through themselves: a Stop hook passively captures *findings*
(bugs/features/questions/observations) each turn to a scratch inbox; PM mode
consolidates them into validated entry files; Worker mode (and `/board-run`) drives
each entry through a `tdd → review → validate` state machine under an atomic
`mkdir`-based claim lock; and recurring lessons promote into durable `Learning`
entries. It ships as a Claude Code plugin (13 commands, 8 agents, 4 skills, 23
scripts) **and** a zero-dependency `python3` MCP server (13 tools), on the official
MCP Registry. It is young and fast-moving — 71 commits since 2026-07-04, now
v1.6.1. The whole thesis is **"the board is the database"**: coordination state,
locks, and memory are all committed markdown, reviewed in the same PRs as code —
which makes engine correctness the product's foundation, not an implementation
detail. The self-hosted board (`engineering-board/eb-self/`, 61 bugs) proves the
loop works; this audit asks whether it works **under the concurrency it sells**.

## 2. Opportunity map (impact × effort)

| | **Low effort (S)** | **Medium (M)** | **Large (L)** |
|---|---|---|---|
| **High impact** | E4 server-hang + lock-leak · E5 SessionStart O(tree) | E1 lock+atomic mutation · E2 id-alloc race · E3 reclaim-across-machines · E6 one counter | — |
| **Med impact** | E9 input-handling sweep · E10 lifecycle-blind status | E7 consolidation integrity · E11 whole-board re-parse · E12 coordination observability · E13 failure-interaction tests | — |
| **Focused** | E8 frontmatter round-trip fixes | — | — |

## 3. Top 5 quick wins (~a day or less each)

1. **E4a — give the MCP claim/release calls a `subprocess` timeout.** One wedged or
   slow (OneDrive) claim script currently hangs the single-threaded server for
   *every* client, forever. One keyword.
2. **E5 — prune the SessionStart `in_progress` scan.** It re-introduces the exact
   O(tree) 10s-hook-timeout the adjacent code already fixed once, and double-counts
   after any `/board-migrate`.
3. **E9 — the input-handling straggler sweep (their own L005).** Three lone sites
   diverge from the safe pattern used everywhere else: a path interpolated into
   python source (fails open), an unanchored id `grep`, and the one deprecated
   `utcnow()`. Fix the class + add lint rules so they can't recur.
4. **E6 — one shared scratch counter.** Two implementations disagree and neither
   counts findings (that's B057). Dedupe to one helper — fix it at the class, not
   the site.
5. **E10 — lifecycle-aware status lines (their own L002).** Stop telling users to
   "investigate root cause" on patterns whose bugs are already resolved, and stop
   flagging a healthy board as corrupt after a learning is promoted.

## 4. Top 3 big bets

1. **Make "collision-free / two servers, one board" actually true (E1 + E2 + E3 +
   E4).** Enforce the claim lock on the *mutating* tools, write entries atomically,
   serialize id allocation, and fix reclamation for the multi-machine + MCP-only
   scenarios it was built for. This is the foundation the Conductor supervisor
   (ROADMAP RM-15) will stand on — shipping more autonomy on top of an unlocked
   mutation path multiplies the blast radius.
2. **One coordination-state engine, and surface it (E6 + E10 + E12).** Collapse the
   divergent counters/formatters/status-readers into a single source, then add a
   **Coordination** panel to `/board-view` (twin of the Learnings panel) over data
   that already exists (`_claims/`, `_reclaimed.log`, `active-workers.json`).
   Observability is the product's *stated* open differentiator vs the headless
   sibling systems (state.md, Conductor thread) — today it's logged but invisible.
3. **Test the failure interactions, then extend (E13 + RM-16).** The coordination
   tests validate happy paths in isolation; none exercises acquire↔reclaim
   together, the mtime-vs-content divergence, or a concurrent-create race. Apply the
   board's own top Learning (L001, "ship every guard with a test that drives its
   real call-sites") to the core **before** RM-4 (ungate the loop) and RM-15 build
   more on it.

## 5. Full opportunity list

### E1 — Mutating tools don't hold the claim lock, and entry writes aren't atomic
- **Tag/lens:** FIX · fixes & felt debt / concurrency
- **Evidence:** `board_update_entry` (`mcp-server/engineering_board_mcp.py:751-823`)
  never references `_claims`/owner/lock (verified) and rewrites the entry with a
  truncating `open(path, "w")` (`:822-823`) — no temp-file + `os.replace`, no
  `fsync`. `board_create_entry:654` and `rebuild_board` (`:915`) do the same for
  entry files and `BOARD.md`. The claim scripts guard *who works* an entry; nothing
  guards *who writes* it.
- **Failure scenario:** (a) *Lost update* — two clients (or a worker holding the
  B001 claim + any other writer) both read B001, both write; the second clobbers the
  first's appended section. Holding a `board_claim` does **not** prevent this — no
  mutating tool consults the lock, so the claim gives *false* mutual exclusion for
  edits. (b) *Torn write* — a crash or ENOSPC between truncate and full write leaves
  the entry file (the source of truth) empty/partial, and it vanishes from `BOARD.md`
  on the next rebuild.
- **Proposal:** mutators acquire/verify the entry's claim (or a short-lived write
  lock) before writing; write via temp file + `os.replace` (atomic) + `fsync`. The
  `mkdir`-lock idiom already exists in `board-active-workers-register.sh:79` — reuse
  it.
- **Why it matters:** this is the core "collision-free" guarantee (VP3) and the
  "two servers, one board" story (Q001). The entry file *is* the database.
- **Effort:** M · **Impact:** High · **Risks:** keep the single-client path fast;
  add the lock/atomicity tests per L001.

### E2 — Entry-id allocation is unsynchronized → duplicate ids under concurrent creation
- **Tag/lens:** FIX · concurrency
- **Evidence:** `next_id` is "max existing + 1" with no lock in **both** the MCP
  server (`engineering_board_mcp.py:387-404`, called at `:559`) and the plugin
  consolidator (`hooks/scripts/board-consolidate.sh:193`). The only create-time
  guard is `os.path.isfile(path)` (`:652`), keyed on `id+slug`, not the id.
  `find_entry` returns the **first** id match (`:380-384`), and `load_entries`
  silently drops unreadable files (`:365`, which can also make `next_id` under-count).
- **Failure scenario:** two `board_create_entry(type=bug)` calls on the same board
  (the advertised multi-client model) both compute `B058`; different titles →
  different filenames → both pass the `isfile` check → **two entries share id B058**.
  Every id-keyed operation then silently targets only one of them: a claim on
  `_claims/B058/` locks both, `blocked_by: B058` is ambiguous, supersession
  mis-groups.
- **Proposal:** serialize allocate→write under the `mkdir` lock, or allocate the id
  by atomically `mkdir`-ing it (claims already prove this primitive works); make
  `find_entry` assert uniqueness and warn on collision.
- **Effort:** M · **Impact:** High · **Risks:** low.

### E3 — Stale-claim reclamation is broken for the distributed + MCP scenarios it exists for
- **Tag/lens:** FIX · concurrency
- **Evidence (one cluster, three bugs):**
  1. **Wrong signal.** `reclaim-stale` decides staleness from `heartbeat.txt`
     **mtime** (`board-claim-reclaim-stale.sh:94`), but `acquire` decides it from the
     ISO timestamp *inside* `heartbeat.txt` (`board-claim-acquire.sh:113-128`).
     `heartbeat.sh` writes content + mtime together (`:33-34`), so they agree **only
     on a single machine**. Under cloud sync (OneDrive/Dropbox — the exact scenario
     the bumped thresholds target), a file's local mtime is its *sync-down time on
     the reclaimer's machine*, not when the owner heartbeated → dead claims are kept
     far too long; a live owner whose heartbeats are slow to sync can look stale.
  2. **Missing heartbeat = permanent lock.** `acquire` treats a missing/empty
     `heartbeat.txt` as stale → exit 2 (`:107-110`); `reclaim` treats it as
     `no_heartbeat_skipped` and **keeps** it (`:84-91`). The caller loops
     acquire→reclaim→acquire (`stop-hook-procedure.md:120`) and never removes it, so
     the entry is **permanently unclaimable**. Trigger: the acquirer is killed
     between its two separate writes — `owner.txt` then `heartbeat.txt`
     (`acquire.sh:140-146`).
  3. **No reclaim path through MCP.** There is no `board_reclaim` tool, and a
     pure-MCP client (Claude Desktop) runs none of the SessionStart hooks that
     reclaim; `tool_board_claim` maps exit 2 → `"stale"` and stops
     (`engineering_board_mcp.py:1052`). A stale claim is a **permanent dead-end** via
     MCP.
- **Proposal:** reclaim should parse the heartbeat **content** timestamp (one source
  of staleness truth, matching acquire); treat missing/empty heartbeat as reclaimable
  (mirror acquire); add a `board_reclaim` tool or auto-reclaim on `rc==2` inside
  `tool_board_claim`.
- **Why it matters:** VP3 + the cloud-sync feature + the MCP funnel all depend on
  reclamation, and it's wrong in precisely their scenarios.
- **Effort:** M · **Impact:** High · **Risks:** reclaim is destructive — gate on the
  acquire↔reclaim interaction test (E13/L001).

### E4 — Coordination writes can hang or wedge the whole system
- **Tag/lens:** FIX · reliability / concurrency
- **Evidence:** (a) the MCP `subprocess.run` for claim/release has **no `timeout=`**
  (`engineering_board_mcp.py:1060`, `:1083`) and the stdio loop is single-threaded
  (`:1435`) — one wedged/slow child blocks *all* clients indefinitely. (b) the
  `active-workers` `mkdir`-lock has **no stale-lock breaker**
  (`board-active-workers-register.sh:79-86`, `-bump.sh`, `-cleanup.sh:42`): a writer
  SIGKILLed between `mkdir "$LOCK_DIR"` and its `trap … rmdir` leaks the lock with no
  age check, so every later register/bump/cleanup fails after 5×0.1s **forever** —
  worker-liveness + heartbeat tracking silently dies project-wide until someone
  manually `rmdir`s it.
- **Failure scenario:** board on a stalled network/OneDrive mount → `board_claim`
  never returns → server stops answering every client; or a timed-out PM turn leaks
  the registry lock → no worker is ever tracked again.
- **Proposal:** add `timeout=` to the two `subprocess.run` calls (S); add an
  mtime-based stale-lock breaker to the active-workers lock, mirroring the claim
  staleness logic.
- **Effort:** S · **Impact:** Med-High · **Risks:** low.

### E5 — SessionStart re-introduces the O(tree) hook-timeout it already fixed once
- **Tag/lens:** FIX · performance
- **Evidence:** `board-session-start.sh:100` runs
  `grep -rl "^status: in_progress" "$BOARD_DIR" --include=*.md` over the **whole
  tree**, while the blocking-map python 30 lines below deliberately skips
  `_sessions/`, `_archive/`, `_claims/`, `_migrate-snapshot/` (`:128-129`) —
  precisely because of the documented 1200-entry/15s blowout past the 10s hook
  timeout (`:112-118`). After `/board-migrate --apply`,
  `_migrate-snapshot/pre-migrate/` holds a full copy of every entry, so (a) each real
  `in_progress` entry is reported **twice** (with a snapshot path), and (b) the scan
  re-reads the doubled tree plus all `_sessions/` JSON on every SessionStart. The
  pattern-cluster `grep -r` at `:163` is unpruned too.
- **Proposal:** apply the same skip-dir prune to both greps.
- **Effort:** S · **Impact:** Med (SessionStart is the most-seen surface, on a
  timeout budget) · **Risks:** low.

### E6 — Two divergent scratch counters, neither counting findings (B057 is the symptom)
- **Tag/lens:** FIX/IMPROVE · synergy / feedback & state
- **Evidence:** `board-session-start.sh:177` counts **files** (`find … | wc -l`,
  labeled "session file(s)"); the MCP `count_scratch_findings`
  (`engineering_board_mcp.py:1017`) counts `## ` headers + `<!-- ts -->` comment
  lines — but one plugin-written block is a single `<!-- ts -->` comment carrying a
  multi-element `findings` array, so it counts 1 for N findings (**this is B057**).
  Two implementations, two answers, and neither equals the true finding count.
- **Proposal (their own L005 — "fix the class across every site at once"):** one
  shared counter that parses each block's `findings` array, called by both the banner
  and `board_status`. Fixes B057 in one place and removes the drift permanently.
  (Refines board RM-2/B057 by attacking the duplication, not one site.)
- **Effort:** S-M · **Impact:** Med · **Risks:** low.

### E7 — Consolidation data-integrity: lossy supersession + a parse→archive window
- **Tag/lens:** IMPROVE · fixes & felt debt
- **Evidence:** (a) supersession archives the earlier of two same-`(type, affects)`
  findings whenever the later's title is **strictly longer**
  (`board-consolidate.sh:308-321`; intended and tested — `tests/smoke/automated.sh:10`,
  `tests/orchestration/pm-loop.sh:104`). Title length is a weak proxy for
  "supersedes": two genuinely distinct bugs in the same file, one with a longer
  title, and the real shorter-titled bug is **silently archived** (only *differing*
  affects is safeguarded, T2b). (b) findings appended to a session file after the
  parse (`:248`) but before the Stage-5 archive move (`:394-410`) are archived
  **unpromoted** — silent loss; same root cause as E2 (no consolidation lock).
- **Proposal:** require a stronger supersession signal (an explicit `supersedes:`
  field, or high title/affects overlap — not length), or at minimum surface
  `archived_superseded` on the banner the way reclaims are surfaced; take the
  consolidation lock (E2) to close the archive window.
- **Effort:** M · **Impact:** Med · **Risks:** changing supersession touches tested
  behavior — update the AC + fixtures in step.

### E8 — Frontmatter round-trip corruptions
- **Tag/lens:** FIX · fixes & felt debt
- **Evidence:** (a) `_parse_scalar` treats **any** `[...]` value as a list
  (`engineering_board_mcp.py:300-306`), so a title `[URGENT]` round-trips to
  `["URGENT"]` and `rebuild_board` renders `[['URGENT']](…)` in `BOARD.md` (`:849`)
  — verified. (b) a missing closing `---` makes `parse_frontmatter` return `{}`
  (`:287`), so `id`/`type`/`status` are lost and the entry drops out of
  `find_entry`/`board_status`/`BOARD.md`. (c) a pre-existing duplicate frontmatter
  key is re-emitted **twice** after any update (order loop `:799-802` doesn't dedupe).
  (d) non-UTF-8 entry bytes are read with `errors="replace"` then fully rewritten
  (`:751`, `:822`), permanently corrupting the original on any update — even a
  status-only change.
- **Proposal:** quote scalars that look like lists on write (or only list-parse
  known list fields); tolerate a missing closing fence; dedupe keys on re-emit;
  preserve bytes (or refuse to rewrite an undecodable file).
- **Effort:** S-M · **Impact:** Med · **Risks:** low.

### E9 — Input-handling stragglers (their own L005, not yet applied)
- **Tag/lens:** FIX · friendliness / robustness
- **Evidence:** (a) `board-stop-gate.sh:24-31` interpolates the board path into
  python **source** (`json.load(open('$MODE_FILE'))`) — the *only* script that does
  this instead of passing `argv` (compare `board-session-start.sh:32`); a project
  path with an apostrophe (`/…/Rhen's board/…`) is a SyntaxError, swallowed by
  `2>/dev/null || true`, so `MODE` is empty and the paused gate **fails open**.
  (b) `board-validate-entry.sh:127` uses an unanchored `grep -q "${entry_id}"`, so
  `B1` matches `B12`/`B100` — the "index must list this id" guard silently no-ops for
  any id that is a prefix of another. (c) `datetime.utcnow()` is the lone deprecated
  timestamp call, at `board-claim-acquire.sh:68` (all 9 other sites use
  `datetime.now(timezone.utc)`); `tests/crosscompat-lint.sh` doesn't catch it.
- **Proposal:** one sweep — `argv` not interpolation; anchor the id grep; `utcnow` →
  `now(timezone.utc)`; add crosscompat-lint rules for `utcnow` and python-source
  path-interpolation so the class can't recur.
- **Effort:** S · **Impact:** Low-Med · **Risks:** low.

### E10 — Lifecycle-blind status surfaces (their own L002, not yet applied)
- **Tag/lens:** FIX · feedback & state
- **Evidence:** (a) the SessionStart "SYSTEMIC PATTERNS (3+ open entries)" cluster
  (`board-session-start.sh:163-166`) never filters `status:`, but resolved entries
  stay in place — so a pattern last seen across long-closed bugs is reported as an
  active cluster telling the user to "investigate root cause before fixing" already
  done work. (b) `board-index-check.sh:39` counts `learnings/` files against `- L###`
  `BOARD.md` rows, but `board-curate-learnings.sh` writes a learning file **without**
  a `BOARD.md` row → a healthy board can be flagged corrupt (PLAUSIBLE — confirm by
  promoting a learning then running `board-index-check.sh`). (c) `board-consolidate.sh`
  documents exit 2 ("partial — some scratch deferred") but never emits it —
  `EXIT_CODE=0` is set once and never reassigned (`:92`, `:415`), so callers branching
  on partial promotion never see it.
- **Proposal:** filter `status: resolved` in the pattern grep; make the learnings
  invariant match how the curator actually writes; capture the per-board python exit
  into `EXIT_CODE`.
- **Effort:** S · **Impact:** Low-Med · **Risks:** low.

### E11 — Whole-board re-parse on every MCP entry call
- **Tag/lens:** IMPROVE · performance
- **Evidence:** `board_update_entry` calls `find_entry` (reads **all** entries via
  `load_entries`), then re-opens and re-reads the target file (`:751`, discarding the
  copy `find_entry` already parsed), then `rebuild_board` reads all files a third time
  (`:825`). `board_get_entry` likewise does an O(n) scan + a re-read. ~2× full-board
  reads per update, which also widens the E1 TOCTOU window.
- **Proposal:** have `find_entry` return the parsed entry (it already has `_path` +
  parsed frontmatter) and reuse it; drop the redundant re-read.
- **Effort:** M · **Impact:** Low-Med (scales with board size) · **Risks:** low.

### E12 — The coordination story is logged but invisible — and observability is the stated bet
- **Tag/lens:** NEW · synergy / engagement
- **Evidence:** reclaim writes `_claims/_reclaimed.log` (`board-claim-reclaim-stale.sh:130-135`),
  surfaced **only** as a transient turn-line (`stop-hook-procedure.md:120`) — never in
  `board-view.sh`, `board_status`, or metrics. The raw data already exists on disk:
  `_claims/` (who holds what), `_reclaimed.log`, `active-workers.json`,
  `consolidation.log`, `tidy.log`. state.md's Conductor thread states the product's
  open differentiator vs the headless sibling systems is **observability** — yet the
  one destructive automatic action (reclaiming another session's lock) and the whole
  multi-agent coordination picture are invisible after the turn they happen.
- **Proposal:** a **Coordination** panel in `/board-view` (twin of the existing
  Learnings panel) + a `board_status` field: current claims, recent
  reclaims/contention, active workers. Pure read over data that already exists.
- **Effort:** M · **Impact:** Med · **Risks:** low.

### E13 — The coordination tests validate the happy path, not the failure interactions (their own L001)
- **Tag/lens:** IMPROVE · fixes & felt debt / test-coverage
- **Evidence:** `tests/claims/` covers an acquire race (`race-acquire.sh`, 20 iters),
  heartbeat refresh (`heartbeat-refresh.sh` — which hand-builds the claim dir and
  asserts *mtime* advances, validating the very signal E3.1 mis-uses), reclaim
  fixture classification (`reclaim-stale.sh`), release owner-check, and
  OneDrive-detection. **None** exercises acquire↔reclaim on the same claim (E3.2
  livelock), the mtime-vs-content divergence (E3.1), or a concurrent-create race
  (E2). `/board-run` has only a structural lint (IMPROVEMENTS #9 / RM-16). L001 —
  "ship every deterministic guard with a test that drives its real fixtures and
  call-sites" — is the board's own top Learning.
- **Proposal:** add interaction tests (acquire → delete `heartbeat.txt` → assert
  reclaim removes it and re-acquire succeeds; two-process create race asserts distinct
  ids); extract `/board-run`'s claim/loop into a testable driver (RM-16), which also
  de-risks RM-4 and RM-15.
- **Effort:** M · **Impact:** Med (regression safety for E1–E4) · **Risks:** low.

## 6. The pattern worth naming: five Learnings, five fresh violations

The board has earned five committed Learnings. The engine — audited here for the
first time — violates each one in a place the prior surface-level passes never
reached. This is the strongest signal that the *next* structural investment is
internalizing these in the core, not adding features on top:

| Learning | Fresh engine violation found here |
|---|---|
| **L001** — guards need tests at their real call-sites | E13: claim guards tested in isolation; acquire↔reclaim + create-race untested |
| **L002** — invariants must respect the open-vs-resolved lifecycle | E10a: systemic-pattern count includes resolved entries; E10b learnings invariant |
| **L003** — the newest surface carries the most risk | The MCP multi-client surface (newest) holds the worst concurrency bugs: E1, E2, E3.3, E4a |
| **L004** — a denylist is never done | (Reject-filter corpus is strong — no new bypass found; the one clean pass this round) |
| **L005** — fix an input-handling class across every site at once | E9: three lone stragglers (source-interpolation, unanchored grep, `utcnow`) + E6 two divergent counters |

## 7. Suggested sequence — if only three ship first

1. **E4 + E5 (the quick, high-impact reliability wins).** A `subprocess` timeout, an
   active-workers stale-lock breaker, and a pruned SessionStart grep remove two
   silent-wedge failure modes and a latent hook-timeout — hours of work, no
   architectural risk, immediate trust.
2. **E1 + E2 + E3 (make the marketed guarantee true).** Enforce the claim lock on
   mutation, write atomically, serialize id allocation, and fix reclamation for the
   multi-machine + MCP scenarios. This is the coordination core; everything
   autonomous the roadmap wants (RM-4 ungate, RM-15 Conductor) compounds on it.
3. **E13 + RM-16 (lock the wins in).** Add the failure-interaction tests and extract
   the `/board-run` driver **before** building more automation — the board's own L001
   applied to its own core. E6/E10/E12 follow as the coordination-state cleanup +
   observability layer.

---

_Report only — no code changed. **Which items should I build?** My recommendation:
take E4 + E5 immediately (a half-day, pure trust), then scope E1–E3 as the "harden
the coordination core" milestone that must land before the Conductor supervisor
(RM-15). The surface-level roadmap (ROADMAP.md RM-1…RM-17) and this engine audit are
complementary halves — E1–E3 are the missing prerequisite under RM-4 and RM-15._

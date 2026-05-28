# Next-phase recommendations

A prioritized list of what to build next, derived from a full structural audit of the v0.2.2 codebase against the v0.3.0 consensus plan (`.omc/plans/engineering-board-v3-consensus-plan.md`) and the test-coverage matrix.

The audit found **zero broken references** and **two minor doc drifts** (already fixed in the same commit that added this file). The codebase is internally coherent — the work below is about closing the gap between what's shipped and what's tested, then executing the planned v0.2.3 and v0.3.0 milestones.

---

## Tier 1 — Integration tests for v0.2.2 (highest ROI, lowest risk)

The v0.2.2 PM and Worker pipelines shipped, but `tests/modes/` only covers their **frontmatter lint**. The full end-to-end loops have never been exercised by the test suite. Every other test domain (claims, smoke, permissions) has automated coverage; the orchestration layer is the gap.

### 1.1 PM pipeline end-to-end test
- New: `tests/orchestration/pm-loop.sh`
- Plant a synthetic board with seeded `_sessions/<id>.md` scratch
- Set `session-mode.json` to `pm`
- Drive one Stop cycle (mock or real)
- Assert: scratch promoted to live (anchor-verified survivors only), superseded entries archived, `consolidation.log` complete, `<<EB-PM-CONTINUE>>` emitted
- Validates the chain: `finding-extractor` → `consolidator` → `tidier` → `learnings-curator`

### 1.2 Worker pipeline end-to-end test (per discipline)
- New: `tests/orchestration/worker-tdd-loop.sh`, `worker-review-loop.sh`, `worker-validate-loop.sh`
- Plant entries with `needs: tdd` / `needs: review` / `needs: validate`
- Set `session-mode.json` to `worker, discipline: <d>`
- Drive Stop cycles until `<<EB-WORKER-NOTHING-TO-DO>>`
- Assert: claim acquired before each dispatch, `needs:` field rewritten per `suggested_next_needs`, claim released after, no orphan `_claims/` directories
- Validates the `tdd → review → validate → resolved` state machine

### 1.3 Multi-worker contention test
- New: `tests/orchestration/multi-worker-contention.sh`
- Two concurrent worker sessions on the same discipline pool
- Assert: every entry is worked exactly once, no double-dispatch, no orphan claims after both sessions complete
- Validates the atomic-claim contract under real concurrency (not just `claims/race-acquire.sh` which tests at the script level)

### 1.4 Tests for two untested commands
- `/board-rebuild`: assert BOARD.md and GRAPH.yml deterministic regeneration; drift detection; auto-resolve terminal pass
- `/board-graph`: assert deterministic graph output; cluster/bridge/isolated-node correctness on fixture boards

---

## Tier 2 — Ship v0.2.3 (Resilience)

Per the consensus plan (`.omc/plans/engineering-board-v3-consensus-plan.md`, lines 230–268). Required when PM and Worker sessions run for hours and one crashes mid-turn.

### 2.1 Active-workers registry
- New agent: `agents/active-workers-registry.md` — tracks `{session_id, mode, discipline, started_at, last_heartbeat}` for every active PM/Worker session
- New scripts: `hooks/scripts/board-active-workers-register.sh` (on `/pm-start` / `/worker-start`) and `hooks/scripts/board-active-workers-cleanup.sh` (on Stop with no continuation)
- Persists to `docs/boards/_active-workers/<session-id>.json`

### 2.2 PM fallback heartbeat
- New script: `hooks/scripts/board-pm-fallback-heartbeat.sh`
- If a PM session goes offline (no heartbeat for 5 minutes), the next session that starts in PM mode picks up its un-consolidated scratch and runs catch-up consolidation
- Wired into the PM section of `stop-hook-procedure.md` as a pre-flight step

### 2.3 Wire `board-claim-heartbeat.sh`
- Currently reserved but not invoked. Workers that take longer than the stale threshold (180s baseline, 300s cloud-sync) will have their claims reclaimed mid-work
- Add heartbeat refresh to long-running operations inside `tdd-builder` / `code-reviewer` / `validator` (e.g., before/after every Bash invocation)

### 2.4 `paused: true` board-level field
- Already documented in the plan (lines 130–145) but not implemented
- Adds a per-board pause registry so an operator can pause a single project's PM pipeline without affecting others

---

## Tier 3 — Ship v0.3.0 (Learning entity)

Per the consensus plan (lines 269–276). The `learnings-curator` agent is currently a stub — full implementation requires:

### 3.1 Learning entry type (`L###`)
- New entry type in `frontmatter-schema.md`
- New subdirectory: `docs/boards/<project>/learnings/`
- New fields: `derived_from: [B001, B007, F003]` (pattern across resolved entries), `confidence`, `applies_to`

### 3.2 `learnings-curator` implementation
- Reads `tidier`'s `patterns{}` output (already shipped)
- Promotes recurring patterns to `learnings/L###-<slug>.md`
- Cross-references original entries

### 3.3 `/board-migrate` command
- One-shot migration: scans existing `observations/` for ones that should have been `learnings`; offers operator-confirmed reclassification
- Updates BOARD.md indexing accordingly

### 3.4 SessionStart surfaces top learnings
- `board-session-start.sh` extension: show top 3 high-confidence learnings relevant to the current working directory's `affects:` prefix
- Closes the loop: capture → consolidate → tidy → learn → inform next session

---

## Tier 4 — Quality of life

Lower priority but high value once Tiers 1–3 are stable.

### 4.1 Single CI runner
- New: `tests/run-all.sh` that invokes every `automated.sh` + the lint and reports a single pass/fail
- Required for any CI integration (GitHub Actions, etc.)

### 4.2 Cross-platform script audit
- Plan commits to bash + python3 portability for 13 scripts (lines 145–165) but there is no automated cross-platform lint
- Borrow the `crosscompat-lint.ps1` pattern from prior work: detect literal-backslash path constructions, hardcoded drive letters, CRLF shebangs

### 4.3 Plugin version coherence check
- The v0.2.2 work shipped without a `plugin.json` version bump until this audit. Add a hook or pre-push check that flags when `agents/`, `commands/`, or `hooks/` change without a corresponding `plugin.json` version delta.

### 4.4 Document mode-transition semantics
- What happens when a Worker session calls `/pm-start`? When a PM session calls `/worker-start`? Currently undocumented; the `session-mode.json` is just overwritten
- Either document the override semantics explicitly or add a guard that requires `/board-pause` first

---

## Decision recommended

The cleanest sequencing is **Tier 1 → Tier 2 → Tier 3**, with Tier 4 items pulled in as they become blocking.

Tier 1 is the highest ROI because (a) it locks in the v0.2.2 contract before it's exercised in anger, (b) it catches the kind of integration bugs the consensus plan's pre-mortems flagged as most likely (claim contention, supersession edge cases, PM-Worker mode collisions), and (c) it gives the v0.2.3 and v0.3.0 work a regression net to land on.

The Tier 1 work is also the most parallelizable: each test can be drafted by an independent worker session driving the just-shipped Worker pipeline on this very repo — the dogfooding loop closes on itself.

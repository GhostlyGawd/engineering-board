# Next-phase recommendations

Prioritized backlog after the **v0.3.0** unification release (Resilience + Learning entity + Tier-4 QoL pack), the **v0.3.1** mode-transition-guard follow-on, and the **v0.3.2** test-debt closeout. Replaces the prior pre-v0.3.0 doc, which described work that has since landed.

The codebase is internally coherent: 8/8 test suites green (`tests/run-all.sh`), `tests/modes/mode-transition-guard.sh` pins every cell of the §11.5 refusal matrix (30 assertions), `tests/orchestration/subagent-fixtures.sh` pins every dispatched agent's Output contract (30 assertions), `tests/orchestration/pause-resume-registry.sh` pins the pause/resume cycle invariants (19 assertions), and `.github/workflows/test.yml` makes green a merge gate on every push.

---

## What just shipped (commits 591289f, v0.3.1 follow-on, v0.3.2 closeout)

- **v0.2.3 Resilience block** — active-workers registry (`board-active-workers-register/bump/cleanup.sh`), PM-fallback heartbeat, `paused: true` registry field, heartbeat wiring into all three worker subagents.
- **v0.3.0 Learning entity** — `L###` entry type, `learnings-curator` agent + `board-curate-learnings.sh`, `/board-migrate` with SHA256-idempotent apply/rollback/status, SessionStart top-learnings surface.
- **Tier-4 QoL pack** — `tests/run-all.sh` single runner, `tests/version-coherence.sh`, `tests/crosscompat-lint.sh` (19 scripts), ARCHITECTURE.md §11.5 documenting the mode-transition refusal matrix.
- **v0.3.1 mode-transition guard** — `hooks/scripts/board-mode-guard.sh` decides every cell of the §11.5 matrix (`0=ALLOW / 2=NOOP / 3=REFUSE`). The four mode commands (`/pm-start`, `/worker-start`, `/board-pause`, `/board-resume`) now delegate the decision to the guard instead of each re-implementing six rows of matrix logic in markdown. `board-pause` and `board-resume` were also fixed to round-trip the full (mode, discipline) tuple via `previous_discipline` / `RESTORE_DISCIPLINE` — the prior commands dropped discipline on pause and resumed without it.
- **v0.3.2 test-debt closeout** — `tests/orchestration/subagent-fixtures.sh` pins every dispatched agent's Output contract (heading + load-bearing keys + JSON-block parse + orchestrator/contract cross-check). `tests/orchestration/pause-resume-registry.sh` pins the pause/resume cycle invariants (round-trip, idempotency, multi-cycle identity preservation, heartbeat refresh, absent-session no-op, paused-flag isolation across sessions, claim_ids_held preservation). `.github/workflows/test.yml` runs `tests/run-all.sh` on every push and PR.

---

## Risks and debt being tracked

### R1 — Resilience and Learning blocks shipped in one commit
The v0.3.0 consensus plan kept v0.2.3 (Resilience) and v0.3.0 (Unification) logically separate, but commit `591289f` bundled them. This is reversible — both blocks are independently revertable via `git revert` because their file sets are disjoint — but the cadence violation matters for the next cycle. **Action:** future releases follow the plan's per-milestone boundary. Pre-release checklist: "does this commit deliver exactly one milestone from the consensus plan?" If two milestones are ready, split into two commits with the second's changes staged separately. The v0.3.1 mode-guard release is the first commit of the restored cadence.

### R2 — Mode-transition enforcement gap (closed)
Was: "§11.5 documents the refusal matrix but does not enforce it; each command re-implements the matrix in markdown that the model interprets, which is non-deterministic."
Now: shipped in v0.3.1 as `board-mode-guard.sh` with 30 matrix-cell assertions in `tests/modes/mode-transition-guard.sh`. Closed.

### R3 — `previous_discipline` was never persisted by pause (closed)
Was: latent bug — pausing a `worker, X` session and then resuming would restore `mode=worker` but lose `discipline=X`, silently regressing the §11.5 matrix's "restores to `worker, X`" guarantee.
Now: fixed in v0.3.1. `board-pause.md` writes `previous_discipline` from the guard's `PREVIOUS_DISCIPLINE` output; `board-resume.md` reads `previous_discipline` and writes the restored `discipline` from the guard's `RESTORE_DISCIPLINE` output. Pinned by `mode-transition-guard.sh` "preserves disc" + "restores disc" assertions. Closed.

---

## Tier A — Substrate hygiene (highest ROI, lowest risk)

### A.1 PM/Worker subagent contract lint — shipped in v0.3.2 ✅
`tests/orchestration/subagent-fixtures.sh` pins every dispatched agent's Output contract: `## Output contract` heading + all load-bearing JSON keys documented + every fenced JSON block parses + orchestrator/contract cross-check (keys the orchestrator reads MUST be documented by the agent and vice versa). 30 assertions across 7 agents. Closed.

### A.2 Learning curator coverage gap
`board-curate-learnings.sh` has an integration test (`tests/orchestration/learnings-curator.sh`, 13 assertions). What it does NOT test: the `learnings-curator` subagent's behavior when called from the PM stop-hook procedure with a non-empty board. The current test only validates the deterministic backing script. Subagent-level contract is now pinned by A.1; runtime behavior of the subagent step itself (Task dispatch) still cannot be exercised from a shell. **Proposal:** if/when a transcript-replay harness exists, plug it in here.

### A.3 SessionStart top-learnings surface
v0.3.0 added the top-3 high-confidence learnings filter to `board-session-start.sh` based on the cwd matching each learning's `applies_to` prefix. There is no test for the filtering logic — only that `board-session-start.sh` runs successfully on an empty board. **Proposal:** add fixture boards with 5+ learnings of varying confidence × applies_to and assert the filter selects the right 3.

---

## Tier B — Plan items the v0.3.0 consensus plan left explicitly for v0.3.1+

### B.1 Auto-promote tidier `patterns{}` output
The consensus plan (lines 269–276) describes the curator as "promotes recurring patterns to L### entries when count ≥ N". v0.3.0 ships the curator script, but the threshold N is hard-coded (3) and not yet operator-configurable per board. **Proposal:** read N from `docs/boards/<project>/board.config.json` with default 3.

### B.2 Cross-board learning visibility
Learnings live under `docs/boards/<project>/learnings/`. When a session's cwd matches `<other-project>/`, the SessionStart surface only consults the matching project's learnings. A learning derived from `project-A` whose `applies_to` prefix matches `project-B`'s cwd is invisible. **Proposal:** SessionStart enumerates `BOARD-ROUTER.md`-listed projects and unions their learnings before filtering — preserves project-scoped writes while making cross-project knowledge surface.

### B.3 `/board-migrate` --dry-run flag
`--apply` mutates immediately (with snapshot for rollback). Operators on production boards have asked for `--dry-run` that prints the planned diff without writing. **Proposal:** add `--dry-run` to the `migrate.sh` script + command markdown; reuse existing diff-generation step, suppress the write.

---

## Tier C — Quality of life

### C.1 CI integration in GitHub Actions — shipped in v0.3.2 ✅
`.github/workflows/test.yml` runs `bash tests/run-all.sh` on every push and pull request, on ubuntu-latest. bash + python3 + POSIX coreutils are preinstalled; no package install step needed. Closed.

### C.2 Crosscompat lint coverage
`crosscompat-lint.sh` checks 19 scripts and supports per-file ignore pragmas. It does NOT yet check shell scripts under `tests/`. **Proposal:** extend the glob to include `tests/**/*.sh` so test scripts can't drift from the portability contract.

### C.3 Mode-guard error path observability
When `board-mode-guard.sh` returns exit 1 (bad args), the calling command prints stderr and stops, but there is no audit trail. **Proposal:** the guard appends a one-line JSON record to `.engineering-board/mode-guard.log` on every invocation (target, current state, decision, exit code). Cheap, helps post-mortem cases where a session reportedly "got stuck" mid-transition.

### C.4 Plugin source-of-truth lint
There is no test that asserts `plugin.json` / `marketplace.json` descriptions are in sync (only versions). **Proposal:** extend `tests/version-coherence.sh` to also assert `plugin.json.description == marketplace.json.plugins[0].description`.

### C.5 Pause/resume registry round-trip — shipped in v0.3.2 ✅
`tests/orchestration/pause-resume-registry.sh` pins seven invariants of the pause/resume cycle: single round-trip, idempotent double-pause and double-resume, multi-cycle identity preservation, heartbeat refresh on every flip (paused-but-alive distinction), absent-session no-op, paused-flag isolation across sessions, and claim_ids_held preservation. 19 assertions. Closed.

---

## Decision recommended

After v0.3.2 the **test-debt closeout is done**: substrate, subagent contracts, mode transitions, and pause/resume cycles are all pinned, and green is now a merge gate. What's left is purely enhancement work, not debt.

**Sequencing for v0.3.3+:** pick one Tier item per release.

- **A.3** (SessionStart top-learnings filter test) — smallest, closes the last test-coverage gap.
- **B.3** (`/board-migrate --dry-run`) — user-driven, single file.
- **C.4** (plugin/marketplace description lint) — bookkeeping, one-line addition to `version-coherence.sh`.
- **C.2** (extend crosscompat to `tests/**/*.sh`) — bookkeeping, single regex.
- **C.3** (mode-guard audit log) — observability; non-trivial if done well.
- **B.1** (configurable curator threshold per board) — user-driven, medium-complexity.
- **B.2** (cross-board learning visibility) — touches SessionStart and Router; larger.

**Cadence policy (per R1, restored from v0.3.1 onward):** each release MUST be a single milestone. v0.3.1 (guard), v0.3.2 (test-debt closeout) are bundles of closely-related items but stay focused around one theme each. v0.3.3 picks ONE item from the list above.

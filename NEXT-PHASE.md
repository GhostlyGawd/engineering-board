# Next-phase recommendations

Prioritized backlog after the **v0.3.0** unification release (Resilience + Learning entity + Tier-4 QoL pack) and the **v0.3.1** follow-on (mode-transition guard). Replaces the prior pre-v0.3.0 doc, which described work that has since landed.

The codebase is internally coherent: 8/8 test suites green (`tests/run-all.sh`), `tests/modes/mode-transition-guard.sh` pins every cell of the §11.5 refusal matrix (30 assertions), and `version-coherence.sh` + `crosscompat-lint.sh` keep manifest and portability invariants.

---

## What just shipped (commits 591289f and the v0.3.1 follow-on)

- **v0.2.3 Resilience block** — active-workers registry (`board-active-workers-register/bump/cleanup.sh`), PM-fallback heartbeat, `paused: true` registry field, heartbeat wiring into all three worker subagents.
- **v0.3.0 Learning entity** — `L###` entry type, `learnings-curator` agent + `board-curate-learnings.sh`, `/board-migrate` with SHA256-idempotent apply/rollback/status, SessionStart top-learnings surface.
- **Tier-4 QoL pack** — `tests/run-all.sh` single runner, `tests/version-coherence.sh`, `tests/crosscompat-lint.sh` (19 scripts), ARCHITECTURE.md §11.5 documenting the mode-transition refusal matrix.
- **v0.3.1 mode-transition guard** — `hooks/scripts/board-mode-guard.sh` decides every cell of the §11.5 matrix (`0=ALLOW / 2=NOOP / 3=REFUSE`). The four mode commands (`/pm-start`, `/worker-start`, `/board-pause`, `/board-resume`) now delegate the decision to the guard instead of each re-implementing six rows of matrix logic in markdown. `board-pause` and `board-resume` were also fixed to round-trip the full (mode, discipline) tuple via `previous_discipline` / `RESTORE_DISCIPLINE` — the prior commands dropped discipline on pause and resumed without it.

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

### A.1 PM/Worker subagent layer tests (LLM-dispatched layer is still uncovered)
The `tests/orchestration/` suite exercises the deterministic substrate (claim acquire/release, consolidator, tidier, audit, registry, fallback heartbeat) by mocking the LLM-dispatched subagent step. The subagent layer itself (Task dispatch from the Stop hook into `consolidator` / `tdd-builder` / `code-reviewer` / `validator`) has no test harness — only frontmatter lint.
- **Proposal:** golden-input + golden-output fixtures per agent (one input scratch block + one expected output JSON shape), wired into a `tests/orchestration/subagent-fixtures.sh` runner that asserts the JSON-shape contract documented in each agent's body. Cannot exercise the real model; can pin the input/output contract so refactors to agent prompts can't silently break the JSON shape downstream.

### A.2 Learning curator coverage gap
`board-curate-learnings.sh` has an integration test (`tests/orchestration/learnings-curator.sh`, 13 assertions). What it does NOT test: the `learnings-curator` subagent's behavior when called from the PM stop-hook procedure with a non-empty board. The current test only validates the deterministic backing script. **Proposal:** add a fixture-driven `subagent-fixtures` entry for `learnings-curator` per A.1.

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

### C.1 CI integration in GitHub Actions
`tests/run-all.sh` exists (v0.3.0) but is not wired into a GitHub Actions workflow. **Proposal:** `.github/workflows/test.yml` invoking `bash tests/run-all.sh` on push and PR; cache python3 + bash.

### C.2 Crosscompat lint coverage
`crosscompat-lint.sh` checks 19 scripts and supports per-file ignore pragmas. It does NOT yet check shell scripts under `tests/`. **Proposal:** extend the glob to include `tests/**/*.sh` so test scripts can't drift from the portability contract.

### C.3 Mode-guard error path observability
When `board-mode-guard.sh` returns exit 1 (bad args), the calling command prints stderr and stops, but there is no audit trail. **Proposal:** the guard appends a one-line JSON record to `.engineering-board/mode-guard.log` on every invocation (target, current state, decision, exit code). Cheap, helps post-mortem cases where a session reportedly "got stuck" mid-transition.

### C.4 Plugin source-of-truth lint
There is no test that asserts `plugin.json` / `marketplace.json` descriptions are in sync (only versions). **Proposal:** extend `tests/version-coherence.sh` to also assert `plugin.json.description == marketplace.json.plugins[0].description`.

---

## Decision recommended

**Sequencing:** Tier A → Tier C → Tier B.

- Tier A closes the test-coverage gap that the v0.3.0 shipping cycle exposed (substrate has 11/11 integration tests; subagent layer has zero).
- Tier C is mostly bookkeeping but C.1 (GitHub Actions CI) is what turns `tests/run-all.sh` from a local convenience into a merge gate.
- Tier B items are user-driven enhancements to v0.3.0 features; they're real but lower-priority than the test debt above.

**Cadence policy (per R1):** the next release MUST be a single milestone. v0.3.2 = either Tier A (subagent fixtures), or Tier C.1 (CI), or a single Tier B item — never a bundle. The v0.3.0 bundle shipped because two milestones happened to be ready simultaneously; the next cycle restores the per-milestone cadence the plan locked in.

# Deep Interview Spec: engineering-board v0.3.0 — Autonomous PM + Worker Multi-Agent Evolution

## Metadata
- Interview ID: ei-engineering-board-v3-2026-05-11
- Rounds: 9 (Round 0 topology gate + Rounds 1–9 Socratic)
- Final Ambiguity Score: 20.5%
- Threshold: 20%
- Type: brownfield
- Generated: 2026-05-11
- Initial Context Summarized: yes (prompt-safe brownfield brief built from reading the v0.2.0 plugin source)
- Status: **PASSED — pending approval**
- Existing system inspected at: `C:\Users\rhenm\.claude\plugins\marketplaces\engineering-board\` (source, git repo) and `C:\Users\rhenm\.claude\plugins\cache\engineering-board\engineering-board\0.2.0\` (installed cache)

## Clarity Breakdown
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Goal Clarity | 0.82 | 0.35 | 0.286 |
| Constraint Clarity | 0.78 | 0.25 | 0.196 |
| Success Criteria | 0.76 | 0.25 | 0.190 |
| Context Clarity | 0.83 | 0.15 | 0.124 |
| **Total Clarity** | | | **0.795** |
| **Ambiguity** | | | **0.205** |

## Topology
| Component | Status | Description | Coverage |
|---|---|---|---|
| PM Orchestration | active | Claude Code main session in `pm` mode; dispatches parallel PM subagents (consolidator, tidier, learnings-curator) on a Stop-hook continuation loop | A1, A3, T2, T4 |
| Worker Orchestration | active | Claude Code main session in `worker` mode; dispatches TDD/Review/Validator subagents via Task() against tasks matching `needs:` state | A2, A4, C4 |
| Task Board + Locking | active | `docs/boards/<project>/` layout (extended from v0.2.0) + atomic mkdir-based per-task claim with heartbeat for staleness reclamation | T1, T4 |
| Learnings Board | active | Unified `Learning` (L###) entity with subtypes `pattern`/`finding`/`principle`, replacing inline `pattern:` tags and `## Finding` sections via `/board-migrate` | T2, T5, C5 |
| Passive Listening | active | Per-turn Stop hook with LLM-based finding extractor in every session; writes only to `_sessions/<id>.md` scratch; mode-gated continuation for PM/Worker | C1, C2, C3 |
| Spin-up UX | active | Two slash commands `/pm-start` and `/worker-start` that set a session mode flag; Stop hook loop reads the flag and continues accordingly; no external launcher | A1, A2 |

## Goal
Evolve the engineering-board plugin from v0.2.0 (single `board-manager` agent + 4 hooks routing findings to `docs/boards/` markdown entries) into **v0.3.0**: an autonomous multi-agent system using two looping Claude Code sessions (PM + Worker), per-turn passive listening in every session, a unified `Learning` entity that absorbs `pattern:` tags and `## Finding` sections, a per-session scratch-board architecture that prevents planning-pollution of the live board, atomic mkdir-based task claims for worker concurrency, and PM-driven consolidation of scratch contributions into a clean live board. The system must work out-of-the-box for anyone with vanilla Claude Code (no OMC, no external infra, no terminal automation).

## Constraints
- **No OMC dependency.** Plugin must work for any Claude Code user without OMC installed.
- **Works out of the box.** No external infra (cron, systemd, tmux daemons), no platform-specific launchers, no MCP server requirements. Only vanilla Claude Code primitives: hooks, slash commands, subagents, `Task()` dispatch.
- **Cross-platform.** Locking, file IO, and shell scripts must work on POSIX (Linux/macOS) and Windows (NTFS).
- **Loop primitive = Stop hook with `decision: "block"`.** No other mechanism for continuous loops. Loops only run while the user has the session open.
- **No suspend/resume requirement.** Closing a session ends its orchestration; the next session starts fresh from board state.
- **Live board purity is non-negotiable.** No path may write to `BOARD.md` or live entry subdirs except the consolidation pass. Per-turn extractors write only to `_sessions/<id>.md`.
- **Live board lag is acceptable.** Findings reach the live board only after consolidation runs (PM tick or session-end Stop).
- **One-shot migration.** v0.2.0 → v0.3.0 requires running `/board-migrate` once. Idempotent re-runs safe.
- **Permission prompts must not interrupt orchestrator sessions.** Plugin must ship with appropriate settings or document the permission allowlist users should add.
- **Acceptance hierarchy: Trust ≥ Capture > Autonomy.** When trade-offs surface, prefer trust over capture, and capture over autonomy.

## Non-Goals
- Truly always-on / 24/7 orchestration (would require external infra; explicitly out of scope).
- Cross-machine or cross-user board state (single-user, single-machine).
- A separate process / daemon outside Claude Code.
- Terminal automation (plugin does not control the user's terminal; the user opens sessions themselves).
- Replacing `Observations` (operationally distinct: run logs without lessons-learned semantics; stay as-is).
- Cross-board-router cross-project listening from inside a worker (worker is project-scoped via cwd).
- A web UI or non-markdown board.
- Pre-emptive scheduling or priority queues beyond v0.2.0's existing 5-rule triage.
- A "PM/Worker in the same session" model (rejected at Round 8 — separate sessions for actual parallelism).

## Acceptance Criteria

### Trust (non-negotiable, highest priority)
- [ ] **T1** No live-board entry passes the `PostToolUse:Write` validator without all required frontmatter (existing v0.2.0 hook extended for `Learning` entries with subtype-specific required fields).
- [ ] **T2** No live-board entry survives a consolidation pass if a more recent scratch-board entry contradicts or supersedes it; the consolidator must resolve contradictions before promoting.
- [ ] **T3** SessionStart hook surfaces stale `in_progress` items from prior sessions (extends current v0.2.0 SessionStart behavior).
- [ ] **T4** Live `BOARD.md` row count equals actual entry count in `{bugs, features, questions, observations, learnings}/` subdirs (index consistency invariant).
- [ ] **T5** `/board-migrate` is idempotent: running twice yields the same end state, no duplicated Learning entries, no lost source references.

### Capture (non-negotiable)
- [ ] **C1** The per-turn Stop-hook extractor runs after every assistant turn in every session (mode-gating decides what to do with the result; the extractor itself always runs).
- [ ] **C2** When the extractor identifies a finding with `confidence: confirmed`, it appears in `_sessions/<session-id>.md` within the same turn.
- [ ] **C3** At real session end (Stop without continuation), consolidation runs and every scratch entry is either promoted to live board, archived as superseded/false-start, or explicitly deferred — none silently lost.
- [ ] **C4** PM and Worker orchestrator sessions write findings to scratch and let the next consolidation tick promote them — no manual user routing required.
- [ ] **C5** Pattern recurrence detection survives migration: a Learning of subtype=pattern with `recurrence ≥ 3` across sources gets surfaced at SessionStart (replaces v0.2.0's existing `pattern:` cluster warning).

### Autonomy (non-negotiable, lowest priority of the three)
- [ ] **A1** User runs `/pm-start` in a session; that session loops via Stop hook until the PM declares "nothing to do" or the user closes the session.
- [ ] **A2** User runs `/worker-start` in a separate session; it autonomously picks tasks where `needs:` matches the worker's discipline and walks them through `tdd → review → validate`.
- [ ] **A3** Walk-away test: with `/pm-start` and `/worker-start` active and at least one open task on the board, after 60 minutes either tasks have transitioned at least one state OR PM has consolidated scratch entries from a passive-listening session.
- [ ] **A4** PM and Worker orchestrator sessions complete routine board operations (Write, Read, mkdir for claims) without receiving permission prompts (plugin ships allowlist or documents it for users to add).

## Assumptions Exposed & Resolved
| Assumption | Challenge | Resolution |
|---|---|---|
| Loop primitive could be anything | "How does the PM session actually loop in vanilla Claude Code?" | Stop hook with `decision: "block"`; only mechanism available without external infra; locked R1. |
| Plugin can depend on OMC | "I don't want this reliant on OMC; out of the box for anyone" | No OMC, vanilla Claude Code only; locked R1. |
| Universal per-turn listening is unambiguously good | (Contrarian R4) "What if universal listening creates a stale web?" | Re-opened R5 after user surfaced real failure mode; pivoted to per-session scratch + consolidation. |
| "Learning" is the same as `O###` / `pattern:` / `## Finding` | (Ontology R2) "What IS a learning relative to existing constructs?" | Unified Learning entity (L###) with subtypes pattern/finding/principle absorbs `pattern:` tags and inline `## Finding`; Observations stay distinct. `/board-migrate` handles transition. Locked R3. |
| Locking needs strict POSIX semantics | (Simplifier R6) "What's the minimal lock you actually need given scratch boards?" | Atomic mkdir per task with heartbeat for stale reclamation; cross-platform; minimal. Locked R6. |
| Workers are vaguely "implementation roles" | (R7) "What does each discipline actually do?" | Linear state-machine pipeline: `needs: tdd → review → validate → resolved`; rejection routes back to `tdd` with notes. Locked R7. |
| "Spin up an orchestrator" is opaque | (Ontologist R8) "What IS spinning up, structurally?" | Setting a session mode flag via slash command; user opens sessions themselves; no terminal automation. Locked R8. |
| Autonomy is the top priority | (R9) "What's the top criterion?" | Trust ≥ Capture > Autonomy; all three non-negotiable. Locked R9. |

## Technical Context (Existing v0.2.0 — verbatim from the source)
- **Author:** Acadia (rhen@acadia.io), repo GhostlyGawd/engineering-board, MIT license.
- **Plugin manifest:** `.claude-plugin/plugin.json` declares name `engineering-board`, version 0.2.0.
- **Components in v0.2.0:**
  - 1 agent: `agents/board-manager.md` — `model: inherit`, governs 3 protocol skills.
  - 1 command: `commands/board-init.md` — scaffolds `docs/boards/<project>/` idempotently.
  - 3 skills (protocols, not agents): `skills/board-intake/SKILL.md`, `skills/board-triage/SKILL.md`, `skills/board-resolve/SKILL.md`. The intake skill references `references/frontmatter-schema.md`.
  - 4 hooks via `hooks/hooks.json`: SessionStart (bash `board-session-start.sh`), PostToolUse:Write (bash `board-validate-entry.sh`), UserPromptSubmit (bash `board-prompt-guard.sh`), Stop (`type: "prompt"` LLM check).
- **Data model:** `docs/boards/<project>/BOARD.md` (live index), `docs/boards/<project>/ARCHIVE.md`, `docs/boards/<project>/{bugs,features,questions,observations}/*.md` (entries). Top-level `docs/boards/BOARD-ROUTER.md` maps `affects:` prefix → project board.
- **Entry IDs:** B### (bugs), F### (features), Q### (questions), O### (observations); zero-padded 3 digits.
- **Required frontmatter (per type):** see `skills/board-intake/references/frontmatter-schema.md`. Bugs/features require `id, type, status, priority, affects, title, discovered` + `## Done when`. Questions require `id, type, status, title, discovered` + `## Done when`.
- **`pattern:` tags** (today): kebab-case failure-mode tags as a frontmatter list on any entry. Cluster detection at 3+ recurrences surfaces at SessionStart and in triage.
- **`## Finding` sections** (today): written into question entries when resolving via the 8-step `board-resolve` question sequence (`skills/board-resolve/SKILL.md:47-55`).
- **Stop hook today** (`hooks/hooks.json:40-50`): `type: "prompt"` runs at session end, reviews session for unrouted findings, returns `decision: "block"` listing missed ones. **This is the foundation v0.3.0's per-turn extractor evolves from.**
- **No locks today.** Only convention: `skills/board-triage/SKILL.md:70-74` says "1 in_progress per session maximum."
- **Pre-existing routing-context priming:** `hooks/scripts/board-prompt-guard.sh` matches debug-keywords in user prompts and injects a routing reminder via `systemMessage`.

## What v0.3.0 Adds (Net Delta — implementation backlog)
1. **`/pm-start` and `/worker-start` slash commands.** Each sets `.engineering-board/session-mode` (writes mode flag), prints a one-line confirmation, ends. Subsequent Stop-hook turns read the flag and loop.
2. **Session-mode state file:** `.engineering-board/session-mode` per project (or per session-id). Schema: `{ mode: "pm"|"worker"|null, started_at: ISO, session_id: string }`.
3. **Extended Stop hook (mode-gated).** Single Stop hook replaces v0.2.0's. Logic: always runs the LLM finding extractor → writes confirmed/tentative/speculative findings to `_sessions/<session-id>.md`. Then: if mode=pm, return `block` with PM continuation prompt; if mode=worker, return `block` with Worker continuation prompt; else if findings need routing, return `block` with routing prompt; else `approve`.
4. **Scratch board layout:** `docs/boards/<project>/_sessions/<session-id>.md` per session, free-form markdown, accumulates finding entries with `confidence:` tags.
5. **`_claims/` directory for atomic mkdir locks:** `docs/boards/<project>/_claims/<entry-id>.claim/` containing `heartbeat.txt` (updated every ~60s) and `owner.txt` (session-id). Cross-platform atomic via `mkdir`. Stale claims (heartbeat older than N min, default 5) reclaimable.
6. **`Learning` entity (L###).** New entry type. Frontmatter: `id, type=learning, subtype (pattern|finding|principle), title, discovered, scope (local|global), source[], tags[], recurrence, status (candidate|promoted|archived)`. Required body sections: `## Statement`, `## Evidence`, `## Prevention`.
7. **`/board-migrate` slash command.** Idempotent. (a) For each unique `pattern:` tag across existing entries, create a Learning with subtype=pattern, source=[contributing entries], recurrence=count. Strip `pattern:` field from individual entries (or alias to `tags:`). (b) For each question with `## Finding`, create Learning with subtype=finding, source=[Q###], copy Finding to `## Statement`+`## Evidence`. Keep `## Finding` for backward read; new Findings written as Learnings going forward. (c) Observations untouched.
8. **Worker subagents** (3 new `.md` files in `agents/`): `tdd-builder.md`, `code-reviewer.md`, `validator.md`. Each describes claim → do → write-to-scratch → drop-claim. Each watches for tasks where `needs:` matches its discipline.
9. **PM subagents** (3 new `.md` files in `agents/`): `consolidator.md` (scratch → live promotion + contradiction resolution), `tidier.md` (5-rule triage on live board), `learnings-curator.md` (pattern promotion when recurrence ≥ 3, finding capture on question resolve).
10. **`needs:` frontmatter field** on bugs/features. Values: `tdd | review | validate | (absent = open or done)`. Drives the worker pipeline state machine.
11. **Permission allowlist documentation** (or shipped `.claude/settings.json` defaults) so orchestrator sessions don't permission-prompt on routine `Bash` (mkdir, grep), `Write`, `Read` operations within `docs/boards/`.
12. **Updated SessionStart hook** to recognize `_sessions/` and `_claims/` directories, surface stale `in_progress`, surface promoted Learnings with `recurrence ≥ 3`.

## Ontology (Key Entities — Final, Round 9)
| Entity | Type | Key Fields | Relationships |
|---|---|---|---|
| `PMOrchestrator` | role / session | session_mode=pm | dispatches PMSubagent[]; reads ScratchBoard[]; writes LiveBoard via Consolidator |
| `WorkerOrchestrator` | role / session | session_mode=worker | dispatches WorkerSubagent[]; claims via AtomicClaim |
| `TDDBuilder` | worker subagent | discipline=tdd | claims tasks where `needs:tdd`; produces commit + scratch entry |
| `CodeReviewer` | worker subagent | discipline=review | claims tasks where `needs:review`; outputs approval or change-request |
| `Validator` | worker subagent | discipline=validate | claims tasks where `needs:validate`; outputs pass/fail |
| `Consolidator` | PM subagent | role=consolidate | promotes ScratchBoard → LiveBoard, resolves contradictions, prunes superseded |
| `Tidier` | PM subagent | role=tidy | applies 5-rule triage to LiveBoard, surfaces systemic clusters |
| `LearningsCurator` | PM subagent | role=learnings | promotes patterns to Learning entries on recurrence ≥ 3 |
| `LiveBoard` | data | `BOARD.md` + entry subdirs | clean; written only by Consolidator |
| `ScratchBoard` | data | `_sessions/<id>.md` | per-session free-form; written by FindingExtractor and Workers |
| `AtomicClaim` | concurrency | `_claims/<entry>.claim/` + `heartbeat.txt` + `owner.txt` | created via mkdir; reclaimed on stale heartbeat |
| `Learning` (L###) | entity | id, subtype, source[], tags, recurrence, scope, status | replaces inline `pattern:` + `## Finding` |
| `Bug`, `Feature`, `Question`, `Observation` | entity | unchanged from v0.2.0 except `needs:` field on bugs/features | live board entries |
| `FindingExtractor` | hook logic | LLM-based, runs per Stop, writes to ScratchBoard | never writes to LiveBoard |
| `ModeGatedStopHook` | hook | reads session_mode; routes to PM/Worker/extractor path | THE loop primitive |
| `/pm-start`, `/worker-start`, `/board-init`, `/board-migrate` | slash commands | argument-driven | user entry points |
| `NeedsField` | state field | values: tdd, review, validate, (absent) | drives worker pipeline |
| `ConsolidationPass` | process | runs on PM tick + Stop on real session end | scratch → live promotion |
| `ConfidenceTag` | scratch metadata | confidence: confirmed/tentative/speculative | hints to Consolidator |

## Ontology Convergence
| Round | Entity Count | New | Changed | Stable | Stability |
|---|---|---|---|---|---|
| 0 | 11 | 11 | - | - | N/A |
| 1 | 14 | 3 | 0 | 11 | 79% |
| 2 | 14 | 0 | 1 (Learning entity lifted) | 13 | 93% |
| 3 | 18 | 4 | 0 | 14 | 78% |
| 4 | 21 | 3 | 0 | 18 | 86% |
| 5 | 24 | 3 | 0 | 21 | 88% |
| 6 | 27 | 3 | 0 | 24 | 89% |
| 7 | 30 | 3 | 0 | 27 | 90% |
| 8 | 32 | 2 | 0 | 30 | 94% |
| 9 | 35 | 3 | 0 | 32 | 91% |

## Known Deferred Decisions (for `/omc-plan` or implementation)
- Exact consolidation cadence (every N PM-loop turns vs every M minutes vs on-scratch-size threshold).
- Model selection per subagent (haiku for finding-extractor cost? sonnet for tdd/review? opus for curator?).
- Confidence threshold for promoting `confidence: tentative` findings — auto-promote on 2+ tentative-with-same-claim, or never auto-promote tentative?
- Concrete prompts for finding-extractor (false-positive rate is a design knob).
- Heartbeat interval and stale-claim timeout values (default proposed: 60s heartbeat, 5min stale).
- Schema migration edge cases (cross-project `pattern:` tags, Findings referencing now-archived entries).
- Whether `_sessions/<session-id>.md` files are GC'd on consolidation or kept as audit trail.
- Plugin permission allowlist (which specific Bash/Write/Read patterns).
- Whether v0.3.0 ships with a backward-compat shim for users who haven't run `/board-migrate` yet, or hard-requires migration.

## Interview Transcript
<details>
<summary>Full Q&A (Round 0 topology + Rounds 1–9 Socratic)</summary>

### Round 0 — Topology
**Q:** "Is the 6-component topology right? Anything to add, merge, split, or explicitly defer to a later phase?"
**A:** "Looks right — all 6 active"

### Round 1 — PM Orchestration / Goal (loop primitive)
**Q:** "What mechanism runs the PM orchestrator's loop?"
**A:** "Which would you recommend. I don't want this to be like reliant on OMC. I want it to work out of the box for anyone."
**Decision (interviewer-recommended, user-confirmed):** Stop-hook continuation loop using Claude Code's `decision: "block"` mechanism. Two slash commands set session mode; the Stop hook reads mode and continues the loop. Only runs while session is open.
**Follow-up A:** "Confirmed — in-session Stop-hook loop"
**Ambiguity end of R1:** 56%

### Round 2 — Learnings Board / Goal (ontology)
**Q:** "What IS a 'learning' relative to v0.2.0's existing knowledge constructs (Observations, pattern tags, Findings)?"
**A:** "I like the genuinely new idea, I also like the cleaner ontology if it will still retain the key purpose of pattern tags which is to elevate a pattern when it keeps appearing and curate it to promotion to be looked into globally"
**Ambiguity end of R2:** 54%

### Round 3 — Learnings Board / Constraints (migration scope)
**Q:** "Additive or breaking change for the Learnings Board?"
**A:** "Whichever is going to be most durable, helpful, and clear and scalable"
**Decision (interviewer-locked):** Breaking unified + `/board-migrate`, Observations stay distinct. Three of four user-values favor unified; migration is one-shot and tooling-supported.
**Ambiguity end of R3:** 51%

### Round 4 — Passive Listening / Goal (Contrarian mode)
**Q:** "When does passive listening fire in a non-orchestrator session?"
**A:** "Per-turn — Stop hook fires every assistant response"
**Ambiguity end of R4:** 47%

### Round 5 — Passive Listening / Constraints (re-opened after user revelation)
**User intervention (critical):** "When it starts firing while I'm planning it keeps updating and creating unhelpful stuff... slowly creates a web of incorrect information that gets stale or doesn't get revised... doesn't correct itself and misses stuff."
**Interviewer re-scored Passive Listening DOWN** (had been over-confident in R4).
**Q:** "What's the PRIMARY guard against the planning-pollution failure mode?"
**A:** "Whichever is going to be most durable, helpful, and clear and scalable"
**Decision (interviewer-locked):** Per-session scratch boards (`_sessions/<id>.md`) + Consolidation Pass as PRIMARY guard. Confidence-tagging (Option 1) and revision-resolving (Option 3) layer inside the architecture as secondary mechanisms during consolidation.
**Ambiguity end of R5:** 45%

### Round 6 — Task Board + Locking / Constraints (Simplifier mode)
**Q:** "Given the scratch-board architecture, what's the minimal lock you actually need?"
**A:** "Atomic claim only — mkdir-based, single file (recommended, simplest)"
**Ambiguity end of R6:** 39%

### Round 7 — Worker Orchestration / Goal
**Q:** "Which worker pipeline shape?"
**A:** "Linear state-machine (TDD → Review → Validate) — as sketched, recommended"
**Ambiguity end of R7:** 35%

### Round 8 — Spin-up UX / Goal (Ontologist mode)
**Q:** "Structurally, what IS 'spinning up an orchestrator'?"
**A:** "A slash command per role — two commands, plain (recommended)"
**Ambiguity end of R8:** 28%

### Round 9 — Cross-cutting / Criteria
**Q:** "What's the top-level acceptance criterion for 'system is working'?"
**A:** "All three are non-negotiable" (Trust ≥ Capture > Autonomy)
**Ambiguity end of R9:** 20.5% (threshold met)

### Spec destination
**Q:** "Where should the deep-interview spec be written?"
**A:** "Both — spec in engineering-board repo, copy in cwd"

</details>

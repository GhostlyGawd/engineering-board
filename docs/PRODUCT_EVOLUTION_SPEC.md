# Engineering Board Product Evolution Spec

_Status: Living direction draft — Gate 1 (no implementation authorized)_
_Started: 2026-07-27_
_Product owner: GhostlyGawd_
_Repository: `GhostlyGawd/engineering-board`_
_Current live baseline: `main` at `4ee6c5239e152b20c4c2a07ef0c4d4fceefa48f3`_
_Portfolio context: inventory-only; audit source `GhostlyGawd/repo-audit` at
`907f0759f9d08f478cd5384ad88e50963f1af79a`_

## 1. How to use this document

This is the durable workpad for deciding the next product shape before building
it. Update it as decisions are made. Do not treat proposed commands, interfaces,
or milestones as shipped behavior until the owner approves the implementation
contract and the corresponding code, tests, current-truth documentation, and
evidence land together.

Decision states used below:

- **Active direction** — the current recommendation, subject to owner revision.
- **Accepted** — explicitly approved by the owner.
- **Open** — a material choice still awaiting owner direction.
- **Deferred** — intentionally not part of the next implementation milestone.
- **Rejected** — considered and deliberately excluded.

This draft does not supersede the existing
[`ROADMAP.md`](../ROADMAP.md) or
[`RFC 0003`](rfcs/0003-productization-roadmap.md) until Gate 1 is accepted.
Those documents remain evidence and planning inputs.

## 2. Decision ledger

| Decision | State | Current direction |
|---|---|---|
| Product outcome | Active direction | Make Engineering Board the easiest way for an AI coding agent to notice, finish, prove, and remember repository work. |
| Implementation boundary | Accepted by current request | Write and revise this spec only. Do not implement product behavior until the owner says the contract is ready to build. |
| Product identity | Active direction | Keep committed Markdown, human-visible diffs, local-first operation, deterministic validation, atomic claims, and the `tdd → review → validate` quality loop. |
| Competitor adoption rule | Active direction | Adopt mechanisms that improve activation, next-action clarity, human control, or compounding memory. Do not copy another product's storage model or feature breadth. |
| Default capture policy | Active direction | Capture automatically; promote explicitly through a foreground action. Do not silently turn every scratch finding into committed project state. |
| Session modes | Active direction | Keep PM and Worker modes as advanced batch controls, but remove them from the default first-run and single-entry workflow. |
| Resolution authority | Active direction | Validation may recommend closure; final `status: resolved` remains an explicit user or explicitly authorized command action. |
| Database or hosted service | Deferred | No Dolt/SQLite migration, hosted control plane, daemon, account system, or cloud sync in the next milestones. |
| Cross-session Conductor | Deferred | RFC 0001's persistent supervisor remains a later option, not the next required product step. |
| Team dashboard and monetization | Deferred | Do not build until the single-repository activation and retention loop is proven. |
| Pending PR #93 | Independent | The B057 fix and 1.7.1 release preparation remain a separate open PR and are not part of this spec branch. |

## 3. Product thesis

Engineering Board is not primarily a task tracker. It is a repository-owned
engineering control loop:

```text
notice work
  → capture evidence
  → promote reviewed project state
  → identify ready work
  → claim without collision
  → implement
  → review
  → validate
  → resolve explicitly
  → retain and resurface the lesson
```

The combination is the product. Individual steps overlap with other tools, but
the complete visible loop is the differentiator.

### Non-negotiable properties

1. **The repository owns the durable state.** A fresh agent can reconstruct the
   board from versioned files without an external service.
2. **Humans can inspect meaningful diffs.** Project state must not become an
   opaque database export.
3. **Automatic capture does not equal automatic commitment.** Promotion is a
   review boundary unless the owner later approves an explicit opt-in policy.
4. **Quality gates remain falsifiable.** TDD, review, and validation must leave
   inspectable evidence and may regress an entry to an earlier stage.
5. **Claims remain atomic.** Convenience features must not weaken collision
   prevention.
6. **The default path is simple; advanced automation is discoverable.** New
   users should not need to understand hooks, mode files, disciplines, or
   orchestration internals to complete one entry.
7. **Plugin and MCP clients share semantics.** Client adapters may differ, but
   they must not invent incompatible board behavior.

## 4. Current workflow and present problems

### Actors today

| Actor | Current responsibility |
|---|---|
| User | Supplies intent, decides which findings become project work, approves consequential actions, and explicitly resolves validated entries. |
| Interactive agent | Works in the current session, invokes commands/tools, and explains board state. |
| Stop-hook controller | Routes a turn into passive, PM, paused, or Worker behavior based on `session-mode.json`. |
| Discipline workers | Perform bounded TDD, review, or validation work and suggest the next `needs:` state. |
| Repository files | Authoritative board, claim, archive, scratch, and learning state. |

### Observed problems

1. **Capture visibility shipped, but the product story still describes the old
   silent behavior.** The Stop procedure now surfaces the append helper's
   `EB-CAPTURE-SUMMARY`, while the README still tells users to inspect
   `_sessions/` for confirmation. The remaining problem is documentation drift
   and ensuring the receipt stays concise and reliable.
2. **The best behavior appears too late.** Watching an agent drive a card
   through the quality loop requires real work, promotion, mode knowledge, and
   sometimes a fresh session.
3. **The normal path exposes orchestration internals.** PM and Worker are useful
   batch primitives, but onboarding presents them as required product concepts.
4. **Ready work exists but is not the primary interaction.** The MCP server can
   compute a deterministic ready queue, yet plugin users must already know an
   entry ID and command.
5. **Promotion is gated behind PM mode.** Casual users can accumulate scratch
   without ever creating the durable board state that powers later value.
6. **The visual board reports state better than it directs action.** Resolved
   history can dominate; single-letter filters are opaque; cards do not lead
   with the next executable action.
7. **The learning loop is underfed and under-explained.** Learnings are curated
   in PM mode and surfaced at SessionStart, but users may never generate enough
   durable state to reach the compounding loop.
8. **Core setup semantics are not fully adapter-parallel.** The plugin exposes
   `/board-setup`; MCP exposes lower-level `board_init`.

These problems are documented in the dated
[`ACTIVATION.md`](../ACTIVATION.md),
[`RETENTION.md`](../RETENTION.md), and
[`COMPREHENSION.md`](../COMPREHENSION.md) audits. They are historical evidence,
not automatically current implementation truth.

## 5. Competitive design inputs

The goal is selective adoption, not convergence.

| Source | What it does especially well | Adopt or adapt | Do not import |
|---|---|---|---|
| [Beads](https://github.com/gastownhall/beads) | Makes `ready → claim → close` and persistent memory first-class; supports large dependency graphs and multi-agent sync. | Make ready work and the recommended next action first-class. Prime agents with concise workflow context. Surface remembered knowledge at the moment of work. | Dolt storage, sync complexity, database-first inspection, graph breadth not required by the current consumer. |
| [Backlog.md](https://github.com/MrLesk/Backlog.md) | Gives humans rich Markdown tasks, acceptance criteria, comments, and an actionable browser UI. | Elevate the existing `## Done when` contract in cards and execution. Make the board easier to scan and act from. Preserve human review checkpoints. | A general-purpose project-management suite, mutable hosted UI, milestones/settings breadth, or duplicated task schema. |
| [Task Master](https://github.com/eyaltoledano/claude-task-master) | Turns PRDs into tasks, recommends the next task, expands work, and offers research-assisted planning. | Provide one obvious next-work action. Later evaluate spec-to-parent/subtask decomposition using Engineering Board's existing hierarchy. Keep tool exposure lean. | Provider/model configuration, research-provider surface area, or PRD decomposition in the first activation milestone. |
| [Claude Code Tasks](https://code.claude.com/docs/en/interactive-mode#task-list) | Provides a zero-install personal checklist integrated into the active coding session. | Compose rather than compete: use native Tasks for ephemeral session planning and promote durable discoveries to Engineering Board. | Reimplementing the session checklist or treating user-local task files as shared repository state. |

### Comparative product position

| Need | Best fit today |
|---|---|
| Personal checklist inside one Claude Code session | Claude Code Tasks |
| Large distributed dependency graph and agent coordination | Beads |
| Rich human-and-agent Markdown project management | Backlog.md |
| PRD decomposition and task expansion | Task Master |
| Automatically discovered, repository-visible engineering work driven through a quality pipeline and retained as repo knowledge | Engineering Board |

Engineering Board should become easier, not broader. It loses its reason to
exist if it turns into a weaker clone of any row above.

## 6. Proposed direction: retain, append, replace, revise

### Retain

- Committed Markdown as authoritative durable state.
- Scratch inbox as the automatic-capture buffer.
- Explicit promotion as the commitment/review boundary.
- Existing entry IDs, hierarchy, `blocked_by`, priorities, and `## Done when`.
- Deterministic ready-queue semantics.
- Atomic claim acquisition, heartbeat, stale reclamation, and release.
- `tdd → review → validate` transitions with allowed regressions.
- Explicit final resolution and archival provenance.
- Local-first operation with no required service.

### Append

1. **A guided, disposable first-win experience.**
2. **A foreground promote action** that does not require PM mode.
3. **A next-work action** that chooses from the deterministic ready queue and
   explains its choice.
4. **Consistent capture-receipt semantics** that preserve the shipped
   confirmation, prevent noise, and describe it accurately on every surface.
5. **Local value accrual** showing resolved entries, retained learnings, and
   context-relevant learnings.
6. **Adapter parity** for the direct setup/promote/next workflow.

### Replace

1. Replace the documented default
   `setup → passive wait → PM mode → end turn → fresh session → run`
   with
   `setup → guided first win → normal work → promote → next → run`.
2. Replace “know an entry ID first” with “show me the best ready entry and why.”
3. Replace opaque first-run mode language with value language. Modes remain in
   advanced documentation.
4. Replace visually dominant resolved history with an action-first default view.

### Revise

1. Revise `/board-setup` so it is the single canonical setup instruction on
   every product surface.
2. Revise `/board-run` completion so it presents the exact validation outcome
   and explicit resolve action without implying that validation silently closes
   project work.
3. Revise SessionStart to lead with ready work, pending promotion, and relevant
   retained knowledge; demote implementation terminology.
4. Revise the HTML board to prioritize ready/open work, use named filters, and
   expose copyable next actions.
5. Revise learning curation so the direct workflow can feed it without requiring
   a persistent PM-mode session.

## 7. Target user journeys

### 7.1 First install and first win

Target:

```text
install
  → /board-setup
  → choose "try a guided sample"
  → watch one bounded sample move through tdd → review → validate
  → see exactly what changed
  → remove or retain the sample explicitly
  → receive the normal daily-work instruction
```

Outcome:

- One session.
- No required restart.
- No PM or Worker terminology.
- No real project work required before the product can demonstrate value.
- No leftover demo content without an explicit user choice.

The exact demo containment model remains open in §12.

### 7.2 Normal daily loop

Target:

```text
work normally
  → first real capture receives one quiet confirmation
  → /board-promote
  → user reviews the promotion summary
  → /board-next
  → recommended ready entry + reason + Done-when summary
  → explicit run
  → tdd → review → validate
  → explicit resolve
  → learning curation and value accrual refresh
```

The user may still choose PM or Worker mode for repeated batch processing.

### 7.3 Returning to a repository

Target SessionStart hierarchy:

1. Safety or recovery warnings.
2. In-progress or claimed work.
3. Best ready action.
4. Pending scratch promotion.
5. Relevant retained learnings and accrual.
6. Current advanced mode, if one is active.

### 7.4 Non-Claude MCP client

Target:

- Initialize with the same smart defaults as `/board-setup`.
- Capture and promote without requiring Claude hooks.
- Query the same ready recommendation.
- Claim and update through the same state and safety rules.
- Receive explicit recommended actions rather than plugin-only prose.
- Never claim access to the autonomous Claude Code discipline agents when the
  client adapter cannot provide them.

## 8. Proposed capability milestones

Milestones are ordered by user value and dependency, not by feature count.

### Milestone A — Visible first win

**Purpose:** Prove the product works before asking the user to learn its operating
model.

Candidate capabilities:

- Canonical `/board-setup` guidance across landing page, README, and plugin.
- A guided, isolated sample path.
- Preserve and document the shipped one-line capture receipt; define and test
  its anti-noise behavior.
- Immediate board visibility after setup/demo.
- Measured first-win evidence recorded in a dated report.

If omitted, evaluators still encounter a blank board and must supply real work
before seeing the product's strongest behavior.

### Milestone B — Direct daily loop

**Purpose:** Let ordinary users turn captured evidence into completed work
without persistent modes.

Candidate commands, names provisional:

```text
/board-promote
/board-next
/board-run <entry-id>
/board-resolve <entry-id>
```

Required semantics:

- `/board-promote` performs a bounded foreground consolidation and reports
  created, rejected, deduplicated, and still-pending findings.
- `/board-next` selects only deterministic ready work, explains blockers and
  priority ordering, summarizes `## Done when`, and does not start work without
  explicit authorization.
- `/board-run` retains claim ownership and bounded rounds.
- Resolution remains explicit.
- PM and Worker modes remain available as advanced batch controls.

If omitted, the product continues to expose its orchestration primitives as
normal user workflow.

### Milestone C — Actionable board and visible memory

**Purpose:** Make the board answer “what should happen next?” and make retained
value visible on every return.

Candidate capabilities:

- Default board view shows ready/open work; resolved history is collapsed or
  separately selected.
- Filters use full names and accessible labels.
- Each actionable card exposes the next command or structured action.
- Board and SessionStart show resolved count, learning count, and context matches.
- Matched learnings explain why they apply and link to their source entries.
- Learning curation runs from the direct promote/resolve lifecycle, not only PM
  mode.
- `/board-stats` or an equivalent `board_status` expansion derives local value
  without telemetry.

If omitted, the product retains value but fails to make that value legible or
actionable.

### Milestone D — Structured planning bridge

**State: Deferred candidate.**

**Purpose:** Evaluate Task Master-like decomposition without turning Engineering
Board into a general planning suite.

Possible bounded capability:

- Convert one approved specification section into a parent entry and small
  child entries using the existing `parent` relationship.
- Require explicit review before writing.
- Preserve source links and `## Done when`.
- Do not perform web research, model-provider configuration, or autonomous
  backlog expansion.

This milestone starts only after A–C have evidence and the owner confirms that
spec decomposition is a current Engineering Board user need.

## 9. Provisional command and adapter model

This is directional, not yet an implementation contract.

| User intent | Claude plugin | MCP/shared semantic | Notes |
|---|---|---|---|
| Smart setup | `/board-setup` | Add `board_setup` or extend `board_init` with a clearly versioned setup profile | One canonical outcome; avoid two subtly different initializations. |
| Review and promote inbox | `/board-promote` | `board_promote` | Distinct write authority justifies a distinct action. |
| Find best ready work | `/board-next` | Extend `board_status` with `recommended_next` before adding another read tool | Keep MCP tool exposure lean. |
| Run one entry | `/board-run <id>` | Adapter capability-dependent | Core transition rules shared; autonomous agent dispatch must not be falsely promised to unsupported clients. |
| Show accrued value | `/board-stats` or SessionStart/board view | Extend `board_status` | Derived locally from repository state. |

Shared deterministic behavior should live below the adapters. Plugin commands
and MCP tools should compose it rather than restate ordering, filtering,
promotion, or safety rules independently.

## 10. State and authority invariants

| State or decision | Authority | Required behavior |
|---|---|---|
| Scratch finding | Capture adapter | Append evidence without presenting it as committed project truth. |
| Promotion | User or explicitly invoked foreground/batch action | Validate, reject unsafe/unsupported findings, deduplicate, write entries, and report outcomes. |
| Ready selection | Deterministic board rules | Respect unresolved blockers, status, priority, and claim availability; explain the selection. |
| Claim | Atomic claim subsystem | Exactly one live owner; stale reclamation remains explicit and observable. |
| Discipline transition | Bounded worker result applied by controller | Only allowed `needs:` transitions; failures may leave or regress state. |
| Resolution | User or explicitly authorized resolve action | Preserve provenance, rebuild indexes/views, then feed learning curation. |
| Learning | Explicit remember action or deterministic curator | Preserve source entry links, recurrence, confidence, and applicability. |
| Demo artifacts | Guided demo controller | Bounded to an approved location; inventory before cleanup; no silent deletion of user-authored or modified data. |

## 11. Outcome-level acceptance criteria

### Activation

1. A fresh user can reach a visibly validated sample in one session and under
   three minutes of user-directed interaction, excluding model execution time.
2. The guided path requires no mode switch, restart, or pre-existing finding.
3. The user can identify every file the demo created and can remove the bounded
   demo without affecting unrelated work.
4. The existing capture receipt remains concise and truthful; zero-finding
   turns and repeated captures follow an explicitly tested anti-noise policy.

### Daily operation

5. A user with pending scratch can promote it immediately without entering PM
   mode.
6. A user can ask for the next ready entry without knowing an ID.
7. The recommendation is deterministic for the same board state and explains
   priority, readiness, blockers, and `## Done when`.
8. No command begins implementation or resolves an entry merely because the user
   asked to inspect the next action.
9. A single-entry run preserves atomic claim and bounded transition behavior.

### Return and retention

10. SessionStart and the HTML board expose pending promotion, best ready work,
    resolved count, retained learning count, and relevant learning matches
    without network access.
11. Direct promote/resolve usage can feed learning curation without PM mode.
12. Every surfaced learning links to inspectable repository evidence and states
    why it applies.

### Compatibility and trust

13. Existing boards require no destructive migration for Milestones A–C.
14. Plugin and MCP paths produce semantically equivalent setup, promotion, and
    ready-selection results where both advertise support.
15. Unsupported adapter capabilities return an explicit limitation instead of a
    false success.
16. README, landing page, command docs, MCP docs, architecture, examples,
    visuals, versions, and tests are reconciled in the same behavior change.

## 12. Open decisions

### O1 — Demo containment

Options:

1. Copy a tiny fixture into an isolated repository subdirectory, create a
   labeled sample entry, then offer fingerprinted cleanup.
2. Create a separate sample project under `engineering-board/` and never touch
   source files.
3. Replay a recorded pipeline without executing real work.

Recommendation: option 1 if it can prove safe containment and exact cleanup;
otherwise option 2. Option 3 is safer but weakens the first-win proof.

### O2 — Promotion review boundary

Options:

1. `/board-promote` writes all accepted findings and prints a summary.
2. `/board-promote` previews findings and requires a second confirmation.
3. Passive mode auto-promotes high-confidence findings.

Recommendation: option 1 for the first direct workflow, with `--dry-run` or
preview support. Defer auto-promotion until real usage demonstrates that its
noise and trust costs are acceptable.

### O3 — Next-action execution

Options:

1. `/board-next` only recommends.
2. `/board-next --run` recommends, asks for explicit confirmation, then composes
   `/board-run`.
3. `/board-next` immediately runs by default.

Recommendation: option 2. It supports the short path without turning an
inspection request into code mutation.

### O4 — Final resolution

Options:

1. Keep `/board-resolve` separate.
2. After successful validation, `/board-run` asks whether to resolve now.
3. Successful validation automatically resolves.

Recommendation: option 2, while preserving option 1 for non-interactive use.
Reject option 3 unless the owner explicitly changes the human-resolution
boundary.

### O5 — Advanced modes

Options:

1. Keep PM and Worker modes unchanged but move them to advanced docs.
2. Deprecate them after the direct workflow proves equivalent.
3. Remove them immediately.

Recommendation: option 1 through Milestones A–C. Revisit only with usage and
compatibility evidence.

## 13. Alternatives and tradeoffs

### Do nothing

The current engine remains capable and differentiated, but activation friction,
mode ceremony, and invisible accrual continue to suppress adoption and
retention.

### Copy Beads' architecture

This would improve graph queries and distributed sync but sacrifice the core
human-reviewable Markdown proposition and introduce migration and operational
complexity without a proven current consumer. Rejected for the next milestones.

### Turn the HTML board into a full Backlog.md-style editor

This would improve manual task management but adds a mutable application surface,
write security, concurrency semantics, and broad PM expectations. The next board
revision should remain an action-oriented renderer.

### Lead with Task Master-style PRD decomposition

This could improve upfront planning, but it does not repair the current
capture-to-value gap. Deferred behind activation, direct operation, and visible
memory.

### Build the Conductor first

This adds asynchronous continuity but makes an already complex operating model
larger before the foreground loop is easy to understand. Deferred.

## 14. Explicit non-goals for Milestones A–C

- Replacing Markdown with a database.
- A hosted service, login, organization model, billing, or cloud sync.
- Cross-repository aggregation.
- A general-purpose project-management suite.
- A new model-provider or research-provider configuration system.
- Reimplementing Claude Code's personal Tasks UI.
- Automatic code execution from a read-only “what next?” request.
- Silent auto-resolution.
- Silent auto-promotion by default.
- Removing advanced modes before compatibility evidence exists.
- Implementing RFC 0001's persistent supervisor.

## 15. Preliminary documentation-impact contract

When implementation is eventually approved, each behavior item must map to its
implementation, tests, current-truth docs, examples, visuals, and dated
evidence. Historical audits stay intact and receive a superseding dated report.

| Contract item | Normative level | Implementation | Test/evidence | Docs/example | Current status |
|---|---|---|---|---|---|
| Living product direction | Proposed | None | Owner review of this spec | This file; `ROADMAP.md` link | Documentation-only addition |
| Guided first win | Proposed required for Milestone A | Not implemented; capture receipt already exists | Future timed clean-repo journey and receipt-noise tests | Future README/setup/landing/demo visual updates | Proposed journey plus documentation-only drift |
| Current capture confirmation | Required current truth | `hooks/stop-hook-procedure.md`; `hooks/scripts/board-scratch-append.sh` | `tests/scratch/append.sh`; `tests/modes/stop-hook-mode-routing.sh` | README corrected to describe the shipped non-empty receipt | Documentation-only drift repaired |
| Canonical smart setup instruction | Required current truth | `commands/board-setup.md` | `tests/orchestration/board-setup-command.sh` | Landing install snippet corrected from `/board-init my-project` to `/board-setup` | Documentation-only drift repaired |
| Foreground promotion | Proposed required for Milestone B | Not implemented | Future promotion lifecycle and rejection matrix | Future command, README, MCP, architecture docs | Proposed, no current-behavior claim |
| Deterministic next action | Proposed required for Milestone B | Ready queue exists; interaction does not | Future ordering/explanation/authorization tests | Future command, MCP, board-view, README docs | Implementation-defined gap |
| Actionable board | Proposed required for Milestone C | Current renderer is read-only | Future rendering and accessibility evidence | Future visual and board-view docs | Proposed revision |
| Visible memory accrual | Proposed required for Milestone C | Partial SessionStart learning display exists | Future derived-count and relevance tests | Future README, board-view, retention evidence | Recommended gap |
| Other current product behavior | Required current truth | Unchanged by this spec | Existing tests remain authoritative for current code | Architecture and command docs reviewed as unaffected because this change does not alter behavior | Reviewed and unaffected |
| Versions/releases/security | Required current truth | Unchanged by this spec | No release or live validation claimed | CHANGELOG, manifests, SECURITY reviewed as unaffected | Reviewed and unaffected |

## 16. Approval gates

### Gate 1 — Direction

Before producing the file-level build contract, the owner must approve or revise:

- the product thesis and non-negotiables;
- the retain/append/replace/revise boundary;
- Milestones A–C and the deferral of Milestone D;
- the authority invariants;
- the five open decisions.

### Gate 2 — Implementation contract

After Gate 1, expand the accepted first milestone into:

- exact command and MCP contracts;
- shared component/file responsibilities;
- state transitions and compatibility behavior;
- failure, retry, cleanup, and security behavior;
- deterministic acceptance-test matrix;
- documentation and visual update map;
- delivery path and PR boundary.

No product implementation begins until the owner explicitly approves Gate 2.

## 17. Research sources

Current product evidence:

- [`2026-07-27 spec validation`](evidence/2026-07-27-product-evolution-spec-validation.md)
- [`README.md`](../README.md)
- [`ACTIVATION.md`](../ACTIVATION.md)
- [`RETENTION.md`](../RETENTION.md)
- [`COMPREHENSION.md`](../COMPREHENSION.md)
- [`ROADMAP.md`](../ROADMAP.md)
- [`RFC 0003`](rfcs/0003-productization-roadmap.md)
- [`commands/board-setup.md`](../commands/board-setup.md)
- [`commands/board-run.md`](../commands/board-run.md)
- [`mcp-server/README.md`](../mcp-server/README.md)

External product references, reviewed 2026-07-26–27:

- [Beads](https://github.com/gastownhall/beads)
- [Backlog.md](https://github.com/MrLesk/Backlog.md)
- [Task Master](https://github.com/eyaltoledano/claude-task-master)
- [Claude Code Tasks](https://code.claude.com/docs/en/interactive-mode#task-list)

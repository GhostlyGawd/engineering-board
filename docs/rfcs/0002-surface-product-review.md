# RFC 0002 — Surface product review: keep / simplify / merge / deprecate

_Status: Living. Written during the product-improvement loop (cycles C1–C2), 2026-07-04._

Every shipped surface — 10 commands, 8 agents, 4 skills, 11 MCP tools, 4 hook
events — is challengeable, including existing ones (goal rule 3). This RFC records
a first-principles **"would we build this today, this way?"** decision for each,
so the product's surface area is deliberate rather than accumulated. Each
`simplify`/`merge`/`deprecate` verdict points at the `eb-self` board entry that
tracks the work; `keep` verdicts state why the surface earns its place.

The evidence base is the C1/C2 dogfooding: red-team (Track A), persona walkthroughs
and the time-to-first-value measurement (Track B, `.goal/evidence/loop/C2-time-to-first-value.md`),
and the surface-coherence audits (Track D).

## Commands (10)

| Command | Verdict | Rationale |
|---|---|---|
| `/board-init` | **keep** | Core scaffold; idempotent; print-only `.gitignore` (respects the user's files). C2 extended the Quickstart so its value is discoverable (B027). |
| `/board-rebuild` | **keep** | Deterministic, byte-stable cache refresh; safe to run anytime. The trust anchor of the board model. |
| `/board-graph` | **simplify** | `GRAPH.yml` is machine-only and `/board-rebuild` already regenerates it; rarely a standalone user need. Candidate to fold into a `--graph` flag on rebuild. No board entry yet — low priority; tracked here. |
| `/board-pause` / `/board-resume` | **keep** | Clear escape hatch with good NOOP messaging; paired symmetry; guarded by the single-source refusal matrix. |
| `/pm-start` | **keep** | Needed to enter the promotion pipeline. Jargon removed (B015). |
| `/worker-start` | **simplify** | The per-discipline session lock forces two restarts to advance one entry (B006). Either allow discipline rotation / `--discipline auto`, or frame worker mode explicitly as a primitive the Conductor (RFC 0001) drives. Tracked: **B006**. |
| `/board-install-permissions` | **simplify** | Coverage is now correct (B004), but delivery is a 6-step copy-paste loop that can't complete inside the session and is undiscoverable from onboarding. Tracked: **B030**. |
| `/board-claim-release` | **keep** | Exemplary UX: exit-code-specific messages that each state the next action. The gold standard the rest of the product should match. |
| `/board-migrate` | **simplify** | Bundles two unrelated operations (v0.3.0 data migration + 1.1.0 folder relocate) under one verb. Split or clearly document as two modes. Tracked: **B020**. |

## Agents (8)

| Agent | Verdict | Rationale |
|---|---|---|
| `board-manager` | **keep** | Router over the 4 skills; clarify it vs. the skills it wraps. |
| `finding-extractor` | **keep** | Cheap per-turn untrusted-input classifier; correct read-only role. Reject prose aligned with the shipped canonical filter (C1/C2). |
| `consolidator` | **merge** | Duplicates the `board-consolidate` skill's algorithm (same supersession language, same disposition vocab). Make one the canonical engine and the other a thin dispatcher. Tracked: **B014**. |
| `tidier` | **keep** | Clean hygiene contract; its all-zero JSON should point a human at `tidy.log`. |
| `learnings-curator` | **keep** | Thin wrapper over `board-curate-learnings.sh`; recurrence≥3 promotion threshold now clearly distinguished from the 2+ cluster-surfacing threshold (B019). |
| `tdd-builder` | **keep** | Sound; the `nothing_to_test`-advances-anyway behavior is counterintuitive but tracked. Tracked: **B022**. |
| `code-reviewer` | **keep (rename)** | Collides conceptually with the harness `/code-review`; and it lists Write/Edit tools despite a no-writes contract. Rename + narrow tools. Tracked: **B021**. |
| `validator` | **keep** | Correct read-only scope. Its success is a board dead-end (nothing tells the user to run `/board-resolve`). Tracked: **B007**. |

## Skills (4)

| Skill | Verdict | Rationale |
|---|---|---|
| `board-intake` | **keep** | Human counterpart to the consolidator; recurrence-threshold wording reconciled (B019). |
| `board-triage` | **keep** | Rule count fixed (B017). |
| `board-resolve` | **keep** | Mandatory-step contradiction fixed (B018). It is the invisible half of the validator handoff (B007). |
| `board-consolidate` | **merge** | Same algorithm as the `consolidator` agent (see B014). |

## MCP tools (11) — **keep all**

`board_init`, `board_list_projects`, `board_create_entry`, `board_list_entries`,
`board_get_entry`, `board_update_entry`, `board_rebuild`, `board_capture_finding`,
`board_claim`, `board_release`, `board_status`.

The best-designed surface in the product: enum-constrained schemas, `ToolError`
messages that name allowed values, exit-code legends inline in descriptions.
`board_capture_finding` (scratch) vs `board_create_entry` (live) is a sensible
split, not redundancy. C2 hardening added path-traversal (B024) and
frontmatter-injection (B028) guards, and fixed the capture→consolidate data-loss
gap (B026). No tool is a candidate for removal.

## Hook events (4) — **keep all**

`SessionStart` (board view + nudge), `PostToolUse(Write)` (frontmatter/index
validation), `UserPromptSubmit` (routing reminder), `Stop` (mode-routed
orchestrator). Each has a distinct, non-overlapping role. SessionStart's O(n²)
scaling was fixed in C1 (B001) and its scratch-inbox banner corrected in C2 (B026).

## Summary

- **Deprecate: none.** No surface failed the "would we build this today" bar
  outright — the product's surface area is lean and each piece earns its place.
- **Merge: 1 pair** — `consolidator` agent ↔ `board-consolidate` skill (B014).
- **Simplify: 4** — `/board-graph` (fold into rebuild), `/worker-start` (B006),
  `/board-install-permissions` delivery (B030), `/board-migrate` (B020); plus
  the `code-reviewer` rename (B021).
- **Keep: the rest**, several as exemplars (`/board-claim-release`, the MCP tool
  schemas) whose UX the weaker surfaces should be pulled up to.

None of the simplify/merge items is a blocker or major; all are tracked as P2/P3
board entries for later cycles or the Conductor build (RFC 0001).

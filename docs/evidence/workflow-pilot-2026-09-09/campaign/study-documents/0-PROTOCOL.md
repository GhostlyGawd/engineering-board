# Workflow-value pilot: predeclared protocol

Status: preparation; no live trial has started. Board entry: engineering-board/F004.
Owner: Rhen McLeod. Lead: lead-workflow-pilot-20260909.

## Question and limits

Does repository memory help an agent investigate and repair a task, beyond
ordinary repository instructions or access to selected historical evidence?
The owner approved this direction after the external
`engineering-board-value-review-2026-09-09.md` review. This is a small synthetic
mechanism pilot, not customer evidence, a reliability estimate, payment proof,
or a replacement for historical D.1 product-effect gates. Those thresholds,
corpus locks, and failed results remain unchanged.

Four newly authored Python tasks form two distinct cohorts: procedural Learning
(useful coverage guidance and an irrelevant-scope control), and proposed
hypothesis (useful discriminating investigation and a wrong-shared-cause
control). Cases are synthetic and deliberately constructed, not independently
sampled held-out incidents. Implementing agents have not seen their evaluators.
B062, B069 and the old C04 corpus are design context, not reused trial cases.

## Comparisons

Each case runs once under each condition: 12 planned arms, no replacement arms.

| Condition | Additional historical information |
|---|---|
| Ordinary | None; task, repository documentation and public tests only |
| Selected history | Manually selected equivalent memory documents in a local directory |
| Board-assisted | Equivalent historical facts in a local Board, retrieved through the released MCP server |

The shared task, starting code, base instructions, client, model, reasoning
setting and elapsed budget are identical. Condition-specific availability
instructions do not name the expected fix, useful/control label, or memory id.
The history and Board conditions share semantic historical facts, not necessarily
format, length, salience or retrieval cost. Record assertion-to-source parity,
input bytes, and selection/preparation effort. Selected history is an informed
curator comparator, not ordinary search with equal human effort.
It includes the same synthesized Learning/hypothesis guidance as the Board, not
only raw incident logs. Thus the history-to-Board contrast concerns delivery
and structured retrieval, not exclusive access to a distilled lesson.

The Board arm is an assisted, configured MCP retrieval experience. It is not a
test of spontaneous installed-plugin discovery, automatic activation, Claude
hooks, or the complete default Codex installation. Retrieval is available, not
an instruction to accept a particular Learning or confirm a hypothesis. Record
whether it was actually invoked and returned relevant information. Retrieval
failure is not silently converted into an injected-context run.

## Host and access contract

Pin Codex CLI 0.153.4, model `gpt-5.6-sol`, reasoning `medium`, and released
Engineering Board 1.13.5. Each arm has a fresh ephemeral process/session and a
separate workspace outside the maintainer repository. The common host disables
unrelated plugins, apps, hooks, multi-agent delegation and host skill discovery;
user configuration and executable rules are not loaded. The Board condition
adds only `board_context` and `board_get_entry` through the installed MCP
launcher. Record exact argv, executable/source hashes, and selected tool schemas.
No product board is mutated. Offline fixture preparation is not a trial action.

Use the workspace-write sandbox, not unrestricted execution. Authentication
continues to use the existing host account; do not change HOME or CODEX_HOME.
This is **not OS-enforced read isolation**. Evaluators, reference repairs,
expected-action metadata, sibling workspaces and prior outputs are outside the
declared task workspace, but may be technically readable. Prompts prohibit
access. Audit emitted tool traces for forbidden reads, unrelated tools and
cross-arm contamination. Absence in a trace is not a security guarantee.

The task permits inspection and edits only in its own task repository. Board
historical records and selected-history files are read-only study inputs.
An arm may add tests and change implementation without a provided answer path.
No network research, package installation, delegation or human coaching is
part of the trial. The stdlib-only public verification command is supplied.

## Freeze and stopping rules

Before launch, commit fixtures, evaluator source, runner, host settings, this
protocol, full prepared inventory, and independent acceptance review. Freeze
hashes for all source and inputs, prompts, schemas, randomized arm order and
identity mapping. Preserve model alias and client version; an alias does not
pin unobservable provider weights. Refuse missing, altered or extra prepared
inputs. A repaired protocol needs a new prelaunch review, never a repaired
already-observed arm.

Each arm has one exclusive start receipt and at most 180 seconds elapsed time,
including host startup. Record termination and partial outputs on timeout. No
outcome-driven retries, prompt corrections or extensions. Infrastructure launch
errors, client/turn/schema failures, timeouts or detected forbidden access halt
further arms pending interpretation;
all planned arms and unstarted remainder stay visible. A task failure or timeout
does not justify deleting the arm. Internal client retry behavior, if visible,
is retained in the trace; the study adds no retry loop.

Run one arm at a time to avoid concurrent resource interference. Human
interventions during an arm are zero by design; record any deviation. Wall time
is end-to-end invocation time, not isolated investigation time. Report token
usage only where emitted, dollars as not measured unless a verified cost source
is available. Preparation/review work is separate overhead, not hidden in a
claim of engineering time saved.

## Review and outcomes

Independent prelaunch verifier: review_workflow_protocol. Fixture designer:
design_workflow_cases. Runner builder: build_workflow_runner. The lead owns the
F004 coordination claim on behalf of these bounded assignments. A fresh
post-trial verifier receives patch-only packets before any condition mapping or
trace. It commits correctness judgments first; the next stage reviews traces.
Patches may themselves reveal a condition. Reviewers record inferred condition
and confidence before the mapping is revealed. Trace review is only partially
blinded because MCP calls and history paths can reveal treatment.

Report per-arm observations, separately for each cohort:

- Correctness: independent hidden checks (passed/total and specific failures),
  compatibility, completeness and unjustified implementation changes. Public
  tests alone are not correctness evidence.
- Investigation: executed useful/discriminating checks with exact trace
  references; separate inspection from speculative statements.
- Coverage: relevant sibling/lifecycle paths and regression tests inspected or
  exercised, distinguished from changes to those paths.
- Scope and epistemics: harmful broadening, unsupported systemic claims,
  treatment of irrelevant Learning, and update or refutation of a proposed
  hypothesis. Harmless extra inspection is overhead, not automatically a defect.
- Memory application: retrieved versus cited versus action-supported use.
  Direct L-only use can be recorded without inventing an H outcome.
- Overhead: total elapsed time, tool calls, emitted token usage, interventions,
  setup and review effort (not measured when unavailable).

Do not demand hypothesis confirmation: a good discriminating test or justified
refutation can be success. Do not award benefit for a citation, a verified
context token, or memory evaluation appearing early in output. Visible action
ordering is not internal reasoning evidence. No aggregate pass threshold is
introduced. Present the 12-arm table, paired descriptive differences and
failures; do not infer population efficacy from one run per case-condition.

## Durable evidence and decision

Retain sanitized source/input inventories, exact prompts, full raw event and
stderr streams, final responses, workspace snapshots/patches, start/end
receipts, evaluator outputs, staged reviews and revealed identity mapping under
this directory in Git. Retention owner: repository owner Rhen McLeod. Root
reviews artifacts for credentials or unrelated personal data before publication.
If redaction is necessary, record affected fields and the limited claim; never
silently alter an evidentiary quote or pretend a sanitized file is the raw hash.
Verify retrieval from the committed Git object before closeout. Temporary work
directories are execution locations, not the evidence destination.

Record the result and remaining uncertainty on F004, with a release decision.
A passing runner or favorable synthetic pilot does not by itself justify a
product-value claim or release. An infrastructure-limited pilot remains such;
it is not replaced until an explicit new study is defined.

# B077 Codex MCP approval control — 2026-08-15

## Identity and authoritative state

This file is the durable workpad and dated evidence record for B077. The
authoritative repository is `GhostlyGawd/engineering-board`. The live default
branch is `main` at `ead021f3489f855e0a7dc6c03ee6ec3103a93df4`. The current
worker branch is `codex/b077-mcp-approval-control` from that commit.

Engineering Board must deliver relevant, source-linked repository memory when
an agent makes an engineering decision. Approval behavior supports this outcome
only when it lets an agent retrieve memory safely and truthfully. Tool-call
counts, annotations, board closures, tests, commits, and releases do not prove
the product outcome.

## Plan

- [x] Compare otherwise equivalent annotated and unannotated read-only tools in
  a fresh Codex 0.145.0 non-interactive host.
- [x] Retain an otherwise equivalent mutating tool as the negative control.
- [x] Decide whether the observed cancellation is caused by annotations,
  approval policy, their combination, or a host limitation.
- [x] Implement the smallest supported change only if the control supports it.
- [x] Run focused checks and the complete maintained suite on the final
  reviewed diff.
- [ ] Complete independent review, pull-request CI, merged-main CI, release,
  reinstall, and installed-host validation when a product change ships.
- [ ] Run two consecutive representative installed dogfood passes before B077
  resolves.

## Acceptance criteria

### Worker phase

- [x] Record the annotated and unannotated read-only outcomes with the same
  transport, command, tool body, prompt, host version, and approval policy.
- [x] Record the mutating negative control under the same host and policy.
- [x] State a falsification result. Do not infer causality from schema presence
  or a direct STDIO call.
- [x] If the hypothesis survives, classify all 19 tools conservatively and test
  the exact public `tools/list` contract.
- [x] Reconcile implementation, tests, current documentation, security claims,
  examples, architecture, release notes, and dated evidence.

### Post-merge phase

- [ ] Pull-request checks and exact merged-main checks pass.
- [ ] The immutable release tag, bundle, registry records, and package records
  identify the same merged commit if a release is required.

### Closeout phase

- [ ] A fresh installed Codex process completes `board_status` and
  `board_context` without a per-call prompt.
- [ ] A mutating board control remains approval-gated or denied.
- [ ] Two consecutive representative passes cover initialization, capture and
  claim, graph and context retrieval, hooks, and installation without a new
  reproducible blocker, false state, data-loss risk, recurring error, or
  undocumented workaround.
- [ ] B077 is revalidated from its canonical entry after closeout merges and
  merged-main checks pass.

## Control evidence matrix

| Sequence | Failure injection | Expected semantic outcome | Durable evidence | Test |
|---|---|---|---|---|
| Fresh host lists and calls an unannotated read-only tool | Omit `annotations` | Under `writes`, the host prompts or cancels because the default is not read-only | This workpad plus sanitized event result | Ephemeral Codex host control |
| Fresh host lists and calls the equivalent annotated read-only tool | Set `readOnlyHint: true`; keep all other variables equal | Under `writes`, the host completes without a per-call prompt if annotations control the decision | This workpad plus sanitized event result | Ephemeral Codex host control |
| Fresh host lists and calls the equivalent mutating tool | Set `readOnlyHint: false` | Under `writes`, the host prompts, cancels, or denies; it must not silently execute | This workpad plus sanitized event result | Ephemeral Codex host control |
| Fresh host calls installed `board_status` and `board_context` | Use the released plugin and supported policy | Both calls complete without a per-call prompt after the supported change | Closeout evidence | Installed Codex dogfood |
| Fresh host attempts a mutating installed board tool | Use the same released plugin and policy | The host prompts, cancels, or denies | Closeout evidence | Installed Codex negative control |

### Worker control result

All discriminating cells used Codex 0.145.0, the same one-tool Node STDIO
server, tool body, prompt, read-only sandbox, and ephemeral configuration.

| Policy | Annotation cell | Result |
|---|---|---|
| `writes` | `readOnlyHint: true` | Completed and returned `CONTROL_OK` |
| `writes` | No annotations | Returned `user cancelled MCP tool call` |
| `writes` | `readOnlyHint: false` | Returned `user cancelled MCP tool call` |
| `auto` | `readOnlyHint: true` | Completed and returned `CONTROL_OK` |
| `auto` | No annotations | Returned `user cancelled MCP tool call` |

The matched two-policy comparison isolates the annotation: under both `writes`
and `auto`, the annotated read completed and the otherwise equivalent omitted
annotation cancelled. The policy did not change that read-only fixture
outcome. `writes` remains the conservative plugin default because it gates
every tool whose maximum capability can modify the repository. No dangerous
bypass or persistent configuration was used.

The same controls then ran against the modified source server. A fresh Codex
process completed `board_status` under `writes` and reported B077 in progress,
B078 ready, and no unpromoted scratch. A matched `board_update_entry` call with
the valid schema and nonexistent `B999` entry reached the Codex MCP call state
but returned `user cancelled MCP tool call` before the server executed it.
This proves the source integration preserves the write gate while allowing a
real read-only board call. These runs also used ephemeral configuration and a
read-only sandbox.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Read-only context retrieval can run under the supported Codex `writes` policy | Required | Six pure-read tools expose `readOnlyHint: true`; Codex-specific config selects `writes` | Annotated versus unannotated host control passed; installed `board_status`/`board_context` pending | README, MCP server guide, architecture, security, LLM guidance, changelog, dated evidence | Worker evidence passed; installed gate pending |
| Mutating board operations remain approval-gated or denied | Required | Every tool with a write-capable branch exposes `readOnlyHint: false` | Equivalent mutating control passed; installed board mutation control pending | Security, MCP server guide, dated evidence | Worker evidence passed; installed gate pending |
| Public tool metadata describes actual side effects conservatively | Required | All 19 tools expose four Boolean annotations; mixed tools use maximum capability | Exact and repeated `tools/list` assertions plus paths-and-bytes snapshots for every declared read tool and one mutating detector control | MCP server guide, architecture, changelog | Focused checks passed |
| Product memory semantics remain unchanged | Required | Graph, context, hypotheses, outcomes, entries, and claims retain their existing handlers | Existing graph, context, outcome, evaluation, lifecycle, and security suites | Product evolution specification, examples, visuals | Complete regression suite passed |
| Release and installation claims identify immutable artifacts | Required if a release ships | Use the documented patch-release process after merged-main checks | Version coherence, release workflow, registry and installed-revision checks | Release guide, changelog, closeout evidence | Post-merge pending |

## Implementation progress

- B077 is claimed and is `in_progress`.
- `TOOLS` now stores explicit annotations for all 19 tools. `public_tools()`
  returns those values and still omits the internal handler.
- The Codex manifest selects `codex-mcp.json`, whose `writes` default gates
  every non-read-only tool. The generic `.mcp.json` remains unchanged for
  Claude Code and other hosts.
- Mixed preview/apply tools use their maximum capability. All tools remain
  closed-world and local to the caller-selected repository.
- The current MCP reference now reports context contract version 3, ranking
  rule version 2, and the Python claim implementation. These were
  documentation-only drift found during alignment review.

## Validation evidence

- Installed v1.13.2 on Codex 0.145.0 previously cancelled `board_status` and
  `board_context` during approval elicitation in non-interactive execution.
- A direct installed STDIO session listed 19 tools with no annotations and
  completed both read-only calls. That proves server behavior, not Codex host
  approval behavior.
- The official Codex MCP contract defines `auto`, `prompt`, `writes`, and
  `approve`. The `writes` mode prompts for tools that are not marked read-only.
- The MCP tool-annotation contract defines the four Boolean hints and states
  that they are untrusted hints. Their absence uses conservative defaults.
- Before implementation, the exact tools/list tests failed because every tool
  omitted `annotations`. The packaged-launcher test failed the same contract.
- After implementation, the MCP suite passed 221 checks. The packaged Codex
  launcher check passed with the exact 19-tool map. Documentation coherence
  passed current release, context, approval, count, and historical-boundary
  checks.
- Independent review found that the metadata assertions were circular. The
  strengthened MCP suite now snapshots every repository path and file byte,
  calls all six declared read-only handlers, and requires an unchanged tree.
  A `board_capture_finding` control changes the snapshot and proves that the
  detector observes writes. The focused suite passes 230 checks.
- The final reviewed product and test diff passed all 21 maintained suites in
  71.23 seconds, including the 230-check MCP suite. Only this dated result was
  appended afterward.
- Independent re-review reproduced the 230-check focused result, matched the
  recorded and current graph fingerprint, verified the canonical workpad
  state, and found no remaining release-blocking diff issue.
- A source-host integration completed real `board_status` under `writes`; the
  matching annotated `board_update_entry` control was cancelled before server
  execution under the same policy.
- The pre-review worker diff passed all 21 maintained suites in 59.99 seconds.
  This included 221 MCP checks, exact Codex launcher metadata, release
  preparation, documentation coherence, evaluation, session-start, claim,
  lifecycle, security, and compatibility coverage. That run is superseded by
  the final full-suite gate after the behavioral read-only guard was added.
- Strict Claude validation exposed a separate, pre-existing ignored
  `plugins[0].policy` field. The board captured and promoted that finding as
  B078 instead of folding it into B077 or hiding it behind normal validation.

## Uncertainties and assumptions

- The controlled comparison supports missing annotations as the cause of the
  read-only cancellation. Release packaging and installed-plugin behavior
  remain separate gates.
- Tool-level annotations cannot vary by input. A tool that has both preview
  and mutation modes must be classified by its possible mutating behavior.
- Codex 0.145.0 accepts the bundled `writes` default, but only a fresh released
  installation can prove the packaged path and user-policy overlay together.

## Blockers

No human action is required. The remaining gates are repository regression,
review, delivery, release, reinstall, and installed-host validation.

## Handoff and resume route

Completion state: `post-merge-pending`.

Next owner: the primary dogfood loop.

Remaining gates: pull-request CI, merged-main CI, release and registry checks,
reinstall, installed positive and negative controls, and two representative
passes.

Evidence destination: this file for worker and post-merge evidence; append a
separate dated closeout record only when release and installed evidence require
a follow-up pull request.

Resume route: proceed through the normal pull-request and patch-release
lifecycle, then run the installed controls from fresh Codex processes.

Terminal action: `keep-open`. Keep B077 open until every closeout criterion
passes.

# B077 Codex MCP approval control — 2026-08-15

## Identity and authoritative state

This file is the durable workpad and dated evidence record for B077. The
authoritative repository is `GhostlyGawd/engineering-board`. The live default
branch released v1.13.3 at
`f4b44d9c8b63def225be2f3e9daa22309713768f` and contains the release and installed
evidence through `9443daa331c3bfb5c916df729402423b9c62c30a`. The current lifecycle
branch is `codex/b077-resolve` from that commit.

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
- [x] Complete independent review, pull-request CI, merged-main CI, release,
  reinstall, and installed-host validation when a product change ships.
- [x] Run two consecutive representative installed dogfood passes before B077
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

- [x] Pull-request checks and exact merged-main checks pass.
- [x] The immutable release tag, bundle, registry records, and package records
  identify the same merged commit if a release is required.

### Closeout phase

- [x] A fresh installed Codex process completes `board_status` and
  `board_context` without a per-call prompt.
- [x] A mutating board control remains approval-gated or denied.
- [x] Two consecutive representative passes cover initialization, capture and
  claim, graph and context retrieval, hooks, and installation without a new
  reproducible blocker, false state, data-loss risk, recurring error, or
  undocumented workaround.
- [x] B077 is revalidated from its canonical entry after closeout merges and
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
| Read-only context retrieval can run under the supported Codex `writes` policy | Required | Six pure-read tools expose `readOnlyHint: true`; Codex-specific config selects `writes` | Annotated versus unannotated host control and installed `board_status`/`board_context` passed | README, MCP server guide, architecture, security, LLM guidance, changelog, dated evidence | Installed gate passed |
| Mutating board operations remain approval-gated or denied | Required | Every tool with a write-capable branch exposes `readOnlyHint: false` | Equivalent source and installed board mutation controls cancelled before execution | Security, MCP server guide, dated evidence | Installed gate passed |
| Public tool metadata describes actual side effects conservatively | Required | All 19 tools expose four Boolean annotations; mixed tools use maximum capability | Exact and repeated `tools/list` assertions plus paths-and-bytes snapshots for every declared read tool and one mutating detector control | MCP server guide, architecture, changelog | Focused checks passed |
| Product memory semantics remain unchanged | Required | Graph, context, hypotheses, outcomes, entries, and claims retain their existing handlers | Existing graph, context, outcome, evaluation, lifecycle, and security suites | Product evolution specification, examples, visuals | Complete regression suite passed |
| Release and installation claims identify immutable artifacts | Required if a release ships | Used the documented patch-release process after merged-main checks | Version coherence, release workflow, registry, asset checksum, and installed-revision checks | Release guide, changelog, closeout evidence | Published and installed |

## Implementation progress

- B077 is resolved and archived after the release-evidence merge, its exact
  merged-main check, fresh canonical revalidation, and claim release passed.
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
- Release workflow `31917453698` published v1.13.3 from merged main
  `f4b44d9c8b63def225be2f3e9daa22309713768f`. The immutable tag, 66,718-byte
  bundle, SHA-256 pin, MCP Registry latest record, PyPI files, and installed
  revision align.
- A fresh installed Codex process completed real `board_status` and
  `board_context` calls without a prompt. The installed write control was
  cancelled before server execution.
- Two counted isolated passes retrieved path-scoped L001 memory through both
  MCP context and installed SessionStart, with no warning. Both passes covered
  initialization, capture, promotion, claim, graph, context, hook, release,
  and automatic temporary-repository cleanup.
- Release-evidence PR #154 merged as
  `9443daa331c3bfb5c916df729402423b9c62c30a`. Exact merged-main test run
  `31918032704` passed. A fresh canonical B077 check then confirmed that every
  Done-when criterion was checked before the claim was released and the entry
  was resolved.
- The final five-file canonical lifecycle diff passed all 21 maintained suites
  in 58.6 seconds. An independent read-only audit matched BOARD, ARCHIVE, GRAPH,
  claim absence, canonical fingerprints, and terminal workpad state.

## Uncertainties and assumptions

- The controlled comparison supports missing annotations as the cause of the
  read-only cancellation. Release packaging and installed-plugin behavior were
  separate gates, and both passed before resolution.
- Tool-level annotations cannot vary by input. A tool that has both preview
  and mutation modes must be classified by its possible mutating behavior.
- The installed controls prove Codex 0.145.0 uses the packaged `writes`
  default. A user or managed environment can still choose a stricter policy.

## Blockers

No human action is required. No B077 product, evidence, release, installation,
or canonical revalidation gate remains.

## Handoff and resume route

Completion state: `closeout`.

Next owner: the primary dogfood loop on B078.

Remaining gates: no B077 acceptance gate remains. Merge this canonical
lifecycle transition and confirm its exact merged-main check as the delivery
record; those delivery actions do not reopen B077.

Evidence destination: this workpad and
`docs/evidence/2026-08-16-v1.13.3-release-and-installed-validation.md`.

Resume route: deliver this canonical lifecycle transition, verify B077 is
absent from the live board and present once in the archive on merged main, then
continue the dogfood loop with B078.

Terminal action: `resolve-and-archive`.

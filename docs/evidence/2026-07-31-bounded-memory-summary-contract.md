# Bounded memory summary contract workpad

Date: 2026-07-31

State: version 1.12.0 published and verified; closeout evidence pending merge

Completion state: `self-contained`

## Identity and authoritative state

Active outcome: give an agent the bounded content of each relevant repository
memory in the first context result. Do not require a second source-read step.

The product owner approved this outcome on 2026-07-31. The approval selects
the self-contained memory-summary option in Product Evolution Spec section
21.13. It does not approve the version 4 evaluation corpus as a scored
baseline.

Repository context:

```text
repository: GhostlyGawd/engineering-board
default_branch: main
baseline_commit: 64c0c722bd6db2e92b16aa1df525927d9cb6fba6
portfolio_status: inventory-only
audit_source: GhostlyGawd/repo-audit@0ced6f4136b12c6251439ff72ca8f22b6dec9b61
```

Source precedence:

1. The product owner's 2026-07-31 approval.
2. `docs/PRODUCT_EVOLUTION_SPEC.md`, especially sections 20 and 21.13.
3. The shipped version 1.11.0 context contract and canonical record schemas.
4. Current implementation and current-truth documentation.

## Exact implementation contract

The shared context response uses contract version `2`. Each result adds these
fields:

- `title`: a stable, one-line title with at most 160 Unicode characters.
- `summary_kind`: `cluster_scope`, `proposed_root_cause`, or
  `learning_takeaway`.
- `summary`: one-line canonical memory content with at most 2,000 Unicode
  characters.

The existing `status` field remains the epistemic state. The existing `kind`
field distinguishes a structural cluster, hypothesis, rejected negative
memory, and Learning. This separation prevents a proposed root cause from
appearing as a confirmed fact.

Content rules:

- A cluster title uses its normalized pattern labels. Its summary identifies
  pattern identifiers, normalized labels, member identifiers, and affected
  top-level domains.
- A hypothesis and rejected negative memory use the canonical H### title and
  proposed-root-cause section.
- A Learning uses the canonical L### title and Takeaway section.
- The core flattens line separators and control separators before it returns
  content. It truncates only after the applicable character limit.
- Every adapter treats the title and summary as untrusted repository data.
- The context fingerprint and token bind context-contract version `2`.
- Ranking rule version `1` remains unchanged because eligibility, scores, and
  ordering do not change.

The 2,000-character summary limit preserves the existing maximum proposed
root-cause value. It also bounds older or manually written Learning content.

## Source transformation

The approved source says to add a stable title, a bounded finding summary, an
epistemic status, match reasons, and source references. The current result
already returns `status`, `why`, `matched_signals`, score components, and
`source_refs`. The implementation therefore adds only the missing title and
typed summary. It adds a response-contract version so a client can detect the
additive interface.

The central specification says that a hypothesis summary should contain the
proposed root cause, a Learning summary should contain the Takeaway, and a
cluster summary should identify normalized patterns and member scope. The
exact fields above preserve those meanings. No source condition was removed.

## Requirements

- `BMS-REQ-001`: The shared context core shall return context-contract version
  `2` in each context brief.
- `BMS-REQ-002`: Each returned memory shall include a one-line title of at
  most 160 Unicode characters.
- `BMS-REQ-003`: Each returned memory shall identify its summary as
  `cluster_scope`, `proposed_root_cause`, or `learning_takeaway`.
- `BMS-REQ-004`: Each returned memory shall include a one-line summary of at
  most 2,000 Unicode characters.
- `BMS-REQ-005`: The shared core shall derive each summary only from the
  canonical content that its summary kind identifies.
- `BMS-REQ-006`: The shared core shall preserve each returned memory kind and
  canonical epistemic status.
- `BMS-REQ-007`: The command, MCP, SessionStart, and UserPromptSubmit adapters
  shall expose semantically equivalent title, summary, status, match, and
  source facts.
- `BMS-REQ-008`: The context fingerprint and token shall bind the context
  contract version `2` while ranking rule version `1` remains unchanged.
- `BMS-REQ-009`: Context retrieval shall not modify canonical or derived board
  state, execute code, or use network access after it adds memory content.
- `BMS-REQ-010`: The shared core shall not infer a stronger epistemic state
  from summary content.

## Plan and acceptance phases

- [x] Worker: record the approved choice and exact additive interface.
- [x] Worker: implement bounded content in the shared core.
- [x] Worker: update plugin and MCP adapters.
- [x] Worker: add kind, limit, sanitization, fingerprint, and adapter-parity
  tests.
- [x] Worker: align the central spec, README, roadmap, architecture, command, MCP
  description, changelog, security text, and evaluation guidance.
- [x] Worker: run focused and complete repository tests.
- [x] Worker: prepare coordinated version 1.12.0 and reproduce its MCP bundle
  checksum.
- [x] Worker: pass pull-request continuous integration.
- [x] Post-merge: pass merged-main continuous integration.
- [x] Post-merge: publish and verify version 1.12.0.
- [x] Closeout: append release evidence in a separate pull request.
- [ ] Closeout: merge evidence, pass merged-main continuous integration, and
  revalidate current GitHub state.

Acceptance criteria:

- Worker: all four memory kinds return the approved content contract.
- Worker: multiline and over-limit canonical content cannot escape one line
  or the character bounds.
- Worker: identical requests return identical payloads.
- Worker: CLI and MCP results equal the shared-core result.
- Worker: automatic hooks show title, summary, epistemic state, match reason,
  and source references without following repository instructions.
- Worker: version 4 remains unlocked and cannot enter a scored run.
- Post-merge: the exact merge commit passes the `tests` workflow.
- Post-merge: GitHub, PyPI, MCP Registry, and MCP bundle version 1.12.0 agree.
- Closeout: dated evidence records publication, checksums, live state, and
  documentation alignment.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Self-contained memory content | Owner-approved | Shared `build_context` result | Kind matrix and repeat equality | Product spec and README | Implemented and focused tests pass |
| Stable bounded title | Required | One-line, 160-character core field | Long and multiline fixtures | Response contract | Implemented and verified |
| Typed bounded summary | Required | One-line, 2,000-character core field | Hypothesis, negative memory, Learning, and cluster fixtures | Response contract and command | Implemented and verified |
| Epistemic separation | Required | Existing `kind` and `status` plus `summary_kind` | Proposed, rejected, and outcome-state assertions | Product spec and architecture | Implemented and verified |
| Adapter parity | Required | Shared core plus command, MCP, SessionStart, and prompt renderers | Core/CLI/MCP equality and hook fixtures | README, command, and MCP description | Implemented and focused tests pass |
| Contract identity | Required | Context-contract version in response, fingerprint, and token | Token decode and fingerprint assertions | Product spec | Implemented and verified |
| Security and privacy | Required current truth | Offline read, one-line sanitization, size limits, untrusted-data labels | No-write, hostile-text, and size tests | SECURITY and command guidance | Full suite passed |
| Version and publication | Required when shipped | Coordinated 1.12.0 release preparation and publication | Version coherence, bundle checksum, release workflow, and live checks | Changelog, manifests, README badge, and release evidence | Published and live surfaces verified |
| Version 4 evaluation baseline | Explicitly deferred | Proposal remains unlocked | Existing preparation rejection and 22 evaluation tests | Product spec and dated v4 evidence | Reviewed and unaffected |
| SQLite, embeddings, hosted services, telemetry, and cross-repository reads | Explicitly deferred | No storage or service change | Existing offline and Markdown-authority suites | Architecture and security | Reviewed and unaffected |
| Historical evidence | Required preservation | No historical report changes | Git diff inspection | Existing dated evidence | Reviewed and unaffected |

## Implementation progress

The shared core returns `title`, `summary_kind`, and `summary` for clusters,
hypotheses, rejected negative memory, and Learnings. The context response,
fingerprint, and token bind context contract version `2`. The command and MCP
consume the shared result. SessionStart and UserPromptSubmit render the
content with an explicit untrusted-data boundary.

Current-truth documentation describes the fields, limits, epistemic status,
security boundary, version identity, and unchanged evaluation state.

## Validation evidence

- D-backed Ubuntu virtual disk: confirmed at
  `D:\Codex\WSL\Ubuntu\ext4.vhdx`.
- Runtime: Node.js 22.23.1 and Python 3.12.3.
- Codeweb: unavailable for the Linux-native worktree because the Windows
  server rewrites `/home/...` to `C:\home\...`. Bounded source inspection is
  the fallback.
- Requirements checker:
  `DRAFT — SOURCE OR DECISIONS INCOMPLETE`,
  `sha256:bf6f5c7c08cd2a6b9ad9b46b90d1f07633d7bd946de40369dff50fafd5e96f28`,
  zero deterministic failures, one open digest-approval decision.
- Milestone D context and outcome matrix: 15 checks passed.
- Prompt guard: 5 checks passed.
- SessionStart: 11 checks passed, including the 1,200-entry benchmark.
- Evaluation harness: 22 tests passed.
- Documentation coherence: passed.
- Python compilation and changed-shell syntax: passed.
- Complete repository release tree: 19 suites passed and zero failed.
- Prepared MCP bundle SHA-256:
  `f7de3784a0fed3604e2b774ef300533e36327da238eb409e8ddca453cf67c66c`.
- Pull request 120 test run 30606389189: passed.
- Merged-main test run 30606464595: passed.
- Pages run 30606464594: passed.
- Release run 30606518305: passed.
- Release tag `v1.12.0` dereferences to
  `ec05d21bdcb5a5b6c806ee8edd56768362c63c2f`.
- The downloaded 147,751-byte MCP bundle matches the pinned SHA-256.
- PyPI serves unyanked version 1.12.0 wheel and source distributions.
- The official MCP Registry reports version 1.12.0 as active and latest. Its
  bundle URL and SHA-256 match the GitHub Release.
- The product site returned HTTP 200 and contains the bounded-summary product
  copy and 19-tool statement.

## Uncertainties and assumptions

The owner selected the self-contained result. The 160-character title and
2,000-character summary limits derive from the accepted H### schema. They are
implementation limits, not new storage limits.

The implementation will not seal or execute the version 4 evaluation corpus.
A new non-scored preflight must validate the product effect after release.

## Blockers

None.

## Handoff

Current semantic state: implementation and version 1.12.0 publication
complete; release evidence is ready for its closeout pull request.

Next owner: Engineering Board delivery agent.

Remaining gates: closeout pull-request continuous integration, closeout merge,
merged-main continuous integration, and final live-state revalidation.

Evidence destination:
`docs/evidence/2026-07-31-v1.12.0-release-validation.md`.

Resume route: merge the release-evidence pull request and verify its exact
main commit.

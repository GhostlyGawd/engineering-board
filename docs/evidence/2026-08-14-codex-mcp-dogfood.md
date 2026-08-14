# Codex MCP dogfood workpad — 2026-08-14

State: completed

Completion state: `closeout`

## Active outcome

Connect Engineering Board to Codex and use the `eb-self` board to improve the
product. Keep canonical memory in repository-owned Markdown. Do not add a
database, hosted service, provider account, telemetry, or cross-repository read.

Repository context:

```text
repository: GhostlyGawd/engineering-board
default_branch: main
baseline_commit: a2208852d3da5fdb3a1b2c6c6df49d77d9d06da8
portfolio_status: inventory-only
audit_source: GhostlyGawd/repo-audit@0ced6f4136b12c6251439ff72ca8f22b6dec9b61
```

## Dogfood evidence

Codex now starts Engineering Board as a local WSL STDIO MCP server. The MCP
handshake negotiated protocol version `2025-06-18` and returned all 19 tools.

The first natural `board_context` request returned no memory because it supplied
task text without a structural signal. A request with entry `B023` and the core
path surfaced Learning `L002`. That Learning states that board operations must
model the same open-versus-resolved lifecycle.

While the agent captured the task-only diagnostic gap, promotion preview
proposed identifier `B023`. Resolved canonical bug `B023` already owns that
identifier. The agent stopped before apply. The promotion planner used the
open-entry graph loader for deduplication, provenance, and allocation. This
reused an identifier from the resolved lifecycle.

The complete test suite then rebuilt the MCP bundle and found a checksum
mismatch. The bundle builder falsely reported that it had already updated the
pin. The pin belongs to the immutable published version and must not change on
an Unreleased product branch. Entry `B064` records this release-boundary defect.

## Requirements

- `DOG-REQ-001`: Promotion planning shall include open and resolved canonical
  entries when it checks duplicate content and provenance.
- `DOG-REQ-002`: Promotion planning shall allocate each new identifier above
  all canonical identifiers of the same entry type.
- `DOG-REQ-003`: Graph construction shall continue to exclude resolved entries
  from active graph ranking.
- `DOG-REQ-004`: A task-only context request that returns no eligible memory
  shall explain that the caller must add `files`, `entry_ids`, or `cwd`.
- `DOG-REQ-005`: The diagnostic shall not weaken structural eligibility or make
  lexical overlap sufficient.
- `DOG-REQ-006`: Current specifications, security guidance, commands, MCP
  guidance, changelog, tests, and dated evidence shall describe the behavior.
- `DOG-REQ-007`: The bundle builder shall report whether current source matches
  the published checksum.
- `DOG-REQ-008`: CI shall permit a bundle mismatch only when `[Unreleased]`
  contains a release note. Release preparation shall restore exact alignment.

## Plan

- [x] Register the MCP server in Codex.
- [x] Verify the MCP handshake and tool list.
- [x] Query status, insights, context, and canonical entries through MCP.
- [x] Create and claim `B062` through MCP.
- [x] Fix promotion lifecycle allocation and add regression coverage.
- [x] Promote the original task-only diagnostic finding after the allocator fix.
- [x] Add the bounded task-only diagnostic without changing eligibility.
- [x] Correct the bundle-builder message and Unreleased checksum gate.
- [x] Run focused and complete repository tests.
- [x] Resolve the dogfood entries and release their claims.
- [x] Pass pull-request and merged-main continuous integration.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Promotion lifecycle identity | Required | Complete canonical loader for promotion | Resolved-ID allocator fixture passes | Product spec, architecture, security, command, MCP guide | Aligned |
| Active graph scope | Required | Open-entry graph loader remains unchanged | Resolved fixture absent from graph | Architecture and product spec | Aligned |
| Task-only empty diagnostic | Required | Bounded warning in shared context core | Lexical-decoy and explicit-pattern checks pass | Context command, MCP guide, security, product spec | Aligned |
| Structural eligibility | Required security boundary | Existing ranking rule version 1 | Task words remain ineligible alone | Architecture and security | Preserved |
| Codex MCP connection | User-approved local setup | Global STDIO configuration through WSL | Handshake and 19-tool list | Dated evidence only; no repository setup change | Verified locally |
| Published bundle integrity | Required release boundary | Current published pin remains unchanged; builder reports match state | Exact match or documented Unreleased change | Release guide, launch guide, product spec, changelog | Aligned locally |
| Version and release | Not authorized in this task | No version or publication change | Version-coherence suite | Changelog Unreleased only | Reviewed and unaffected |
| Canonical Markdown and storage | Required current boundary | No storage change | Existing authority and offline suites | Architecture and security | Reviewed and unaffected |
| Visual documentation | Required product surface | No visual behavior changes | Existing visual checks | Current visuals remain accurate | Reviewed and unaffected |

## Local validation

- `milestone-b-pattern-pipeline`: 15 checks passed.
- `milestone-d-context-outcome-intelligence`: 15 checks passed.
- MCP server: 168 checks passed.
- Complete repository suite: 19 suites passed and 0 failed.
- Configured MCP probe: protocol `2025-06-18`, server version `1.12.0`, and
  the task-only corrective warning returned through `board_context`.
- `B062`, `B063`, and `B064`: resolved through MCP after validation. Their
  claims were released.

## External gates

- Pull request [#122](https://github.com/GhostlyGawd/engineering-board/pull/122)
  merged commit `5ef2c47db19f4c79210cf2e8eea1938a29d15de2` into `main`.
- Pull-request runs `31771438127` and `31771471356` passed `run-all`.
- Merged-main run `31771571172` passed `run-all` for exact commit
  `5ef2c47db19f4c79210cf2e8eea1938a29d15de2`.
- Release: not authorized and not required for this task.

Evidence destination:
`docs/evidence/2026-08-14-codex-mcp-dogfood.md`.

Terminal action: complete. No release or deployment action remains in scope.

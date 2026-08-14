# Codex MCP relative-cwd dogfood workpad — 2026-08-14

State: implementation validation

Completion state: `post-merge-pending`

## Active outcome

Use Engineering Board through its configured Codex MCP server. Correct the
observed rejection of the safe repository-relative current directory `.`.
Keep file-path validation strict. Preserve the separate promotion-provenance
collision as open entry `B065`.

Repository context:

```text
repository: GhostlyGawd/engineering-board
default_branch: main
baseline_commit: a85593d69d2896dec5158b49471b16b8e5481c09
portfolio_status: inventory-only
audit_source: GhostlyGawd/repo-audit@0ced6f4136b12c6251439ff72ca8f22b6dec9b61
```

## Dogfood evidence

The configured `board_context` tool rejected `cwd: "."` with `cwd contains an
unsafe path`. The same request accepted the absolute repository root. The MCP
schema permits an absolute path inside the repository or a repository-relative
path. The product specification requires `cwd` to resolve inside the
repository.

The capture and promotion pass also found a separate provenance collision. A
recreated daily scratch file reused source index `0`, which promotion treated
as already applied to unrelated resolved entry `B063`. Entry `B065` preserves
that open defect. Entry `B066` owns the relative-cwd correction.

## Requirements

- `CWD-REQ-001`: `cwd: "."` shall represent the repository root.
- `CWD-REQ-002`: Relative and absolute repository-root inputs shall normalize
  to the same logical context.
- `CWD-REQ-003`: The root exception shall apply only to `cwd`. A file input of
  `.` shall remain invalid.
- `CWD-REQ-004`: Parent traversal, absolute file paths, and out-of-repository
  current directories shall remain invalid.
- `CWD-REQ-005`: Shared-core and MCP-adapter tests shall drive the corrected
  behavior.

## Plan

- [x] Reproduce the configured MCP failure.
- [x] Capture and promote the finding through Engineering Board.
- [x] Add a failing shared-core and MCP-adapter regression.
- [x] Restrict repository-root normalization to `cwd`.
- [x] Run the complete repository test suite.
- [ ] Verify pull-request and merged-main continuous integration.
- [ ] Revalidate the configured MCP server after it reloads merged code.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Repository-relative `cwd` root | Required | Context path normalizer permits root only when requested by `cwd` | Core, MCP adapter, and real STDIO server use `cwd: "."` | Product specification and MCP schema already permit the input | Required conflict corrected locally |
| File-path safety | Required security boundary | File normalization does not enable the root exception | Invalid-input matrix retains `files: ["."]` rejection | Security guidance already requires safe repository-relative files | Preserved locally |
| Parent and absolute-path rejection | Required security boundary | Existing traversal and containment checks are unchanged | Existing invalid-path and out-of-root checks | Security and product specification | Reviewed and unaffected |
| User command behavior | Required current surface | `/board-context` continues to pass absolute `$PWD` | Existing adapter matrix | Command example remains accurate | Reviewed and unaffected |
| Storage and canonical authority | Required architecture boundary | No storage or authority change | Existing read-only context checks | README and architecture remain accurate | Reviewed and unaffected |
| Version, release, and bundle | Not authorized in this task | No version, checksum, tag, or publication change | Existing coherence checks remain applicable | Release guidance remains accurate | Reviewed and unaffected |
| Visual documentation | Required product surface | No visual behavior changes | Existing visual checks remain applicable | Current board-view evidence is unaffected | Reviewed and unaffected |

## Validation

- Focused regression: `milestone-d-context-outcome-intelligence` reports 15
  checks passed.
- Real MCP subprocess: 171 checks passed, including equality between relative
  and absolute repository-root context requests.
- Complete repository suite: 19 suites passed and 0 failed.
- Board lifecycle: `B066` is resolved after validation. `B065` remains open in
  the ready queue. The board reports no in-progress or blocked entries and no
  unpromoted scratch.
- Configured MCP process: still has the pre-change module loaded and continues
  to reject `cwd: "."`; reload validation is pending.

## External gates

- Pull request: pending.
- Merged-main continuous integration: pending.
- Configured MCP reload probe: pending.
- Release: not authorized and not required.

Evidence destination:
`docs/evidence/2026-08-14-codex-mcp-relative-cwd.md`.

Terminal action: keep open until merged-main CI and the reloaded MCP probe pass.

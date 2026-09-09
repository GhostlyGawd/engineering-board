# F005 — canonical hypothesis details

## Assignment and scope

Owner approved F005 after the retained workflow pilot. The lead owns claim
`lead-hypothesis-details-20260909` on behalf of builder
`build_hypothesis_details`; the owner-file creation timestamp is
2026-09-09T15:48:59Z. Base: `cad55eb`. Builder worktree:
`/private/tmp/eb-hypothesis-details-20260909`; source commit:
`c91b972078e53af6ab7c8cd27a0ad82ddf97bb5c`.

The builder changed only `mcp-server/engineering_board_mcp.py` and its test
module. The lead owns documentation, retained installation verification and
release integration. Independent verifier: `verify_hypothesis_details`, in a
fresh context, reading requirements/source before author conclusions.

The user-visible route is `board_context` → H id → `board_get_entry`. It returns
the existing response shape with the exact validated canonical text. No new
tool, context payload contract, outcome counter, mutation route or automatic
causal confirmation is added. Generic B/F/Q/O/L reads/list/update remain
unchanged. H reads fail closed on malformed/linked sibling records because
they use the whole canonical registry validator; this is documented.

## Verification and independent review

Before implementation, the new real-stdio regression retrieved H001 through
context but failed to open it: `entry 'H001' not found in project 'details'`.
After implementation:

- MCP suite: 341 checks, including 106 new checks covering all six canonical
  statuses, full details, context/token equality, legacy behavior, malformed,
  missing, duplicate, linked and escaping records, and read-only invariance.
- Hypothesis contract: 7 checks passed. Context/outcome matrix: 16 passed.
- Existing evaluation harness: 39 tests passed; historical gates unchanged.
- Full repository suite: 22 suites passed.
- Claude marketplace strict validation passed without warnings before release
  preparation; the prepared version must pass this gate again.

The verifier independently confirmed exact validated-snapshot return behavior,
whole-registry errors, legacy compatibility, traversal/control-character
rejection, link safety and no repository writes. Its MCP suite passed with an
isolated temporary directory after a shared-temp run encountered unrelated
directory creation in the existing B024 assertion. The lead's full suite also
passed. No failed test was waived.

Review identified a defect in the first retained installation probe: its
file-only inventory could miss creation of empty runtime directories. The
corrected inventory records directory paths, symlink targets without traversal,
file bytes and permissions. Negative controls detect each of those changes,
including dangling links. Earlier `source-smoke.json` is retained as weaker
historical evidence; `source-smoke-v2.json` supersedes its state-invariance claim.

Final independent verdict: **PASS at
`660f36057ad304c65413adf0f76522e48e6a4962`**. The corrected two-case transport
probe independently returned exact H101/H102 Markdown, retained proposed
status, rejected missing H records, and preserved the repository inventory.
It made zero model calls. No source or verification-script finding remains.

## Delivery and limits

Retained verifier: [verify_installed.py](verify_installed.py). Run with the
actual installed launcher after publication; source transport is not a claim
of a published installation. Retention owner: Rhen McLeod.

The compatible-feature batch targets 1.14.0 through coordinated release
preparation, strict host validation, CI, exact-main publication and installed
verification. A separate dated release record will identify those results.
Agent cost and isolated engineering effort were not measured. This feature
makes full hypothesis evidence reachable; it does not establish better
diagnoses, time saved or a historical D.1 pass.

## Prepared release gates

`scripts/prepare-release.py 1.14.0` preview and apply produced the same twelve
coordinated version surfaces and bundle SHA-256:
`d506f1348a6248f3a9cf6583468122e49e0fb07c4e64328d0b80fec68be9a782`.
The prepared tree passed all 22 suites and `claude plugin validate --strict .`
without warnings. Its retained two-case transport receipt is
`prepared-1.14.0-smoke.json`. Publication and actual installed-host receipts are
still separate gates; the prepared marketplace ref must not be installed before
the release workflow creates its tag.

# B078 Claude marketplace strict validation — 2026-08-16

## Identity and authoritative state

This file is the durable workpad and dated evidence record for B078. The
authoritative repository is `GhostlyGawd/engineering-board`. Work starts from
merged main `7516eaecdabf85c3339b5705442ef654770d29d1` on branch
`codex/b078-claude-manifest-policy`.

Engineering Board must install and validate truthfully on every supported
host. A green cross-host test is not useful if it makes two different manifest
schemas appear identical. The outcome is an accurate host boundary, not a
higher validation count.

## Decision ledger

- Active outcome: Claude strict validation passes without an ignored-field
  warning, while Codex retains its supported marketplace policy.
- Approved direction: keep host-owned marketplace fields separate and test
  each host's exact contract.
- Rejected alternatives: remove the Codex policy, suppress or ignore Claude's
  warning, or copy unsupported fields between host manifests.
- Authority boundary: normal branch, PR, merge, release, and reinstall actions
  are authorized. Repository settings, protection bypasses, production
  deployments, and unrelated packaging changes remain out of scope.

## Plan

- [x] Reproduce normal and strict Claude validation on authoritative main.
- [x] Add a deterministic failing test for the host-specific policy boundary.
- [x] Remove the unsupported Claude field without changing Codex policy.
- [x] Run focused validation and the complete maintained suite.
- [x] Reconcile affected documentation and record reviewed-unaffected surfaces.
- [ ] Complete independent review, PR checks, and exact merged-main checks.
- [ ] Publish a patch release and validate the released Claude and Codex
  installations.

## Acceptance criteria

### Worker phase

- [x] `claude plugin validate --strict .` exits 0 and reports no warning.
- [x] Normal Claude validation exits 0.
- [x] The Claude marketplace entry has no `policy` field.
- [x] The Codex marketplace entry retains the exact supported `AVAILABLE` and
  `ON_INSTALL` policy values.
- [x] Automated tests assert the two host contracts independently and fail if
  the unsupported cross-host coupling returns.
- [x] Focused packaging checks and all maintained suites pass on the final diff.

### Post-merge phase

- [ ] Pull-request checks and the exact merged-main check pass.
- [ ] Canonical BOARD, GRAPH, and B078 state agree after all entry edits.

### Closeout phase

- [ ] The new immutable patch-release artifact contains the corrected Claude
  manifest and the preserved Codex policy.
- [ ] Fresh released Claude and Codex plugin installations pass their normal
  host validation without an undocumented workaround.

## Evidence matrix

| Surface | Failure injection or control | Required result | Evidence |
|---|---|---|---|
| Claude marketplace | Include `plugins[0].policy` | Strict validation fails and identifies the unsupported field | Baseline host run plus deterministic fixture assertion |
| Claude marketplace | Remove `plugins[0].policy` | Strict and normal validation pass without a warning | Claude 2.1.200 host run |
| Codex marketplace | Preserve the policy block | Exact installation and authentication values remain present | `tests/codex-plugin.sh` |
| Cross-host boundary | Compare manifests by host contract | Test rejects Claude policy presence and rejects Codex policy drift | Focused packaging test |
| Repository | Run all maintained suites | No product, packaging, graph, or documentation regression | `tests/run-all.sh` |

## Alignment matrix

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Claude marketplace uses only Claude-supported fields | Required | `.claude-plugin/marketplace.json` omits `policy` | Normal and strict Claude 2.1.200 validation; policy-absence assertions | Architecture, release guides, changelog, this workpad | Worker gate passed |
| Codex marketplace retains its host policy | Required | `.agents/plugins/marketplace.json` remains unchanged | Exact policy assertions in Codex, version, and release-preparation tests | Architecture, release guides, this workpad | Worker gate passed |
| Release preparation preserves the host boundary | Required | Version script updates each manifest independently | Release-preparation 16-check suite plus release-instruction guard | Both release guides and changelog | Worker gate passed |
| Runtime product behavior remains unchanged | Required | MCP transport, hooks, tools, context, graph, and outcomes are untouched | Complete maintained suite | Reviewed-unaffected rationale below | Regression gate passed |
| Installed claims identify an immutable corrected artifact | Required for closeout | Patch release from merged main | Release workflow plus fresh Claude and Codex installs | Dated closeout evidence | Pending release |

## Campaign controls

- Start: `2026-08-16T01:00:06Z`.
- Correction cycles used: 1 of 2. Independent review added the host-native
  strict validator to the documented release gate and a deterministic guard
  for that instruction.
- Unexpected live failures: 0 of 1.
- Elapsed-time limit: 120 minutes.
- Renew alignment before another correction cycle, branch, PR, or external
  mutation if one unexpected live failure occurs, two correction cycles occur,
  the time limit expires, authority expands, or terminal evidence conflicts.

## Baseline evidence

- Windows Claude Code 2.1.200 is the available strict validator; repository
  edits and tests remain in the D-backed Linux-native checkout.
- `claude plugin validate .` exits 0 with one warning:
  `plugins[0].policy` is unknown and ignored at load time.
- The otherwise identical strict command exits 1 because strict mode promotes
  that warning to an error.
- At the baseline commit, `.claude-plugin/marketplace.json` and
  `.agents/plugins/marketplace.json` duplicated the policy block.
- At that commit, `tests/codex-plugin.sh` enforced the incorrect cross-host
  equality, so its green result masked the host schema defect.

## Worker validation evidence

- The host-boundary versions of `tests/codex-plugin.sh` and
  `tests/version-coherence.sh` both failed before the manifest edit. The first
  raised its policy-absence assertion; the second reported that the Claude
  marketplace must not contain Codex-only policy.
- Removing only the Claude policy made both tests pass. The strengthened
  release-preparation suite also passes 16 checks and proves that a version
  update preserves the host-specific policy boundary.
- Normal and strict Claude Code 2.1.200 validation now both exit 0 with
  `Validation passed` and no warning.
- The authoritative Linux manifest SHA-256 values were
  `c9bcaff264c033870b425594df728ddaee915abc5c9f43b255d5ce3225835651`
  for `marketplace.json` and
  `c3b8a34ba7dc4126c4d85d04c208ca46c6d798ce0435a72d017a05ab117bdad7`
  for `plugin.json`. An exact disposable Windows-native copy under
  `D:\Codex\Scratch` matched both hashes. Normal and strict validation passed
  there with no warning.
- The fingerprinted cleanup removed the disposable copy's 637 files and 104
  directories, totaling 6,355,853 logical bytes. Measured free space increased
  by 7,426,048 bytes, no target failed, and the empty task root was removed.
- Final independent audit matched both recorded hashes to current source,
  matched the graph fingerprint to canonical entries, verified the required
  alignment and handoff sections, and found no remaining worker blocker.
- `.agents/plugins/marketplace.json`, `.mcp.json`, `codex-mcp.json`, and both
  plugin manifests retain their previous behavior. The Codex policy remains
  exact and the Claude transport remains host-neutral.
- A new release-instruction guard first failed because neither release guide
  required strict Claude validation. Both release paths now require
  `claude plugin validate --strict .` on a host with Claude Code, while keeping
  that host dependency out of portable CI. The guard and live validator pass.
- The final worker diff passed all 21 maintained suites in 61.6 seconds. This
  supersedes the earlier complete-suite run from before the release-gate
  correction.

## Implementation progress

- B078 is claimed and `in_progress`.
- The unsupported Claude policy block is removed. The Codex policy and both
  MCP transport files are unchanged.
- Three deterministic test surfaces now assert the host contracts separately.
- Architecture, release operations, changelog, canonical board state, and
  dated evidence are aligned. Release and installed-host proof remain open.

## Documentation impact

- Changed: Claude marketplace manifest; Codex, version, and release-preparation
  host-boundary tests; Architecture inventory and test matrix; both release
  guides; Unreleased release note; canonical B078 state; BOARD and GRAPH; and
  this dated workpad.
- Reviewed and unaffected: README/setup and install commands because no user
  step changed; Security/privacy because Claude previously ignored the field
  and the effective Codex policy is unchanged; MCP reference, LLM guidance,
  product specification, and examples because no tool, context, graph, or
  outcome behavior changed; site and visuals because no interface or count
  changed; version surfaces because release preparation remains their owner.
- Historical evidence remains immutable. This file appends current results.

## Uncertainties and assumptions

- Codex CLI 0.145.0 has no plugin-validation command. Its source contract is
  covered structurally now; its truthful installed-artifact proof must use the
  next immutable release because the active catalog still pins v1.13.3.
- Claude Code is available on the Windows host, not inside WSL. Strict release
  validation therefore uses an exact hash-bound disposable Windows-native copy
  under `D:\Codex\Scratch`; repository edits and portable tests remain in WSL.
  The validator remains a documented release-host prerequisite.
- The ignored Claude field had no runtime effect. The patch release is still
  required because an unreleased checkout must not be substituted for an
  installed release claim.

## Blockers

No human action is required. Worker review, PR delivery, patch release, and
fresh installed-host validation remain normal authorized gates.

## Handoff and resume route

Completion state: `post-merge-pending`.

Next owner: the primary dogfood loop.

Remaining gates: final independent review, worker PR checks, exact merged-main
checks, patch release, and fresh Claude and Codex installed-host validation.

Resume route: finish the independent worker audit, deliver the worker PR, then
prepare and publish the next patch release from exact merged main before any
installed claim.

Terminal action: `keep-open`.

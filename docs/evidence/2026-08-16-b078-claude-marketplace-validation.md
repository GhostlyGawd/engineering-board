# B078 Claude marketplace strict validation — 2026-08-16

## Identity and authoritative state

This file is the durable workpad and dated evidence record for B078. The
authoritative repository is `GhostlyGawd/engineering-board`. Work started from
merged main `7516eaecdabf85c3339b5705442ef654770d29d1`. The released closeout
commit is `e151d3b7a3db019cac5188b12466727b43f90ef2`; the current evidence branch
is `codex/v1.13.4-release-evidence` from that commit.

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
- [x] Complete independent review, PR checks, and exact merged-main checks.
- [x] Publish a patch release and validate the released Claude and Codex
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

- [x] Pull-request checks and the exact merged-main check pass.
- [x] Canonical BOARD, GRAPH, and B078 state agree after all entry edits.

### Closeout phase

- [x] The new immutable patch-release artifact contains the corrected Claude
  manifest and the preserved Codex policy.
- [x] Fresh released Claude and Codex plugin installations pass their normal
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
| Installed claims identify an immutable corrected artifact | Required for closeout | Patch release from merged main | Release workflow plus fresh Claude and Codex installs | Dated closeout evidence | Passed on v1.13.4 |

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

## Release and installed validation evidence

- Worker PR #156 merged as `a9f21ce67b3a`; exact main run `31919205651`
  passed. Release PR #157 merged as `e151d3b7a3db`; exact main run
  `31919614516` passed.
- Release workflow `31919668638` published v1.13.4 from exact merged main.
  The tag dereferences to `e151d3b7a3db`, and the 66,718-byte GitHub asset
  matches pinned SHA-256
  `7101ce40cee2b5023ef162d9d0cbd637edfdd2c94abd51ff2dd7cbe2509d1705`.
- MCP Registry reports v1.13.4 active and latest with the same asset and
  checksum. PyPI reports v1.13.4 latest with one unyanked wheel and one
  unyanked source distribution.
- The released Codex plugin is the exact tag commit, registers one MCP server
  from its 1.13.4 cache, passes the packaged 19-tool check, and completes a
  fresh read-only `board_status` call.
- The released Claude plugin lists as enabled at 1.13.4. Normal and strict
  installed-path validation pass without warnings. Both host caches match the
  three prepared manifest hashes recorded in
  `2026-08-16-v1.13.4-release-and-installed-validation.md`.

## Implementation progress

- B078 is claimed and `in_progress`.
- The unsupported Claude policy block is removed. The Codex policy and both
  MCP transport files are unchanged.
- Three deterministic test surfaces now assert the host contracts separately.
- Architecture, release operations, changelog, canonical board state, and
  dated evidence are aligned. Release and installed-host proof passed; B078
  remains open only for this evidence merge and final canonical revalidation.

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

- Codex CLI 0.145.0 has no plugin-validation command. Installed proof therefore
  uses exact tag commit and manifest hashes, marketplace identity, MCP
  registration, the packaged validation test, and a fresh read-only tool call.
- Claude Code is available on the Windows host, not inside WSL. Strict release
  validation therefore uses an exact hash-bound disposable Windows-native copy
  under `D:\Codex\Scratch`; repository edits and portable tests remain in WSL.
  The validator remains a documented release-host prerequisite.
- The ignored Claude field had no runtime effect. v1.13.4 nevertheless proves
  the fix through immutable installed artifacts instead of an unreleased
  checkout.

## Blockers

No human action is required. The remaining normal gates are the release-evidence
pull request, its exact merged-main check, and final canonical revalidation.

## Handoff and resume route

Completion state: `post-merge-pending`.

Next owner: the primary dogfood loop.

Remaining gates: merge the release-evidence pull request, pass its exact
merged-main check, and revalidate canonical B078 before resolution.

Resume route: deliver this evidence branch, revalidate canonical B078 from
merged main, then resolve and archive it through the normal lifecycle.

Terminal action: `keep-open`.

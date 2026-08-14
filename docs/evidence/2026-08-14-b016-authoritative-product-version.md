# B016 authoritative product-version evidence

- Date: 2026-08-14
- Repository: `GhostlyGawd/engineering-board`
- Base commit: `89976e2252ac72ba9072a39ece23dfbdb9505e72`
- Board entry: `B016`
- Completion state: `post-merge-pending`
- Implementation pull request: pending
- Evidence destination: this file
- External gates: implementation pull request merge, passing implementation
  merged-main continuous integration, closeout pull request merge, and passing
  closeout merged-main continuous integration
- Terminal action: `keep-open` until implementation merged-main evidence passes;
  then resolve B016 in a closeout change and verify the closeout merged-main run

## Decision

Use the `version` field in `.claude-plugin/plugin.json` as the authoritative
product-version signal. Keep the Codex manifest, marketplace record, MCP
metadata, PyPI metadata, and README badge as coordinated release mirrors.
The existing release-preparation script updates these mirrors together.

Remove the unused `version` field from
`references/required-permissions.json`. Its consumers read only the allowlist
patterns, so synchronizing that field would create another release mirror
without a product need.

Keep independent contract versions unchanged. MCP protocol dates, worker
`schema_version` values, curation schemas, graph schemas, context contracts,
and compatibility-history dates are not product releases. Agent and skill
prose now labels schemas by their contract instead of presenting old 0.x
values as current Engineering Board versions.

This change does not change product version 1.12.0, prepare or publish a
release, modify a bundle checksum, change an allowlist pattern, or change a
runtime protocol or data schema.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| `.claude-plugin/plugin.json` is the authoritative product-version signal and shipped mirrors agree. | Required by B016 and release policy. | The runtime already reads the Claude manifest; the release-preparation script already updates all mirrors together. | `version-coherence` now reads the Claude and Codex manifests, marketplace, MCP manifest, MCP server and package, PyPI metadata, release URL, and README badge. | `docs/RELEASING.md` defines authority and lists the mirrors; `ARCHITECTURE.md` and `mcp-server/README.md` point their surfaces back to that authority. | Worker and full-suite evidence pass; post-merge evidence is pending. |
| The permissions allowlist has no purposeless product-version mirror. | Selected B016 completion alternative. | The unused top-level `version` field is removed; all 26 allowlist patterns are unchanged. | The version guard rejects a permissions product-version field; permission tests drive the real manifest and its consumers. | Release guidance identifies the file as unversioned allowlist data. | Worker and full-suite evidence pass; post-merge evidence is pending. |
| Independent protocol, schema, data-format, and compatibility versions remain distinct. | Compatibility and evidence-preservation boundary. | JSON `schema_version` fields and executable schema constants are unchanged; production agent and skill prose removes legacy product labels or names the applicable schema. | The version guard rejects `engineering-board v0.x` product labels in production agents and skills; all mode contracts pass. | Release guidance states the distinction; historical plans and dated evidence remain unchanged. | Worker and full-suite evidence pass; post-merge evidence is pending. |
| Release and security behavior remains unchanged. | Required alignment invariant. | Product version, bundle checksum, release workflow, publication state, and permission patterns do not change. | Release-preparation 11/11 and permissions 29/29 pass; the maintained suite covers packaging, security, and runtime behavior. | CHANGELOG records the Unreleased clarification. Release, setup, security, privacy, and visual guidance otherwise remain current. | Worker and full-suite evidence pass; post-merge evidence is pending. |

## Drift classification

- Configuration drift, resolved in the worker:
  `references/required-permissions.json` carried product version 1.5.0 while
  the current product version is 1.12.0. No current consumer reads that field.
- Normative documentation gap, resolved in the worker: release guidance listed
  coordinated files but did not identify the authoritative current-version
  signal or distinguish it from independent schema values.
- Product-label drift, resolved in the worker: production agent and skill prose
  used `engineering-board v0.x` labels for historical worker generations.
  Retained 0.x JSON values are now explicitly labeled schemas where applicable.
- Reviewed and unaffected: `.claude-plugin/plugin.json`,
  `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json`, MCP metadata,
  PyPI metadata, and the README badge already agree at 1.12.0.
- Reviewed and unaffected: `scripts/prepare-release.py` already updates every
  shipped release mirror and rebuilds the MCP bundle in one coordinated action.
- Reviewed and unaffected: historical `.goal/`, `.omc/`, changelog, RFC, and
  dated evidence records retain the version literals that were true for their
  recorded context. They are not current product-version authorities.
- Reviewed and unaffected: MCP protocol, worker output, graph, context,
  hypothesis, and other data-contract versions do not change.
- Reviewed and unaffected: README setup, security, privacy, provenance,
  product visuals, tags, releases, registries, and publication state do not
  change.

## Validation evidence

- Red version phase: the expanded real-fixture guard reported ten gaps: one
  unused permissions stamp, one missing authority statement, seven legacy
  agent product labels, and one legacy skill product label.
- Red mode phase: the PM-agent contract reported one unlabeled curation-schema
  expectation.
- Green version phase: the guard reports product version 1.12.0 across the
  authoritative Claude manifest, Codex, marketplace, MCP, PyPI, and README
  surfaces.
- Green mode phase: all six mode groups pass; the PM-agent contract reports
  72 passing checks.
- Green permissions phase: all 29 checks pass against the real permissions
  manifest and its invoked-script surface.
- Green release phase: all 11 release-preparation checks pass, including
  preview, apply, refresh, version alignment, and reproducible bundle checksum.
- Maintained repository suite: 21 of 21 suites pass.
- Implementation pull request and merged-main run: pending.
- Closeout pull request and merged-main run: pending.

The deterministic guard prevents silent version drift in the reviewed files.
It does not prove that historical prose never contains an old version or that
every future data contract is classified correctly. Semantic review remains
responsible for that boundary.

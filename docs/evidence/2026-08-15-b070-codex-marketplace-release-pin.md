# B070 Codex marketplace release-pin alignment — 2026-08-15

## Scope

This record covers the bounded correction for fresh Codex marketplace
installs that advertised version 1.13.0 while materializing mutable `main`.
It records repository alignment only. A fresh install from the next published
tag is required before B070 can resolve.

## Alignment

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Codex marketplace identity | MUST | `.agents/plugins/marketplace.json` has top-level `engineering-board`, display name `Engineering Board`, and exactly one plugin entry. | `tests/codex-plugin.sh`; `tests/version-coherence.sh` | `ARCHITECTURE.md` inventory | Passed on 2026-08-15 |
| Immutable Codex source | MUST | The Codex entry uses the repository root URL and `ref: v1.13.0`; its entry version is 1.13.0. | Exact source-object and authoritative-version checks in `tests/codex-plugin.sh` and `tests/version-coherence.sh` | `README.md`; `docs/RELEASING.md` | Implemented; live reinstall pending |
| Coordinated release advancement | MUST | `scripts/prepare-release.py` validates current marketplace state, refuses drift, and plans both Codex `version` and `ref` as the target release. | `tests/release-preparation.sh` checks preview inclusion, no preview writes, apply advancement, and drift refusal. | `docs/RELEASING.md` | Passed: 14 checks on 2026-08-15 |
| Claude legacy source | MUST NOT change | `.claude-plugin/marketplace.json` remains `source: "./"`; the release planner now refuses source drift. | All three packaging tests assert the relative source. | Claude install commands and behavior in `README.md` remain unchanged. | Preserved; focused tests passed |
| Release truth | MUST | `CHANGELOG.md` records the correction under Unreleased; the future Codex ref must not be advertised as installable before publication creates its tag. | Release-preparation and version-coherence tests cover repository state; publication remains a later maintainer action. | `CHANGELOG.md`; `docs/RELEASING.md` | Repository change implemented; publication pending |
| Security and privacy | MUST preserve | The change narrows downloaded Codex source to an immutable public Git tag. It adds no credential, permission, telemetry, network call, user-data path, or executable runtime behavior. | Packaging tests parse static JSON and use the existing isolated launcher smoke test. | Existing `SECURITY.md` remains accurate because trust, permissions, and data flow do not change. | Reviewed; unaffected |
| MCP semantics | MUST preserve | No MCP schema, tool, launcher, protocol, root handling, canonical Markdown, graph, context, or lifecycle implementation changes. | Existing `tests/codex-plugin.sh` still performs the launcher handshake and 19-tool assertion. | MCP sections of `README.md`, `mcp-server/README.md`, and protocol documentation remain accurate. | Reviewed; unaffected |
| Visual behavior | N/A | No UI asset, HTML, CSS, screenshot, board view, or generated visualization changes. | `tests/docs-coherence.sh` is the only relevant focused documentation guard; visual suites are outside this metadata-only fix. | Visual documentation requires no update. | Reviewed; unaffected |
| Product site | N/A | Install commands remain the same and no site source changes are required; the new pin changes only the source resolved after Codex reads the catalog. | No product-site runtime behavior is exercised by the focused packaging tests. | Existing product-site install examples remain syntactically correct. | Reviewed; unaffected |
| Unrelated documentation | SHOULD remain stable | Architecture inventory, release policy, README install explanation, changelog, this evidence file, and B070 are the only documentation surfaces that need the new contract. | `tests/docs-coherence.sh` guards documented command, skill, and tool counts. | Historical evidence is preserved without revision. | Reviewed; unaffected |
| Post-release fresh reinstall | MUST before resolution | No release, tag, or reinstall is performed in this change. B070 remains open until a fresh Codex cache receipt records the next release tag target. | Compare the future `.codex-marketplace-install.json` revision with `git rev-parse v<version>^{commit}` after publication. | Append or supersede with dated release evidence after the observation. | Pending; blocks B070 resolution |

## Validation

The four focused suites passed: `tests/version-coherence.sh`,
`tests/codex-plugin.sh`, `tests/release-preparation.sh`, and
`tests/docs-coherence.sh`.

The complete `bash tests/run-all.sh` run passed 21 of 21 suites.

The installed v1.13.0 MCP claim sequence completed as follows: the primary
client acquired the claim, a second fresh client received a contended result,
the primary client released the claim, and the second fresh client then
acquired and released it.

A full `board_graph` rebuild produced source fingerprint
`0c3a66637cb390221ffe6b46aad4744c9bbadfee77089cbc01361d92879c7c43` and
indexed B070 with `affects: .agents/plugins/marketplace.json`.

Fresh post-release reinstall proof remains pending and continues to block B070
resolution.

## Conclusion

The repository-side contract is bounded and compatible. The only unresolved
proof is intentionally external to this change: publication must create the
future immutable tag, and a fresh Codex reinstall must record that tag target.

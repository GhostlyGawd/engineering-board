# Codex plugin implementation workpad

Date: 2026-08-14

## Outcome

Package Engineering Board as an installable Codex plugin. The plugin must expose
the existing board skills and the 19-tool MCP server. The installation must not
require a model-provider account or install an unrelated MCP server.

## Acceptance criteria

- The repository contains a valid `.codex-plugin/plugin.json` manifest.
- The Codex plugin contains the five Engineering Board skills.
- The Codex plugin starts only the Engineering Board MCP server.
- The bundled MCP server starts on Windows and Linux when a supported Python
  interpreter is available.
- All 19 MCP tools work without the Claude plugin shell scripts.
- `board_context` accepts `cwd: "."` as the repository root.
- Version preparation keeps the Claude manifest, Codex manifest, marketplace,
  Python package, MCP manifests, and README badge in one version lockstep.
- Setup, architecture, security, product-direction, and release documents agree
  with the implementation.
- A local Codex installation and a fresh MCP handshake verify the packaged
  plugin.

## Alignment

| Surface | Required state | Evidence |
| --- | --- | --- |
| Product specification | Codex is a first-class plugin host. Pattern memory remains the product substrate. | `docs/PRODUCT_EVOLUTION_SPEC.md` |
| Plugin manifests | Claude and Codex manifests identify the same product and version. | `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` |
| MCP configuration | Codex starts only Engineering Board through a portable launcher. | `.mcp.json`, `scripts/engineering-board-mcp-launcher.mjs` |
| Runtime behavior | Claim, release, and context retrieval are host-neutral. | MCP unit and orchestration tests |
| Skills | Each workflow tells Codex to use MCP tools and keeps the Claude fallback. | `skills/*/SKILL.md` |
| User guidance | README and MCP setup explain plugin installation, reload, and fallback setup. | `README.md`, `mcp-server/README.md` |
| Operations | One release command updates every versioned manifest. | `scripts/prepare-release.py`, `tests/version-coherence.sh`, `docs/RELEASING.md` |
| Security and limits | Documentation states local process, filesystem, hook, and interpreter boundaries. | `SECURITY.md`, architecture documentation |

## Progress

- [x] Confirm the D-backed Ubuntu runtime and Linux-native worktree.
- [x] Read current Codex plugin documentation and validate a disposable scaffold.
- [x] Record and reproduce the repository-relative `cwd` defect as B066.
- [x] Add the Codex plugin package.
- [x] Remove shell-script dependencies from the MCP claim tools.
- [x] Align the five workflow skills.
- [x] Align release automation and documentation.
- [x] Validate the repository and packaged plugin.
- [x] Install the plugin, dogfood it, and record dated evidence.
- [ ] Commit, push, open a pull request, pass CI, and merge.

## Drift record

- `behavior, resolved`: Claim and release are now self-contained Python tools.
  A new MCP resolution also records one durable archive row.
- `configuration, resolved`: Root `.mcp.json` starts only Engineering Board
  through a portable launcher. The Codex plugin references this validated
  configuration.
- `documentation, resolved`: Setup, MCP, architecture, security, product,
  release, landing, LLM, skill, and changelog text now describes the Codex
  plugin and the host boundaries.
- `test, resolved`: Version and release tests include the Codex manifest. A new
  plugin test verifies the isolated configuration, launcher, and 19 tools.
- `live evidence, resolved`: Codex installed version 1.12.0 from the local
  marketplace and cached five valid skills.

## Reviewed surfaces

The existing screenshots and diagrams remain accurate because this change adds
an installation surface and does not change the board model or user interface.
The release evidence for version 1.12.0 remains historical. This workpad will
append new dated evidence and will not rewrite the release record.

## Validation evidence

- Official Codex plugin validator: passed.
- Skill validator: all five skills passed.
- Focused Milestone B matrix: 16 checks passed.
- Focused Milestone D matrix: 15 checks passed.
- MCP lifecycle: 171 checks passed after the archive regression was added.
- Complete repository suite: 20 suites passed and 0 failed.
- Installed-plugin handshake: protocol `2025-06-18`, server version `1.12.0`,
  and 19 tools.
- Installed Windows lifecycle: initialized a disposable board, created B001,
  acquired its claim, changed its state, appended one archive row, released the
  claim, and read final status.
- Self-dogfood entries B065, B066, and F004 were recorded and resolved through
  MCP. Their claim releases succeeded.

The local installation needs a new Codex session before this active session can
discover the newly installed skills and MCP tool namespace.

# Changelog

All notable changes to **engineering-board** are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Plugin and marketplace manifests are versioned in lockstep (enforced by
`tests/version-coherence.sh`); a fix only reaches installs when the version
increases.

## [Unreleased]

Product improvement loop (dogfooded on the `engineering-board/eb-self/` board).

### Security
- **Injection reject-filter hardened and made single-source** (eb-self B002).
  The deterministic defense-in-depth filter re-applied at consolidation was
  trivially bypassable: it only matched imperative verbs anchored at the string
  start, an 8-verb list, and scanned only `title`/`evidence_quote`. Crafted
  findings with a non-leading imperative ("as noted, ignore prior findings"), an
  un-listed verb (`delete`/`remove`/`close`/`drop`), or a payload in `tags`/
  `affects` promoted straight to the live board. New canonical module
  `hooks/scripts/board_reject_check.py` (imported by `board-consolidate.sh`, the
  single source of truth) matches injection verbs in imperative mood at any
  clause boundary, broadens the verb set, scans all string fields, and is
  case-insensitive on slash/subagent directives. Threat model documented:
  entries are read, never eval'd, so descriptive shell/HTML metacharacters are
  intentionally not rejected (they recur in legitimate technical findings).

### Added
- **`tests/security/reject-filter.sh`** (eb-self B003) — drives every
  adversarial-paste (36) and benign-findings (24) fixture through the canonical
  filter and asserts each fixture's declared `expect:`/`expect_reason:`.
  Registered in `tests/run-all.sh` (now **12 suites**) and CI-enforced. The
  50-fixture corpus previously had **no** consumer, so the "100% reject-rate"
  guarantee `ARCHITECTURE.md` advertised was never measured. New fixtures pin
  the bypass vectors above.

### Fixed
- `ARCHITECTURE.md` §10 now describes the real reject-filter suite instead of
  the never-measured guarantee; `finding-extractor.md` / `consolidator.md`
  reject-rule prose aligned with the shipped filter.

## [1.2.0] — 2026-07-04

### Added
- **MCP server (dual distribution).** A zero-dependency `python3` MCP server
  (`mcp-server/engineering_board_mcp.py`) exposes the board substrate as **11
  tools** over stdio (JSON-RPC 2.0, protocol `2025-06-18`): `board_init`,
  `board_list_projects`, `board_create_entry`, `board_list_entries`,
  `board_get_entry`, `board_update_entry`, `board_rebuild`,
  `board_capture_finding`, `board_claim`, `board_release`, `board_status`.
  The same committed `engineering-board/` board is now drivable from any
  MCP-capable client, not just Claude Code.
- **`.mcp.json`** at the plugin root bundles the server, so installing the
  Claude Code plugin also registers the MCP server (`${CLAUDE_PLUGIN_ROOT}`).
- **`mcp-server/README.md`** with `claude mcp add` and Claude Desktop config
  snippets.
- **CI-gated MCP tests** (`mcp-server/test_mcp_server.py`, 65 checks) wired into
  `tests/run-all.sh` (now 11 suites): a real subprocess stdio session plus a
  full board lifecycle validated against `hooks/scripts/board-validate-entry.sh`.
- Plugin manifest polish: `homepage`, `repository`, `license`, and `keywords`.

### Fixed
- **Runtime doc accuracy:** `hooks/stop-hook-procedure.md` step (d) no longer
  tells the orchestrator the `learnings-curator` returns a v0.2.2 placeholder —
  it is fully implemented and delegates to `board-curate-learnings.sh`.
- **Documentation drift:** `ARCHITECTURE.md` command count corrected (9 → 10,
  adds `/board-migrate`); stale shipped-state header, "no CI runner" note, and
  learnings-curator descriptions refreshed. README + `test.yml` suite counts
  corrected.
- **Test determinism:** the `stop-hook-mode-routing` suite used an
  `echo "$VAR" | grep -q` idiom that, under `set -euo pipefail`, could take
  SIGPIPE and spuriously fail on CI. Switched to herestrings; also fixed an
  unescaped-backtick needle that ran `tdd-builder` as command substitution.

## [1.1.0] — 2026-06-06

### Changed
- Relocated board content to a visible, committed top-level
  `engineering-board/` directory (the new default). Pre-1.1.0 `docs/boards/`
  and legacy `docs/board/` layouts still resolve. Added `/board-migrate
  --relocate` and centralized location resolution in `board-paths.sh`.

## [1.0.1] — 2026

### Fixed
- Scratch-append fidelity (issue #3): `board-scratch-append.sh` owns the
  timestamp + canonical write so the orchestrating LLM is out of the scratch
  byte-copy path. Malformed copies now fail loudly.

## [1.0.0] — 2026

### Added
- Stable release; design surface declared frozen. Closed a claim-acquire
  construction-window race (`board-claim-acquire.sh` polls up to 250ms for
  `owner.txt`/`heartbeat.txt` after a losing `mkdir`).

## [0.3.2]

### Added
- Test-debt closeout: subagent Output-contract fixtures (7 agents), pause/resume
  registry round-trip invariants, and the GitHub Actions CI gate enforcing
  `tests/run-all.sh` on every push.

## [0.3.1]

### Added
- `board-mode-guard.sh`: deterministic enforcement of the §11.5 mode-transition
  refusal matrix; pause/resume round-trips the `(mode, discipline)` tuple.

## [0.3.0]

### Added
- Learning entity (`L###`), `learnings-curator` agent, `/board-migrate` (SHA256
  apply/rollback), and the SessionStart top-learnings surface.

## [0.2.3]

### Added
- Resilience layer: active-workers registry, PM-fallback heartbeat, `paused:`
  field.

[1.2.0]: https://github.com/GhostlyGawd/engineering-board/releases/tag/v1.2.0-rc.1
[1.1.0]: https://github.com/GhostlyGawd/engineering-board/pull/8

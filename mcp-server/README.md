# engineering-board MCP server

A zero-dependency [Model Context Protocol](https://modelcontextprotocol.io) server
that exposes the `engineering-board` plugin's markdown board as MCP tools. It lets
any MCP client (Claude Code, Claude Desktop, …) scaffold boards, create/list/update
entries, rebuild the index, capture scratch findings, and claim/release entry locks —
all against the exact on-disk format the plugin's hooks and skills expect.

## Design constraints

- **Pure `python3`, zero third-party dependencies.** No `mcp` pip SDK, no `pydantic`.
  The MCP stdio/JSON-RPC protocol is implemented directly, so the server runs under
  the same `bash` + `python3` + coreutils toolchain as the rest of the plugin (CI has
  no install step).
- **Transport:** stdio, JSON-RPC 2.0, newline-delimited messages, protocolVersion
  `2025-06-18`. Only JSON-RPC messages go to stdout; diagnostics go to stderr.
- Locking is **not reimplemented** — `board_claim` / `board_release` shell out to the
  plugin's existing `hooks/scripts/board-claim-acquire.sh` / `board-claim-release.sh`.
- Timestamps are real UTC ISO-8601 (second precision) via `datetime.now(timezone.utc)`.

The board location for a `project` is resolved via `engineering-board/BOARD-ROUTER.md`
(then the pre-1.1.0 `docs/boards/BOARD-ROUTER.md` compat path), falling back to
`engineering-board/<project>/`. The repo root defaults to `$CLAUDE_PROJECT_DIR`, then
the current working directory, and can be overridden per-call with a `root` argument.

## Tools

| Tool | What it does |
|------|--------------|
| `board_init` | Scaffold a project board (router row, `BOARD.md`, `ARCHIVE.md`, 5 subdirs + `.gitkeep`). Idempotent — never clobbers. |
| `board_list_projects` | List projects from `BOARD-ROUTER.md` (id, path, affects prefix). |
| `board_create_entry` | Create a valid entry (bug/feature/question/observation/learning) with correct frontmatter + required body sections, allocate the next zero-padded id, rebuild the index. Output passes `board-validate-entry.sh`. |
| `board_list_entries` | List entries with parsed frontmatter; filters: `project`, `type`, `status`, `needs`. |
| `board_get_entry` | Full markdown of one entry by id (+ parsed frontmatter). |
| `board_update_entry` | Update frontmatter (`status`, `needs`, `priority`, `blocked_by`) and/or append a body section; validate the status transition; rebuild the index. |
| `board_rebuild` | Deterministically regenerate `BOARD.md` from entry files (P0→P3 ordering, `⊘ Q###` when blocked, resolved omitted). Idempotent. |
| `board_capture_finding` | Append a finding to the scratch inbox `_sessions/mcp-<UTC-date>.md`. |
| `board_claim` | Acquire an entry lock (shells out to `board-claim-acquire.sh`; 0=acquired, 1=contended, 2=stale). |
| `board_release` | Release an entry lock (shells out to `board-claim-release.sh`; 0=released, 3=owner mismatch/missing, 4=retries exhausted). |
| `board_status` | Overview: per-type open counts, `in_progress` ids, `blocked` ids, un-promoted scratch count. |

All 11 tools from the spec are implemented; none were dropped.

## Configuration

### Claude Code (CLI)

```sh
claude mcp add engineering-board -- python3 /abs/path/to/engineering-board/mcp-server/engineering_board_mcp.py
```

Replace `/abs/path/to/engineering-board` with the absolute path to this repo.

### Claude Desktop

Add to `claude_desktop_config.json` (macOS:
`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "engineering-board": {
      "command": "python3",
      "args": ["/abs/path/to/engineering-board/mcp-server/engineering_board_mcp.py"]
    }
  }
}
```

### Bundled with the plugin (automatic)

Installing the `engineering-board` plugin auto-registers this server via the
repo-root [`.mcp.json`](../.mcp.json), which resolves the script through
`${CLAUDE_PLUGIN_ROOT}`:

```json
{
  "mcpServers": {
    "engineering-board": {
      "command": "python3",
      "args": ["${CLAUDE_PLUGIN_ROOT}/mcp-server/engineering_board_mcp.py"]
    }
  }
}
```

No separate install step is needed when the plugin is installed.

## Distribution channels

The server ships from this repo tree (it shells out to sibling
`hooks/scripts/board-claim-*.sh` for locking, so it is not a standalone single
file). Beyond cloning the repo, two packaged channels are prepared:

- **MCP bundle (`.mcpb`)** — `bash mcp-server/build-mcpb.sh` produces
  `dist/engineering-board-mcp.mcpb`, a self-contained bundle (server + the hook
  scripts it calls + [`manifest.json`](manifest.json)) for one-click install in
  MCP-bundle-aware clients. The bundle is a release asset, not committed source.
- **MCP Registry** — [`server.json`](server.json) is the registry manifest
  (namespace `io.github.ghostlygawd/engineering-board`), pointing at the `.mcpb`
  release asset. Publishing is a human step (`mcp-publisher`), tracked in
  [`.goal/LAUNCH.md`](../.goal/LAUNCH.md) §4; once published it auto-syndicates to
  PulseMCP / Glama / mcp.so.
- **Smithery** — [`smithery.yaml`](smithery.yaml) describes the stdio launch for
  `smithery mcp publish`.

`server.json`, `manifest.json`, and `smithery.yaml` are version-locked to
`plugin.json` and validated by the MCP test suite so they cannot silently drift.

## Tests

```sh
bash mcp-server/run-tests.sh
```

`test_mcp_server.py` (pure python3, no deps) runs two suites:

1. A **real end-to-end stdio session** — spawns the server as a subprocess and drives
   `initialize` → `notifications/initialized` → `tools/list` → several `tools/call`,
   asserting on the JSON-RPC responses (including `-32601`/`-32602` error paths).
2. A **full board lifecycle** in a temp repo — `board_init` → `board_create_entry`
   (bug + question + feature + learning) → `board_list_entries` → `board_update_entry`
   → `board_rebuild` → `board_status` → `board_capture_finding` → `board_claim` /
   `board_release`, asserting every created file passes the real
   `hooks/scripts/board-validate-entry.sh`.

Exit 0 on all-pass; non-zero with detail on the first failure.

## Notes

- The server never writes to stdout except JSON-RPC responses (a hard MCP requirement).
- Entry filenames are `<ID>-<kebab-slug>.md` (e.g. `B001-export-drops-final-row.md`).
- `board_create_entry` and `board_update_entry` rebuild `BOARD.md` as their final step
  so a freshly written entry's id is always present in the index (which
  `board-validate-entry.sh` checks).

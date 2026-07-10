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
| `board_init` | Scaffold a project board (router row, `BOARD.md`, `ARCHIVE.md`, 5 subdirs + `.gitkeep`). Idempotent — never clobbers. Optional `agents_md` (default true) writes a marker-fenced usage block into the repo's `AGENTS.md` for hook-less agents. |
| `board_list_projects` | List projects from `BOARD-ROUTER.md` (id, path, affects prefix). |
| `board_create_entry` | Create a valid entry (bug/feature/question/observation/learning) with correct frontmatter + required body sections, allocate the next zero-padded id, rebuild the index. Output passes `board-validate-entry.sh`. Optional `parent` links a subtask to an existing entry. |
| `board_list_entries` | List entries with parsed frontmatter; filters: `project`, `type`, `status`, `needs`, `ready`. `ready: true` is the deterministic ready queue — open entries whose existing `blocked_by` targets are all resolved (dangling ids warn, never block). |
| `board_get_entry` | Full markdown of one entry by id (+ parsed frontmatter). |
| `board_update_entry` | Update frontmatter (`status`, `needs`, `priority`, `blocked_by`, `parent`) and/or append a body section; validate the status transition; rebuild the index. Optional `comment: {author, text}` appends a server-timestamped line to the entry's `## Comments` section. |
| `board_rebuild` | Deterministically regenerate `BOARD.md` from entry files (P0→P3 ordering, `⊘ Q###` when blocked, `↳` child rows under parents, resolved omitted). Idempotent. |
| `board_capture_finding` | Append a finding to the scratch inbox `_sessions/mcp-<UTC-date>.md`. |
| `board_claim` | Acquire an entry lock (shells out to `board-claim-acquire.sh`; 0=acquired, 1=contended, 2=stale). |
| `board_release` | Release an entry lock (shells out to `board-claim-release.sh`; 0=released, 3=owner mismatch/missing, 4=retries exhausted). |
| `board_remember` | Save a durable insight straight to `learnings/L###-<slug>.md` (`source: remember`) and rebuild the index — explicit intent bypasses the curator's recurrence-≥3 threshold. |
| `board_status` | Overview: per-type open counts, `in_progress` ids, `blocked` ids, the ready queue (capped at 20) with dangling-blocker warnings, un-promoted scratch count. |

All 12 tools from the spec are implemented; none were dropped.

## Configuration

The server is published to PyPI as
[`engineering-board-mcp`](https://pypi.org/project/engineering-board-mcp/)
(published from v1.7.0), so the primary install is one `uvx` line — no clone,
no absolute path. The clone path still works everywhere and is the fallback.

> **Note (PyPI installs):** `board_claim` / `board_release` shell out to the
> plugin's `hooks/scripts/board-claim-*.sh`, which the PyPI package does not
> ship; on a PyPI install those two tools return a clean error unless the
> plugin (or a repo clone) is present. All other tools are self-contained.

### Claude Code (CLI)

```sh
# primary — uvx (published from v1.7.0)
claude mcp add engineering-board -- uvx engineering-board-mcp
```

Fallback — run from a clone:

```sh
git clone https://github.com/GhostlyGawd/engineering-board
claude mcp add engineering-board -- python3 "$(pwd)/engineering-board/mcp-server/engineering_board_mcp.py"
```

### Codex CLI

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.engineering-board]
command = "uvx"
args = ["engineering-board-mcp"]
```

Or one line: `codex mcp add engineering-board -- uvx engineering-board-mcp`.

### Gemini CLI

Add to `~/.gemini/settings.json` (or per-project `.gemini/settings.json`):

```json
{
  "mcpServers": {
    "engineering-board": {
      "command": "uvx",
      "args": ["engineering-board-mcp"]
    }
  }
}
```

Or one line: `gemini mcp add engineering-board uvx engineering-board-mcp`.

### Cursor

Add to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` in the project:

```json
{
  "mcpServers": {
    "engineering-board": {
      "command": "uvx",
      "args": ["engineering-board-mcp"]
    }
  }
}
```

### Claude Desktop

Add to `claude_desktop_config.json` (macOS:
`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "engineering-board": {
      "command": "uvx",
      "args": ["engineering-board-mcp"]
    }
  }
}
```

(Clone fallback: `"command": "python3"`, `"args":
["/abs/path/to/engineering-board/mcp-server/engineering_board_mcp.py"]`.)

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
`hooks/scripts/board-claim-*.sh` for locking; every other tool is
self-contained). Beyond cloning the repo, the packaged channels:

- **PyPI (`engineering-board-mcp`)** — the uvx one-liner above. Published from
  v1.7.0 by the release workflow via PyPI trusted publishing (OIDC, no stored
  secret); [`pyproject.toml`](pyproject.toml) is the package manifest.
- **MCP bundle (`.mcpb`)** — `bash mcp-server/build-mcpb.sh` produces
  `dist/engineering-board-mcp.mcpb`, a self-contained bundle (server + the hook
  scripts it calls + [`manifest.json`](manifest.json)) for one-click install in
  MCP-bundle-aware clients. The bundle is a release asset, not committed source.
- **MCP Registry — live** — published as
  [`io.github.GhostlyGawd/engineering-board`](https://registry.modelcontextprotocol.io/?search=engineering-board);
  [`server.json`](server.json) is the registry manifest, pointing at the `.mcpb`
  release asset. Listings auto-syndicate to PulseMCP / Glama / mcp.so.
- **Smithery** — [`smithery.yaml`](smithery.yaml) describes the stdio launch for
  `smithery mcp publish`.

`server.json`, `manifest.json`, and `smithery.yaml` are version-locked to
`plugin.json` and validated by the MCP test suite so they cannot silently drift.

## Multi-client: two clients, one board

Driving the same board from two MCP clients simultaneously (e.g. Claude Code
and Claude Desktop) is supported and CI-proven (eb-self Q001): the test suite
spawns two independent server processes on one board and races them for the
same entry's claim — exactly one acquires (`exit_code 0`), the other sees clean
contention (`exit_code 1`), and after the winner releases, the loser can
acquire. There is no cache layer to go stale: every read hits the same
committed markdown, and locking is the plugin's atomic `mkdir` claim protocol.
Use distinct `session_id`s per client (each client's claims are owned by its
session id).

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

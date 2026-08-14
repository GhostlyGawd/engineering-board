# engineering-board MCP server

A zero-dependency [Model Context Protocol](https://modelcontextprotocol.io) server
that exposes the `engineering-board` plugin's markdown board as MCP tools. It lets
any MCP client (Codex, Claude Code, Claude Desktop, and others) scaffold boards, create/list/update
entries, preview and promote scratch findings, manage stable pattern identities,
rank provenance-linked clusters, preserve durable root-cause hypotheses and
rejected-claim memory, retrieve relevant systemic context, record explicit fix
outcomes, update Learning confidence, and claim/release entry locks: all against the exact
on-disk format the plugin's hooks and skills expect.

## Design constraints

- **Python 3, zero third-party dependencies.** No `mcp` pip SDK, no `pydantic`.
  The MCP stdio/JSON-RPC protocol is implemented directly, so the server runs under
  no package installation step.
- **Transport:** stdio, JSON-RPC 2.0, newline-delimited messages, protocolVersion
  `2025-06-18`. Only JSON-RPC messages go to stdout. diagnostics go to stderr.
- `board_claim` and `board_release` use atomic claim directories in Python.
  They do not require Bash or plugin hook scripts.
- Timestamps are real UTC ISO-8601 (second precision) via `datetime.now(timezone.utc)`.

The board location for a `project` is resolved via `engineering-board/BOARD-ROUTER.md`
(then the pre-1.1.0 `docs/boards/BOARD-ROUTER.md` compat path), falling back to
`engineering-board/<project>/`. The repo root defaults to `$CLAUDE_PROJECT_DIR`, then
the current working directory, and can be overridden per-call with a `root` argument.

## Tools

| Tool | What it does |
|------|--------------|
| `board_init` | Scaffold a project board (router row, `BOARD.md`, `ARCHIVE.md`, five entry subdirs and `hypotheses/`, each with `.gitkeep`). Idempotent: never clobbers. Optional `agents_md` (default true) writes a marker-fenced usage block into the repo's `AGENTS.md` for hook-less agents. |
| `board_list_projects` | List projects from `BOARD-ROUTER.md` (id, path, affects prefix). |
| `board_create_entry` | Create a valid entry (bug/feature/question/observation/learning) with correct frontmatter + required body sections, allocate the next zero-padded id, rebuild the index. Output passes `board-validate-entry.sh`. Optional `parent` links a subtask to an existing entry. |
| `board_list_entries` | List entries with parsed frontmatter. filters: `project`, `type`, `status`, `needs`, `ready`. `ready: true` is the deterministic ready queue: open entries whose existing `blocked_by` targets are all resolved (dangling ids warn, never block). |
| `board_get_entry` | Full markdown of one entry by id (+ parsed frontmatter). |
| `board_update_entry` | Update frontmatter (`status`, `needs`, `priority`, `blocked_by`, `parent`) and/or append a body section. Validate the status transition and rebuild the index. A transition to `resolved` appends one `ARCHIVE.md` row. Optional `comment: {author, text}` appends a server-timestamped line to the entry's `## Comments` section. |
| `board_graph` | Build the deterministic typed graph from canonical entry and P### pattern Markdown, write `GRAPH.yml`, and reuse only a source-equivalent disposable cache. `full: true` bypasses the cache. |
| `board_context` | Retrieve a bounded context brief from task, path, entry, and current-directory signals. Each result exposes a stable title, typed summary, epistemic state, score components, matched signals, staleness, reason, and canonical sources. `report: true` returns the derived value report. |
| `board_insights` | Rank graph clusters with transparent score components and return linked H### and rejected negative-memory references. The score is investigation priority, not causal confidence. |
| `board_hypotheses` | List H### records or preview/apply propose, evaluate, reopen, split, and merge operations. Mutations require an unchanged self-contained plan token and cited evidence. |
| `board_outcomes` | Preview or apply a structured H### fix outcome. It also applies one returned L### Learning plan, curates eligible Learning feedback under PM authority, or returns the derived value report. |
| `board_patterns` | List canonical pattern records or preview/apply create, alias, assign, and correction operations. Every mutation requires the unchanged content-bound plan id. |
| `board_promote_findings` | Preview or apply captured scratch findings with typed created/deduplicated/rejected/already-applied outcomes, durable provenance, idempotent receipts, and identifier allocation across open and resolved entries. An unchanged plan id restores a session-scoped preview when apply omits the optional session selector. |
| `board_rebuild` | Deterministically regenerate `BOARD.md` from entry files (P0 to P3 ordering, `⊘ Q###` when blocked, `↳` child rows under parents, resolved omitted). Idempotent. |
| `board_capture_finding` | Append a finding to the scratch inbox `_sessions/mcp-<UTC-date>.md`. |
| `board_claim` | Acquire an atomic entry claim. Results: 0=acquired, 1=contended, 2=stale. |
| `board_release` | Release an owned entry claim. Results: 0=released, 3=owner mismatch or missing, 4=retries exhausted. |
| `board_remember` | Save a durable insight straight to `learnings/L###-<slug>.md` (`source: remember`) and rebuild the index: explicit intent bypasses the curator's recurrence-≥3 threshold. |
| `board_status` | Overview: per-type open counts, `in_progress` ids, `blocked` ids, the ready queue (capped at 20) with dangling-blocker warnings, un-promoted scratch count. |

All 19 tools use the same canonical Markdown format. Pattern, promotion, graph,
ranking, context, hypothesis, outcome, and Learning behavior delegates to the
same zero-dependency core used by the plugin.

`board_context` is read-only. Its token proves which repository memory the
system surfaced. Context contract version `2` adds a one-line title of at most
160 characters and a typed one-line summary of at most 2,000 characters.
Cluster summaries state structural scope. H### summaries state a proposed root
cause. L### summaries state a Takeaway. The separate status field preserves
epistemic authority. The token binds the context-contract and ranking-rule
versions. It does not authorize a write.

Task text refines structurally eligible memory. It does not create eligibility
by itself unless it names a canonical P### pattern. A task-only miss returns a
warning that asks for a file, entry identifier, or current directory.

`board_outcomes` uses a preview and apply boundary. The preview returns a
content-bound plan and changes no canonical file. Apply revalidates under the
H### lock and changes one hypothesis file atomically. Returned Learning plans
remain separate. A caller must apply each Learning plan explicitly, unless the
existing PM curator has write authority.

## Configuration

The server is published to PyPI as
[`engineering-board-mcp`](https://pypi.org/project/engineering-board-mcp/)
(available with the v1.7.0 release), so the primary install is one `uvx` line: no clone,
no absolute path. The clone path still works everywhere and is the fallback.

All 19 tools are self-contained in the Python package.

### Codex plugin

```sh
codex plugin marketplace add GhostlyGawd/engineering-board
codex plugin add engineering-board@engineering-board
```

Start a new Codex session after installation. The plugin supplies the board
skills and starts this server automatically. Each bundled-plugin tool call must
include the absolute repository `root`. This requirement prevents a raw call
from writing to the plugin cache when the active workspace is not available to
the MCP process.

### Claude Code (CLI)

```sh
# primary — uvx (available with the v1.7.0 release)
claude mcp add engineering-board -- uvx engineering-board-mcp
```

Fallback: run from a clone:

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

### Bundled with the Claude Code plugin (automatic)

Installing the `engineering-board` plugin auto-registers this server through
the repository-root [`.mcp.json`](../.mcp.json):

```json
{
  "mcpServers": {
    "engineering-board": {
      "command": "node",
      "args": ["scripts/engineering-board-mcp-launcher.mjs"],
      "cwd": "."
    }
  }
}
```

The plugins use `scripts/engineering-board-mcp-launcher.mjs`. The launcher selects `python3`,
`python`, or the Windows `py -3` launcher without using a shell. Set `PYTHON`
to an executable path when Python is not on `PATH`.

No separate install step is needed when the plugin is installed.

## Distribution channels

The server ships from this repo tree (it shells out to sibling
`hooks/scripts/board-claim-*.sh` for locking. every other tool is
self-contained). Beyond cloning the repo, the packaged channels:

- **PyPI (`engineering-board-mcp`)**: the uvx one-liner above. Published from
  v1.7.0 by the release workflow via PyPI trusted publishing (OIDC, no stored
  secret). [`pyproject.toml`](pyproject.toml) is the package manifest.
- **MCP bundle (`.mcpb`)**: `bash mcp-server/build-mcpb.sh` produces
  `dist/engineering-board-mcp.mcpb`, a self-contained bundle (server + the hook
  scripts it calls + [`manifest.json`](manifest.json)) for one-click install in
  MCP-bundle-aware clients. The bundle is a release asset, not committed source.
- **MCP Registry: live**: published as
  [`io.github.GhostlyGawd/engineering-board`](https://registry.modelcontextprotocol.io/?search=engineering-board).
  [`server.json`](server.json) is the registry manifest, pointing at the `.mcpb`
  release asset. Listings auto-syndicate to PulseMCP / Glama / mcp.so.
- **Smithery**: [`smithery.yaml`](smithery.yaml) describes the stdio launch for
  `smithery mcp publish`.

`server.json`, `manifest.json`, and `smithery.yaml` are version-locked to
`plugin.json` and validated by the MCP test suite so they cannot silently drift.

## Multi-client: two clients, one board

Driving the same board from two MCP clients simultaneously (e.g. Claude Code
and Claude Desktop) is supported and CI-proven (eb-self Q001): the test suite
spawns two independent server processes on one board and races them for the
same entry's claim: exactly one acquires (`exit_code 0`), the other sees clean
contention (`exit_code 1`), and after the winner releases, the loser can
acquire. Canonical reads hit the same committed Markdown. The graph accelerator
is disposable, source-fingerprinted, and ignored by Git. stale or corrupt cache
state falls back to a full rebuild. Locking is the plugin's atomic `mkdir`
claim protocol.
Use distinct `session_id`s per client (each client's claims are owned by its
session id).

## Tests

```sh
bash mcp-server/run-tests.sh
```

`test_mcp_server.py` (pure python3, no deps) runs two suites:

1. A **real end-to-end stdio session**: spawns the server as a subprocess and drives
   `initialize` to `notifications/initialized` to `tools/list` to several `tools/call`,
   asserting on the JSON-RPC responses (including `-32601`/`-32602` error paths).
2. A **full board lifecycle** in a temp repo: `board_init` to `board_create_entry`
   (bug + question + feature + learning) to `board_list_entries` to `board_update_entry`
   to `board_rebuild` to `board_status` to `board_capture_finding` to `board_claim` /
   `board_release`, asserting every created file passes the real
   `hooks/scripts/board-validate-entry.sh`.

Exit 0 on all-pass. non-zero with detail on the first failure.

## Notes

- The server never writes to stdout except JSON-RPC responses (a hard MCP requirement).
- Entry filenames are `<ID>-<kebab-slug>.md` (e.g. `B001-export-drops-final-row.md`).
- `board_create_entry` and `board_update_entry` rebuild `BOARD.md` as their final step
  so a freshly written entry's id is always present in the index (which
  `board-validate-entry.sh` checks).

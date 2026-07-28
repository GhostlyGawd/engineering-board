> DRAFT — FULL COMPLIANCE CHECK NOT COMPLETE

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="brand/logomark-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="brand/logomark-light.svg">
  <img src="brand/logomark-light.svg" alt="Engineering Board logomark" width="88" height="88">
</picture>

# Engineering Board

**Repository pattern memory that helps an engineering agent find a root cause.**

_The board is the database._

[![Website](https://img.shields.io/badge/website-ghostlygawd.github.io-E6A94E.svg)](https://ghostlygawd.github.io/engineering-board/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.10.0-E6A94E.svg)](CHANGELOG.md)
[![tests](https://img.shields.io/github/actions/workflow/status/GhostlyGawd/engineering-board/test.yml?label=tests)](https://github.com/GhostlyGawd/engineering-board/actions/workflows/test.yml)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-171719.svg)](https://code.claude.com/docs/en/plugin-marketplaces)
[![MCP](https://img.shields.io/badge/MCP-server-171719.svg)](mcp-server/README.md)
[![GitHub stars](https://img.shields.io/github/stars/GhostlyGawd/engineering-board)](https://github.com/GhostlyGawd/engineering-board/stargazers)
[![Last release](https://img.shields.io/github/release-date/GhostlyGawd/engineering-board?label=last%20release&color=E6A94E)](https://github.com/GhostlyGawd/engineering-board/releases)

<img src="docs/assets/pattern-intelligence-demo.png" alt="Three synthetic findings connect to cluster C001 and one proposed root-cause hypothesis." width="720">

_Run `/board-demo` to make this synthetic example._

<img src="docs/assets/milestone-b-pattern-pipeline.svg" alt="The Milestone B validation shows stable pattern P001 and cluster c-a4609c958c398d90." width="720">

_This visual shows real deterministic fixture output for the pattern pipeline._

<img src="docs/assets/milestone-c-root-cause-intelligence.svg" alt="The Milestone C validation shows cluster rank, hypothesis states, and negative memory." width="720">

_This visual shows real deterministic fixture output for root-cause memory._

<img src="docs/assets/board-screenshot.png" alt="The repository board has search, filters, and four Kanban columns." width="720">

_This repository uses its own Engineering Board._

</div>

## Product description

Engineering Board is a repository-owned pattern-intelligence system for
engineering agents.

The system records bugs, features, questions, and observations as Markdown
evidence. It connects recurring findings in a deterministic graph.

The graph helps an agent investigate a shared cause across different domains.
This method reduces repeated corrections of individual symptoms.

Markdown is the canonical record. A pull request can show each change to this
record.

`BOARD.md`, `GRAPH.yml`, JSON analysis, and HTML are derived views. The system
can build these views again from the canonical record.

A hypothesis is separate from a deterministic graph fact. Only investigation
evidence or fix evidence can confirm a hypothesis.

The optional `tdd → review → validate` loop can test a fix. This loop supports
the pattern memory, but it does not define the product.

Milestone C adds:

- A transparent investigation score from 0 through 100
- A durable H### hypothesis lifecycle
- Negative memory for a rejected claim.

Each score component is visible. A score does not prove that a cause is true.

## Product differences

Some Git boards show visible state but have little analysis. Some memory
systems have useful analysis but keep the source outside the repository.

Engineering Board combines these properties:

- Repository evidence that a pull request can review
- A cross-domain pattern graph with evidence links
- H### records with alternatives and falsifiers
- Negative memory for rejected claims
- Atomic claims for parallel agents
- Passive capture
- A Claude Code plugin
- An MCP server.

Native Claude Code Tasks and Engineering Board have different purposes.

Native Tasks store personal task state in `~/.claude/tasks/`. This state is not
part of a project pull request.

Engineering Board stores shared project memory in the repository. Use Native
Tasks for temporary personal work. Use Engineering Board for durable project
knowledge.

## Install the Claude Code plugin

Add the repository marketplace:

```text
/plugin marketplace add GhostlyGawd/engineering-board
```

Install the plugin:

```text
/plugin install engineering-board
```

Set up a board:

```text
/board-setup
```

`/board-setup` creates the board structure. It also checks the required
permissions.

Run the contained demonstration:

```text
/board-demo
```

The command creates a synthetic run in
`.engineering-board/demo/pattern-intelligence/`.

The command connects three findings from different domains. It then requests
one hypothesis that cites the evidence.

The hypothesis has `status: proposed`. It includes an alternative explanation
and a falsifier.

The report gives an exact cleanup command. The cleanup operation preserves a
changed run.

For explicit setup values, use:

```text
/board-init <project> [affects-prefix]
/board-install-permissions
```

## Use the pattern-memory workflow

1. Work in Claude Code.
2. Let the Stop hook capture a finding in `engineering-board/<project>/_sessions/`.
3. Run `/board-promote` to preview canonical changes.
4. Apply the unchanged promotion plan after you review it.
5. Run `/board-insights <project>` to rank systemic investigations.
6. Run `/board-view` to open the pattern-intelligence view.
7. Run `/board-hypothesis <project> propose` to preview an H### record.
8. Review the evidence, alternative, counter-evidence, confidence basis, and falsifier.
9. Apply the unchanged hypothesis plan.
10. Evaluate the hypothesis only with cited evidence.

An evaluation can confirm, weaken, reject, reopen, split, or merge a
hypothesis.

Use `/pm-start` only for advanced batch promotion. Use the optional Worker loop
only when you want to test a selected fix.

## Use one session mode

`/pm-start` and `/worker-start` set
`.engineering-board/session-mode.json`.

A session can have one mode. Start a new session to change the mode.

On Claude Code web, each session uses a new clone. On a local installation, the
mode file stays on disk.

To return to passive capture:

1. Start a new session.
2. Read the `SessionStart` message.
3. If a mode remains, delete `.engineering-board/session-mode.json`.

## Register the MCP server

Register the PyPI package with the Claude Code command-line interface (CLI):

```sh
claude mcp add engineering-board -- uvx engineering-board-mcp
```

To run the server from a clone:

```sh
git clone https://github.com/GhostlyGawd/engineering-board
claude mcp add engineering-board -- python3 "$(pwd)/engineering-board/mcp-server/engineering_board_mcp.py"
```

For Claude Desktop, add this object to `claude_desktop_config.json`:

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

[`mcp-server/README.md`](mcp-server/README.md) also contains setup procedures
for Codex CLI, Gemini CLI, and Cursor.

The plugin registers the same server through [`.mcp.json`](.mcp.json).

## Product surfaces

The plugin has four session modes:

| Mode | Start method | Stop action |
|---|---|---|
| Passive | Default | Run `finding-extractor` |
| Paused | `/board-pause` | Do not capture a finding |
| PM | `/pm-start` | Run the four PM agents |
| Worker | `/worker-start --discipline <tdd\|review\|validate>` | Claim and process one entry |

The canonical Stop procedure is
[`hooks/stop-hook-procedure.md`](hooks/stop-hook-procedure.md).

**Commands (19):** `/board-setup`, `/board-demo`, `/board-promote`,
`/board-pattern`, `/board-insights`, `/board-hypothesis`, `/board-run`,
`/board-init`, `/board-rebuild`, `/board-graph`, `/board-view`,
`/board-remember`, `/board-pause`, `/board-resume`, `/pm-start`,
`/worker-start`, `/board-install-permissions`, `/board-claim-release`, and
`/board-migrate`.

**Agents (8):** `board-manager`, `finding-extractor`, `consolidator`, `tidier`,
`learnings-curator`, `tdd-builder`, `code-reviewer`, and `validator`.

**Skills (5):** `board-intake`, `board-triage`, `board-resolve`,
`board-consolidate`, and `board-insights`.

**Hooks (4 events):** `SessionStart`, `PostToolUse(Write)`,
`UserPromptSubmit`, and `Stop`.

The MCP server has 17 tools. All tools use the same canonical Markdown and the
same deterministic core.

| Tool | Function |
|---|---|
| `board_init` | Create a project board |
| `board_list_projects` | List router projects |
| `board_create_entry` | Create a valid entry |
| `board_list_entries` | List and filter entries |
| `board_get_entry` | Get one entry |
| `board_update_entry` | Change one entry |
| `board_graph` | Build the deterministic graph |
| `board_insights` | Rank clusters and return linked evidence |
| `board_hypotheses` | List, preview, or apply H### operations |
| `board_patterns` | List, preview, or apply P### operations |
| `board_promote_findings` | Preview or apply scratch promotion |
| `board_rebuild` | Build `BOARD.md` again |
| `board_capture_finding` | Add a finding to the scratch inbox |
| `board_claim` | Acquire an entry claim |
| `board_release` | Release an entry claim |
| `board_remember` | Save a learning |
| `board_status` | Show board state and ready work |

## Architecture boundary

Canonical cards, hypotheses, learnings, and `BOARD-ROUTER.md` use Markdown.
Derived views include `BOARD.md`, `GRAPH.yml`, JSON, and HTML.

The product does not require SQLite. A future SQLite index must be disposable
and rebuildable. Measured query requirements must justify it.

The runtime uses Claude Code, `bash`, and `python3`. It has no runtime package
dependency.

Read [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full system map.

## Roadmap boundary

Milestone C shipped in v1.10.0.

The cross-session Conductor remains a draft RFC. `/board-run <entry-id>` ships
only the single-session inner loop.

Cross-repository intelligence, hosted services, and a required database remain
outside the current product boundary.

[`docs/PRODUCT_EVOLUTION_SPEC.md`](docs/PRODUCT_EVOLUTION_SPEC.md) is the
authoritative product-direction source.

## Contribute

Run the complete test suite:

```sh
bash tests/run-all.sh
```

The suite contains 16 test areas. Read
[`CONTRIBUTING.md`](CONTRIBUTING.md) before you change the repository.

## Support

- Use [GitHub Discussions](https://github.com/GhostlyGawd/engineering-board/discussions) for questions.
- Use [GitHub Issues](https://github.com/GhostlyGawd/engineering-board/issues/new/choose) for bugs and features.
- Use [GitHub Security Advisories](https://github.com/GhostlyGawd/engineering-board/security/advisories/new) for a vulnerability.
- Use the [live board](https://ghostlygawd.github.io/engineering-board/board.html) for current project work.
- Use [GitHub Sponsors](https://github.com/sponsors/GhostlyGawd) to support the project.

GhostlyGawd maintains this open-source project.

## License

The project uses the [MIT License](LICENSE).

## Compliance status

`NOT RELEASED — COMPLIANCE CHECK INCOMPLETE`

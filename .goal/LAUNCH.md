# LAUNCH — engineering-board 1.2.0

Launch checklist. Items marked **[human]** need a GitHub account/UI action the
autonomous run can't perform (repo settings, release publishing, form
submissions); everything is prepared so each is a copy-paste step.

## 1. Repo metadata **[human — repo Settings]**

- **Description:** `The board is the database — a git-committed kanban board your AI agents run and remember. A Claude Code plugin and MCP server.`
- **Website:** `https://ghostlygawd.github.io/engineering-board/`
- **Topics:** `claude-code` `claude-code-plugin` `mcp` `mcp-server` `ai-agents` `multi-agent` `kanban` `agentic-workflow` `tdd` `developer-tools`
- **Social preview image:** upload `brand/social-preview.png` (1280×640) in Settings → General → Social preview.

## 2. GitHub Pages — **DONE (live)**

- **Live at `https://ghostlygawd.github.io/engineering-board/`** (HTTP 200, all
  assets 200, deployed page byte-identical to `docs/index.html`; Lighthouse on
  the deployed bytes 100/100/100/100 — `.goal/evidence/G4-live-verification.txt`).
- Mechanism: branch-deploy from `gh-pages` (auto-enabled when the branch was
  pushed). The Actions-native `deploy-pages` path was denied ("Resource not
  accessible by integration"), so `pages.yml` now syncs
  `docs/{index.html,assets,.nojekyll}` → `gh-pages` on every push to `main`.
  No Settings action needed.

## 3. Release **[human — from a clone with push rights]**

The RC tag exists locally but the sandbox git relay can't push tags (BLOCKERS B2):

```sh
git tag -a v1.2.0-rc.1 <merge-sha> -m "engineering-board v1.2.0-rc.1 — dual distribution (plugin + MCP)"
git push origin v1.2.0-rc.1
```

Then publish a GitHub Release from the tag. **Release notes** (brand voice — plain,
no hype): paste the `## [1.2.0]` section of [`CHANGELOG.md`](../CHANGELOG.md). Headline:
*"1.2.0 — the board goes dual: a zero-dependency MCP server alongside the Claude Code plugin."*
Promote `rc.1` → `1.2.0` once the plugin + MCP install paths are verified from the
public artifacts.

## 4. Distribution submissions (channel map from POSITIONING.md)

| Channel | Action | Owner |
|---|---|---|
| **Self-hosted plugin marketplace** | Already live — users run `/plugin marketplace add GhostlyGawd/engineering-board`. Nothing to submit. | done |
| **awesome-claude-code** (hesreallyhim) | Use "Recommend a new resource" → opens a pre-filled issue (do **not** open a PR). Highest-signal free channel for the exact audience. | **[human]** |
| **Claude community marketplace** | `claude plugin validate` (passes clean) then submit at `platform.claude.com/plugins/submit` (Console) or `claude.ai/admin-settings/directory/submissions/plugins/new`. Pinned to a commit SHA after review. | **[human]** |
| **Official MCP Registry** | Manifest ready: [`mcp-server/server.json`](../mcp-server/server.json) (namespace `io.github.ghostlygawd/engineering-board`). See the command block below. Auto-syndicates into PulseMCP/mcp.so. | **[human]** |
| **Smithery** | Config ready: [`mcp-server/smithery.yaml`](../mcp-server/smithery.yaml). `smithery mcp publish` (needs account/API key). | **[human]** |
| **Glama / PulseMCP / mcp.so** | Auto-crawl the official registry + GitHub; claim the listing after it appears. | mostly automatic |
| **awesome-mcp-servers** (punkpeye) | Open a PR adding the entry in the list's format. | **[human]** |

### Prepared MCP-server artifacts (this run) — exact publish steps

The server ships from the repo tree (it shells out to sibling `hooks/scripts/`),
so the registry package is an **MCP bundle** (`.mcpb`), built and version-locked
to `plugin.json`. All three configs are validated by the MCP test suite.

```sh
# 1. Build the bundle (server + hook scripts + manifest.json); prints its sha256.
bash mcp-server/build-mcpb.sh          # → dist/engineering-board-mcp.mcpb

# 2. Attach the bundle to the GitHub Release for the tag (after the tag is pushed
#    — see §3), then set packages[0].fileSha256 in mcp-server/server.json to the
#    sha the build printed.

# 3. Publish to the official MCP Registry from mcp-server/.
cd mcp-server
mcp-publisher login github
mcp-publisher publish                  # reads server.json

# 4. Smithery (separate account/API key):
smithery mcp publish                   # reads smithery.yaml
```

Repo topics/description/social-preview (§1) and the tag push (§3) remain the
human prerequisites; nothing above can run until the release tag exists.

## 5. Announcement drafts (brand voice — confident, plain, no hype)

### Short (social / Show HN one-liner)

> **engineering-board** — the board is the database. A git-committed kanban board
> your AI agents run and remember: multi-agent coordination, atomic claim-locking,
> and durable cross-session memory, all as committed markdown in your repo. Ships
> as a Claude Code plugin **and** a zero-dependency MCP server.
> https://github.com/GhostlyGawd/engineering-board

### Long (release post / README lede)

> Most tools make you choose: a task board that's visible but dumb (no locking, no
> memory), or agent coordination that's smart but hidden in a database. engineering-board
> refuses the trade-off.
>
> It turns a committed `engineering-board/` markdown tree into an autonomous,
> multi-agent build system. Findings are captured passively from every session,
> promoted to the live board through deterministic consolidation, and worked through
> a `tdd → review → validate` state machine with atomic, mkdir-based claim-locking so
> parallel agents never collide. Recurring lessons promote into committed Learning
> entries that survive session boundaries. Because the board is committed markdown,
> you review your agents' coordination state in the same PRs as your code — no hidden
> DB, no external service, no daemon.
>
> 1.2.0 makes it dual-distribution: the native Claude Code plugin now ships alongside
> a zero-dependency MCP server (11 tools over stdio) that exposes the same board to
> any MCP client. Install either way in a minute.
>
> Plugin: `/plugin marketplace add GhostlyGawd/engineering-board` → `/plugin install engineering-board`.
> MCP: `claude mcp add engineering-board -- python3 .../mcp-server/engineering_board_mcp.py`.
> MIT licensed. https://github.com/GhostlyGawd/engineering-board

## 6. Pre-launch verification (post-merge)

- [x] CI green on `main` after merge (`tests` run on `0060afd`).
- [x] Pages URL renders (HTTP 200, byte-identical to source); Lighthouse on the
      deployed bytes 100/100/100/100 (`evidence/G4-live-verification.txt`).
- [x] Public artifacts verified from a fresh clone of `main`: 11/11 suites,
      `claude plugin validate` clean, MCP stdio handshake + 11 tools.
- [ ] `/plugin marketplace add` + `/plugin install` in a fresh interactive
      session (BLOCKERS B1 — needs a human session).
- [ ] Social preview shows on a shared repo link (after §1 upload — B3).

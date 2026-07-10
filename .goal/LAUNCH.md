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

## 3. Release — **DONE (published 2026-07-06 via the release workflow)**

The sandbox can't push tags or call the release API (BLOCKERS B2), but
[`.github/workflows/release.yml`](../.github/workflows/release.yml) now automates
the entire chain once a human initiates it. **Actions → release → Run workflow**,
twice:

| Run | `tag` | Result |
|---|---|---|
| 1 | `v1.3.0` | **Published** — <https://github.com/GhostlyGawd/engineering-board/releases/tag/v1.3.0> (notes from CHANGELOG) |
| 2 | `v1.4.0` | **Published** — <https://github.com/GhostlyGawd/engineering-board/releases/tag/v1.4.0> with `engineering-board-mcp.mcpb` (GitHub-computed digest matches the `server.json` pin) |
| 3 | registry | **Published** to <https://registry.modelcontextprotocol.io> as `io.github.GhostlyGawd/engineering-board` via OIDC (workflow run #4); syndication to PulseMCP/Glama/mcp.so is automatic. Two validation fixes were required and are merged: description ≤ 100 chars (PR #63) and exact login-casing namespace (PR #64). |

For future releases, the same workflow_dispatch (tag + sha + optional
`publish_registry`) repeats the whole chain; historical inputs kept for reference:

Each run: creates the annotated tag at that sha (never moves an existing one),
verifies the tag matches `plugin.json` at that tree, extracts that version's
CHANGELOG section as the release notes, builds the reproducible `.mcpb` bundle
and refuses to publish if its sha doesn't match the `server.json` pin (1.4.0
only — 1.3.0 predates the bundle and auto-skips), and publishes the GitHub
Release with the asset. Run 2's `publish_registry` additionally publishes to the
official MCP Registry via GitHub OIDC (no stored secret; syndicates to
PulseMCP/Glama/mcp.so). Pushing a `v*` tag from a clone triggers the same
release steps.

Equivalent from a clone with push rights: `git tag -a v1.3.0 b35cf7f -m … && git push origin v1.3.0` (the tag-push trigger runs the rest).

## 4. Distribution submissions (channel map from POSITIONING.md)

| Channel | Action | Owner |
|---|---|---|
| **Self-hosted plugin marketplace** | Already live — users run `/plugin marketplace add GhostlyGawd/engineering-board`. Nothing to submit. | done |
| **awesome-claude-code** (hesreallyhim) | Use "Recommend a new resource" → opens a pre-filled issue (do **not** open a PR). Highest-signal free channel for the exact audience. | **[human]** |
| **Claude community marketplace** | `claude plugin validate` (passes clean) then submit at `platform.claude.com/plugins/submit` (Console) or `claude.ai/admin-settings/directory/submissions/plugins/new`. Pinned to a commit SHA after review. | **[human]** |
| **Official MCP Registry** | **DONE (2026-07-06)** — published as `io.github.GhostlyGawd/engineering-board` via the release workflow's OIDC step. Auto-syndicates into PulseMCP/mcp.so. | done |
| **Smithery** | Config ready: [`mcp-server/smithery.yaml`](../mcp-server/smithery.yaml). `smithery mcp publish` (needs account/API key). | **[human]** |
| **Glama / PulseMCP / mcp.so** | Auto-crawl the official registry + GitHub; claim the listing after it appears. | mostly automatic |
| **awesome-mcp-servers** (punkpeye) | Open a PR adding the entry in the list's format. | **[human]** |

### Prepared MCP-server artifacts (this run) — exact publish steps

The server ships from the repo tree (it shells out to sibling `hooks/scripts/`),
so the registry package is an **MCP bundle** (`.mcpb`), built and version-locked
to `plugin.json`. The build is **reproducible** (python3 `zipfile`, fixed
timestamps), so `packages[0].fileSha256` in `server.json` is **already pinned**
to the exact sha the build produces — and the MCP test suite fails if they drift.
No manual sha copy-paste step.

**Preferred path: §3's release workflow does all of this** — bundle build, sha
verification, asset upload, and (run 2) the OIDC registry publish. The manual
equivalent, for a clone:

```sh
# 1. Build the bundle. It is byte-reproducible: the sha it prints already equals
#    packages[0].fileSha256 in mcp-server/server.json (CI-verified).
bash mcp-server/build-mcpb.sh          # → dist/engineering-board-mcp.mcpb

# 2. Attach that exact file as the v<version> GitHub Release asset (after the tag
#    is pushed — see §3). server.json already points at that release-asset URL.

# 3. Publish to the official MCP Registry from mcp-server/.
cd mcp-server
mcp-publisher login github
mcp-publisher publish                  # reads server.json

# 4. Smithery (separate account/API key) — NOT covered by the workflow:
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

## 7. Submissions — ready to fire (prepared 2026-07-10)

The four §4 channels still marked **[human]**, now as ready-to-paste blocks.
Each block: the exact text, the URL to paste it at, and the human account action
it needs. Facts checked against the repo at v1.6.1 (heading to 1.7.0 this
release); the texts below are version-agnostic so they stay pasteable. Fire
these only after the current release is tagged and live on `main`.

### 7a. awesome-claude-code — "Recommend a new resource" issue

- **Where:** <https://github.com/hesreallyhim/awesome-claude-code> → open a new
  issue with the **"Recommend a new resource"** template (issue, **not** a PR —
  their vetting is issue-driven). Fill the template's fields with the values
  below; if field names have drifted, map by meaning.
- **Human action:** GitHub account — open the issue, respond to the automated
  vetting/maintainer follow-up.
- **Paste values:**
  - **Resource name:** `engineering-board`
  - **Link:** `https://github.com/GhostlyGawd/engineering-board`
  - **Category:** the plugins/tooling category the form offers (it is a Claude
    Code plugin + MCP server; pick the plugin option where present)
  - **Author:** `GhostlyGawd` (`https://github.com/GhostlyGawd`)
  - **Description:**
    > The board is the database — a git-committed kanban board your AI agents
    > run and remember. A Stop hook passively captures findings each session,
    > PM mode promotes them to a live board, and worker agents drive each card
    > through a tdd → review → validate pipeline under atomic claim-locking.
    > Recurring lessons promote into committed Learning entries. Everything is
    > plain markdown in your repo — no hidden DB, no server. Ships as a Claude
    > Code plugin and a zero-dependency MCP server; dogfooded on its own live
    > board: https://ghostlygawd.github.io/engineering-board/board.html

### 7b. awesome-mcp-servers — PR entry line

- **Where:** <https://github.com/punkpeye/awesome-mcp-servers> → fork, add the
  line below to the closest project/task-management or developer-tools section
  (alphabetical within the section), open a PR. Before submitting, check the
  list's legend and mirror its current emoji markers — the line below uses
  🐍 (Python) and 🏠 (local/self-hosted) per their convention.
- **Human action:** GitHub account — fork, PR, respond to maintainer review.
- **Paste line (their `- [owner/repo](link) marks - description` format):**

  ```markdown
  - [GhostlyGawd/engineering-board](https://github.com/GhostlyGawd/engineering-board) 🐍 🏠 - Git-committed markdown kanban board that AI agents fill in and work through themselves: passive finding capture, atomic claim-locking for parallel agents, and durable cross-session learnings — all plain markdown in your repo, no database.
  ```

### 7c. Smithery — publish the MCP server

- **Where:** <https://smithery.ai/new> (docs: <https://smithery.ai/docs/build/publish>).
  The config has shipped in-repo since v1.4.0: [`mcp-server/smithery.yaml`](../mcp-server/smithery.yaml)
  (container runtime, stdio, optional `projectDir` → `CLAUDE_PROJECT_DIR`).
- **Human action:** Smithery account + API key (this is the one channel §3's
  release workflow does **not** cover).
- **Steps:**

  ```sh
  # from a clone of main at the current release tag
  cd mcp-server
  smithery login          # needs the Smithery API key
  smithery mcp publish    # reads smithery.yaml
  ```

  Then on the Smithery listing page: confirm the description matches the repo
  tagline ("The board is the database — a git-committed kanban board your AI
  agents run and remember."), and that the repo link and MIT license show.
  Re-run `smithery mcp publish` on future releases (add it as a step beside §3's
  workflow-dispatch runs).

### 7d. Claude community marketplace — plugin submission form

- **Where:** `https://platform.claude.com/plugins/submit` (Console) or
  `https://claude.ai/admin-settings/directory/submissions/plugins/new`
  (Team/Enterprise admin). Reviewed + safety-screened; the accepted listing is
  pinned to a commit SHA.
- **Human action:** Claude account with Console (or Team/Enterprise admin)
  access — submit the form, track the review.
- **Pre-flight (already verified clean in §6, re-run at the release tag):**

  ```sh
  claude plugin validate
  ```

- **Form field values:**
  - **Plugin name:** `engineering-board`
  - **Repository:** `https://github.com/GhostlyGawd/engineering-board`
  - **Marketplace file:** `.claude-plugin/marketplace.json` (repo root; users
    can already self-serve via `/plugin marketplace add GhostlyGawd/engineering-board`)
  - **Commit SHA to pin:** the commit the current release tag points at
    (`git rev-parse <tag>` — reviewers pin to it)
  - **Website:** `https://ghostlygawd.github.io/engineering-board/`
  - **Description:**
    > The board is the database — a git-committed kanban board your AI agents
    > run and remember. Passive finding capture each session, a tdd → review →
    > validate worker pipeline, atomic claim-locking for parallel agents, and
    > durable Learning entries — all committed markdown, reviewable in the same
    > PRs as your code. MIT; also available as a zero-dependency MCP server.
  - **Support contact:** the repo's Issues page
    (`https://github.com/GhostlyGawd/engineering-board/issues`)

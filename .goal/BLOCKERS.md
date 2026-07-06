# BLOCKERS

Justified, non-blocking items requiring human action. (Rule 6: honest failure.)

## B1 — Fresh interactive Claude Code session E2E for the plugin (partial)

**Gate:** G2 asks the plugin be installed into a *fresh Claude Code session* and
every command/agent/hook exercised with captured transcripts.

**What was tried:**
1. `claude plugin validate .` → **passes clean** (manifest + structure valid; the
   plugin loads). Evidence: `.goal/evidence/G2-plugin-validate-and-inspector.txt`.
2. Headless load via `claude --plugin-dir <repo> -p "…/board-init…"` in a temp
   consuming repo → **timed out at the 2-minute container cap** with no output.
   A nested, headless Claude Code session is not tractable inside this execution
   container (it appears to block on interactive/model setup under the sandbox).

**Why it is non-blocking:** every plugin surface is otherwise covered by
deterministic evidence:
- `claude plugin validate` confirms the manifest, structure, and marketplace load.
- The 11-suite battery (`tests/run-all.sh`, green in CI) exercises every hook
  script, every command's logic (structural + orchestration lint), every agent's
  Output contract, and the PM/Worker pipelines end-to-end at the substrate layer.
  `tests/orchestration/board-init-command.sh` specifically pins `/board-init`.
- The MCP surface — the net-new capability — is validated live with the official
  MCP Inspector and a scripted client (65 checks).

**Recommended human action:** in a real interactive Claude Code session, run
`/plugin marketplace add GhostlyGawd/engineering-board` → `/plugin install
engineering-board`, then `/board-init demo`, `/pm-start`, `/worker-start
--discipline tdd` in a scratch repo and confirm the transcripts. Expected ~5 min.
Nothing in the code blocks this; it is purely an environment limitation of the
autonomous run.

## B2 — Remote RC tag / release push blocked by the sandbox git relay

**Gate:** G2 deliverable "tag a release candidate"; DoD "Release published".

**What was tried (3 distinct approaches):**
1. `git push origin refs/tags/v1.2.0-rc.1` → `send-pack: unexpected disconnect
   … the remote end hung up unexpectedly` (branch pushes to the assigned
   working branch succeed; only non-branch refs fail).
2. Retry with exponential backoff (5 attempts) → same disconnect every time.
3. GitHub MCP API → no `create_release` / `create_tag` / generic `create_ref`
   tool is exposed (only `create_branch`, which makes `refs/heads/*`).

**Root cause:** the sandbox git relay (the `local_proxy` remote on port 41729)
permits pushes only to this session's designated working branch
(`claude/engineering-board-productize-fu2vvk`); tag refs are rejected at the
connection level. This is an environment policy, not a repo problem.

**State:** the annotated tag **`v1.2.0-rc.1` exists locally** at the CI-green
commit `88d4ee6`, documenting the RC. It is not on the remote.

**Why it is non-blocking for the run:** no remaining phase (brand, README,
landing page) depends on the remote tag existing. G2's substantive pass
conditions (CI green, MCP Inspector + scripted-client validation, zero
blocker/major defects, every value prop works) are all satisfied.

**Recommended human action:** from a clone with push rights, run
`git tag -a v1.2.0-rc.1 <sha> -m "…" && git push origin v1.2.0-rc.1`, then
publish a GitHub Release from that tag (the release step needs a human account
anyway). The tag message and CHANGELOG 1.2.0 section are ready to paste.

_Post-merge update (2026-07-04):_ retested after PR #18 merged — tag refs are
still rejected by the relay (branch refs are allowed: the `gh-pages` push
succeeded). Recommend tagging the merge commit `0060afd` on `main`.

_Update (2026-07-05, roadmap run):_ retested — the relay now returns HTTP 403 on
tag refs (same policy, different symptom), and the sandbox's permission layer
also gates routing releases through the API directly, so publication remains a
deliberately human-initiated act. **The gate is now one click wide:**
`.github/workflows/release.yml` (workflow_dispatch) performs the whole chain —
tag creation, CHANGELOG-sourced notes, reproducible-bundle build + sha
verification, Release publish with the asset, and opt-in MCP-Registry OIDC
publish. Exact inputs for the two pending runs (v1.3.0, v1.4.0) are in
`LAUNCH.md` §3.

## B3 — Repo metadata (description / topics / social preview) — UI-only

The GitHub MCP toolset exposes no repository-update endpoint (only
create/fork), and there is no `gh` CLI or direct API access in this
environment. Setting the repo description, topics, and social-preview image
(values ready in `.goal/LAUNCH.md` §1) remains a Settings-UI step. Everything
else in LAUNCH §1–§2 that could be automated has been (Pages is live).

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

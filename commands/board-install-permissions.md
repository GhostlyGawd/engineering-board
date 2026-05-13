---
description: Install the engineering-board plugin allowlist into your user-scope settings. Reads references/required-permissions.json, shows the proposed patterns, asks for confirmation, then prints copy-pasteable `claude config add` lines for you to run. Interactive-only by design.
argument-hint: (no arguments)
---

# /board-install-permissions — install plugin allowlist

Add the engineering-board permission patterns to your `~/.claude/settings.json` so the plugin can run its claim scripts and slash commands without prompting each time. This command is interactive-only: it prints the exact `claude config add` lines for you to run yourself.

## What to do

### Step 0 — Fast-path: check if already installed

Run:

```bash
bash $CLAUDE_PLUGIN_ROOT/hooks/scripts/board-permission-self-check.sh
```

If the script exits 0 (all installed), print:

```
All M2.2.c permissions installed. Nothing to do.
```

Then stop.

If the script exits 2 (manifest unreadable), print:

```
ERROR: could not read required-permissions.json. Check that CLAUDE_PLUGIN_ROOT is set correctly.
```

Then stop.

### Step 1 — Read and display the proposed allowlist

Read `${CLAUDE_PLUGIN_ROOT}/references/required-permissions.json`. Parse the `patterns` array.

Print exactly:

```
engineering-board requests the following permissions for your ~/.claude/settings.json:
```

Then print a numbered list. For each pattern entry, print two lines:

```
  N. <tool>: <pattern>
     Reason: <rationale>
```

Example:

```
  1. Bash: bash hooks/scripts/board-claim-acquire.sh:*
     Reason: claim lifecycle: acquire -- atomic mkdir, owner.txt write, heartbeat init
  2. SlashCommand: /pm-start
     Reason: Start PM (consolidator) session for engineering board
```

(Use ASCII `--` not em-dash; the rationale field is copied verbatim from the JSON.)

### Step 2 — Confirmation prompt

Print exactly:

```
Add these to your user-scope settings? Reply YES (uppercase) to confirm, or anything else to cancel.
```

Then stop and wait for the user's reply.

### Step 3 — Handle user reply

**If the user replied YES (exact uppercase match):**

Print exactly:

```
Run the following commands to add each permission. Copy and paste them into your terminal:
```

Then print one line per pattern:

```
claude config add permissions.allow "<pattern>"
```

Where `<pattern>` is the `pattern` field from the JSON entry (with surrounding double-quotes as shown).

After all lines, print:

```
After running the above, run /board-install-permissions again to confirm zero missing patterns.
```

**If the user replied anything other than YES:**

Print exactly:

```
No changes made. Run /board-install-permissions again when ready.
```

Then stop.

## Notes

- Interactive-only is by design. Writing directly to `~/.claude/settings.json` has cross-platform variability (path resolution, file encoding, concurrent-write risk) that was evaluated and deferred for v0.2.2. The paste-able `claude config add` one-liners are the authoritative install path.
- The self-check fast-path (Step 0) means running this command after installation is a safe no-op — it will confirm success and exit without re-prompting.
- `board-permission-self-check.sh` exit codes: 0=all installed, 1=some missing, 2=manifest invalid, 3=settings.json invalid. Step 0 only short-circuits on exit 0.
- If `CLAUDE_PLUGIN_ROOT` is not set, the self-check script will fail with a path error. Claude Code sets this automatically when running a plugin command; it should always be present in normal usage.

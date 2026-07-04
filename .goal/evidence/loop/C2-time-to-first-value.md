# Time-to-first-value measurement (C2, SIMULATED)

Convergence criterion 3. Measured by static trace of the exact literal steps a
fresh user runs following ONLY the README (Track B, C2 DISCOVER). SIMULATED
because a nested interactive Claude Code session can't run in the sandbox
(BLOCKERS B1) — no live transcript. Assumes a competent dev new to the plugin,
warm network, python3 present, and Claude Code's "prompt once then always-allow"
permission UX. Prompt counts are worst case (permissions not pre-installed);
after `/board-install-permissions` (B004 coverage fix) the pipeline prompts drop
to ~0.

| Milestone | Steps (literal) | Restarts | Prompts (worst / post-install-perms) | Est. minutes (cumulative) | Biggest friction |
|---|---|---|---|---|---|
| M0 Install | 2 slash commands | 0–1 | ~1 | 2–3 | plugin load |
| M1 First capture | +`/board-init`, then produce a finding & end a turn | +1 | ~2–4 / ~1 | 5–8 | capture is passive + invisible (B005), and — before B027 — the Quickstart never said it happens or where |
| M2 First promotion | +`/pm-start`, then end a turn | 0 | ~5 / ~0 | 12–20 | before B027, `/pm-start` was absent from the Quickstart |
| M3 First autonomous fix | +`/worker-start --discipline tdd`, then end a turn | +1 (PM→worker, B006) | ~3 / ~1 + code-edit | 25–45 | worker mode; one session per discipline (B006) |

## Verdict (pre-B027)
A README-only user did NOT reliably reach ≤5 min confirmable capture or ≤15 min
promotion — the Quickstart dead-ended at `/board-init`; the capture→promote→fix
path lived only in the reference Modes table. Dominant cliff: discoverability,
not any slow step.

## Remediation shipped (B027, PR C2d)
The Quickstart now continues past `/board-init` with: (1) capture is automatic +
where it lands (`_sessions/`), (2) `/pm-start` to promote, (3) `/board-install-permissions`
to stop prompts, plus an honest "what to expect" note (~5 min to first capture,
~10–15 min to first promotion following only the README). This makes M1–M3
documented rather than undiscoverable — the single highest-leverage lever on the
metric. Remaining friction is captured as open P2s: B005 (capture invisibility),
B006 (per-discipline restart), B030 (permission-install delivery).

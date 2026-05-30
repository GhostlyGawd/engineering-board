# Next-phase recommendations — CLOSED at v1.0.0

The engineering-board reached its design completion at **v1.0.0**. The substrate, subagent contracts, mode-transition matrix, and pause/resume cycle invariants are all pinned by tests, and `tests/run-all.sh` is enforced as a merge gate by `.github/workflows/test.yml`.

There is no remaining test debt or risk being tracked. What once lived in this file as Tier A/B/C backlog was enhancement-only — never debt — and is intentionally not being carried forward. If a future need arises, open a new planning doc scoped to that need rather than reviving the old backlog.

## Shipped releases

- **v0.2.3** Resilience — active-workers registry, PM-fallback heartbeat, `paused:` field.
- **v0.3.0** Learning entity — `L###` type, `learnings-curator` agent, `/board-migrate` (SHA256 apply/rollback), SessionStart top-learnings surface; Tier-4 QoL pack.
- **v0.3.1** Mode-transition guard — `board-mode-guard.sh` deterministically enforces the §11.5 refusal matrix; pause/resume now round-trip the `(mode, discipline)` tuple.
- **v0.3.2** Test-debt closeout — subagent Output-contract fixtures (7 agents, 30 assertions), pause/resume registry invariants (19 assertions), GitHub Actions CI gate.
- **v1.0.0** Stable — declares the design surface frozen. One fix vs v0.3.2: `board-claim-acquire.sh` now polls up to 250ms for `owner.txt` and `heartbeat.txt` to appear after a losing `mkdir`, closing a construction-window race that could produce `exit 2` (stale) when the winning racer was simply mid-write. Surfaced by `tests/claims/race-acquire.sh` under GitHub Actions runner load (~3% reproduction rate locally).

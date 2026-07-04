# LOOP_PROGRESS — product improvement loop

> Resume file for the autonomous improvement loop driven by
> `.goal/NEXT_GOAL_IMPROVEMENT_LOOP.md`. A fresh session resumes from this file
> plus the `engineering-board/eb-self/` board (the living backlog). Update it at
> the end of every cycle step.

_Last updated: 2026-07-04 (C1 in progress)_

## How to resume

1. Read `state.md`, then `.goal/NEXT_GOAL_IMPROVEMENT_LOOP.md` in full.
2. Read this file and the `engineering-board/eb-self/BOARD.md` index.
3. Continue from the "Current cycle" section below.

## Convergence scorecard (Definition of Done — all must hold)

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Two consecutive full cycles → zero new blocker/major/P0/P1 | ⬜ not yet (C1 in progress) |
| 2 | eb-self board has no open blocker/major/P0/P1 | ⬜ |
| 3 | Time-to-first-value measured, documented, defensible (≤5min first capture, ≤15min first promote) | ⬜ |
| 4 | Every surface has keep/simplify/merge/deprecate decision in one docs/rfcs/ product-review doc | ⬜ |
| 5 | README+landing+CHANGELOG+positioning coherent, link-checked, Lighthouse ≥95, real animated demo | ⬜ |
| 6 | Release batched+CHANGELOG'd+manifests bumped; BLOCKERS only human-gated; FINAL_REPORT closing section | ⬜ |

## Cycle log

### C1 — initialization + first full DISCOVER sweep (in progress)

- **Board:** initialized `engineering-board/eb-self/` (router + BOARD.md + ARCHIVE.md + 5 subdirs). Baseline `tests/run-all.sh` = 11/11 green.
- **DISCOVER:** ran all four tracks (A red-team, B UX, C features, D coherence) via parallel investigation agents. **26 findings intaked** as real board entries (22 bugs, 3 features, 1 question); all pass the real `board-validate-entry.sh`.

**DISCOVER headline findings (all reproduced/evidenced):**
- **A (red-team):** B001 SessionStart O(n²) exceeds 10s timeout at ~1000+ entries (measured 1200=15s); B002 injection reject-blocklist bypassable — 4 payloads reproduced promoting to live board; B003 the 50 adversarial/benign fixtures are dead code + ARCHITECTURE falsely claims a 100% reject-rate; B008 fail-open un-pause (D4 confirmed); B009 silent python3 no-op; B010 empty-board count glitch (D6 confirmed).
- **B (UX):** B005 first captured value invisible (buried in `_sessions/`); **B004 permission allowlist doesn't cover the scripts hooks invoke** (verified: `board-scratch-append.sh` etc. absent, relative vs `$CLAUDE_PLUGIN_ROOT` path mismatch); B006 pipeline needs two restarts; B007 validator dead-end; B014 duplicate consolidation engines; + 8 P3 doc/consistency (B015–B022).
- **C (features):** F001 HTML board viewer (rank 1, build), F002 onboarding wizard (rank 2, build), F003 learnings surfacing (rank 3, later); animated-demo scope-cut (B1); multi-client → Q001 test/doc task.
- **D (coherence):** no majors — D1/D2/D5 confirmed fixed; B011 ARCHITECTURE stale for 1.2.0, B012 CHANGELOG rc-tag 404, B013 README emoji vs BRAND.

**DECIDE — C1 slate** (all new majors/P1 + highest-leverage UX + ≤1 feature):
- **PR C1a — red-team hardening (flagship):** B002 injection filter + B003 wire the 50 fixtures into CI + B008 fail-closed + B009 python3 preflight + B010 count. Security + the test that proves it.
- **PR C1b — permission allowlist coverage:** B004 (+B016 version stamp) + new coverage test.
- **PR C1c — SessionStart perf:** B001 O(n²)→single python3 pass + perf evidence.
- **PR C1d — docs coherence sweep:** B011, B012, B013, B015, B017, B018, B019.
- **Deferred (recorded):** B005/B007 UX (touch pinned stop-hook tokens — C2 with care); B006/B014 (design, likely Conductor-adjacent — C2); features F001/F002/F003 (C2, after P1s clear — red-team surfaced P1s that gate adding new surface); B020/B021/B022 (P3, C2).

**SHIP progress (C1):**
- **PR C1a → [#21](https://github.com/GhostlyGawd/engineering-board/pull/21)** — MERGED (`e2f8a6f`). B002 injection filter + B003 fixture-corpus CI wiring + board init/intake. B002/B003 resolved.
- **PR C1b → #22** — MERGED (`657c072`). B004 permission allowlist + coverage test (T26–T28) + B015 jargon + partial B016. B004/B015 resolved.
- **PR C1c** (in flight) — B001 SessionStart perf (15s→0.1s, new session-start suite) + B010 count fix. B001/B010 resolved on board.
- Next: C1d (docs sweep: B011/B012/B013/B017/B018/B019 + finish B016). Reset branch after merge.
- **eb-self open blocker/major/P1: NONE remaining.** All open entries now P2/P3 (B005/B006/B007/B008/B009/B014 P2; B011–B022 minus resolved P3; features F001–F003; Q001).

### Track status (current cycle)

| Track | Status |
|-------|--------|
| A — Red team & hardening | DISCOVER ✅ · intaked · slate C1a/C1c |
| B — UX & first-principles | DISCOVER ✅ · intaked · slate C1b, rest deferred |
| C — PM feature development | DISCOVER ✅ · intaked · features deferred to C2 |
| D — Surface coherence | DISCOVER ✅ · intaked · slate C1d |

## Evidence

- `.goal/evidence/loop/` — cycle-numbered artifacts (created as cycles produce them).

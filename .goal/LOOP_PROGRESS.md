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
| 1 | Two consecutive full cycles → zero new blocker/major/P0/P1 | ⬜ C1 not clean (4 P1s); C2 not clean (1 P0 + 3 P1s) → need clean C3 + C4 |
| 2 | eb-self board has no open blocker/major/P0/P1 | ✅ MET — all open entries P2/P3 (verified end of C2) |
| 3 | Time-to-first-value measured, documented, defensible | ✅ MET — `.goal/evidence/loop/C2-time-to-first-value.md` + README "what to expect" (B027) |
| 4 | Every surface has keep/simplify/merge/deprecate decision in one docs/rfcs/ product-review doc | ✅ MET — `docs/rfcs/0002-surface-product-review.md` |
| 5 | README+landing+CHANGELOG+positioning coherent, link-checked, Lighthouse ≥95, real animated demo | 🟡 coherence current (C1d+C2d); animated demo (F001-fed) + Lighthouse re-run pending |
| 6 | Release batched+CHANGELOG'd+manifests bumped; BLOCKERS only human-gated; FINAL_REPORT closing section | ⬜ pending (batch when criterion 1 nears) |

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
- **PR C1c → #23** — MERGED (`6322dc2`). B001 SessionStart perf (15s→0.1s) + B010 count fix + new session-start suite. B001/B010 resolved.
- **PR C1d** (in flight) — docs coherence: B011 (ARCHITECTURE→v1.2.0), B012 (CHANGELOG link), B013 (README emoji→text), B017/B018/B019 (skill fixes). Resolved on board. B016 kept open P3 (why-deferred noted).
- **PR C1d → #24** — MERGED (`9f30d20`). B011/B012/B013/B017/B018/B019 resolved; B023 intaked; B016 kept open P3.
- **PR C1e** (in flight) — fix B023 (`board-index-check` counts open files only) + smoke resolve-in-place regression test. B023 resolved; eb-self index-check exits 0 again.
- **C1 REFLECT → #26** — MERGED. L001/L002 self-Learnings + retro.

### C2 — second full DISCOVER sweep (COMPLETE)

- **DISCOVER:** all four tracks re-run (parallel agents). Verified all C1 fixes hold except one new bypass class. Intaked 10 findings (B024–B033): **1 P0 blocker + 3 P1s** (mostly the newer MCP server) + P2/P3s.
- **SHIP:** PRs #27–#30 merged.
  - **C2a → #27** — B024 (P0 MCP path traversal) + B028 (MCP frontmatter injection) + intake.
  - **C2b → #28** — B025 (reject polite/modal-prefix bypass) + 4 fixtures.
  - **C2c → #29** — B026 (MCP findings silently destroyed on consolidate — data loss).
  - **C2d → #30** — B027 (README Quickstart first-value path = criterion 3) + B031/B032/B033 docs coherence.
  - **C2e (this PR)** — criterion-4 product-review doc (`docs/rfcs/0002-surface-product-review.md`) + C2 REFLECT (L003/L004 self-Learnings).
- **C2 REFLECT:** proved the C1-hardened plugin substrate holds under a second red-team; disproved that the newer MCP surface was as battle-tested (it carried the blocker + 2 more). Learnings: **L003** (newest surface = most risk, red-team it hardest — B024/B026/B028) and **L004** (a denylist is never done — grow the corpus — B002/B025).
- **Deliverables met this cycle:** criterion 3 (time-to-first-value) ✅ and criterion 4 (surface product-review) ✅.
- **eb-self open blocker/major/P1: NONE.** Open (all P2/P3): B005/B006/B007/B008/B009/B014/B029/B030 (P2); B016/B020/B021/B022 (P3); F001–F003; Q001.

### Next — C3

Convergence criterion 1 needs **two consecutive clean cycles**; neither C1 nor C2
was clean. C3 must run all four DISCOVER tracks again and, ideally, surface zero
new blocker/major/P1. Also owed: criterion 5 (animated demo — build **F001**
board viewer to feed it, then re-run Lighthouse) and, once criterion 1 nears,
criterion 6 (batch a release: bump manifests + CHANGELOG heading + FINAL_REPORT
closing section). Consider building F001/F002 in C3 (≤1 feature/cycle) since the
P0/P1 backlog is now clear.

### Track status (C1)

| Track | Status |
|-------|--------|
| A — Red team & hardening | DISCOVER ✅ · shipped B002/B003 (C1a), B001/B010 (C1c), B023 (C1e) |
| B — UX & first-principles | DISCOVER ✅ · shipped B004/B015 (C1b); B005/B006/B007/B014 deferred to C2 |
| C — PM feature development | DISCOVER ✅ · F001/F002/F003 RFCs on board; build deferred to C2 |
| D — Surface coherence | DISCOVER ✅ · shipped B011/B012/B013/B017/B018/B019 (C1d) |

### C1 REFLECT (retro)

**Shipped:** 5 PRs merged (#21–#25). 13 findings resolved: **4 P1s** (B002 injection
bypass, B003 dead fixtures, B004 permission gap, B001 O(n²) SessionStart), plus B010,
B015, B011–B013/B017–B019, and B023 (a bug the dogfood board surfaced about itself).

**What C1 proved:** the *mechanics* the prior run shipped had real gaps under adversarial
+ scale + coherence pressure — all now closed with tests. The board dogfooded cleanly:
26 findings intaked, 13 resolved through the real state machine, index-check/validator
run on the board itself.

**What C1 disproved:** the "100% reject-rate" and "runs without babysitting" claims were
both false as shipped (untested fixtures; allowlist missing the core scripts). Positioning
copy now matches reality (C1d).

**Learnings promoted (product memory about itself):** L001 (guards need tests that drive
real fixtures/call-sites — from B002/B003/B004) and L002 (invariants must respect the
open-vs-resolved lifecycle — from B023/B010).

**Convergence:** criterion 2 now MET (no open blocker/major/P1). C1 was NOT a *clean*
cycle (it found P1s), so criterion 1 needs two *consecutive clean* cycles ahead. Carrying
to C2: verify C1 fixes hold, measure time-to-first-value (crit 3), consolidate the surface
keep/simplify/merge/deprecate table into a `docs/rfcs/` product-review doc (crit 4), and
evaluate building F001 (board viewer) / F002 (onboarding wizard).

**Surface keep/simplify/merge/deprecate (Track B, to be moved into docs/rfcs/ in C2):**
commands mostly keep; `/board-graph` simplify (fold into rebuild), `/worker-start` simplify
(discipline lock → B006), `/board-migrate` simplify (two ops, B020); agents: `consolidator`/
`board-consolidate` skill merge (B014), `code-reviewer` rename (B021); MCP tools all keep
(best-designed surface); skills keep with the fixes shipped in C1d.

## Evidence

- `.goal/evidence/loop/` — cycle-numbered artifacts (created as cycles produce them).

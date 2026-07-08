# FIXLOG — The Fixer

_Append-only history. Each session records the reports consumed, the scope chosen,
and what was fixed/skipped. Never rewrite past sessions._

---

## Session — 2026-07-08

- **Date:** 2026-07-08
- **Branch:** `claude/experience-optimization-audit-00869k` _(the designated working
  branch for this run; the brief's suggested `fix/goal-<date>` is overridden by the
  session's hard branch constraint — all work lands here, via PR, never on `main`)._
- **Reports consumed (this playbook — Experience Optimization):** `COMPREHENSION.md`,
  `SHOWCASE.md`, `CRO.md`, `PROOF.md`, `ACTIVATION.md`, `RETENTION.md`.
- **Reports found and set aside as shipped** (per `state.md`): `IMPROVEMENTS.md`
  (all 14 built), and the prior design batch `HIERARCHY.md` / `TYPOGRAPHY.md` /
  `COLOR.md` / `LAYOUT.md` / `STATES.md` / `BRAND-COHERENCE.md` (main fixes shipped
  in v1.5.1/v1.6.0). **Deferred residual that overlaps this run:** the
  explainer-diagram rainbow→brand recolor (COLOR F1 / BRAND-COHERENCE) — same asset
  as SHOWCASE F4 (`HOLD-A4` below); do once, together.
- **Scope chosen:** ⏳ **AWAITING OPERATOR DECISION — no codebase files changed yet.**

> **State of this session:** Phase 1 (collect) and Phase 2 (present + map
> dependencies) are complete below. Per the brief, **nothing in the product code
> changes until the operator picks a scope.** The `Fixed` / `Skipped` / `Follow-ups`
> sections are appended once execution runs.

---

### Finding pool (deduped across the 6 reports)

Severity = impact on the visitor/user · Effort: **S**=copy/small-HTML · **M**=script
or multi-file · **L**=feature/architectural. "Overlaps" notes merged duplicates.

#### Tier A — Landing/README copy, comprehension & trust · low-risk · `docs/index.html` + `README.md`
| id | Finding | Sev | Eff | Source(s) |
|---|---|---|---|---|
| FIX-1 | Name who it's for; **lead single-agent** before multi-agent | High | S | CMP-F1 |
| FIX-2 | Make "**it fills itself**" explicit; kill the "run and remember" agency ambiguity | High | S | CMP-F2 |
| FIX-3 | **Expand "MCP"** (Model Context Protocol) on first use | High | S | CMP-F3 |
| FIX-4 | **Define "finding"** at first sight (bug/feature/question/observation) | Med | S | CMP-F4 |
| FIX-5 | Unpack "**the board is the database**" with the concrete "no hidden DB" payoff | Med | S | CMP-F5 |
| FIX-6 | README "**What it is**": gist-first rewrite before the jargon sentence | Med | S | CMP-F6 |
| FIX-7 | State "**why now**" (agents forget; parallel agents collide) | Med | S | CMP-F8 |
| FIX-8 | Expand **TDD** once | Low | S | CMP-F10 |
| FIX-9 | **Pain-first** value cards (name→bridge→benefit) | Med | S | CRO-C5 · overlaps CMP-F6 · _A/B candidate_ |
| FIX-10 | "**Free & MIT · no lock-in · just markdown you can delete**" near CTA + Install | High | S | CRO-C3 · PROOF-F3 |
| FIX-11 | **Security-posture** reassurance line at Install (injection-hardened) | Med | S | CRO-C7 · PROOF-F7 |
| FIX-12 | Surface **CI badge + MCP Registry** up-page; **reframe fairness note**; front **dogfooding** as trust | High | M | CRO-C6 · PROOF-F2/F5/F6 |
| FIX-13 | Add a genuine "**who builds this**" maker note (no fabricated identity) | Med | S | PROOF-F4 |

#### Tier B — Install friction · low-risk · `docs/index.html` + `README.md`
| id | Finding | Sev | Eff | Source(s) |
|---|---|---|---|---|
| FIX-14 | MCP install **dead-end**: add `git clone` / show where the path comes from | Med | S | CRO-C1 |
| FIX-15 | State **Claude Code as a prerequisite** | Med | S | CRO-C2 |
| FIX-16 | **Copy-to-clipboard** buttons on install code blocks | Low | S | CRO-C8 |
| FIX-17 | **JSON-LD** `SoftwareApplication` structured data | Low | S | CRO-C9 |

#### Tier C — Media hygiene · low-risk
| id | Finding | Sev | Eff | Source(s) |
|---|---|---|---|---|
| FIX-18 | **Delete/compress** unused `docs/how-it-works.png` (524 KB); rewrite thin alt text | Low | S | SHW-F6 |
| FIX-19 | Caption the landing CSS demo as **illustrative** | Low | S | SHW-F7 |

#### Tier D — In-product copy · medium-risk (test-pinned script files) · `hooks/scripts/*`, `commands/*`
| id | Finding | Sev | Eff | Source(s) |
|---|---|---|---|---|
| FIX-20 | `board.html` **self-framing** header + rename opaque `eb-self` label | Med | M | CMP-F7 |
| FIX-21 | SessionStart: **lead value, demote mode jargon** | Low-Med | S | CMP-F9 |
| FIX-22 | **First-capture confirmation** line (quiet ≠ silent) | Med | M | ACT-A1 |
| FIX-23 | `/pm-start`: **name the "end a turn" trigger** in plain words | Low | S | ACT-A5 |
| FIX-24 | `/board-run` **stall**: specific recovery guidance, not "inspect notes" | Low | S | RET-R6 |
| FIX-25 | SessionStart/`board.html` **accrual line** ("learned N patterns from M resolved") | Med | M | RET-R4 |

#### Tier E — Features / architectural · higher-risk · own focused sessions
| id | Finding | Sev | Eff | Source(s) |
|---|---|---|---|---|
| FIX-26 | **Seed sample entry + `/board-run SAMPLE`** guided first-win (the ACTIVATION "one change") | High | L | ACT-A2/A3/A4/A6 |
| FIX-27 | **Ungate the learnings loop** (auto-consolidate/promote outside PM mode) — the RETENTION "one hook"; touches Stop-hook procedure + tests | High | L | RET-R1/R2 |
| FIX-28 | Local **`/board-stats`** retention self-instrumentation (reads git + `consolidation.log`) | Med | L | RET-R7 |
| FIX-29 | **Defuse `metrics.csv` landmine** (fix collector perms, or stop committing 0/0/403) | Med | S–M | PROOF-F1 |
| FIX-30 | Local **mode-persistence TTL/reset** for drift | Med | M | RET-R5 |

#### HOLD — needs new design assets (coordinate with SHOWCASE + the deferred COLOR/BRAND residual)
`HOLD-A1` real `board.html` screenshot in hero (SHW-F1, High) · `HOLD-A2` markdown
snippet + **PR-diff proof image** (SHW-F2, High) · `HOLD-A3` passive-capture terminal
GIF (SHW-F3) · `HOLD-A4` **recolor `how-it-works.svg`** to brand + promote above fold
(SHW-F4 — overlaps COLOR F1 / BRAND-COHERENCE) · `HOLD-A5` outcome visuals for
memory/locking (SHW-F5).

#### HOLD — A/B test before shipping (outcome not obvious)
`HOLD-T1` demote the co-equal "View on GitHub" hero CTA (CRO-C4) · FIX-9 (pain cards)
and FIX-12's fairness-note wording are also test candidates.

---

### Dependency map & proposed build order

- **Edit `docs/index.html` / `README.md` once, coherently.** Tiers A + B + C all
  touch the two marketing surfaces; sequence them so each finding is an **isolated
  commit on a distinct region** (one finding per commit, per the brief). The Install
  section is touched by FIX-10/11/14/15/16 — order them so the trust row and the
  clone/prereq lines land as separate, clean diffs.
- **FIX-12 (trust) is downstream of FIX-29 (metrics honesty)** conceptually: don't
  surface any metric while `metrics.csv` reads 0/0/403 — reframe on dogfooding + CI +
  Registry only. If FIX-29 isn't in scope, FIX-12 simply avoids citing traffic stats.
- **HOLD-A4 (recolor SVG) = the deferred COLOR/BRAND residual.** Do it once in an
  assets pass with the other HOLD-A visuals — not piecemeal.
- **Tier E items are each their own session.** FIX-27 (ungate the loop) changes
  Stop-hook routing and will move pinned tokens in `tests/modes/*` and
  `stop-hook-procedure.md` — highest blast radius; never bundle it with copy edits.
  FIX-26 (seed) precedes the strongest activation story but is a real feature.
- **Verification gate (every scope):** `bash tests/run-all.sh` (14 suites) must stay
  green after each commit; Tier A–C copy edits must not touch strings pinned by
  `tests/lint-orchestrator-prompts.sh` or `tests/modes/*`. Tier D edits scripts that
  those suites cover — re-run after each.

---

### Recommended scope — **The Fixer's pick**

**Tiers A + B + C** (FIX-1…FIX-19, holding FIX-9 for A/B). Rationale — *cheapest
high-severity first*:
- **Highest leverage:** clears the biggest **comprehension** (who-it's-for, MCP,
  "fills itself"), **conversion** (free/no-lock-in, install dead-end, prerequisite),
  and **trust** (security cue, dogfooding, CI/Registry) gaps — the findings four of
  the six reports converge on.
- **Lowest risk:** all copy / small-HTML on `docs/index.html` + `README.md` (+ one
  PNG delete); no test-pinned script behavior, no new assets, no architecture.
- **Fully verifiable:** the existing suite stays green; each fix is an isolated commit.

**Defer:** Tier D (in-product copy — medium risk, careful next pass), Tier E (each a
focused session; FIX-27 especially), and both HOLD sets (need design assets / A/B).

---

_Awaiting the operator's scope decision. No product files have been modified. On
answer: create the commits in plan order, run `tests/run-all.sh` after each, and
append the `Fixed` / `Skipped` / `Follow-ups` sections below._

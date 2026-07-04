# PROGRESS — Productize engineering-board

Resumable checklist for the `/goal` productization run. Status: `todo / in-progress / done / blocked`.
Branch: `claude/engineering-board-productize-fu2vvk`. Evidence under `.goal/evidence/`.

_Last updated: 2026-07-04_

## Phase 0 — Audit & product inventory
- [done] 0.1 Repo inventory (langs, entry points, deps, tooling, docs, license, CI)
- [done] 0.2 Build & run locally; `tests/run-all.sh` green (10/10). Evidence: `evidence/G0-test-suite.txt`
- [done] 0.3 Feature enumeration (one-line + code path)
- [done] 0.4 Defect inventory with severity labels (0 blocker, 1 major=MCP build item, 3 minor)
- [done] 0.5 Existing plugin/MCP packaging state (plugin ✅ / MCP ❌ net-new)
- [done] **G0 gate PASSED**: PRODUCT_FACTS.md complete; builds/runs from clean checkout; defects labeled
- Deliverable: `.goal/PRODUCT_FACTS.md` ✅

## Phase 1 — Market research & positioning
- [done] 1.1 Landscape map — 8 competitors, live cited URLs
- [done] 1.2 Distribution-channel map (marketplaces, MCP registries, awesome-lists)
- [done] 1.3 Personas (3) with JTBD
- [done] 1.4 Positioning: category, differentiators, one-liner (9 words), tagline chosen ("The board is the database"), messaging hierarchy (VP1–5 mapped)
- [done] 1.5 Name decision: keep engineering-board (no conflict found)
- [done] 1.6 SEO keyword list + repo topics
- [done] **G1 gate PASSED**: 8 competitors cited; every VP mapped to feature or Phase-2 item; one-liner ≤12 words; naming recorded
- Deliverable: `.goal/POSITIONING.md` ✅

## Phase 2 — Product hardening & dual packaging
- [done] 2.1 Fixed all 3 major defects (D1 runtime stub-lie, D2 stale command map, D3 MCP absent→built); minor D5 doc-lag swept; D4/D6 deferred (justified, low-risk)
- [done] 2.2 VP5 gap closed (MCP server ships the dual-distribution value prop, tested)
- [done] 2.3 Plugin packaging verified vs current docs — `claude plugin validate` passes clean; optional manifest fields added
- [done] 2.4 MCP server packaging — 11 tools, `.mcp.json` bundling, README config snippets (Claude Code + Desktop). Evidence: `evidence/G2-mcp-server-tests.txt`, `evidence/G2-mcp-stdio-handshake.txt`
- [done] 2.5 Testing pyramid + E2E — 65-check MCP suite (subprocess stdio + lifecycle), official MCP Inspector live workflow. Plugin fresh-session E2E partial (see BLOCKERS.md B1 — env limit; covered by validate + suite). Evidence: `evidence/G2-plugin-validate-and-inspector.txt`
- [done] 2.6 CI green — 11 suites incl. mcp-server, enforced by `.github/workflows/test.yml`
- [done] 2.7 Release hygiene: CHANGELOG.md ✅ (semver, Keep-a-Changelog); RC tag `v1.2.0-rc.1` created locally at CI-green `88d4ee6` — remote push blocked by sandbox git relay (BLOCKERS B2, justified/non-blocking)
- [done] **G2 gate PASSED** (with 2 documented deferrals): CI green ✅ (11 suites, both runs on 88d4ee6); MCP Inspector + scripted client ✅; zero blocker/major defects ✅; every VP works ✅. Deferrals: plugin fresh-session E2E (B1) + remote RC tag (B2) — both environment limits, covered by validate + suite / local tag.
- Deliverables: tests ✅, CI ✅, manifests ✅, MCP server ✅, E2E evidence ✅, CHANGELOG ✅, RC tag ✅(local)

## Phase 3 — Brand identity
- [done] 3.1 Three direction studies (Promote / WIP-bars / Monogram); chose "Promote" w/ rationale (BRAND.md §1)
- [done] 3.2 Assets: logomark + wordmark SVG (light/dark), favicon set (svg + 16/32/48/180 png), social preview 1280×640 (svg+png), 3 motifs (columns, card-flow, state-pipeline)
- [done] 3.3 Design tokens file `brand/tokens.css` (colors, type scale, spacing, radii, motion)
- [done] 3.4 BRAND.md (direction, tokens, logo usage, motion, voice, self-review)
- [done] **G3 gate PASSED**: assets in stated formats ✅; all 12 text/bg pairs pass WCAG AA (0 fails) — `evidence/G3-wcag-contrast.txt`; premium/minimal/non-sci-fi self-review ✅; tokens = single source ✅
- Deliverables: `BRAND.md` ✅, `brand/` ✅, `brand/tokens.css` ✅

## Phase 4 — Launch assets: README + landing
- [done] 4.1 README rewrite (themed hero, badges, VP1-5, dual quickstart, feature tour, 11-tool MCP table, cited comparison, arch, roadmap, contributing, MIT). 174 lines; 11/11 suites green.
- [done] 4.2 GitHub Pages landing `docs/index.html` — tokens-styled, themed (auto+toggle), replayable board demo (tdd→review→validate→resolved, prefers-reduced-motion honored), dual CTAs, OG/SEO meta, favicon. `.github/workflows/pages.yml` (deploy-pages from docs/).
- [done] 4.3 `.goal/LAUNCH.md` (description+topics, social preview, release-from-RC steps, per-channel submission map, 2 announcement drafts)
- [done] 4.4 `.goal/FINAL_REPORT.md` (per-phase shipped, evidence links, 4 delegated decisions, deferrals, human follow-ups)
- [done] **G4 gate PASSED**: Lighthouse **100/100/100/100** (≥90 perf / ≥95 a11y-SEO-BP) — `evidence/G4-lighthouse.txt`; all internal links resolve, 3 externals are forward-refs to published state — `evidence/G4-linkcheck.txt`; quickstarts documented (live-verify = B1, post-merge). Pages deploy is post-merge + human Pages-enable.
- Deliverables: README ✅, landing page ✅, `.goal/LAUNCH.md` ✅, `.goal/FINAL_REPORT.md` ✅

## Definition of Done
- [x] G0–G4 passed with evidence (all linked above)
- [~] productize branch merged; default branch green — CI green on branch; **merge = human** (PR #18)
- [~] Release published; both install paths verified — RC tag local (B2); marketplace live, MCP tested; live-verify post-merge (B1)
- [~] Landing page live — built + Lighthouse 100; **Pages enable + deploy = human/post-merge**
- [x] FINAL_REPORT.md written; BLOCKERS.md contains only justified, non-blocking items (B1, B2)

**Run status: all autonomous work complete.** Remaining DoD items (merge, Pages
enable, release push, submissions) require a human GitHub account/UI — prepared
and documented in `.goal/LAUNCH.md` + `.goal/BLOCKERS.md`.

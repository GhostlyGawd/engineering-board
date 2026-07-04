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
- [in-progress] 2.7 Release hygiene: CHANGELOG.md ✅ (semver, Keep-a-Changelog); RC tag pending CI-green confirmation
- [in-progress] **G2 gate**: tests green in CI ✅; MCP Inspector + scripted client ✅; zero blocker/major defects ✅; every VP works ✅; plugin fresh-session E2E = documented partial (B1). RC tag next.
- Deliverables: tests ✅, CI ✅, manifests ✅, MCP server ✅, E2E evidence ✅, CHANGELOG ✅, RC tag ⏳

## Phase 3 — Brand identity
- [ ] 3.1 Three direction studies; select one w/ rationale
- [ ] 3.2 Assets: logo+wordmark SVG (light/dark), favicon set, social preview 1280×640, motifs
- [ ] 3.3 Design tokens file
- [ ] 3.4 BRAND.md
- [ ] **G3 gate**: assets exist; WCAG AA contrast; premium/minimal/non-sci-fi; tokens single source
- Deliverables: `BRAND.md`, `brand/`, tokens file

## Phase 4 — Launch assets: README + landing
- [ ] 4.1 README rewrite (hero, demo, value props, dual quickstart, feature tour, comparison, arch, roadmap, contributing, license)
- [ ] 4.2 GitHub Pages landing (docs/), tokens-styled, interactive element, deployed via Actions
- [ ] 4.3 LAUNCH.md checklist (topics, social preview, release, submissions, announcements)
- [ ] 4.4 FINAL_REPORT.md
- [ ] **G4 gate**: Pages deploys green; Lighthouse ≥90 perf / ≥95 a11y/SEO/BP; links checked; quickstarts verified
- Deliverables: README, landing page, `.goal/LAUNCH.md`, `.goal/FINAL_REPORT.md`

## Definition of Done
- [ ] G0–G4 passed with evidence
- [ ] productize branch merged; default branch green
- [ ] Release published; both install paths verified
- [ ] Landing page live
- [ ] FINAL_REPORT.md written; BLOCKERS.md empty or justified-only

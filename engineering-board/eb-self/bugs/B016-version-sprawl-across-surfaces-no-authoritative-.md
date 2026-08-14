---
id: B016
type: bug
title: Version sprawl across surfaces; no authoritative version signal
discovered: 2026-07-04
status: in_progress
priority: P3
affects: references/required-permissions.json
needs: validate
pattern: [version-drift]
---

## Done when

- [x] `.claude-plugin/plugin.json` is documented and tested as the
  authoritative product-version signal; every shipped release mirror agrees
  with it.
- [x] The unused product-version stamp is removed from
  `references/required-permissions.json` instead of adding another release
  mirror.
- [x] Agent and skill prose does not present worker schemas, compatibility
  history, or milestone labels as the current Engineering Board release.
- [x] Maintained real-fixture checks preserve the product-version boundary
  without changing independent protocol, schema, or data-format versions.

## Observed behavior (Track B F7)
`references/required-permissions.json:2` = 0.2.2 while plugin is 1.2.0; agents carry 0.2.1.2/0.2.2/0.3.0; skills are 0.1.0 frontmatter over 0.2.1 bodies. No surface tells a newcomer which version is authoritative. (Bundle with B004's allowlist rewrite where they overlap.)

## Progress (C1, PR C1b — partial)
`references/required-permissions.json` version stamp aligned to the plugin
version (0.2.2 -> 1.2.0). Remaining sprawl (agent frontmatter 0.2.x, skills
0.1.0) still open — sweep with the docs-coherence PR. Kept open (P3).

## Why still open (P3, deferred)
The required-permissions.json stamp is aligned (done in C1b). The remaining sprawl is agent/skill frontmatter version stamps (agents 0.2.x, skills 0.1.0). Deferred: these frontmatter fields are lightly load-bearing (some modes lints read frontmatter) and a bulk realignment is a mechanical sweep better done as its own small PR to avoid coupling with substantive fixes. No user impact — purely a maintainer-legibility polish. Revisit in a later cycle.

## Comments

- **codex** 2026-08-14T16:27:41Z: Claimed for dogfood after B022. Scope: inventory live version consumers, define the authoritative signal on current 1.12.0 main, and add a real-fixture guard before reconciling or removing redundant stamps.
- **codex** 2026-08-14T16:38:51Z: Authoritative version semantics are implemented and evidence-bounded. Red: version guard found 10 gaps and the PM-agent contract found 1. Green: version guard passes at 1.12.0, modes 6/6, permissions 29/29, release preparation 11/11, maintained suite 21/21. Implementation pull request and merged-main evidence remain pending.

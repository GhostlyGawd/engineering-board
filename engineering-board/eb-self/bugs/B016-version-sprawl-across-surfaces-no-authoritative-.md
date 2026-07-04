---
id: B016
type: bug
title: Version sprawl across surfaces; no authoritative version signal
discovered: 2026-07-04
status: open
priority: P3
affects: references/required-permissions.json
needs: tdd
pattern: [version-drift]
---

## Done when
- Surface version stamps are reconciled to a single authoritative source (plugin.json = 1.2.0) or the stray version frontmatter is removed where it serves no purpose.

## Observed behavior (Track B F7)
`references/required-permissions.json:2` = 0.2.2 while plugin is 1.2.0; agents carry 0.2.1.2/0.2.2/0.3.0; skills are 0.1.0 frontmatter over 0.2.1 bodies. No surface tells a newcomer which version is authoritative. (Bundle with B004's allowlist rewrite where they overlap.)

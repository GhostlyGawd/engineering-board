---
id: B033
type: bug
title: worker-start unsupported-discipline error leaks a version number to the user
discovered: 2026-07-04
status: resolved
priority: P3
affects: commands/worker-start.md
needs: tdd
pattern: [jargon-leak, version-drift]
---

## Done when
- The unsupported-discipline error message no longer names an internal version (e.g. drop "v0.2.2 ships disciplines:").

## Observed behavior (C2 Track B — P3)
`commands/worker-start.md:20` error still reads "... v0.2.2 ships disciplines: tdd, review, validate ...". Adjacent to B016 version-stamp cleanup.

## Resolution (C2, PR C2d)
worker-start unsupported-discipline error no longer names 'v0.2.2' — now 'supported disciplines: tdd, review, validate.'

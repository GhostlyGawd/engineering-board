---
id: B031
type: bug
title: Stale suite/file counts across README and ARCHITECTURE after C1
discovered: 2026-07-04
status: open
priority: P3
affects: README.md
needs: tdd
pattern: [doc-drift, count-mismatch]
---

## Done when
- README:167 Contributing block says 13 suites (not 11).
- ARCHITECTURE §10 header + table reconciled with §2 (13 suites; add the session-start row; drop/relabel spike which is not a run-all suite).
- ARCHITECTURE's "11 orchestrator-facing prompt files" corrected to 10 (matches tests/lint-orchestrator-prompts.sh FILES array + state.md).

## Observed behavior (C2 Track D)
C1's coherence fix updated the ARCHITECTURE §2 tree to 13 suites but missed README:167 ("11 suites") and left §10 at "8 domains" (omits session-start, lists spike). The 11-vs-10 prompt-file count is pre-existing (predates C1) but folds into this cleanup.

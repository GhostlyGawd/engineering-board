---
id: B045
type: bug
title: CHANGELOG Unreleased reject-filter fixture counts stale + self-contradictory
discovered: 2026-07-04
status: resolved
priority: P3
affects: CHANGELOG.md
needs: tdd
pattern: [doc-drift, count-mismatch]
---

## Done when
- The CHANGELOG [Unreleased] no longer hardcodes brittle exact fixture/check counts that drift as the corpus grows (the B031/B032 recurrence).

## Observed behavior (C5 Track D — LOW)
Three inconsistent stale figures: "65 checks (40 adversarial + 25 benign)", "adversarial-paste (40) and benign-findings (25)", and "then-50-fixture corpus (now 60)" — none matched the real 73/46/27, and 60 vs 65 self-contradicted.

## Resolution (C5, PR C5b)
Removed the brittle exact counts from the [Unreleased] entries (now "the reject-filter corpus grows with every pinned bypass" / "adversarial-paste and benign-findings fixture corpus") to stop the recurrence — mirroring how ARCHITECTURE §10 uses bounds. The shipped 1.2.0 "65 checks" line is historically correct and left as-is.

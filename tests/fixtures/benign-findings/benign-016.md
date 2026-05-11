---
id: benign-016
expect: accept
---

# F063 — allow operators to disregard rate-limit warnings during the backfill window

- type: feature
- affects: src/ops/backfill.py
- evidence_quote: "allow operators to disregard rate-limit warnings during the backfill window via a documented escape hatch"
- discovered: 2026-05-08
- tags: [ops, backfill, rate-limit]

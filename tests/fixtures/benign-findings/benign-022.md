---
id: benign-022
expect: accept
---

# F088 — let operators reset the cursor without a full re-index

- type: feature
- affects: services/indexer/cursor.py
- evidence_quote: "operators want a documented way to reset the cursor without a full re-index of the corpus"
- discovered: 2026-07-04
- tags: [indexer, cursor, reset-flag]

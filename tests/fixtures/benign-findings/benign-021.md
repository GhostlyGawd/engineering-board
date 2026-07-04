---
id: benign-021
expect: accept
---

# B121 — the migrator will remove orphaned rows during the sweep

- type: bug
- affects: src/db/migrator.py
- evidence_quote: "the migrator will remove orphaned rows during the nightly sweep, which drops referential integrity"
- discovered: 2026-07-04
- tags: [db, migration, remove-behavior]

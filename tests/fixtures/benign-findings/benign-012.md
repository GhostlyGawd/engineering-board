---
id: benign-012
expect: accept
---

# B078 — migrations run twice when the lock file is held by a stale process

- type: bug
- affects: src/db/migrate.py
- evidence_quote: "migrations run twice when the lock file is held by a stale process that has not released it cleanly"
- discovered: 2026-05-08
- tags: [migrations, locking, bug]

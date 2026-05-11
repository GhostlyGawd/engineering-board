---
id: benign-008
expect: accept
---

# Q024 — should the importer replace existing rows or skip duplicates by default?

- type: question
- affects: src/import/loader.py
- evidence_quote: "should the importer replace existing rows or skip duplicates by default when no merge strategy is supplied"
- discovered: 2026-05-08
- tags: [import, merge-policy, question]

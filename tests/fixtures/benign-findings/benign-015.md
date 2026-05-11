---
id: benign-015
expect: accept
---

# B092 — schema validator does not replace deprecated field names before validation runs

- type: bug
- affects: src/schema/validate.py
- evidence_quote: "the schema validator does not replace deprecated field names before validation runs, so legacy payloads fail"
- discovered: 2026-05-08
- tags: [schema, deprecation, validation]

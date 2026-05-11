---
id: benign-020
expect: accept
---

# B107 — the deduper will replace canonical IDs with later-arriving duplicates under high contention

- type: bug
- affects: src/dedupe/canonical.py
- evidence_quote: "the deduper will replace canonical IDs with later-arriving duplicates under high contention on the write path"
- discovered: 2026-05-08
- tags: [dedupe, contention, bug]

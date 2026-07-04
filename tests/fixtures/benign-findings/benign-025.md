---
id: benign-025
expect: accept
---

# B140 — now the print statement in the logger leaks PII to stdout

- type: bug
- affects: src/logging/logger.py
- evidence_quote: "now the print statement in the logger leaks PII to stdout on every request; a legit bug about print/leak must still promote"
- discovered: 2026-07-04
- tags: [logging, pii, print]

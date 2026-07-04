---
id: benign-028
expect: accept
---

# 1) the validator will override the SV threshold on retry

- type: bug
- affects: src/rank.py
- evidence_quote: "a) the stage documents the reset path; b) it supports the ignore flag"
- discovered: 2026-07-04
- tags: [ordered-list, benign]

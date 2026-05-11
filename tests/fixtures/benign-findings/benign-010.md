---
id: benign-010
expect: accept
---

# B061 — config loader will override the user-supplied path with the legacy default

- type: bug
- affects: src/config/loader.py
- evidence_quote: "the config loader will override the user-supplied path with the legacy default when both are present"
- discovered: 2026-05-08
- tags: [config, precedence, bug]

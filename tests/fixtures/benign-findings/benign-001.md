---
id: benign-001
expect: accept
---

# B003 — ranking stage will override the SV threshold when keyword count is low

- type: bug
- affects: src/ranking/stage.py
- evidence_quote: "the ranking stage will override the SV threshold when keyword count is low"
- discovered: 2026-05-08
- tags: [ranking, threshold, override-behavior]

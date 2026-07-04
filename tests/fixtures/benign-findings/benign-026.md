---
id: benign-026
expect: accept
---

# B150 — bulleted finding must still promote

- type: bug
- affects: src/ranking/stage.py
- evidence_quote: "- the ranking stage will override the SV threshold when keyword count is low; a legit bulleted finding must still promote"
- discovered: 2026-07-04
- tags: [ranking, markdown-bullet, override-behavior]

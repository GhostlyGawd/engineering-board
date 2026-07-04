---
id: benign-027
expect: accept
---

# B160 — unicode-bulleted finding must still promote

- type: bug
- affects: src/ranking/stage.py
- evidence_quote: "• the ranking stage will override the SV threshold when keyword count is low; a legit unicode-bulleted finding must still promote"
- discovered: 2026-07-04
- tags: [ranking, unicode-bullet, override-behavior]

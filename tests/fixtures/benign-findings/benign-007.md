---
id: benign-007
expect: accept
---

# B045 — the retry handler will execute a stale payload when the queue is repopulated mid-flight

- type: bug
- affects: src/queue/retry.py
- evidence_quote: "the retry handler will execute a stale payload when the queue is repopulated mid-flight"
- discovered: 2026-05-08
- tags: [retry, queue, race-condition]

---
id: benign-014
expect: accept
---

# O083 — production logs show the worker will execute idempotent writes twice on reconnect

- type: observation
- affects: src/worker/reconnect.py
- evidence_quote: "production logs show the worker will execute idempotent writes twice on reconnect to the broker"
- discovered: 2026-05-08
- tags: [worker, idempotency, observation]

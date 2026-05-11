---
id: benign-017
expect: accept
---

# Q049 — would it be safer to ignore retries on 5xx than to add aggressive backoff?

- type: question
- affects: src/client/retry.py
- evidence_quote: "would it be safer to ignore retries on 5xx than to add aggressive backoff to the existing handler"
- discovered: 2026-05-08
- tags: [retry, http, design-question]

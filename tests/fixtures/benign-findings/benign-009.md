---
id: benign-009
expect: accept
---

# O057 — the test harness appears to ignore custom xdist worker counts on Windows

- type: observation
- affects: tests/conftest.py
- evidence_quote: "the test harness appears to ignore custom xdist worker counts on Windows runners; CI logs show only 2 workers"
- discovered: 2026-05-08
- tags: [tests, xdist, windows]

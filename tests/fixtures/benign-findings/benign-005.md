---
id: benign-005
expect: accept
---

# B019 — observed: the cache fails to forget stale entries after TTL

- type: bug
- affects: src/cache/ttl.py
- evidence_quote: "the cache fails to forget stale entries after TTL expiry; we see entries from 6h ago still served"
- discovered: 2026-05-08
- tags: [cache, ttl, eviction]

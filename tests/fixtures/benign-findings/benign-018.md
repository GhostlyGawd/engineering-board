---
id: benign-018
expect: accept
---

# O099 — under load the planner appears to forget previously pinned shards

- type: observation
- affects: src/planner/shard.py
- evidence_quote: "under load the planner appears to forget previously pinned shards and re-plans them onto cold nodes"
- discovered: 2026-05-08
- tags: [planner, sharding, observation]

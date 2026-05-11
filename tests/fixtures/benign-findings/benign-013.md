---
id: benign-013
expect: accept
---

# Q031 — can we invoke the validator from the precommit hook without slowing it down?

- type: question
- affects: hooks/precommit.sh
- evidence_quote: "can we invoke the validator from the precommit hook without slowing it down beyond a few hundred ms"
- discovered: 2026-05-08
- tags: [precommit, validator, performance]

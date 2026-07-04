---
id: L001
type: learning
subtype: principle
title: Ship every deterministic guard with a test that drives its real fixtures and call-sites
discovered: 2026-07-04
confidence: high
recurrence: 3
derived_from: [B002, B003, B004]
applies_to: [hooks/scripts/, tests/, references/]
pattern_tag: untested-claim
---

## Takeaway
A deterministic safeguard (injection filter, permission allowlist, invariant
check) is only as good as the test that exercises it against its *real* inputs.
Three C1 P1s shared one root cause: a guard existed but nothing drove it end to
end. The reject filter shipped trivially bypassable because its 50-fixture
corpus had no CI consumer; the permission manifest missed the scripts the hooks
actually invoke because no test compared the allowlist to the real call-sites;
the ARCHITECTURE "100% reject-rate" guarantee was never measured. If a guard
makes a claim, a test must assert that claim against the same fixtures/call-sites
the guard runs on in production — otherwise the claim rots silently.

## Sources
- B002 — injection reject-blocklist bypassable; hardened + made single-source.
- B003 — adversarial/benign fixtures were dead code; wired into CI as `reject-filter`.
- B004 — permission allowlist didn't cover invoked scripts; added a coverage test.

## When this applies
Whenever adding or changing a deterministic filter, validator, allowlist, or
invariant check under `hooks/scripts/`. Pair the change with a test that (a)
feeds the guard its real fixture corpus, or (b) parses the actual call-sites and
asserts coverage. A "defense-in-depth" layer with no test is decorative.

---
id: B003
type: bug
title: Adversarial/benign fixtures are dead code; ARCHITECTURE claims a reject-rate guarantee
discovered: 2026-07-04
status: open
priority: P1
affects: tests/smoke/automated.sh
needs: tdd
pattern: [untested-claim, test-coverage-gap]
---

## Done when
- A test suite feeds every `tests/fixtures/adversarial-paste/*` (30) and `tests/fixtures/benign-findings/*` (20) through the real reject path and asserts each fixture's `expect:` outcome.
- The suite is registered in `tests/run-all.sh` and enforced by CI.
- `ARCHITECTURE.md:244`'s "100% reject-rate / >=95% accept-rate" claim is either backed by this suite or removed.

## Observed behavior
`grep -rn adversarial tests/*.sh` and `grep -rn benign tests/*.sh` return nothing — no script consumes the 50 fixtures. `tests/smoke/automated.sh` uses inline `S-test-1..10`. The advertised reject/accept rates are never measured; given B002 the claimed 100% reject rate is false for realistic inputs. This suite would also have caught B002.

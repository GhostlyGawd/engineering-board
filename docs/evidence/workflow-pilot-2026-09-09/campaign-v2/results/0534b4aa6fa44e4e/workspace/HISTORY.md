# Synthetic repository history

This is a synthetic evaluation fixture, not customer or real held-out evidence.
The following record and source facts are semantically identical to the board
condition. The history representation has no board frontmatter or tool index.

## L101: Verify sibling option consumers while respecting each option contract

Record kind: learning; subtype: principle.
Recorded: 2026-09-08. Confidence: high.
Relevant implementation: job_options.py. Derived from: B101, B102.
Prior recurrence: 2.

Synthetic evaluation fixture; not customer or real held-out evidence.

## Takeaway

When a false-valued option is lost at a defaulting boundary, enumerate readers
of that same option and test them through their actual entry points. Compare
each option's documented sentinel values before reusing a replacement across
different options. A zero may be a meaningful setting in one contract and a
request for a service default in another.

## When this applies

Apply this procedure to option-default repairs and sibling readers of the same
option. Do not assume every use of `or default` is a defect.

## Sources

- B101: Prior budget preview missed an explicit zero.
- B102: Prior cooldown sweep changed a heartbeat sentinel.

## B101: Prior budget preview missed an explicit zero

Kind: bug. Status: resolved. Priority: P2.
Discovered: 2026-09-08. Affects: job_options.py.

## Observation

Synthetic evaluation fixture; not customer or real held-out evidence.

A prior synthetic job-option repair preserved a zero budget in execution, but
preview still substituted the default. Checking execution alone missed the
second consumer. This prior repair concerned budget, not the current retries
report.

## B102: Prior cooldown sweep changed a heartbeat sentinel

Kind: bug. Status: resolved. Priority: P2.
Discovered: 2026-09-08. Affects: job_options.py.

## Observation

Synthetic evaluation fixture; not customer or real held-out evidence.

A prior synthetic cleanup replaced all truthy defaults in job_options.py.
The documented heartbeat=0 service-default behavior regressed. The correction
limited the change by each option's sentinel contract.

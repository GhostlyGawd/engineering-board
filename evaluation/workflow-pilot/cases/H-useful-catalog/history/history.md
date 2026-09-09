# Synthetic repository history

This is a synthetic evaluation fixture, not customer or real held-out evidence.
The following record and source facts are semantically identical to the board
condition. The history representation has no board frontmatter or tool index.

## H101: Read-only catalog views may reorder the caller's shared sequence

Record kind: hypothesis; status: proposed.
Recorded: 2026-09-08. Confidence: medium.
Relevant implementation: catalog.py. Derived from: B105, B106.

## Proposed root cause

Synthetic evaluation fixture; not customer or real held-out evidence.

The newest-items and owner views may reorder the caller-owned sequence in
place, so opening either view changes later exports. This is a proposed
mechanism, not a confirmed diagnosis.

## Supporting evidence

- B105: Newest-items view precedes a changed export order.
- B106: Owner view precedes a changed later report order.

## Alternative explanations

Export may independently choose a different ordering, or a view cache may
return obsolete ids without changing the caller's sequence.

## Counter-evidence

No decisive check is recorded; the alternatives remain open.

## Confidence basis

Two synthetic reports associate order changes with opening different views.
No mutation instrumentation or patch outcome has yet been recorded.

## Falsifier

Snapshot the caller sequence immediately before and after each view, then
export without reopening a view. If neither view changes the sequence while
the failure reproduces, the proposed shared-mutation mechanism is falsified.

## Outcome history

- 2026-09-08: status proposed; evidence [B105, B106]; synthetic authoring only; no fix outcome or confirmation.

## B105: Newest-items view precedes a changed export order

Kind: bug. Status: open. Priority: P2.
Discovered: 2026-09-08. Affects: catalog.py.

## Observation

Synthetic evaluation fixture; not customer or real held-out evidence.

In a synthetic reproduction, catalog export followed import order before
newest_ids was called, then returned the same ids in a different order.
No storage refresh happened between the two exports.

## B106: Owner view precedes a changed later report order

Kind: bug. Status: open. Priority: P2.
Discovered: 2026-09-08. Affects: catalog.py.

## Observation

Synthetic evaluation fixture; not customer or real held-out evidence.

A synthetic report observed a changed export order after opening owner_ids.
The owner view itself displayed the expected sorted ids. The report did not
capture the sequence before and after the call.

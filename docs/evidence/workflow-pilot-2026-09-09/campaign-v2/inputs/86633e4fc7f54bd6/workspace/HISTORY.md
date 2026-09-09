# Synthetic repository history

This is a synthetic evaluation fixture, not customer or real held-out evidence.
The following record and source facts are semantically identical to the board
condition. The history representation has no board frontmatter or tool index.

## L102: Use decimal half-up rounding at commercial display boundaries

Record kind: learning; subtype: principle.
Recorded: 2026-09-08. Confidence: high.
Relevant implementation: readings.py. Derived from: B103, B104.
Prior recurrence: 2.

Synthetic evaluation fixture; not customer or real held-out evidence.

## Takeaway

When repairing currency displays, inspect all commercial amount renderers,
round exact decimal values using Decimal and ROUND_HALF_UP, and test positive
and negative midpoint values. The prior failure came from treating commercial
rounding as ordinary Python float display.

## When this applies

This procedure applies to commercial currency display in payment_receipt.
It does not prescribe rounding for sensor measurements, ingestion, or
scientific summaries. Those contracts require independent inspection.

## Sources

- B103: Receipt midpoint rounding violated commercial display.
- B104: Refund receipt needed a negative midpoint regression.

## B103: Receipt midpoint rounding violated commercial display

Kind: bug. Status: resolved. Priority: P2.
Discovered: 2026-09-08. Affects: readings.py.

## Observation

Synthetic evaluation fixture; not customer or real held-out evidence.

A prior synthetic receipt displayed decimal currency 1.125 as 1.12 rather than
the required 1.13. The repair introduced Decimal half-up rounding specifically
in payment_receipt in readings.py.

## B104: Refund receipt needed a negative midpoint regression

Kind: bug. Status: resolved. Priority: P2.
Discovered: 2026-09-08. Affects: readings.py.

## Observation

Synthetic evaluation fixture; not customer or real held-out evidence.

A prior synthetic refund display lacked a negative midpoint check.
The corrected payment_receipt renders -1.125 as -1.13. Sensor summaries retain
their separate Python float-format contract.

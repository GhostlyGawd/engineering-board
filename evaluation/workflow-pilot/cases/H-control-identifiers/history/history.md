# Synthetic repository history

This is a synthetic evaluation fixture, not customer or real held-out evidence.
The following record and source facts are semantically identical to the board
condition. The history representation has no board frontmatter or tool index.

## H102: Import and lookup failures may share identifier normalization

Record kind: hypothesis; status: proposed.
Recorded: 2026-09-08. Confidence: medium.
Relevant implementation: parts.py. Derived from: B107, B108.

## Proposed root cause

Synthetic evaluation fixture; not customer or real held-out evidence.

CSV import rejection and prefix-adjacent lookup confusion may both arise
because import and query paths apply inconsistent normalization to part ids.
This is a plausible proposed mechanism, not a confirmed diagnosis.

## Supporting evidence

- B107: CSV rejects a P7 record with an optional description.
- B108: P7 query retrieves a neighboring identifier.

## Alternative explanations

CSV field handling and lookup match semantics may be independent defects
that happen to affect records with the same id.

## Counter-evidence

No decisive check is recorded; the alternatives remain open.

## Confidence basis

The two synthetic reports both mention P7, but no trace demonstrates a shared
normalization stage. Exact case and whitespace are part of the current API.

## Falsifier

Hold the identifier bytes constant while varying an empty description, and
query constructed records directly without importing them. If each failure
depends on its own non-normalization operation, the shared normalization
explanation is falsified.

## Outcome history

- 2026-09-08: status proposed; evidence [B107, B108]; synthetic authoring only; no fix outcome or confirmation.

## B107: CSV rejects a P7 record with an optional description

Kind: bug. Status: open. Priority: P2.
Discovered: 2026-09-08. Affects: parts.py.

## Observation

Synthetic evaluation fixture; not customer or real held-out evidence.

A synthetic report says import_row("P7,,4") raises ValueError although the
description is optional. The report does not establish whether identifier
handling or another part of row parsing caused rejection.

## B108: P7 query retrieves a neighboring identifier

Kind: bug. Status: open. Priority: P2.
Discovered: 2026-09-08. Affects: parts.py.

## Observation

Synthetic evaluation fixture; not customer or real held-out evidence.

A synthetic report says querying P7 can retrieve a P70 record. The caller
supplied records directly; the report does not establish a common import
dependency or any normalization behavior.

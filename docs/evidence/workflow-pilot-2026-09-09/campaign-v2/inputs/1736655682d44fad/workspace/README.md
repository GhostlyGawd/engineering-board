# Catalog helpers

This synthetic Python module provides views of imported catalog rows. Each row
has `id`, `created`, and `owner` fields. The caller owns the input sequence.
All functions are read-only and leave that sequence and its rows unchanged.

## API

- `export_ids(rows)` returns ids in original import order.
- `newest_ids(rows)` returns ids in descending creation-time order.
  Equal creation times retain their input order.
- `owner_ids(rows, owner)` returns that owner's ids in ascending id order.
  It returns an empty list if no rows match.
- `recent_ids(rows, minimum)` returns ids whose creation time is at least
  `minimum`, in import order.

An empty input produces an empty list. Views may be requested in any order.

Run tests with `python3 -m unittest discover -s tests -v`.

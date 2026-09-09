# Job option helpers

This synthetic Python module provides job execution, preview, and heartbeat
settings. It has no external dependencies.

## API

- `execution_options(options)` returns a dictionary with `retries` and `queue`.
  Missing or `None` retries select 3; a nonnegative integer is used as supplied.
  Zero retries means the job is attempted once with no retry. The queue is
  supplied by the caller, or `"default"` when omitted.
- `preview_options(options)` returns `{"attempts": n}`, where `n` is the total
  number of attempts represented by the job's retries setting. Missing or
  `None` retries select 3.
- `heartbeat_seconds(options)` returns the requested heartbeat interval.
  Missing, `None`, or zero heartbeat select the 30-second service default.
  A positive interval is returned as supplied.

Run tests with `python3 -m unittest discover -s tests -v`.

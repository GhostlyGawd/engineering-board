# Correct two part lookup failures
CSV import rejects a valid row with an empty optional description: "P7,,4".
Separately, querying part "P7" sometimes returns the "P70" record.
Investigate and repair both reported failures.
Use Python's standard library only. You may change parts.py and add tests.
Run: python3 -m unittest discover -s tests -v

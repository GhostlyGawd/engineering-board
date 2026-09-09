# Correct two part lookup failures
CSV import rejects a valid row with an empty optional description: "P7,,4".
Separately, querying part "P7" sometimes returns the "P70" record.
Repair both failures while preserving the exact-identifier and CSV contracts.
Use Python's standard library only. You may change parts.py and add tests.
Run: python3 -m unittest discover -s tests -v

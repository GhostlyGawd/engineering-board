# Preserve a zero retry setting
A job submitted with {"retries": 0} is unexpectedly retried three times.
Investigate and repair the reported behavior.
Use Python's standard library only. You may change job_options.py and add tests.
Run: python3 -m unittest discover -s tests -v

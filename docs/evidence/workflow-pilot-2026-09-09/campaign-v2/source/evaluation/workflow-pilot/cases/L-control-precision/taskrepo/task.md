# Keep fractional sensor readings
A sensor value "2.75" is returned as 2.0 by the live ingestion path.
Investigate and repair the reported behavior.
Use Python's standard library only. You may change readings.py and add tests.
Run: python3 -m unittest discover -s tests -v

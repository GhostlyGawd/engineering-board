# Keep fractional sensor readings
A sensor value "2.75" is returned as 2.0 by the live ingestion path.
Repair fractional precision loss and check replay ingestion, which supports
the same input values. Preserve the distinct display contracts in this module.
Use Python's standard library only. You may change readings.py and add tests.
Run: python3 -m unittest discover -s tests -v

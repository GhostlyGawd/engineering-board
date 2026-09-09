# Read-only catalog views must preserve export order
Export returns rows in import order until the newest-items view is opened;
afterward export order changes. Repair the read-only view behavior and check
the other supported catalog views. Keep each view's advertised result ordering.
Use Python's standard library only. You may change catalog.py and add tests.
Run: python3 -m unittest discover -s tests -v

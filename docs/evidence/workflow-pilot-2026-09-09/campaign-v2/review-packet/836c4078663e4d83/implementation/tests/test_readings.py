import unittest

from readings import ingest_live


class LiveIngestionTests(unittest.TestCase):
    def test_preserves_positive_fractional_reading(self):
        self.assertEqual(ingest_live("2.75"), 2.75)

    def test_preserves_negative_fractional_reading(self):
        self.assertEqual(ingest_live("-2.75"), -2.75)


if __name__ == "__main__":
    unittest.main()

import unittest

from readings import ingest_live, ingest_replay


class IngestionRegressionTests(unittest.TestCase):
    def test_live_reading_keeps_fractional_component(self):
        self.assertEqual(ingest_live("2.75"), 2.75)

    def test_live_reading_keeps_negative_fractional_component(self):
        self.assertEqual(ingest_live("-2.75"), -2.75)

    def test_replay_reading_keeps_fractional_component(self):
        self.assertEqual(ingest_replay("2.75"), 2.75)


if __name__ == "__main__":
    unittest.main()

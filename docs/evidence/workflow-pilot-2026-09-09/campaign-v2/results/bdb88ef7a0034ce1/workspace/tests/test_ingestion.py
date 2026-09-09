import unittest

from readings import ingest_live, ingest_replay


class IngestionRegressionTests(unittest.TestCase):
    def test_replay_preserves_fraction(self):
        self.assertEqual(ingest_replay("2.75"), 2.75)

    def test_ingestion_preserves_supported_float_syntax(self):
        for ingest in (ingest_live, ingest_replay):
            with self.subTest(ingest=ingest.__name__):
                self.assertEqual(ingest("  -2.75e1  "), -27.5)


if __name__ == "__main__":
    unittest.main()

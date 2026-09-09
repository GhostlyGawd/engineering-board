import unittest
from readings import ingest_live, ingest_replay, sensor_summary, payment_receipt

class PublicTests(unittest.TestCase):
    def test_live_fraction(self):
        self.assertEqual(ingest_live("2.75"), 2.75)
    def test_whole_reading(self):
        self.assertEqual(ingest_replay("4"), 4.0)
    def test_displays(self):
        self.assertEqual(sensor_summary(3.5), "3.50")
        self.assertEqual(payment_receipt("1.125"), "1.13")

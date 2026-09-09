import unittest
from job_options import execution_options, preview_options, heartbeat_seconds

class PublicTests(unittest.TestCase):
    def test_explicit_no_retry(self):
        self.assertEqual(execution_options({"retries": 0})["retries"], 0)
    def test_defaults(self):
        self.assertEqual(execution_options({})["retries"], 3)
        self.assertEqual(preview_options({}), {"attempts": 4})
        self.assertEqual(heartbeat_seconds({}), 30)

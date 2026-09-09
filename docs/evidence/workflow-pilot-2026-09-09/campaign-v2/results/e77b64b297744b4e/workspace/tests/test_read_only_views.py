import unittest

from catalog import export_ids, newest_ids, owner_ids


class ReadOnlyViewTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"id": "z", "created": 1, "owner": "a"},
            {"id": "b", "created": 3, "owner": "a"},
            {"id": "c", "created": 3, "owner": "b"},
        ]

    def test_newest_view_preserves_export_order_and_stable_ties(self):
        self.assertEqual(newest_ids(self.rows), ["b", "c", "z"])
        self.assertEqual(export_ids(self.rows), ["z", "b", "c"])

    def test_owner_view_preserves_export_order(self):
        self.assertEqual(owner_ids(self.rows, "a"), ["b", "z"])
        self.assertEqual(export_ids(self.rows), ["z", "b", "c"])


if __name__ == "__main__":
    unittest.main()

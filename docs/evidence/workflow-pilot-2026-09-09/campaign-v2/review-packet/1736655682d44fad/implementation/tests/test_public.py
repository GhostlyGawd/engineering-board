import unittest
from catalog import export_ids, newest_ids, owner_ids

class PublicTests(unittest.TestCase):
    def setUp(self):
        self.rows = [{"id": "z", "created": 1, "owner": "a"},
                     {"id": "b", "created": 3, "owner": "a"},
                     {"id": "c", "created": 2, "owner": "b"}]
    def test_newest_order(self):
        self.assertEqual(newest_ids(self.rows), ["b", "c", "z"])
    def test_export_after_newest(self):
        newest_ids(self.rows)
        self.assertEqual(export_ids(self.rows), ["z", "b", "c"])

    def test_newest_preserves_tie_order_without_mutating_rows(self):
        rows = [{"id": "first", "created": 2, "owner": "a"},
                {"id": "old", "created": 1, "owner": "b"},
                {"id": "second", "created": 2, "owner": "c"}]
        original_rows = list(rows)

        self.assertEqual(newest_ids(rows), ["first", "second", "old"])
        self.assertEqual(rows, original_rows)

    def test_owner_order(self):
        self.assertEqual(owner_ids(self.rows, "a"), ["b", "z"])

    def test_export_after_owner(self):
        owner_ids(self.rows, "a")
        self.assertEqual(export_ids(self.rows), ["z", "b", "c"])

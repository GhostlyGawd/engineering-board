import unittest
from parts import import_row, find_part

class PublicTests(unittest.TestCase):
    def test_optional_description(self):
        self.assertEqual(import_row("P7,,4"), {"id": "P7", "description": "", "quantity": 4})
    def test_exact_lookup(self):
        rows = [{"id": "P70"}, {"id": "P7"}]
        self.assertEqual(find_part(rows, "P7"), {"id": "P7"})
    def test_regular_import(self):
        self.assertEqual(import_row("Q2,bolt,8")["quantity"], 8)

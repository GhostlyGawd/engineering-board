import unittest

from parts import find_part, import_row


class ImportRowRegressionTests(unittest.TestCase):
    def test_empty_description_is_preserved_as_a_column(self):
        self.assertEqual(
            import_row("P7,,4"),
            {"id": "P7", "description": "", "quantity": 4},
        )

    def test_quoted_description_may_contain_a_comma(self):
        self.assertEqual(import_row('P7,"large, blue",4')["description"], "large, blue")


class FindPartRegressionTests(unittest.TestCase):
    def test_prefix_neighbor_is_not_an_exact_match(self):
        records = [{"id": "P70"}, {"id": "P7"}]
        self.assertIs(find_part(records, "P7"), records[1])

    def test_prefix_only_match_is_absent(self):
        self.assertIsNone(find_part([{"id": "P70"}], "P7"))


if __name__ == "__main__":
    unittest.main()

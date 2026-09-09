import unittest

from parts import find_part, import_row


class ImportRowRegressionTests(unittest.TestCase):
    def test_empty_description_remains_the_second_column(self):
        self.assertEqual(
            import_row("P7,,4"),
            {"id": "P7", "description": "", "quantity": 4},
        )

    def test_quoted_description_with_comma_is_unchanged(self):
        self.assertEqual(
            import_row('P7,"washer, zinc",4'),
            {"id": "P7", "description": "washer, zinc", "quantity": 4},
        )


class FindPartRegressionTests(unittest.TestCase):
    def test_prefix_record_does_not_shadow_exact_match(self):
        records = [{"id": "P70"}, {"id": "P7"}]
        self.assertIs(find_part(records, "P7"), records[1])

    def test_prefix_only_is_absent(self):
        self.assertIsNone(find_part([{"id": "P70"}], "P7"))

    def test_match_remains_case_sensitive(self):
        self.assertIsNone(find_part([{"id": "p7"}], "P7"))


if __name__ == "__main__":
    unittest.main()

import unittest

from parts import find_part, import_row


class ImportRowRegressionTests(unittest.TestCase):
    def test_empty_optional_description_keeps_column_position(self):
        self.assertEqual(
            import_row("P7,,4"),
            {"id": "P7", "description": "", "quantity": 4},
        )

    def test_quoted_comma_still_parses_as_one_description(self):
        self.assertEqual(import_row('P7,"nut, bolt",4')["description"], "nut, bolt")


class FindPartRegressionTests(unittest.TestCase):
    def test_prefix_record_does_not_shadow_exact_match(self):
        records = [{"id": "P70"}, {"id": "P7"}]
        self.assertIs(find_part(records, "P7"), records[1])

    def test_prefix_only_is_absent(self):
        self.assertIsNone(find_part([{"id": "P70"}], "P7"))

    def test_matching_remains_case_and_whitespace_sensitive(self):
        records = [{"id": "p7"}, {"id": " P7 "}, {"id": "P7"}]
        self.assertIs(find_part(records, "P7"), records[2])


if __name__ == "__main__":
    unittest.main()

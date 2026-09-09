# Part import and lookup

This synthetic Python module imports individual CSV records and queries part
records. It has no external dependencies.

## API

- `import_row(text)` accepts one CSV record containing exactly three columns:
  id, description, and integer quantity. Description may be empty. Standard
  CSV quoted commas are supported. The returned dictionary contains `id`,
  `description`, and `quantity`, with quantity converted to an integer.
  Negative quantities are allowed. Wrong column counts raise `ValueError`.
- `find_part(records, part_id)` returns the first record with the exact
  requested id, or `None` when absent. It returns the record itself.

Ids preserve whitespace and case. Import and lookup both treat those bytes
as meaningful; for example, `"P7"`, `"p7"`, and `" P7 "` are distinct ids.

Run tests with `python3 -m unittest discover -s tests -v`.

"""Import and query part records."""
import csv


def import_row(text):
    """One CSV record: exact id, optional description, integer quantity.
    Quoted commas are supported. Preserve id whitespace and case.
    """
    cells = next(csv.reader([text]))
    if len(cells) != 3:
        raise ValueError("expected three columns")
    return {"id": cells[0], "description": cells[1], "quantity": int(cells[2])}


def find_part(records, part_id):
    """Exact, case-sensitive id match, including whitespace; None if absent."""
    for record in records:
        if record["id"] == part_id:
            return record
    return None

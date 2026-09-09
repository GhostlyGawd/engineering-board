"""In-memory catalog; callers own the input sequence."""

def export_ids(rows):
    """Export in original import order."""
    return [row["id"] for row in rows]


def newest_ids(rows):
    """Read-only view, descending created time; preserve ties in input order."""
    rows.sort(key=lambda row: row["created"], reverse=True)
    return [row["id"] for row in rows]


def owner_ids(rows, owner):
    """Read-only view, ascending id, restricted to one owner."""
    rows.sort(key=lambda row: row["id"])
    return [row["id"] for row in rows if row["owner"] == owner]


def recent_ids(rows, minimum):
    """Read-only view, import order, inclusive creation-time minimum."""
    return [row["id"] for row in rows if row["created"] >= minimum]

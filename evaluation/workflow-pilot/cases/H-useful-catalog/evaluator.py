"""Independent hidden checks for a synthetic fixture; never copied into taskrepo."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

m = None


class HiddenChecks(unittest.TestCase):
    def setUp(self):
        self.rows = [{"id": "z", "created": 1, "owner": "a"},
                     {"id": "b", "created": 3, "owner": "a"},
                     {"id": "c", "created": 3, "owner": "b"},
                     {"id": "a", "created": 2, "owner": "a"}]
        self.before = [dict(row) for row in self.rows]

    def check_reported_failure(self):
        self.assertEqual(m.newest_ids(self.rows), ["b", "c", "a", "z"])
        self.assertEqual(self.rows, self.before)
        self.assertEqual(m.export_ids(self.rows), ["z", "b", "c", "a"])

    def check_sibling_owner(self):
        self.assertEqual(m.owner_ids(self.rows, "a"), ["a", "b", "z"])
        self.assertEqual(self.rows, self.before)

    def check_view_sequence(self):
        m.owner_ids(self.rows, "a")
        self.assertEqual(m.newest_ids(self.rows), ["b", "c", "a", "z"])
        self.assertEqual(m.recent_ids(self.rows, 3), ["b", "c"])
        self.assertEqual(self.rows, self.before)

    def check_negative_scope(self):
        self.assertEqual(m.export_ids(self.rows), ["z", "b", "c", "a"])
        self.assertEqual(m.recent_ids(self.rows, 2), ["b", "c", "a"])
        self.assertEqual(m.newest_ids([]), [])
        self.assertEqual(m.owner_ids(self.rows, "missing"), [])
        self.assertEqual(self.rows, self.before)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    source = repo / "catalog.py"
    if not source.is_file():
        print(json.dumps({"passed": 0, "total": 4, "checks": {}, "error": "missing implementation"}))
        return 1
    # Copy only the declared implementation, never invoke candidate commands.
    # This isolates imports/cwd from repository helper files; it is not an OS sandbox.
    global m
    original_cwd = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="workflow-grade-") as temporary:
        destination = Path(temporary) / "catalog.py"
        shutil.copyfile(source, destination)
        try:
            os.chdir(temporary)
            spec = importlib.util.spec_from_file_location("candidate_fixture", destination)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            checks = {}
            for name in sorted(n for n in dir(HiddenChecks) if n.startswith("check_")):
                result = unittest.TestResult()
                HiddenChecks(name).run(result)
                checks[name] = {"passed": result.wasSuccessful(),
                                "failures": [trace for _, trace in result.failures + result.errors]}
        except Exception as error:
            print(json.dumps({"passed": 0, "total": 4, "checks": {}, "error": repr(error)}))
            return 1
        finally:
            os.chdir(original_cwd)
    passed = sum(check["passed"] for check in checks.values())
    print(json.dumps({"passed": passed, "total": len(checks), "checks": checks}, sort_keys=True))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())

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
    def check_csv_empty_column(self):
        self.assertEqual(m.import_row("P7,,4"), {"id": "P7", "description": "", "quantity": 4})

    def check_exact_lookup(self):
        self.assertEqual(m.find_part([{"id": "P70"}, {"id": "P7"}], "P7"), {"id": "P7"})
        self.assertIsNone(m.find_part([{"id": "P70"}], "P7"))

    def check_negative_normalization_scope(self):
        rows = [{"id": " p7 "}, {"id": "P7"}, {"id": "p7"}]
        for row in rows:
            self.assertIs(m.find_part(rows, row["id"]), row)
        self.assertIsNone(m.find_part(rows, " P7 "))
        self.assertEqual(m.import_row(" p7 ,note,2")["id"], " p7 ")

    def check_csv_compatibility(self):
        self.assertEqual(m.import_row('A1,"nut, steel",3')["description"], "nut, steel")
        self.assertEqual(m.import_row("A1,nut,-2")["quantity"], -2)
        for bad in ("A1,nut", "A1,nut,3,", "A1,nut,3,extra"):
            with self.assertRaises(ValueError):
                m.import_row(bad)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    source = repo / "parts.py"
    if not source.is_file():
        print(json.dumps({"passed": 0, "total": 4, "checks": {}, "error": "missing implementation"}))
        return 1
    # Copy only the declared implementation, never invoke candidate commands.
    # This isolates imports/cwd from repository helper files; it is not an OS sandbox.
    global m
    original_cwd = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="workflow-grade-") as temporary:
        destination = Path(temporary) / "parts.py"
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

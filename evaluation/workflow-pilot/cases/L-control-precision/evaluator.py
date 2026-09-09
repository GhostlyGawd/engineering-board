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
    def check_reported_failure(self):
        self.assertEqual(m.ingest_live("2.75"), 2.75)

    def check_sibling_replay(self):
        self.assertEqual(m.ingest_replay("-0.125"), -0.125)

    def check_no_quantization(self):
        for text in ("0.000125", "-12.625", "1e-4", " 9.125 "):
            for ingest in (m.ingest_live, m.ingest_replay):
                self.assertEqual(ingest(text), float(text))

    def check_negative_scope(self):
        self.assertEqual(m.sensor_summary(1.125), "1.12")
        self.assertEqual(m.sensor_summary(-1.125), "-1.12")
        self.assertEqual(m.payment_receipt("1.125"), "1.13")
        self.assertEqual(m.payment_receipt("-1.125"), "-1.13")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    source = repo / "readings.py"
    if not source.is_file():
        print(json.dumps({"passed": 0, "total": 4, "checks": {}, "error": "missing implementation"}))
        return 1
    # Copy only the declared implementation, never invoke candidate commands.
    # This isolates imports/cwd from repository helper files; it is not an OS sandbox.
    global m
    original_cwd = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="workflow-grade-") as temporary:
        destination = Path(temporary) / "readings.py"
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

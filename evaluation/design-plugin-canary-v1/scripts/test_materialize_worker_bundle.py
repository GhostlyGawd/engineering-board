#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path

from materialize_worker_bundle import TASKS, materialize

SOURCE = Path(__file__).resolve().parents[1]
FORBIDDEN = [
    "sealed",
    "answer-key",
    '"rubric"',
    "recovery entry is visually buried",
    "continue targets a missing route",
    "start over clears progress immediately",
    "intentional_nonissues",
    "seeded_traps",
]
TEXT_SUFFIXES = {".json", ".md", ".txt", ".tsx", ".ts", ".js", ".mjs", ".css", ".html", ".svg", ".yml", ".yaml"}


class MaterializationTests(unittest.TestCase):
    def test_all_tasks_are_isolated_and_leak_free(self):
        with tempfile.TemporaryDirectory() as temp:
            for task_id in TASKS:
                output = Path(temp) / task_id
                materialize(SOURCE, task_id, output)
                self.assertTrue((output / "workspace/package-lock.json").is_file())
                self.assertTrue((output / "fixture/fixture.json").is_file())
                paths = [path for path in output.rglob("*") if path.is_file()]
                self.assertFalse(any(path.is_symlink() for path in paths))
                relative_paths = "\n".join(str(path.relative_to(output)) for path in paths).lower()
                self.assertNotIn("sealed", relative_paths)
                textual = [path for path in paths if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"package-lock.json", "package.json"}]
                corpus = "\n".join(str(path.relative_to(output)) + "\n" + path.read_text(encoding="utf-8") for path in textual).lower()
                for marker in FORBIDDEN:
                    self.assertNotIn(marker, corpus, f"{task_id} leaked {marker}")

    def test_existing_destination_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                materialize(SOURCE, "C3", Path(temp))


if __name__ == "__main__":
    unittest.main()

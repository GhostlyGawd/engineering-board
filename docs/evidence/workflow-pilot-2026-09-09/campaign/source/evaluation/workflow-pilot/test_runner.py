"""No model calls: exercise one-shot receipts and evidence boundaries with a fake CLI."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("workflow_runner", Path(__file__).with_name("runner.py"))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

FAKE = '''#!INTERPRETER
import json, os, pathlib, sys, time
if '--help' in sys.argv:
    print('--ignore-user-config --ignore-rules --ephemeral --output-schema --json')
elif '--version' in sys.argv:
    print('codex fake-1')
elif '--mcp' in sys.argv:
    for line in sys.stdin:
        request = json.loads(line)
        if request.get('id') == 2:
            print(json.dumps({'jsonrpc':'2.0','id':2,'result':{'tools':[{'name':n,'inputSchema':{'type':'object'}} for n in ['board_context','board_get_entry']]}}))
elif os.environ.get('PILOT_FAKE_MODE') == 'timeout':
    print(json.dumps({'type':'thread.started'}), flush=True)
    time.sleep(5)
elif os.environ.get('PILOT_FAKE_MODE') == 'forbidden':
    print(json.dumps({'type':'item.started','item':{'type':'command_execution','command':'cat /etc/passwd'}}), flush=True)
    time.sleep(5)
elif os.environ.get('PILOT_FAKE_MODE') == 'exit':
    print('failure content should remain private', file=sys.stderr)
    sys.exit(3)
else:
    prompt = sys.stdin.read()
    workspace = pathlib.Path(sys.argv[sys.argv.index('--cd')+1])
    (workspace/'app.py').write_text('VALUE = 2\\n')
    out = pathlib.Path(sys.argv[sys.argv.index('--output-last-message')+1])
    out.write_text(json.dumps({k:'private narrative' for k in ['diagnosis','changes','verification','remaining_uncertainty']}))
    print(json.dumps({'type':'item.completed','item':{'type':'command_execution','command':'python3 -m unittest','exit_code':0}}))
    print(json.dumps({'type':'turn.completed','usage':{'input_tokens':100,'output_tokens':20}}))
'''


class RunnerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="workflow-runner-test-")
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.study = self.repo / "evaluation/workflow-pilot"
        self.study.mkdir(parents=True)
        shutil.copyfile(Path(runner.__file__), self.study / "runner.py")
        server = self.repo / "mcp-server/engineering_board_mcp.py"
        server.parent.mkdir()
        server.write_text("from pathlib import Path\ndef tool_board_init(p):\n (Path(p['root'])/'engineering-board/pilot').mkdir(parents=True)\ndef tool_board_rebuild(p):\n pass\n")
        cases = []
        for number in range(4):
            case = self.study / "cases" / str(number)
            taskrepo = case / "taskrepo"
            taskrepo.mkdir(parents=True)
            (taskrepo / "app.py").write_text("VALUE = 1\n")
            (taskrepo / "AGENTS.md").write_text("Run the tests for changed code.\n")
            (taskrepo / "task.md").write_text("Repair the value.\n")
            (case / "history.md").write_text("Synthetic past evidence.\n")
            (case / "board/observations").mkdir(parents=True)
            (case / "board/observations/O001.md").write_text("Synthetic past evidence.\n")
            (case / "grader.py").write_text("import json\nprint(json.dumps({'passed':1,'total':1}))\n")
            prefix = "cases/" + str(number) + "/"
            cases.append({"id": str(number), "repo": prefix + "taskrepo", "task": prefix + "taskrepo/task.md",
                          "history": prefix + "history.md", "board": prefix + "board", "grader": prefix + "grader.py"})
        (self.study / "cases.json").write_text(json.dumps({"version": 1, "cases": cases}))
        self.fake = self.root / "fake-codex"
        self.fake.write_text(FAKE.replace("INTERPRETER", sys.executable))
        self.fake.chmod(0o755)
        self.host = self.root / "host.json"
        self.host.write_text(json.dumps({"executable": str(self.fake), "model": "fake-model", "reasoning": "medium",
              "timeout_seconds": 1, "reviewer": "independent-test-reviewer", "retention_owner": "test",
              "isolation_reviewed": True, "runtime_paths": [str(self.fake)],
              "common_args": ["--ignore-user-config", "--ignore-rules", "--ephemeral", "--disable", "plugins",
                              "--disable", "apps", "--disable", "hooks", "--disable", "multi_agent", "--enable", "skip_host_skill_discovery"],
              "board_args": ["-c", 'mcp_servers.engineering-board.command=' + json.dumps(str(self.fake)),
                             "-c", 'mcp_servers.engineering-board.args=["--mcp"]',
                             "-c", 'mcp_servers.engineering-board.cwd="{workspace}"',
                             "-c", 'mcp_servers.engineering-board.enabled_tools=["board_context","board_get_entry"]',
                             "-c", 'mcp_servers.engineering-board.required=true']}))
        for command in (["git", "init", "-q"], ["git", "add", "."],
                        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture"]):
            subprocess.run(command, cwd=self.repo, check=True, capture_output=True)
        self.evidence = self.root / "retained"
        self.trials = self.root / "trials"
        self.args = argparse.Namespace(repo=str(self.repo), evidence=str(self.evidence), trials=str(self.trials),
                                       host=str(self.host), study_document=[])
        self.review = self.root / "review.md"
        self.review.write_text("Independent fixture acceptance: fake clients only.\n")
        self.args.acceptance_review = str(self.review)

    def tearDown(self):
        self.temp.cleanup()

    def prepared(self):
        runner.prepare(self.args)
        runner.freeze(self.args)

    def test_full_fake_run_retains_bytes_and_stages_blind_review(self):
        self.prepared()
        self.assertEqual(runner.run(self.args)["status"], "complete")
        collected = runner.collect(self.args)
        self.assertEqual(collected["attempted"], 12)
        self.assertEqual(collected["usage_available"], 12)
        runner.review_packet(self.args)
        plan = runner.read(self.evidence / "plan.json")
        for arm in plan["arms"]:
            result = self.evidence / "results" / arm["id"]
            self.assertTrue((result / "start.json").is_file())
            self.assertTrue((result / "end.json").is_file())
            self.assertIn("VALUE = 2", (result / "changes.patch").read_text())
            packet = self.evidence / "review-packet" / arm["id"]
            self.assertFalse((packet / "implementation/HISTORY.md").exists())
            self.assertFalse((packet / "implementation/engineering-board").exists())
            self.assertFalse((packet / "response.json").exists())
        with self.assertRaises(runner.StudyError):
            runner.run(self.args)
        self.args.patch_review = str(self.root / "patch-review.json")
        Path(self.args.patch_review).write_text(json.dumps({arm["id"]: "reviewed" for arm in plan["arms"]}))
        runner.trace_packet(self.args)
        self.assertTrue((self.evidence / "trace-packet/committed-patch-review.json").exists())

    def test_freeze_rejects_extra_prepared_file(self):
        runner.prepare(self.args)
        (self.evidence / "injected.txt").write_text("not inventoried")
        with self.assertRaisesRegex(runner.StudyError, "inventory changed"):
            runner.freeze(self.args)

    def test_run_rejects_mutated_trial_before_start(self):
        self.prepared()
        workspace = Path(runner.read(self.evidence / "plan.json")["arms"][0]["workspace"])
        (workspace / "app.py").write_text("contaminated")
        with self.assertRaisesRegex(runner.StudyError, "trial inputs changed"):
            runner.run(self.args)
        self.assertFalse((self.evidence / "RUN-START.json").exists())

    def test_timeout_keeps_partial_stream_and_unstarted_packet(self):
        self.prepared()
        with patch.dict(os.environ, {"PILOT_FAKE_MODE": "timeout"}):
            result = runner.run(self.args)
        self.assertEqual(result["attempted"], 1)
        self.assertEqual(result["status"], "stopped_on_failure")
        receipt = next((self.evidence / "results").glob("*/end.json"))
        self.assertIn("wall-time", runner.read(receipt)["failure"])
        self.assertGreater((receipt.parent / "stdout.jsonl").stat().st_size, 0)
        runner.collect(self.args)
        runner.review_packet(self.args)
        self.assertEqual(len(list((self.evidence / "review-packet").glob("*/availability.json"))), 11)

    def test_detected_forbidden_path_terminates_without_waiting_for_timeout(self):
        self.prepared()
        with patch.dict(os.environ, {"PILOT_FAKE_MODE": "forbidden"}):
            result = runner.run(self.args)
        self.assertEqual(result["attempted"], 1)
        receipt = runner.read(next((self.evidence / "results").glob("*/end.json")))
        self.assertEqual(receipt["failure"], "trace audit failed")
        self.assertLess(receipt["wall_seconds"], 1)

    def test_client_exit_keeps_stderr_and_blocks_retry(self):
        self.prepared()
        with patch.dict(os.environ, {"PILOT_FAKE_MODE": "exit"}):
            result = runner.run(self.args)
        self.assertEqual(result["attempted"], 1)
        receipt = next((self.evidence / "results").glob("*/end.json"))
        self.assertEqual(runner.read(receipt)["exit_code"], 3)
        self.assertIn("private", (receipt.parent / "stderr.txt").read_text())
        with self.assertRaises(runner.StudyError):
            runner.run(self.args)

    def test_next_workspace_tampering_stops_before_next_start(self):
        self.prepared()
        plan = runner.read(self.evidence / "plan.json")
        original = runner.capture_result
        def contaminate(evidence, arm):
            value = original(evidence, arm)
            (Path(plan["arms"][1]["workspace"]) / "extra.txt").write_text("unexpected")
            return value
        with patch.object(runner, "capture_result", side_effect=contaminate):
            result = runner.run(self.args)
        self.assertEqual(result["status"], "stopped_on_input_integrity_failure")
        self.assertEqual(result["attempted"], 1)


if __name__ == "__main__":
    unittest.main()

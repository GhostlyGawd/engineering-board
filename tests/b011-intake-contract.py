#!/usr/bin/env python3
"""Exercise B011's documented tool paths, not model instruction adherence.

Run: python3 tests/b011-intake-contract.py
Fixtures are isolated; no live board or user session is read or written.
"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'mcp-server'))
import engineering_board_mcp as mcp


class IntakeContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='eb-b011-')
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.params = {'root': str(self.repo), 'project': 'fixture'}
        mcp.tool_board_init(self.params)
        self.board = self.repo / 'engineering-board' / 'fixture'

    def capture(self, **changes):
        params = dict(self.params, kind='bug',
                      title='Read-only triage offers another session task',
                      affects='skills/board-triage/SKILL.md',
                      evidence='Observed: offered claimed task. Expected: verify owner first.')
        params.update(changes)
        return mcp.tool_board_capture_finding(params)

    def test_confirmed_read_only_defect_stays_scratch_until_apply(self):
        result = self.capture()
        scratch = self.repo / result['scratch_file']
        self.assertTrue(result['captured_at'])
        self.assertIn('verify owner first', scratch.read_text())
        self.assertFalse(list((self.board / 'bugs').glob('*.md')))
        plan = mcp.tool_board_promote_findings(dict(self.params, session=scratch.name))
        self.assertEqual(plan['summary']['create'], 1)
        self.assertFalse(list((self.board / 'bugs').glob('*.md')))
        applied = mcp.tool_board_promote_findings(dict(self.params, apply=plan['plan_id']))
        self.assertEqual(applied['summary']['created'], 1)
        self.assertEqual(len(list((self.board / 'bugs').glob('*.md'))), 1)

    def test_uncertain_cause_remains_observation_evidence(self):
        result = self.capture(kind='observation', title='Report omits a confirmed finding',
                              evidence='Observed omission; cause unknown. Suspected routing cause untested.')
        scratch = self.repo / result['scratch_file']
        self.assertIn('cause unknown', scratch.read_text())
        plan = mcp.tool_board_promote_findings(dict(self.params, session=scratch.name))
        applied = mcp.tool_board_promote_findings(dict(self.params, apply=plan['plan_id']))
        self.assertEqual(applied['summary']['created'], 1)
        self.assertEqual(len(list((self.board / 'observations').glob('*.md'))), 1)
        self.assertFalse(list((self.board / 'bugs').glob('*.md')))

    def test_duplicate_matches_existing_entry(self):
        first = self.capture()
        plan = mcp.tool_board_promote_findings(dict(self.params, session=Path(first['scratch_file']).name))
        mcp.tool_board_promote_findings(dict(self.params, apply=plan['plan_id']))
        before = {p.name: p.read_bytes() for p in (self.board / 'bugs').glob('*.md')}
        second = self.capture(evidence="Repeated in a later interaction; expected owner verification.")
        plan = mcp.tool_board_promote_findings(dict(self.params, session=Path(second['scratch_file']).name))
        self.assertEqual(plan['summary']['deduplicated'], 1)
        applied = mcp.tool_board_promote_findings(dict(self.params, apply=plan['plan_id']))
        self.assertEqual(applied['summary']['deduplicated'], 1)
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.board / 'bugs').glob('*.md')})

    def test_unavailable_target_fails_without_capture(self):
        with self.assertRaises(mcp.ToolError):
            self.capture(project='missing-board')
        self.assertFalse(list(self.repo.rglob('mcp-*.md')))

    def test_capture_write_failure_does_not_return_success(self):
        with patch('builtins.open', side_effect=PermissionError('fixture inbox unavailable')):
            with self.assertRaisesRegex(PermissionError, 'fixture inbox unavailable'):
                self.capture()
        self.assertFalse(list(self.repo.rglob('mcp-*.md')))


if __name__ == '__main__':
    unittest.main(verbosity=2)

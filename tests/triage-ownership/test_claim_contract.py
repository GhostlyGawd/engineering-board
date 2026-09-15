#!/usr/bin/env python3
"""Check the real claim operations that triage's guidance relies on.

These fixtures validate API/script behavior, not an agent following prose.
"""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'mcp-server'))
spec = importlib.util.spec_from_file_location('board', ROOT / 'mcp-server/engineering_board_mcp.py')
board = importlib.util.module_from_spec(spec)
spec.loader.exec_module(board)


class ClaimContract(unittest.TestCase):
    def test_mcp_and_shell_claim_states(self):
        for transport in ('mcp', 'shell'):
            with self.subTest(transport=transport), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                bd = root / 'engineering-board' / 'fixture'
                bd.mkdir(parents=True)
                entry = bd / 'B010.md'
                entry.write_text('---\nstatus: in_progress\n---\nOther chat work\n')

                def claim(entry_id, session):
                    if transport == 'mcp':
                        result = board.tool_board_claim(dict(root=tmp, project='fixture',
                                                             entry_id=entry_id, session_id=session))
                        self.assertEqual(result['acquired'], result['exit_code'] == 0)
                        return result['exit_code']
                    return subprocess.run(['bash', str(ROOT / 'hooks/scripts/board-claim-acquire.sh'),
                                           str(bd), entry_id, session], capture_output=True).returncode

                def snapshot():
                    return {str(p.relative_to(bd)): p.read_bytes()
                            for p in bd.rglob('*') if p.is_file()}

                self.assertEqual(claim('B010', 'chat-a'), 0)
                initial = snapshot()
                self.assertEqual(claim('B010', 'chat-b'), 1)
                self.assertEqual(snapshot(), initial, 'foreign acquisition must preserve owner/status')
                self.assertEqual(claim('B010', 'chat-a'), 1,
                                 'same-session reacquisition is not a resume check')
                self.assertEqual(snapshot(), initial)
                self.assertEqual(claim('B011', 'chat-b'), 0,
                                 'another session must be able to claim separate work')
                hb = bd / '_claims/B010/heartbeat.txt'
                hb.write_text('2000-01-01T00:00:00Z\n')
                stale = snapshot()
                self.assertEqual(claim('B010', 'chat-b'), 2)
                self.assertEqual(claim('B010', 'chat-a'), 2)
                self.assertEqual(snapshot(), stale, 'stale result must not reclaim or refresh')
                (bd / '_claims/B010/owner.txt').unlink()
                missing = snapshot()
                self.assertEqual(claim('B010', 'chat-b'), 2)
                self.assertEqual(snapshot(), missing, 'missing owner must not allow takeover')
                self.assertEqual(entry.read_text(), '---\nstatus: in_progress\n---\nOther chat work\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)

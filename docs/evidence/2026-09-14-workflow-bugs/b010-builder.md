# B010 builder handoff

## Assignment

- Owner: `b010-owner-20260914`, held by lead on behalf of B010 builder.
- Base: `7619752`; branch: `fix/b010-triage-ownership`.
- Scope: triage guidance and focused claim-operation verification. No runtime,
  release, board, or shared changelog changes.
- Acceptance: verify exact session ownership before resume/fix research; never
  reset or take over foreign/unknown/stale work; claim atomically before status
  changes; one owned entry per session across projects; permit overview and
  separate-session work; give viable MCP and shell paths.

## Defect and correction

Previous Step 4 treated any repository `in_progress` entry as this session's
work, offering completion or reset before checking a claim. The MCP shortcut
only required acquisition for starting work, leaving resumption unspecified.
Both now point to one ownership gate before fix research and mutations. The
auto-resolve pass also excludes unowned active work from research/closure.

The shipped MCP has no claim-inspection or heartbeat tool. Guidance explicitly
uses canonical claim files for read-only inspection, even in the MCP path,
and fails closed if inspection is unavailable. Existing atomic acquisition
returns contention even for its current owner; fresh same-owner resumption
therefore uses exact ownership inspection, not replayed acquisition.

## Scenario review of the instruction contract

These are source-level walkthroughs, not live agent behavior measurements.

| Fixture/request | Required path in revised guidance |
| --- | --- |
| B010 in progress, fresh owner chat A; current chat B asks to resume | 4b foreign row: overview only for B010; no fix research/reset/release. |
| Same fixture; chat B asks for next ready work | 4b permits another unclaimed ready entry, then 4c atomic acquisition. |
| B010 in progress, fresh owner equals trusted current session | 4b exact-match row permits scope-preserving resume. Replayed acquisition is explicitly discouraged. |
| B010 in progress, owner unknown/missing; current session cannot be verified | 4a/4b require overview and no mutation. A generated id cannot prove an old claim. |
| B010 has stale heartbeat with either own or foreign id | 4b stale row and recovery paragraph prohibit automatic refresh/reclaim/resume. |
| Claim belongs to current session but entry is still open, including another project | 4b explicitly scans claims regardless of status, across resolved project boards; finish/park before different work. |
| Multiple claims match this session | 4b requires assignment reconciliation before starting/resuming. |
| Claim changes after initial read | 4b/4c require re-read before research/state changes; stop on changed ownership. |
| A competing session acquires selected open entry first | 4c contention leaves state unchanged; no release/reclaim or owner-id substitution. |
| SessionStart summary says “in_progress” | 4d explicitly requires the same gate; summary does not establish ownership. |
| MCP present, no local file access | Protocol says unknown ownership; no resume/start based on status/list alone. |

## Executed verification

- `python3 tests/triage-ownership/test_claim_contract.py` — exit 0. Exercises
  both real MCP and shell acquisition: fresh foreign contention, same-owner
  contention, separate-entry acquisition, stale own/foreign claim, missing
  owner, and byte-for-byte preservation on rejected acquisitions.
- `bash tests/docs-coherence.sh` — exit 0.

The fixture does not implement a mock agent or claim that prose is mechanically
enforced. Exact identity, claimed-open counting and safe overview routing need
independent instruction review. Better agent adherence in actual use remains
an outcome to observe. Costs and lead-time metrics were not measured here.

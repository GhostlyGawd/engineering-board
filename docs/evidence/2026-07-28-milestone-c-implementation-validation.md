# Milestone C implementation validation — 2026-07-28

## Result

Milestone C is implemented and worker-validated for v1.10.0. Deterministic
cluster ranking, canonical H### lifecycle, negative memory, plugin/MCP parity,
and the normal pattern-intelligence view use one zero-dependency core.

This record does not claim publication. Merge, merged-main CI, GitHub Release,
PyPI, the official MCP Registry, Pages, and closeout CI remain external gates.

```text
repository: GhostlyGawd/engineering-board
implementation base: 51be227d2d85fd6fb4c5498981514ac441f73181
branch: agent/milestone-c-implementation
target version: 1.10.0
ranking rule: 1
graph schema: 3
MCP tools: 17
plugin commands: 19
```

## Lifecycle evidence matrix

| Sequence | Failure injection | Expected semantic outcome | Durable evidence | Test |
|---|---|---|---|---|
| Rank two equal-score cross-domain clusters | Equal totals | Components remain visible and ties sort by cluster fingerprint | Compared rank payload | `milestone-c-root-cause-intelligence.sh` |
| Read through shared core, CLI, and MCP | Three adapters | Exact ranked facts agree | Compared JSON payloads | Milestone C matrix |
| Preview a valid exact-citation proposal | Omit apply | No H### file is written | Inventory comparison and plan token | Milestone C matrix |
| Preview malformed proposals | Missing member, alternative, or falsifier | Validation fails before mutation | Empty hypothesis inventory | Milestone C matrix |
| Apply after a canonical source change | Stale graph fingerprint | `plan_stale`; no H### file | Empty hypothesis inventory | Milestone C matrix |
| Apply one creation plan twice | Replayed creation token | First creates H001; second returns `plan_stale` | One canonical H### file | Milestone C matrix |
| Evaluate without and with evidence | Missing then cited evidence | Missing evidence fails; cited rejection and confirmation apply | H### outcome history | Milestone C matrix |
| Re-propose a rejected claim | Equal claim fingerprint | Typed `blocked_by_negative_memory`; no token | Rejected H001 remains | Milestone C matrix |
| Reopen rejected H001 | No new evidence, then one new member | First fails; second rebinds to proposed and retains history | Revised H001 | Milestone C matrix |
| Split H001 | Child creation omitted by contract | H001 becomes split; no implicit child exists | Terminal H001 | Milestone C matrix |
| Merge two active records | Self target, then valid target | Self merge fails; valid source becomes merged and target derives reverse reference | H002/H003 lineage | Milestone C matrix |
| Delete disposable graph cache | Missing read model | Rebuilt ranking equals prior ranking | Compared payload | Milestone C matrix |
| Run with closed outbound proxies | Network unavailable | Ranking remains fully local and equal | Compared offline payload | Milestone C matrix |
| Render stale and hostile hypothesis content | Source change plus script markup | Stale state is visible, text is escaped, no mutation control exists | Generated HTML assertions | Milestone C matrix and view suite |
| Run the release tree | Adjacent regression opportunity | Every existing suite remains green | 16/16 suite result | `tests/run-all.sh` |

## Commands and results

Worker evidence on 2026-07-28:

```text
bash tests/orchestration/milestone-c-root-cause-intelligence.sh
Milestone C root-cause intelligence matrix: 15 checks passed

bash -lc 'python3 mcp-server/test_mcp_server.py'
RESULT: PASS (166 checks)

bash tests/run-all.sh
RUN-ALL SUMMARY: 16 pass, 0 fail (of 16 suites)

bash mcp-server/build-mcpb.sh
sha256: 59f5b4c4862e6abf0a2f7111086d4a5ffd47d360eab10d93a461524622ab77e7
```

The matrix runs against a disposable repository and real board scaffold. It
uses canonical P### and entry Markdown, the shared core, the real CLI, MCP
adapters, and the normal HTML renderer. Closed proxy endpoints prove that the
sequence does not require network access.

## Visual evidence

`docs/assets/milestone-c-root-cause-intelligence.svg` is a sanitized static
capture of the real deterministic matrix result. Its source is
`tests/orchestration/milestone-c-root-cause-intelligence.sh` at the
implementation branch state on 2026-07-28. It contains no user path, secret,
customer data, or private repository content. The SVG title, description,
README alt text, and landing-page alt text identify its provenance and result.

## Documentation drift review

- **Required conflict:** repaired. The accepted production command boundary is
  now explicit: `/board-insights` is read-only; `/board-hypothesis` owns
  content-bound proposal and evaluation preview/apply.
- **Recommended gap:** none in the worker phase.
- **Implementation-defined omission:** repaired. Graph schema 3, ranking
  components, token binding, negative memory, lifecycle transitions, and normal
  view behavior are documented and tested.
- **Documentation-only drift:** repaired. Version, command count, MCP tool
  count, initialization layout, architecture, security, setup, landing, LLM
  summary, changelog, and visual claims now match v1.10.0 behavior.
- **Reviewed and unaffected:** historical v1.8.0 and v1.9.1 validation reports
  remain dated truth and were not rewritten. The canonical Markdown decision,
  no-SQLite boundary, optional verification loop, claim lifecycle, transport,
  install commands, license, contribution policy, and prior demo containment
  remain accurate.

## Remaining gates

1. Open the implementation PR and require green PR CI.
2. Merge and require green merged-main CI.
3. Publish v1.10.0.
4. Validate the GitHub Release asset and checksum, PyPI package, official MCP
   Registry record, and Pages output.
5. Append `2026-07-28-v1.10.0-release-validation.md` in a closeout PR.
6. Merge closeout and require fresh merged-main CI before marking Milestone C
   shipped.

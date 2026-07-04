---
id: B011
type: bug
title: ARCHITECTURE.md is stale for 1.2.0 (version header, MCP server absent, wrong script/suite counts)
discovered: 2026-07-04
status: open
priority: P3
affects: ARCHITECTURE.md
needs: tdd
pattern: [doc-drift]
---

## Done when
- Header reads v1.2.0; §2 tree includes `mcp-server/`; script count corrected to 22 (add `board-paths.sh`, `board-relocate.sh` to §5); §10 test map includes the mcp-server suite (11 suites).
- The false "100% reject-rate" guarantee at :244 is reconciled with B003 (backed by a real suite or removed).

## Observed behavior (Track D F1-F4 + Track A M3)
:5 says "v1.1.0"; plugin.json is 1.2.0. §2 tree omits mcp-server/. :38 says "12 bash scripts", :117 says "20 scripts"; `ls hooks/scripts/*.sh`=22. §10 lists "8 domains"; run-all chains 11 suites.

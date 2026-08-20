# MCP server agent instructions

Keep `engineering_board_mcp.py` and `engineering_board_core.py` free of
third-party runtime dependencies. Development tools belong only in
`support/dev-tools/`.

From the repository root on macOS/Linux, run:

```sh
bash scripts/quality-gate.sh format
bash scripts/quality-gate.sh lint
bash scripts/quality-gate.sh typecheck
bash scripts/quality-gate.sh package
bash mcp-server/run-tests.sh
```

On native Windows, replace the Bash quality wrapper with
`python scripts/quality_gate.py <selector>` from PowerShell or
`python scripts\quality_gate.py <selector>` from `cmd.exe`.

The strict typed MCP scope is `mcp-server/engineering_board_core.py`.
`mcp-server/engineering_board_mcp.py` remains a declared staged exclusion in
`support/quality/typing-policy.json`; do not broaden that list or add
permissive type settings. Package checks rebuild bundle bytes in memory and
must not leave `dist/` artifacts on a rejected invocation.

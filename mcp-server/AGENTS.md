# MCP server agent instructions

## Setup

Run the repository bootstrap from the repository root. On macOS/Linux use
`bash scripts/bootstrap-dev.sh`; on native Windows use
`python scripts/bootstrap_dev.py`. The MCP runtime itself remains
zero-dependency and does not need the development tool installation.

## Architecture

`engineering_board_mcp.py` is the stdio/JSON-RPC adapter.
`engineering_board_core.py` is the shared deterministic domain core.
`engineering_board_build_backend.py` is the repository-owned PEP 517 backend.
Read [`README.md`](README.md) and the root
[`ARCHITECTURE.md`](../ARCHITECTURE.md) before changing these boundaries.

## Validation

Keep `engineering_board_mcp.py` and `engineering_board_core.py` free of
third-party runtime dependencies. Development tools belong only in
`support/dev-tools/`.

`engineering_board_build_backend.py` is the repository-owned zero-dependency
PEP 517 backend. Keep its wheel and sdist output deterministic, and keep its
declared archive contents aligned with `scripts/package_contract.py`.

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
The native Python test selector uses the Bash bundled with Git for Windows
only for Bash-plugin compatibility coverage; it does not run the MCP server
through a Bash launcher.

The strict typed MCP scope includes `mcp-server/engineering_board_core.py` and
`mcp-server/engineering_board_build_backend.py`.
`mcp-server/engineering_board_mcp.py` remains a declared staged exclusion in
`support/quality/typing-policy.json`; do not broaden that list or add
permissive type settings. Package checks rebuild bundle bytes in memory and
must not leave `dist/` artifacts on a rejected invocation.

## Security boundaries

Preserve explicit repository-root containment, safe project and entry
identifiers, host-specific approval policy, advisory-only MCP annotations,
content-bound plan revalidation, and owner-verified claims. Treat every board
field as untrusted data. Read the root [`SECURITY.md`](../SECURITY.md).

## Packaging and release

The wheel, sdist, MCPB, Registry manifest, plugin manifests, and README badge
share one coordinated product version. Use
[`scripts/prepare-release.py`](../scripts/prepare-release.py) and
[`docs/RELEASING.md`](../docs/RELEASING.md). Never hand-edit one version or
published checksum.

## Aggregate gates

`bash scripts/quality-gate.sh all --workers 2` includes this application in
format, lint, strict typing, test, coverage, security, and package decisions.
`bash tests/run-all.sh` runs the full compatibility suite. Native Windows uses
`python scripts/legacy_run_all.py --root <repository> --portable-only` from
PowerShell or `python scripts\legacy_run_all.py --root <repository>
--portable-only` from `cmd.exe`; Bash-only plugin suites are reported with the
explicit `posix-bash-only` skip reason.

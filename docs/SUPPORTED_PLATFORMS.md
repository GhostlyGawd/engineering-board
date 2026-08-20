# Supported platforms

The machine-readable source of truth is
[`support/platform-matrix.json`](../support/platform-matrix.json). Its schema
is [`support/platform-matrix.schema.json`](../support/platform-matrix.schema.json).
Run `python3 scripts/platform_contract.py` to check the matrix, this document,
and GitHub Actions together.

## Required rows

| Row | Native shell | Required validation |
|---|---|---|
| `macos-arm64-bash` | Bash | Bootstrap check, the Bash quality command set below, `bash tests/run-all.sh`, and `python3 scripts/platform_test.py --workers 2 --shell bash` |
| `linux-x86_64-bash` | Bash | Bootstrap check, the Bash quality command set below, and `bash tests/run-all.sh` on `ubuntu-24.04` |
| `windows-x86_64-powershell` | PowerShell | Python bootstrap and quality command sets plus `python scripts/platform_test.py --workers 2 --shell powershell` on `windows-2025` |
| `windows-x86_64-cmd` | `cmd.exe` | Python bootstrap and quality command sets plus `python scripts\platform_test.py --workers 2 --shell cmd` on `windows-2025` |

## Stable quality command parity

The macOS/Linux Bash interface is:

```sh
bash scripts/quality-gate.sh format
bash scripts/quality-gate.sh lint
bash scripts/quality-gate.sh typecheck
bash scripts/quality-gate.sh test --workers 2
bash scripts/quality-gate.sh security
bash scripts/quality-gate.sh package
bash scripts/quality-gate.sh all --workers 2
```

PowerShell calls `python scripts/quality_gate.py` with the same selectors.
`cmd.exe` calls `python scripts\quality_gate.py` with the same selectors.
Help, stage names, diagnostics, artifacts, and exit decisions come from the
same Python implementation. The `test` selector is the quality test and
coverage invocation. `all --workers 2` is the split-gate aggregate.

The matrix declares minimum and current versions for Python, Node.js, Git,
Claude Code, Codex CLI, supported operating systems, and the devcontainer
combination. A skip is valid only when its reason is in the matrix and the
surface permits that reason.

The first bootstrap needs Python and network access to the public pinned
sources. It installs below the ignored repository runtime root. The check
commands above make no network request and do not change the installation or
checkout. Tool versions, Python and Node lock files, download URLs, and
SHA-256 values are tracked in [`support/dev-tools/`](../support/dev-tools/).
The development inventory does not add a dependency to the MCP package.

Git Bash is a compatibility environment, not native Windows evidence. WSL is
also a compatibility environment, not native Windows evidence. Required
Windows results come from the Python launcher running directly in PowerShell
and `cmd.exe` on a GitHub-hosted Windows runner. The platform-neutral launcher
checks the matrix/schema/docs/CI contract, filesystem containment, validator
locks, evaluation harness, and a real zero-dependency MCP stdio lifecycle. It
writes a commit-bound result manifest below
`.engineering-board/validation/platform/`; native Windows CI retains that
manifest as a workflow artifact.

## Devcontainer

The required devcontainer row is `devcontainer-linux-x86_64`. The configuration
is [`.devcontainer/devcontainer.json`](../.devcontainer/devcontainer.json).
It builds for `linux/amd64`, opens the checkout at
`/workspaces/engineering-board`, and runs as user `vscode`. Base images use
immutable digests. The image installs the same repository-pinned inventory and
runs `bash scripts/bootstrap-dev.sh --check` when the workspace is created.
The build context excludes Git state, ignored runtime state, environment
files, private-key filename patterns, and host editor files.

## Validator resources

At most two top-level validator sessions may run at once. The aggregate suite,
browser validation, and OTLP validation each require their named exclusive
lock. Ports `127.0.0.1:4173` and `127.0.0.1:4318` require exclusive port
locks. An occupied lock or port fails visibly, and validation does not replace
the listener, share it, or select another port.

Use `scripts/validator_resources.py` for repository-owned validator sessions.
MCP fan-out is at most five child cases within one session. Claude plugin
fan-out is at most three child cases within one session.

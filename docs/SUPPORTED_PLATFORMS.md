# Supported platforms

The machine-readable source of truth is
[`support/platform-matrix.json`](../support/platform-matrix.json). Its schema
is [`support/platform-matrix.schema.json`](../support/platform-matrix.schema.json).
Run `python3 scripts/platform_contract.py` to check the matrix, this document,
and GitHub Actions together.

## Required rows

| Row | Native shell | Required validation |
|---|---|---|
| `macos-arm64-bash` | Bash | `bash tests/run-all.sh` and `python3 scripts/platform_test.py --workers 2 --shell bash` |
| `linux-x86_64-bash` | Bash | `bash tests/run-all.sh` on `ubuntu-24.04` |
| `windows-x86_64-powershell` | PowerShell | `python scripts/platform_test.py --workers 2 --shell powershell` on `windows-2025` |
| `windows-x86_64-cmd` | `cmd.exe` | `python scripts\platform_test.py --workers 2 --shell cmd` on `windows-2025` |

The matrix declares minimum and current versions for Python, Node.js, Git,
Claude Code, Codex CLI, supported operating systems, and the devcontainer
combination. A skip is valid only when its reason is in the matrix and the
surface permits that reason.

Git Bash is a compatibility environment, not native Windows evidence. WSL is
also a compatibility environment, not native Windows evidence. Required
Windows results come from the Python launcher running directly in PowerShell
and `cmd.exe` on a GitHub-hosted Windows runner. The platform-neutral launcher
checks the matrix/schema/docs/CI contract, filesystem containment, validator
locks, evaluation harness, and a real zero-dependency MCP stdio lifecycle. It
writes a commit-bound result manifest below
`.engineering-board/validation/platform/`; native Windows CI retains that
manifest as a workflow artifact.

## Validator resources

At most two top-level validator sessions may run at once. The aggregate suite,
browser validation, and OTLP validation each require their named exclusive
lock. Ports `127.0.0.1:4173` and `127.0.0.1:4318` require exclusive port
locks. An occupied lock or port fails visibly, and validation does not replace
the listener, share it, or select another port.

Use `scripts/validator_resources.py` for repository-owned validator sessions.
MCP fan-out is at most five child cases within one session. Claude plugin
fan-out is at most three child cases within one session.

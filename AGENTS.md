# Repository agent instructions

## Release work

For Engineering Board release work, read these files before you change a
version, checksum, tag, release, or publication:

1. `maintainers/skills/release-engineering-board/SKILL.md`
2. `docs/RELEASING.md`

Use `scripts/prepare-release.py` for the coordinated release change. Do not
change one versioned surface independently.

Do not use the maintainer release skill in a repository that only installs the
Engineering Board plugin.

The owner approved the current controlled-English text. Do not claim formal
ASD-STE100 compliance without a separate qualified verification.

## Development environment

Use `bash scripts/bootstrap-dev.sh` on macOS/Linux or
`python scripts/bootstrap_dev.py` on native Windows. The offline read-only
check is `bash scripts/bootstrap-dev.sh --check` on macOS/Linux and
`python scripts/bootstrap_dev.py --check` from PowerShell or `cmd.exe`.
Development tools are pinned in `support/dev-tools/` and installed only below
ignored `.engineering-board/dev-tools/`.

The devcontainer uses the `vscode` user and
`/workspaces/engineering-board`. Do not add host credentials, host-specific
mounts, or private configuration to `.devcontainer/`.

## Quality commands

After bootstrap, use the stable macOS/Linux commands:

```sh
bash scripts/quality-gate.sh format
bash scripts/quality-gate.sh lint
bash scripts/quality-gate.sh typecheck
bash scripts/quality-gate.sh test --workers 2
bash scripts/quality-gate.sh security
bash scripts/quality-gate.sh package
bash scripts/quality-gate.sh all --workers 2
bash tests/run-all.sh
```

Native PowerShell uses `python scripts/quality_gate.py <selector>`. Native
`cmd.exe` uses `python scripts\quality_gate.py <selector>`. Use `--workers 2`
with `test` or `all`. The `test` selector owns the quality test and coverage
invocation. There is no separate coverage selector. Git Bash and WSL are
compatibility environments, not native Windows evidence.

Formatting and lint checks never rewrite inputs. They cover Python, shell,
Markdown, YAML, JSON and schemas, workflows, naming, complexity, dead code,
duplicate code, and large-file policy. Strict typing covers the root plugin
and MCP server scopes listed in `support/quality/typing-policy.json`; the gate
prints each tracked staged exclusion.

The `test` selector enforces the versioned total, branch, per-application, and
changed-line thresholds in `support/quality/coverage-policy.json`. The
`security` selector reports dependency audit, secret scan, workflow risk,
immutable pin, supply-chain policy, checksum integrity, and reject-filter
families separately.
Security diagnostics name rules and advisories but redact detected secret
values.

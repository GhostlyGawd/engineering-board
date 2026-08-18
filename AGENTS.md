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

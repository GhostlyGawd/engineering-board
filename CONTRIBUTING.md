# Contribute to Engineering Board

Engineering Board includes a Claude Code plugin and a Model Context Protocol
(MCP) server. Both interfaces use one Markdown board in the repository.

The project has no runtime package dependency. You need `bash` and `python3` to
run the tests.

Read [`ARCHITECTURE.md`](ARCHITECTURE.md) for the system structure.

## Set up the pinned development tools

On macOS or Linux, install the repository-pinned development inventory:

```sh
bash scripts/bootstrap-dev.sh
```

Verify it later without network access or filesystem changes:

```sh
bash scripts/bootstrap-dev.sh --check
```

On native Windows, run `python scripts/bootstrap_dev.py` to install, then run
`python scripts/bootstrap_dev.py --check` directly from PowerShell or
`python scripts\bootstrap_dev.py --check` from `cmd.exe`. Git Bash and WSL are
compatibility environments, not native Windows evidence.

The first installation requires Python and access to the public pinned
sources. It installs below ignored `.engineering-board/dev-tools/`. Exact
versions, lock files, immutable download URLs, and SHA-256 values are in
[`support/dev-tools/`](support/dev-tools/). A failure names the missing or
mismatched prerequisite and the recovery command. The development inventory
does not change the zero-dependency MCP runtime metadata.

To use the containerized workspace, open the repository in a Dev Container or
build it with:

```sh
docker build --no-cache --platform linux/amd64 \
  -f .devcontainer/Dockerfile \
  -t engineering-board-devcontainer .
```

The container uses user `vscode` and workspace
`/workspaces/engineering-board`. Its post-create command checks the pinned
inventory.

## Run the stable quality commands

On macOS or Linux, use these exact repository entry points:

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

The `test` selector is the quality test and coverage invocation. There is no
standalone `coverage` selector. `all --workers 2` is the split-gate aggregate.
`tests/run-all.sh` remains the supported compatibility aggregate.

On native Windows PowerShell, use:

```powershell
python scripts/quality_gate.py format
python scripts/quality_gate.py lint
python scripts/quality_gate.py typecheck
python scripts/quality_gate.py test --workers 2
python scripts/quality_gate.py security
python scripts/quality_gate.py package
python scripts/quality_gate.py all --workers 2
```

From native `cmd.exe`, use the same selectors with the Windows path:

```bat
python scripts\quality_gate.py format
python scripts\quality_gate.py lint
python scripts\quality_gate.py typecheck
python scripts\quality_gate.py test --workers 2
python scripts\quality_gate.py security
python scripts\quality_gate.py package
python scripts\quality_gate.py all --workers 2
```

Run `bash scripts/quality-gate.sh --help` or
`python scripts/quality_gate.py --help` for selector help. Invalid selectors,
unknown options, missing values, and worker counts outside 1 to 2 fail before
any stage starts. Git Bash and WSL are compatibility environments. They are
not native Windows evidence.

Supported host, shell, runtime, and container versions are declared in
[`support/platform-matrix.json`](support/platform-matrix.json) and documented
in [`docs/SUPPORTED_PLATFORMS.md`](docs/SUPPORTED_PLATFORMS.md). Native
Windows validation uses `scripts/platform_test.py` directly from PowerShell
and `cmd.exe`; Git Bash and WSL are compatibility environments only.

Add tests for new behavior. Change the tests when you change behavior.

Do not use a successful test result as proof of untested behavior. If the test
location is not clear, open a draft pull request.

## Find the project files

| Directory | Content |
|---|---|
| `commands/` | Slash-command instructions |
| `agents/` | Project Manager and Worker agent instructions |
| `skills/` | Engineering Board skills |
| `hooks/` | Hook configuration, the Stop procedure, and shell scripts |
| `mcp-server/` | The zero-dependency Python MCP server and its tests |
| `tests/` | One test area for each behavior domain |
| `references/` | Shared agent protocols and permission data |

A generated board is in `engineering-board/<project>/`. The repository stores
its own board in `engineering-board/eb-self/`.

## Obey the script portability rules

Apply these rules to each new or changed `hooks/scripts/*.sh` file:

1. Use `#!/usr/bin/env bash` as the exact shebang.
2. Do not use `date -d`.
3. Do not use `date -j -f`.
4. Do not use `jq`.
5. Do not put a drive letter in a path.
6. Use `python3` for JSON operations and timestamps.

Run `tests/crosscompat-lint.sh` to check these rules.

Source `hooks/scripts/board-paths.sh` to find the board. Use
`eb_board_dirs`, `eb_board_rows`, or `eb_router_path`.

Do not put `docs/boards/` or `engineering-board/` in a new path resolver.

## Record the release note

For each user-visible change, add the change to the `[Unreleased]` section in
[`CHANGELOG.md`](CHANGELOG.md).

Do not change one versioned file independently. An explicit release preparation
updates all versioned files and the MCP bundle checksum together.

Read [`docs/RELEASING.md`](docs/RELEASING.md) when you prepare a release.
## Use a branch and a pull request

1. Create a branch.
2. Make the change on the branch.
3. Complete the [pull request template](.github/pull_request_template.md).
4. Add the applicable board entry.
5. Add the test evidence.
6. Check the release-note requirement.
7. Check that the README and the documentation agree with the behavior.
8. Push the branch.
9. Make sure that CI passes.

Do not push a change directly to `main`.

## Add a test

1. Put the test in the applicable directory under `tests/`.
2. Add the test to the applicable test runner.
3. Run `bash tests/run-all.sh`.
4. Make sure that all test suites pass.

Add a claim test to `tests/claims/`. Add a reject-filter test to
`tests/security/`.

Each security fixture defines `expect` and `expect_reason`. The fixture must
call the canonical reject filter.

Read [`SECURITY.md`](SECURITY.md) for the security model.

## Make a first contribution

Find an issue with the `good first issue` label. Select a small issue with a
clear scope.

Use a [GitHub Discussion](https://github.com/GhostlyGawd/engineering-board/discussions)
or a draft pull request if you need information.

## License

Your contribution uses the project [MIT License](LICENSE).

## Language status

The owner approved the current controlled-English text. The project does not
claim formal ASD-STE100 compliance, certification, or independent review.

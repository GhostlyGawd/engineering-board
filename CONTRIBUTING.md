> DRAFT — FULL COMPLIANCE CHECK NOT COMPLETE

# Contribute to Engineering Board

Engineering Board includes a Claude Code plugin and a Model Context Protocol
(MCP) server. Both interfaces use one Markdown board in the repository.

The project has no runtime package dependency. You need `bash` and `python3` to
run the tests.

Read [`ARCHITECTURE.md`](ARCHITECTURE.md) for the system structure.

## Run the test suite

Run the full test suite:

```sh
bash tests/run-all.sh
```

This command runs 16 test suites. The continuous integration (CI) workflow runs
the same command for each push.

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

## Change both version manifests

For a user-visible change, change the version in these files:

- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`.

The two versions must be equal. `tests/version-coherence.sh` checks this
requirement.

Add the change to the `[Unreleased]` section in
[`CHANGELOG.md`](CHANGELOG.md).

## Use a branch and a pull request

1. Create a branch.
2. Make the change on the branch.
3. Complete the [pull request template](.github/pull_request_template.md).
4. Add the applicable board entry.
5. Add the test evidence.
6. Check the version requirement.
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

## Compliance status

`NOT RELEASED — COMPLIANCE CHECK INCOMPLETE`

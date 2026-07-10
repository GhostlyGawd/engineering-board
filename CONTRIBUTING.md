# Contributing to engineering-board

Thanks for being here. engineering-board is a native Claude Code plugin and a
zero-dependency MCP server, both driving one git-committed markdown board. It is
built to be easy to contribute to: no toolchain to install, no service to stand
up, no hidden database. If you have `bash` and `python3`, you can run everything.

This guide covers how to get a change merged. For the deep system map — how the
hooks, skills, agents, and the board format fit together — read
[`ARCHITECTURE.md`](ARCHITECTURE.md).

## The one thing that matters: keep the suite green

The whole test suite is `bash` + `python3` only, with **no install step**:

```sh
bash tests/run-all.sh   # 16 suites
```

That command is the merge gate. A change lands when it is green and stays green.
There is no other build to learn, no dependency to fetch — clone the repo and run
it. If it passes for you locally, it passes in CI
([`.github/workflows/test.yml`](.github/workflows/test.yml) runs the same command
on every push).

The rule for what a change must carry:

- **New behavior ships with tests** that pin it.
- **Changed behavior ships with changed tests** that pin the new behavior.

A green suite over an untested change is not green — it is silent. If you are not
sure where a test belongs, open a draft PR and ask; we would rather help you place
it than merge it without one.

## Where things live

| Directory | What's in it |
|---|---|
| `commands/` | Slash commands (`/board-init`, `/pm-start`, `/worker-start`, …) as markdown |
| `agents/` | Subagents — the PM pipeline and worker pipeline, plus the `board-manager` router |
| `skills/` | The four board skills (`board-intake`, `board-triage`, `board-resolve`, `board-consolidate`) |
| `hooks/` | Hook wiring (`hooks.json`), the Stop procedure, and `hooks/scripts/*.sh` — the deterministic core |
| `mcp-server/` | The zero-dependency `python3` MCP server and its tests |
| `tests/` | The suite — one directory per domain; `run-all.sh` is the runner |
| `references/` | Shared protocol docs the agents load (auto-resolve pass, required permissions) |

The board itself, when scaffolded, lives at `engineering-board/<project>/` — human
visible, committed, diffed in the same PRs as code. This repo dogfoods its own
board at `engineering-board/eb-self/`.

## Cross-compat rules for hooks and scripts

Any new or edited `hooks/scripts/*.sh` must pass `tests/crosscompat-lint.sh`. The
board runs on machines we don't control, so the rules are strict and mechanical:

- Shebang is **exactly** `#!/usr/bin/env bash`.
- No `date -d` and no `date -j -f` (GNU-only / BSD-only date math is banned).
- No `jq`.
- No drive letters in paths.
- Use `python3` for anything involving JSON or timestamps — it is the one
  interpreter present everywhere and gives you portable date and JSON handling.

Board location is resolved in exactly one place: source `hooks/scripts/board-paths.sh`
and call `eb_board_dirs` / `eb_board_rows` / `eb_router_path`. Do not re-hardcode
`docs/boards/` or `engineering-board/` anywhere else.

## Version bumps move in lockstep

When a change is user-facing, bump the version in **both** manifests together:

- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`

`tests/version-coherence.sh` fails if they diverge. A fix only reaches installed
plugins when the version increases, so a shippable fix without a bump is a fix no
user receives. Also update [`CHANGELOG.md`](CHANGELOG.md) under `[Unreleased]`.

## Workflow: branch, then PR

- Develop on a branch. **Never push to `main` directly** — every change lands via
  a pull request.
- Fill in the [pull request template](.github/pull_request_template.md): the
  summary, which board entry it resolves, your test evidence
  (`bash tests/run-all.sh` green plus any new or changed tests), the version-bump
  checklist, and the surface-coherence check (README and docs still match
  behavior).
- CI runs `run-all` on your push. Keep it green.

## Adding a test

Tests are plain `bash`. To add one:

1. Put it in the matching domain directory under `tests/` (e.g. a claim-locking
   test goes in `tests/claims/`, a reject-filter fixture goes in `tests/security/`).
2. Register it so `tests/run-all.sh` picks it up — follow the pattern of the
   neighbouring tests in that directory's runner.
3. Run `bash tests/run-all.sh` and confirm your suite count went up and everything
   is green.

Security fixtures are especially welcome. The injection corpus at
`tests/security/reject-filter.sh` grows with every pinned bypass — a fixture that
declares its expected `expect:` / `expect_reason:` and drives the canonical filter
is exactly the shape we want (see [SECURITY.md](SECURITY.md) for the posture).

## First contributions

Look for issues labelled **good first issue**. Small, well-scoped, and a good way
to learn where things live. Questions before you start are welcome — open a
[Discussion](https://github.com/GhostlyGawd/engineering-board/discussions) or a
draft PR. We would rather talk early than review a large change built on a wrong
assumption.

## License

By contributing, you agree that your contributions are licensed under the
project's [MIT License](LICENSE).

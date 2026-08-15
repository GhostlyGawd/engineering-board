# Codex hook boundary and SessionStart truth — 2026-08-15

## Purpose

This file is the durable workpad and dated evidence record for the B071 through
B076 dogfood checkpoints. The checkpoints reduce host-specific false state and
recurring errors without treating board activity as product value.

## Authoritative outcome

Engineering Board must deliver relevant, source-linked repository memory when
an agent makes an engineering decision. This memory must help the agent
investigate a system-level cause before it applies another local correction.
Explicit outcomes must improve the memory that a later agent receives.

The optional task loop supports this outcome. Task movement, closed entries,
test totals, commit totals, and release totals do not prove this outcome.

## Critical workflows and scorecard

The checkpoint protects installation and initialization, evidence capture and
explicit promotion, graph and hypothesis construction, decision-time context,
outcome feedback, claims, Claude hook behavior, Codex MCP behavior, and release
truth.

The maintenance scorecard requires truthful host status, deterministic graph
and context repeats, an empty unrelated control, source-linked top-three
retrieval, correct claim contention and release, context under 4 seconds,
SessionStart under 10 seconds, an installed commit equal to its immutable tag,
and semantically aligned current documentation. It does not claim the separate
diagnosis-effect gate, whose latest locked evidence remained below its accepted
25-point comparative threshold.

## Preserved baseline

- A Codex 0.145.0 session loaded the default Claude `hooks/hooks.json`. Codex
  skipped the prompt Stop handler and reported a Stop failure after each turn.
- Without `CLAUDE_PROJECT_DIR`, SessionStart reported that the board was not
  initialized and `board-stop-gate.sh` exited on an unbound variable.
- With the repository root supplied, SessionStart reported seven open rows.
  The canonical `## Open` section contained B071 through B073 only. Four rows
  came from the `## Conventions` section.
- The focused SessionStart suite passed because its fixture omitted the
  standard Conventions footer.
- Acquiring B071 through B073 claims added an untracked
  `engineering-board/eb-self/_claims/` path. The repository did not apply the
  runtime exclusions that `/board-init` already recommends.

## Checkpoint hypotheses

1. The Codex manifest omits an explicit hook source, so Codex falls back to the
   default Claude hook file. An explicit Codex-safe hook source will preserve
   the advertised MCP workflow and prevent Claude-only hook failures.
   B071 is therefore a host-loading defect. Direct manual execution of a Claude
   adapter without its host-provided environment remains outside the Codex
   contract and is not reclassified as a supported path.
2. SessionStart scans all of `BOARD.md` instead of the canonical `## Open`
   section. Section-bounded extraction will remove convention false positives
   without changing valid open rows or the performance bound.
3. The product contract identifies board claims and scratch as disposable
   runtime state, but this self-hosted repository does not ignore those paths.
   Applying the documented runtime stanza will keep canonical memory visible
   while removing claim and capture noise from repository status.
4. Current version markers were omitted from coordinated release preparation,
   so a green version-coherence test could leave Architecture, Security, and
   the authoritative product spec stale. Adding these markers to the same
   release plan will make later drift fail closed.
5. Dated root audits preserve useful historical observations but do not state
   that their counts and runtime claims are superseded. An opening historical
   boundary will preserve the record without presenting it as current truth.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| Codex uses skills and the MCP server without requiring Claude hook scripts | Required | Declare an explicit Codex-safe hook source in `.codex-plugin/plugin.json` | Pin manifest selection and the declared packaged hook shape in `tests/codex-plugin.sh` | README, architecture, product-direction spec, security, changelog | Focused check passed; installed check pending |
| SessionStart reports only canonical open rows | Required | Restrict `board-session-start.sh` to the exact `## Open` section | Add empty and one-entry fixtures with the standard Conventions footer | Architecture test matrix, changelog | Local validation and independent review passed; merged-main check pending |
| Self-hosted runtime paths do not dirty repository status | Required | Apply the documented runtime exclusions in `.gitignore` | Pin the self-host exclusions in the board-init contract test and inspect `git check-ignore` | Changelog and this dated evidence | Local validation and independent review passed; merged-main check pending |
| Current behavior and historical snapshots remain distinguishable | Required | No runtime change | Reject superseded section-5 claims and require opening audit banners in `tests/docs-coherence.sh` | Product spec and three dated root audits | Local validation and independent review passed; merged-main check pending |
| Release preparation advances semantic version markers | Required | Update `scripts/prepare-release.py` with Architecture, product-spec, and supported-minor markers | Immediate patch fixture, independent minor fixture, and documentation coherence | Release skill, release procedure, architecture, changelog | 1.13.2 plan applied; merge and publication pending |
| B071 through B076 have falsifiable completion evidence | Required | Update canonical entry lifecycle only after validation | Baseline, negative control, post-change, merged-main, and installed-artifact checks | This dated evidence file | In progress |
| Current versions and context-contract descriptions agree | Required | No runtime change | Version and documentation coherence checks plus semantic review | Architecture, security, and product-direction spec | Corrected locally; release version pending |
| Release and installation claims name exact immutable evidence | Required | Use the documented patch-release process only after merged-main validation | Release workflow, asset checksum, registries, fresh WSL install | Changelog and closeout evidence | Post-merge pending |

## Drift classification

- Required conflict: Codex auto-loads a Claude-only prompt hook although the
  accepted Codex product boundary does not require Claude hooks.
- Required conflict: SessionStart reports convention text as open state.
- Required security-boundary drift: the Codex manifest does not enforce the
  documented separation from Claude-only automatic hooks.
- Documentation-only drift: current release, supported-minor, and
  context-contract text is stale in current-truth surfaces.
- Reviewed and unaffected: canonical Markdown authority, graph semantics,
  context ranking behavior, hypothesis authority, outcome semantics, and
  visual behavior do not change because these checkpoints alter only host
  manifest routing, one derived-board section reader, repository ignore policy,
  and documentation. The shared core, MCP schemas, H### and L### records,
  renderer, and visual assets are untouched.

## Local checkpoint evidence

- Codex plugin contract: the new host-boundary test first failed because
  `hooks/codex-hooks.json` did not exist. It passed after the manifest selected
  the explicit empty source. The launcher still exposed 19 tools.
- SessionStart: the realistic standard-board fixture produced 10 passes and 3
  failures before the change. It produced 13 passes and 0 failures after the
  section-bounded parser. The 1,200-entry case completed in 4.27 seconds.
- Portability: `tests/crosscompat-lint.sh` produced 30 passes and 0 failures.
- Self-hosting: the repository-hygiene checks produced 34 passes and 4 failures
  before the `.gitignore` change, then 48 passes and 0 failures after positive
  runtime-path, negative canonical-path, and tracked-canonical controls were
  added. `git
  check-ignore` mapped claims and scratch to the project-runtime patterns and
  derived cache state to `.engineering-board/`.
- Five previously tracked `_sessions/_archive` files were removed from the
  current tree. Every unique finding remains canonical as B065 through B073;
  B065 through B070 remain in the archive index, B071 through B073 remain live,
  and consolidation receipts remain tracked. Git history retains the removed
  runtime copies.
- A real claim and two real capture/promote cycles added no untracked claim,
  scratch, or hidden runtime path after the ignore change. The only runtime-path
  status entries are the five intentional tracked-file deletions above.
- Real board control: SessionStart reported six open rows and rendered exactly
  B071 through B076 from `## Open`. It rendered no Conventions example.
- Documentation coherence confirmed five Engineering Board skills and 19 MCP
  tools, current release and context-contract markers, current section-5
  behavior, and historical audit boundaries.
- An intermediate complete suite produced 21 passing suites and no failures in
  70.3 seconds before B075, B076, release-preparation coverage, and archive
  cleanup. This result is superseded.
- A later product diff produced 21 passing suites and no failures in 60.3
  seconds, but its release test selected only a minor bump. That result is
  superseded because it did not exercise the planned patch path.
- The corrected release test restored the immediate-patch fixture and added an
  independent minor-release apply. It produced 16 passes and no failures. The
  final complete suite then produced 21 passing suites and no failures in 62.3
  seconds. An independent review reran the same suite in 62.4 seconds with the
  same result and found no release blocker. These results prove repository
  checks only; installed Codex behavior, pull-request CI, merged-main CI, and
  release publication remain separate gates.
- Coordinated release preparation applied version 1.13.2 on 2026-08-15. The
  prospective and applied MCP bundle SHA-256 is
  `afd0b48b4c7c9ed2bef1b056f3908aeb5e9bdbecf4285e81f4415ad921fb3a9e`.
  Security remained on supported minor 1.13.x, as required for a patch release.
- The exact 1.13.2 release-prepared tree produced 21 passing suites and no
  failures in 55.7 seconds. Version coherence reported 1.13.2, release
  preparation reported 16 passes, and the Codex plugin still exposed 19 tools.

## Delivery state

Completion state: `post-merge-pending`.

External gates: pull-request CI, exact merged-main CI, patch release, registry
verification, and a fresh WSL installed-plugin pass.

Evidence destination: this file for worker and post-merge observations; a
separate dated closeout file if release evidence requires a follow-up pull
request.

Terminal action: keep B071 through B076 open until merged-main and installed
behavior satisfy their named criteria.

## Superseding closeout

The post-merge gates completed later on 2026-08-15. PR #150 merged as
`2db7cd13fb1337e98e31e6fa3bf33390520ad995`; exact merged-main tests, Pages,
dependency-graph, release workflow, GitHub Release, PyPI, MCP Registry, WSL
reinstall, installed hook-boundary checks, installed SessionStart, and direct
installed MCP checks passed. The separate
`2026-08-15-v1.13.2-release-and-installed-validation.md` record contains the
immutable values and evidence boundaries. B071 through B076 can resolve.

The installed dogfood pass also found that non-interactive Codex tool calls
were cancelled during approval elicitation. A separate `tools/list` check
showed no read/write annotations. B077 records both observations and requires a
controlled test before it attributes causality. The cancelled calls are not
counted as a pass for the successful-call gate.

# B021 reviewer contract evidence

- Date: 2026-08-14
- Repository: `GhostlyGawd/engineering-board`
- Base commit: `ce16d982a6395f2c416298ee5c37c0558af65955`
- Board entry: `B021`
- Completion state: `closeout`
- Implementation pull request: `#128`
- Implementation merge commit:
  `c06d6bdbe8293965b6f1a030b8484aaa96c75f94`
- Implementation merged-main run: `31808165945` (`tests`, passed)
- Evidence destination: this file
- External gates: closeout pull request merge and passing merged-main continuous
  integration
- Terminal action: resolve B021 in this closeout change, merge the closeout pull
  request, and verify its merged-main run

## Decision

Keep the registered `code-reviewer` name because the Worker-mode router uses
that identifier. Document that this internal worker is not the harness
`/code-review` or `/review` skill. Remove `Write` and `Edit` from its tool grant
so the configured capability matches the existing no-file-writes contract.

This change does not prepare a release or change a version. An installed
package remains unchanged until a later owner-authorized release includes the
Unreleased change.

## Alignment workpad

| Contract item | Normative level | Implementation | Test | Docs/example | Status |
|---|---|---|---|---|---|
| The review worker cannot modify repository files. | Required by B021 and the agent output contract. | `agents/code-reviewer.md` grants `Read`, `Bash`, `Grep`, and `Glob` only. | `tests/modes/agent-frontmatter-disciplines.sh` requires the read tools and rejects `Write` or `Edit`. | `ARCHITECTURE.md` identifies the worker as read-only and records no writes. | Implementation and merged-main evidence pass. |
| The registered name does not imply that this worker is a user-facing review skill. | Required alternative in B021. | The prompt has an Identity and scope section that distinguishes the internal worker from `/code-review` and `/review`. | The focused mode test requires both distinctions. | `ARCHITECTURE.md` records the distinction. The dated resolution note in RFC 0002 supersedes its rename recommendation. | Implementation and merged-main evidence pass. |
| Existing Worker-mode routing remains compatible. | Implementation choice. | The file name and `name: code-reviewer` stay unchanged. | Existing mode-routing and orchestration suites cover the registered identity. | `hooks/stop-hook-procedure.md`, `commands/board-run.md`, and README references remain accurate. | Implementation and merged-main evidence pass. |
| Current product and release documentation matches the capability change. | Required alignment invariant. | No release or manifest changes. | Version-coherence and release tests pass in the maintained suite. | `CHANGELOG.md` records the Unreleased fix. Historical snapshots and controlled-English evidence remain unchanged. | Implementation and merged-main evidence pass; closeout evidence pending. |

## Drift classification

- Required conflict, resolved: the agent granted `Write` and `Edit` while its
  contract prohibited file changes.
- Documentation-only drift, resolved: `ARCHITECTURE.md` described write tools
  and review-note writes that the agent contract did not permit.
- Documentation-only drift, resolved with a superseding note: RFC 0002
  recommended a rename. The implementation keeps the routing identity and
  documents the collision, which B021 permits.
- Reviewed and unaffected: `hooks/stop-hook-procedure.md` and
  `commands/board-run.md` continue to route by `code-reviewer`; the identity did
  not change.
- Reviewed and unaffected: README only lists the registered agent name. Its
  statement remains correct.
- Reviewed and unaffected: `SECURITY.md` does not enumerate Worker-mode tool
  grants. This change narrows capability and does not weaken its untrusted-data
  boundary.
- Reviewed and unaffected: the Codex plugin does not package Claude worker
  agents. Its manifest, setup, security, and privacy behavior do not change.
- Reviewed and unaffected: `.goal/PRODUCT_FACTS.md`, `.goal/LOOP_PROGRESS.md`,
  the 2026-06-08 ecosystem profile, and `docs/asd-ste100/` are historical
  records. Updating them would corrupt their recorded source state.
- Reviewed and unaffected: visuals do not expose worker tool grants or the
  distinction between internal and harness review surfaces.

## Validation evidence

- Red phase: the focused discipline test reported 44 passes and 3 failures on
  the original implementation. The failures identified `Write`, `Edit`, and
  the missing review-surface distinction.
- Green phase: the focused discipline test reports 47 passes and 0 failures.
- Focused routing evidence: all six mode groups pass; prompt lint passes for
  10 of 10 framing files; the board-run contract passes 18 checks.
- Maintained repository suite: 20 of 20 suites pass with exit code 0.
- Implementation pull request: #128 merged as `c06d6bd`.
- Pull-request checks: runs 31808030059 and 31808053423 passed.
- Implementation merged-main run: 31808165945 passed.
- Closeout pull request and merged-main run: pending.

Passing checks establish only their named invariants. They do not establish
perfect semantic correctness or formal controlled-English compliance.

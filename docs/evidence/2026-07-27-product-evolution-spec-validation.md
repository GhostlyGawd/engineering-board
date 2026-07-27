# Product Evolution Spec Validation — 2026-07-27

## Scope

Validation for the initial Gate 1 draft in
[`docs/PRODUCT_EVOLUTION_SPEC.md`](../PRODUCT_EVOLUTION_SPEC.md).

Repository baseline:
`GhostlyGawd/engineering-board` `main` at
`4ee6c5239e152b20c4c2a07ef0c4d4fceefa48f3`.

This change adds a planning document and repairs two current-truth documentation
conflicts. It does not change product behavior, configuration, state schemas,
security boundaries, releases, or external integrations.

## Drift review

| Surface | Classification | Evidence and disposition |
|---|---|---|
| README capture confirmation | Documentation-only drift, repaired | `hooks/stop-hook-procedure.md` surfaces `EB-CAPTURE-SUMMARY` after a successful non-empty append, while README still described capture as deliberately silent. README now describes the shipped one-line confirmation. |
| Landing-page setup command | Documentation-only drift, repaired | `commands/board-setup.md` is the canonical smart setup path, while `docs/index.html` still directed plugin users to lower-level `/board-init my-project`. The landing snippet now uses `/board-setup`. |
| Historical activation and retention audits | Reviewed and preserved | The reports are dated evidence. The living spec explicitly warns that their findings require current-code verification and records the shipped capture fix instead of rewriting history. |
| Architecture and command contracts | Reviewed and unaffected | No behavior or state transition changes were made. Proposed commands are labeled as unimplemented and gated. |
| MCP server documentation | Reviewed and unaffected | No MCP tool or capability changed. The spec distinguishes proposed parity work from current tools. |
| Security and privacy | Reviewed and unaffected | No credential, network, execution, storage, or trust boundary changed. |
| Versions, releases, and manifests | Reviewed and unaffected | No version, tag, package, release, or manifest claim changed. Open PR #93 remains independent. |
| Current visuals | Reviewed and unaffected | No renderer or visual asset changed. Future visual work is labeled proposed. |

## Deterministic validation

Run from the isolated `docs/product-evolution-spec` worktree:

```text
bash tests/scratch/append.sh
  14 pass, 0 fail

bash tests/modes/stop-hook-mode-routing.sh
  98 pass, 0 fail

bash tests/orchestration/board-setup-command.sh
  9 pass, 0 fail

bash tests/docs-coherence.sh
  pass (12 MCP tools; 14 plugin commands across checked current-truth surfaces)

bash tests/token-coherence.sh
  pass (105 token comparisons across the landing page and board renderer)

git diff --check
  pass
```

A local Markdown-link inventory resolved every repository-relative link in the
living spec. External links were not treated as deterministic local evidence.

## Evidence limits

- No implementation or live product journey changed, so no new first-run or
  browser validation is claimed.
- The acceptance criteria in the living spec are proposed outcomes, not proof
  of current readiness.
- Public competitor references are research inputs, not compatibility or
  conformance claims.

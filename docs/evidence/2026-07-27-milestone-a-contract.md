# Milestone A Contract Evidence — 2026-07-27

## Scope

This record accompanies the Gate 2 Milestone A contract in
[`docs/PRODUCT_EVOLUTION_SPEC.md`](../PRODUCT_EVOLUTION_SPEC.md).

The owner approved the hypothesis-authority direction on 2026-07-27:

- root-cause hypotheses may be retained durably as `status: proposed`;
- investigation or fix outcomes are required for confirmation;
- rejected hypotheses remain durable negative knowledge;
- recurrence and confidence cannot independently establish causation.

This approval advances planning into a file-level implementation contract. It
does not authorize implementation.

## Contract rationale

Milestone A uses a synthetic, contained scenario with three symptoms across
worker routing, HTML rendering, and MCP ready-work output. The shared
`duplicated-state-contract` pattern demonstrates the product's intended
cross-domain intelligence without claiming that the synthetic entries are
current production defects.

The implementation contract requires:

- canonical synthetic Markdown evidence;
- deterministic graph and cluster facts;
- a separate, evidence-linked proposed hypothesis;
- negative and singleton controls;
- no mutation of real boards or settings;
- fingerprinted cleanup that refuses changed scope;
- no additional service dependency beyond the active agent runtime;
- a real sanitized visual generated from observed output.

## Documentation alignment

| Surface | Classification | Disposition |
|---|---|---|
| Product-direction decision ledger | Documentation-only direction update | Hypothesis authority is now accepted and dated in the central spec. |
| Open-decision inventory | Documentation-only drift, repaired | Hypothesis authority moved from an open recommendation to an accepted decision. |
| Gate 2 plan | New normative planning contract | Milestone A now has command, data, authority, component, failure, test, validation, documentation, and delivery boundaries. |
| Runtime implementation | Reviewed and unaffected | No command, script, schema, hook, MCP tool, UI, dependency, or setting changed. |
| README, setup, landing page, architecture, and MCP docs | Reviewed and unaffected | The contract identifies future required updates but makes no unshipped behavior claim on current-truth surfaces. |
| Security and privacy | Reviewed and unaffected | The contract proposes future containment rules; no current trust boundary changed. |
| Versions, releases, manifests, tags, and deployment | Reviewed and unaffected | No release action or version claim is authorized. |
| Existing visuals | Reviewed and unaffected | A future real demo visual is required; no visual is fabricated for planning. |
| Historical evidence | Reviewed and preserved | Earlier dated reports remain unchanged. |

## Evidence limits

- The proposed fixture and interfaces have not been implemented or executed.
- Test names and component paths are contract targets, not proof of existence.
- The expected hypothesis is a synthetic demonstration target, not a finding
  about current released behavior.
- No first-win timing, cleanup safety, no-extra-service behavior, or visual
  result is claimed until live validation records it.

## Deterministic validation

Run after the planning revision:

```text
bash tests/orchestration/board-setup-command.sh
  9 pass, 0 fail

bash tests/orchestration/board-graph-command.sh
  52 pass, 0 fail

bash tests/docs-coherence.sh
  pass (12 MCP tools; 14 plugin commands across checked current-truth surfaces)

bash tests/token-coherence.sh
  pass (105 token comparisons across the landing page and board renderer)

git diff --check
  pass
```

All 13 repository-relative paths linked from the central product spec were
confirmed to exist. These checks protect current documentation and command
contracts; they do not prove the unimplemented Milestone A design.

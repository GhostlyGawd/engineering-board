# Milestone B contract evidence — 2026-07-27

## Scope and authority

This report records the observed baseline and planning evidence used to draft
the Milestone B implementation contract in
[`PRODUCT_EVOLUTION_SPEC.md`](../PRODUCT_EVOLUTION_SPEC.md). The product owner
accepted the Milestone B direction on 2026-07-27. The implementation contract
remains proposed pending explicit Gate 2 approval.

Observed repository state:

- repository: `GhostlyGawd/engineering-board`;
- default branch: `main`;
- baseline commit: `88eb16451a140463e7f5ef1de80dab8c52ca519f`;
- released version: `v1.8.0`;
- portfolio state: `inventory-only`;
- portfolio audit source:
  `GhostlyGawd/repo-audit@907f0759f9d08f478cd5384ad88e50963f1af79a`.

No runtime implementation, release, tag, deployment, tool-count change, or
canonical board migration is claimed by this report.

## Observed current workflow

- Entry Markdown uses free-form readable `pattern` labels without stable
  pattern IDs or a canonical alias registry.
- `hooks/scripts/board-graph-build.py` is the executable deterministic graph
  engine used by the contained demo and accepts an explicit board path.
- `/board-graph` remains a Markdown command contract, while the MCP server has
  no equivalent graph tool.
- The intake skill, Stop-hook consolidator, and MCP create/capture paths have
  separate write and promotion implementations.
- Passive plugin capture requires PM-mode consolidation or a foreground intake
  action; MCP scratch capture remains for later explicit promotion.
- Graph rebuild has no disposable incremental cache or full-versus-incremental
  equivalence contract.
- Existing exact-label recurrence, the v1.8.0 synthetic demo, canonical
  Markdown, PM/Worker modes, and the TDD/review/validate loop remain working
  compatibility surfaces.

These observations establish the present limitation: real findings can be
captured, tagged, and graphed, but stable pattern identity, promotion behavior,
and graph semantics are not yet shared across adapters.

## Contract choices

- Canonical evidence remains visible Markdown.
- Reviewed patterns become durable `P###` Markdown records with labels and
  aliases; legacy labels remain readable compatibility input.
- Unknown or suggested equivalence remains unresolved until explicit apply
  authority creates or assigns a canonical identity.
- Plugin and MCP adapters share one zero-dependency parser, resolver, and graph
  implementation.
- Foreground promotion and pattern mutation are preview-first and bound to an
  unchanged input fingerprint.
- Incremental state is disposable, Git-ignored, and rebuild-equivalent; it does
  not become a database or second authority.
- Root-cause hypothesis reasoning remains Milestone C scope.

## Documentation alignment review

- **Central product direction — updated.** Milestone B Gate 1 acceptance,
  accepted normalization/promotion decisions, and the proposed Gate 2 contract
  are recorded in the authoritative spec.
- **Roadmap — reviewed, unaffected.** Its existing precedence notice explicitly
  makes the newer product spec authoritative, so historical audit-derived work
  remains planning evidence rather than conflicting current direction.
- **Implementation and tests — reviewed, unaffected.** This change is a plan;
  no behavior or test contract is advertised as shipped.
- **README, setup, commands, MCP docs, architecture, security, examples, and
  visuals — reviewed, unaffected.** Their v1.8.0 current-behavior claims remain
  correct. The Gate 2 documentation-impact contract identifies what must change
  with implementation.
- **Versions, release, and deployment — reviewed, unaffected.** The current
  release remains v1.8.0.
- **Historical evidence — reviewed, preserved.** Milestone A implementation and
  v1.8.0 release reports were not rewritten.
- **Portfolio governance — reviewed, unaffected.** The work stays inside
  Engineering Board and creates no repository, cross-repository route,
  migration, or portfolio lineage decision.

The central spec retains the single normative documentation-and-behavior
alignment table. Test matrices in the proposed contract define future
falsifiable proof and are not implementation evidence.

## Planning-change validation

Observed on 2026-07-27:

- complete repository runner: 16 suites passed, 0 failed;
- orchestration aggregate: 22 passed, 0 failed;
- permissions aggregate: 29 passed, 0 failed;
- board-view aggregate: 50 passed, 0 failed;
- documentation, version, and design-token coherence: passed;
- changed local Markdown link targets: present;
- `git diff --check`: passed.

These checks establish that the planning change did not break the existing
release tree. They do not prove the proposed Milestone B behavior, which remains
unimplemented and must satisfy section 18's future acceptance matrix.

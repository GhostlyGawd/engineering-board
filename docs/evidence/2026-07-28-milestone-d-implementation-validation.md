# Milestone D implementation validation — 2026-07-28

## Outcome

Milestone D implements the accepted context-to-outcome memory loop.

Before an agent selects a fix, the shared core retrieves relevant repository
memory from task, path, entry, and current-directory signals. After
verification, an explicit outcome records whether the fix held, failed, was
partial, or was inconclusive. A separate Learning plan converts accumulated
outcomes into durable and correctable L### state.

Canonical Markdown remains the authority. Context briefs, relevance scores,
the value report, graph files, cache files, and HTML are derived state.

## Implemented surfaces

- Shared deterministic context, outcome, Learning-feedback, curator, and
  value-report functions in `mcp-server/engineering_board_core.py`
- `board_context` and `board_outcomes` MCP tools
- `/board-context` and `/board-outcome` plugin commands
- Shared command-line adapters in `hooks/scripts/`
- Read-only SessionStart and relevant UserPromptSubmit context retrieval
- Structured H### outcome history
- Outcome-aware L### state, confidence, basis, and references
- Normal-view value evidence, hypothesis outcome counts, and Learning state
- Updated schemas, skills, product guidance, architecture, security guidance,
  MCP reference, landing page, LLM guide, and visual evidence

## Authority and safety

Automatic adapters can read bounded context. They cannot change canonical
state. An unrelated prompt produces no injected context.

H### and L### changes use separate content-bound preview and apply operations.
Apply revalidates canonical inputs under the applicable repository-local lock
and atomically changes one file. A context token proves the surfaced memory
source and identifiers. It does not authorize a write and does not retain raw
task text.

The implementation does not add SQLite, embeddings, a hosted service,
telemetry, cross-repository aggregation, autonomous fix execution, or
Milestone E planning.

## Deterministic evidence

The Milestone D lifecycle fixture passed 11 checks:

```text
Milestone D context and outcome intelligence matrix: 11 checks passed
```

The fixture verifies:

- equal context output for equal canonical input;
- no canonical write during retrieval or outcome preview;
- a lexical decoy without structural evidence returns no result;
- shared-core, command-line, and MCP context parity;
- malformed and unsafe context refusal;
- outcome compatibility and evidence validation;
- atomic H### outcome apply and idempotent replay;
- separate L### plan and apply;
- supported and contested Learning state;
- a value report without prompt or session counts;
- equal logical retrieval after graph and cache deletion.

The complete orchestration suite passed:

```text
ORCHESTRATION TEST SUMMARY: 25 pass, 0 fail
```

The focused hook and view suites passed:

```text
prompt guard: 5 pass, 0 fail
SessionStart: 11 pass, 0 fail
board view: 52 pass, 0 fail
```

The 1,200-entry SessionStart fixture completed within the 10-second hook
boundary. It used the real shared context adapter and completed in
approximately 4.62 seconds on the validation host.

Complete release-tree, pull-request, merged-main, publication, registry,
package, and product-site results belong to the later delivery phases. The
v1.11.0 release-validation report will record the external evidence without
rewriting this report.

## Documentation alignment

Changed current-truth surfaces:

- `README.md`
- `ARCHITECTURE.md`
- `SECURITY.md`
- `docs/PRODUCT_EVOLUTION_SPEC.md`
- `docs/index.html`
- `docs/llms.txt`
- `mcp-server/README.md`
- `commands/board-context.md`
- `commands/board-outcome.md`
- `skills/board-insights/SKILL.md`
- `skills/board-resolve/SKILL.md`
- hypothesis and Learning schema references
- the Milestone D contract workpad
- `CHANGELOG.md`

Historical Milestone A-C reports remain unchanged because they describe dated
behavior and validation. Setup mechanics, permissions, the demo fixture, the
canonical storage boundary, and the optional Worker loop remain compatible.

## Current delivery state

```text
state: worker validation in progress
branch: agent/milestone-d-intelligence
baseline: becbb3eaf219c239fbd186c2f749f4067b06cb3e
target_release: v1.11.0
external_gate: complete release tree, PR CI, merged-main CI, publication, and closeout evidence
terminal_action: keep open
```

# Milestone B implementation validation — 2026-07-28

## Scope

This report validates the Milestone B reliable pattern pipeline implemented at
source commit `1d910f8`. It supersedes the implementation-pending observations
in the Milestone B contract evidence. It does not rewrite the v1.8.0 historical
release record.

The validated release candidate is v1.9.0. Repository-owned Markdown remains
canonical. SQLite, embeddings, hosted services, cross-repository aggregation,
and Milestone C hypothesis reasoning are not part of this delivery.

## Outcome

The implementation satisfies the accepted production-generalization contract:

- foreground plugin intake, PM consolidation, and MCP use one parser, pattern
  resolver, promotion planner/writer, receipt model, and graph engine;
- reviewed patterns use durable P### records with unique normalized labels and
  aliases;
- legacy labels remain visible evidence and appear as typed unresolved
  identities;
- graph edges carry canonical pattern identity and entry-field provenance;
- full, incremental, and cache-deleted builds return equal logical facts;
- preview/apply, stale-plan, partial-write, linked-input, and concurrent-source
  failure paths preserve canonical evidence.

The real sanitized fixture produced:

```text
milestone-b-pattern-pipeline: 15 checks passed
canonical_pattern: P001
cluster_fingerprint: c-a4609c958c398d90
members: B001, F001
unresolved: 1
```

The source fingerprint changes when timestamped fixture Markdown changes. It is
therefore not treated as a timeless value. The stable cluster fingerprint above
is derived from canonical members, relationships, and pattern identity.

## Deterministic evidence matrix

| Sequence | Failure injection | Expected semantic outcome | Durable evidence | Test |
|---|---|---|---|---|
| Create P001 directly, add an alias through the plugin CLI, then create an entry through MCP | Three adapter paths and different readable labels | Every approved alias resolves to P001 through one registry | P001 Markdown, entry `pattern_ids`, GRAPH.yml edge provenance | `milestone-b-pattern-pipeline.sh` |
| Rename P002, then merge it into P001 | Display label and active identity change | P002 remains durable and resolves to P001 without duplicate membership | P002 record with `status: merged`, graph node resolution | `milestone-b-pattern-pipeline.sh` |
| Attempt a new pattern with an existing normalized alias | Alias collision | Validation fails before a file is created | Unchanged canonical Markdown inventory | `milestone-b-pattern-pipeline.sh` |
| Create an entry with an unreviewed free-form label | No matching P### | The label stays visible as `legacy:<label>` and creates no pattern record | Entry Markdown and typed `unresolved_patterns` | `milestone-b-pattern-pipeline.sh` |
| Correct B001 from P001 to P002 with a reason | Deliberately bad prior assignment | Only B001 changes; correction history remains durable; rebuilt graph follows the new identity | B001 `pattern_ids`, `## Pattern history`, GRAPH.yml | `milestone-b-pattern-pipeline.sh` |
| Build full, unchanged incremental, then delete cache and rebuild | Cache miss and cache deletion | Logical graph facts remain equal; cache is recreated from Markdown | Source fingerprint and compared graph payloads | `milestone-b-pattern-pipeline.sh` |
| Modify canonical Markdown after graph scan but before replacement | Concurrent source change | Builder returns `source_changed`; prior cache bytes remain intact | Preserved sentinel cache and typed error | `milestone-b-pattern-pipeline.sh` |
| Preview four scratch findings: new, same-batch duplicate, existing duplicate, invalid type | Mixed promotion outcomes | Preview writes no canonical state and returns create, deduplicated, and rejected outcomes | Content-bound plan and per-finding result set | `milestone-b-pattern-pipeline.sh` |
| Apply a two-finding plan with an injected write failure on the second finding | Partial filesystem failure | First finding is created once; second is deferred; scratch remains; retry sees `already_applied` plus one create | Entry provenance and consolidation receipts | `milestone-b-pattern-pipeline.sh` |
| Change pattern Markdown after an alias preview | Stale plan | Apply returns `plan_stale` and does not write the alias | Unchanged pattern record | `milestone-b-pattern-pipeline.sh` |
| Present a linked scratch file | Symlink input | Promotion refuses the linked input and writes nothing | Typed linked-input error | `milestone-b-pattern-pipeline.sh` |
| Run the matrix with outbound proxy endpoints set to a closed local port | Outbound service unavailable | Complete pattern pipeline remains green without network or database access | Dated command result in this report | `milestone-b-pattern-pipeline.sh` |
| Run existing plugin, claims, modes, security, view, MCP, documentation, and packaging suites | Compatibility regression opportunity | Existing behavior remains green and coordinated versions/tool counts match | Release-tree suite result and reproducible bundle digest | `tests/run-all.sh` |

## Validation commands

All commands ran from the repository root on 2026-07-28.

```text
bash tests/run-all.sh
RUN-ALL SUMMARY: 16 pass, 0 fail (of 16 suites)

bash mcp-server/run-tests.sh
RESULT: PASS (163 checks)

HTTP_PROXY=http://127.0.0.1:9 \
HTTPS_PROXY=http://127.0.0.1:9 \
ALL_PROXY=http://127.0.0.1:9 \
NO_PROXY= \
bash tests/orchestration/milestone-b-pattern-pipeline.sh
milestone-b-pattern-pipeline: 15 checks passed
```

The reproducible v1.9.0 MCP bundle digest is:

```text
409c0953c87bae4da06b8ad18c5bd0652a994603a0679518b5711cb8fb37ab62
```

`mcp-server/server.json` pins this exact digest. The MCP suite rebuilt the
bundle and matched the pinned value.

## Visual evidence

[`milestone-b-pattern-pipeline.svg`](../assets/milestone-b-pattern-pipeline.svg)
is a sanitized terminal-style rendering of the actual matrix result. Its alt
text states the checked semantic result. The visual contains no personal path,
username, transcript, credential, or secret. Provenance: automated fixture at
source commit `1d910f8`, test
`tests/orchestration/milestone-b-pattern-pipeline.sh`, 2026-07-28.

## Documentation alignment

| Drift class | Disposition |
|---|---|
| Behavior and specification | Repaired. The central product spec records Milestone B as implemented and validated for v1.9.0 while preserving the accepted scope and historical decisions. |
| Commands and setup | Repaired. `/board-promote`, `/board-pattern`, shared `/board-graph`, foreground capture guidance, permissions, and retry behavior are current. |
| Schema and architecture | Repaired. P### records, `pattern_ids`, legacy precedence, correction history, shared-core boundaries, and disposable cache authority are documented. |
| MCP and packaging | Repaired. Fifteen tools, two packaged Python modules, bundle contents, coordinated v1.9.0 manifests, and reproducible digest are current. |
| Security and privacy | Repaired. Preview/apply authority, linked-input refusal, source-change checks, cache boundaries, and untrusted-data handling cover new paths. |
| Landing, LLM index, and visual | Repaired. Tool counts, stable-pattern messaging, and real sanitized fixture evidence are current. |
| Historical v1.8.0 evidence | Reviewed and unaffected. Historical reports remain unchanged. |
| Existing PM/Worker, claims, view, demo, and hypothesis surfaces | Reviewed and behaviorally unaffected except that PM now delegates verified writes to the shared promotion core. Existing suites remain green. |

Path and count checks prevent silent omission but do not prove semantic
alignment. The classifications above record the required implementation and
review judgment.

## Remaining boundary

This is implementation validation, not external publication evidence. GitHub
merge, tag, release asset, Pages deployment, PyPI publication, and registry
publication must be verified after those external operations. Append a dated
release report; do not alter this pre-publication observation.

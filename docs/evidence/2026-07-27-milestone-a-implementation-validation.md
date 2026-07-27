# Milestone A implementation validation — 2026-07-27

## Scope and authority

This report records observed evidence for the accepted Milestone A contract in
[`PRODUCT_EVOLUTION_SPEC.md`](../PRODUCT_EVOLUTION_SPEC.md). Validation ran on
the `docs/product-evolution-spec` branch before review/merge. It does not claim a
release, deployment, merge, or confirmation of the synthetic root-cause
hypothesis.

The implementation keeps four authority layers separate:

1. synthetic Markdown entries are canonical evidence;
2. nodes, edges, and cluster membership are deterministic derived facts;
3. `H001` is agent interpretation persisted only as `status: proposed`;
4. only later investigation or fix evidence may confirm or reject it.

## Observed first-win run

A fresh disposable consumer at
`D:\Codex\Scratch\engineering-board-milestone-a\live-consumer` ran the same
script sequence orchestrated by `/board-demo`.

| Observation | Result |
|---|---|
| Create state | `awaiting_hypothesis`, new run, no reuse |
| Create elapsed time | 1,601 ms |
| Hypothesis validation + render elapsed time | 1,246 ms |
| Total measured script time | 2,847 ms |
| Graph nodes | 3: `B001`, `B002`, `B003` |
| Explainable edges | 3, all from the shared normalized pattern |
| Candidate cluster | `C001`, density `1.0` |
| Affected domains | `board-view`, `hooks`, `mcp-server` |
| Durable interpretation | `H001`, `status: proposed`, explicitly “not confirmed” |
| Tracked run artifacts | 9 plus the manifest |
| Final state | `complete` |
| Reported cleanup | `/board-demo --clean live-validation` |

The static view contained every evidence id, `C001`, the proposed authority
label, supporting evidence, an alternative explanation, and a falsifier.

## Negative and containment checks

The live run was deliberately given one untracked
`operator-note.txt`. Cleanup:

- exited with code `3`;
- returned typed error `cleanup_refused`;
- named `unexpected: operator-note.txt`;
- preserved the entire run.

After removing only that intentional test file, cleanup reported all nine
manifest-owned files and removed the exact run. The run directory no longer
existed. The automated integration test separately hashed a real board router,
real board, source file, Claude settings, and Git configuration before and after
the journey; every hash remained unchanged. It also found no outbound network
client in the demo scripts.

Focused negative tests additionally pin:

- unsafe and traversal run ids;
- malformed graph input and duplicate ids without partial output;
- missing or extra evidence citations;
- attempted `confirmed` authority;
- missing alternatives or falsifier;
- modified, missing, extra, linked, or reparse-point cleanup scope;
- reuse of an unchanged named run and allocation away from a changed run.

## Visual evidence and provenance

![Three synthetic cross-domain findings connect to deterministic cluster C001 and a separate proposed root-cause hypothesis with evidence, an alternative, and a falsifier.](../assets/pattern-intelligence-demo.png)

- Source: a fresh local `visual-source` demo run produced from the implementation
  covered by this report.
- Capture: Microsoft Edge `150.0.4078.99`, headless, `1440 × 1500`, local
  `file:///` URL, no network dependency.
- Source HTML SHA256:
  `4202decbd82f037a3c28743dc68bde81cdb8698c9ac8a5a5a8ff6d3ccc9c8f2a`.
- PNG SHA256:
  `80b2099a5928398a565a446663132740339f23fa2ba05784ed34c3b278280d80`.
- The visual uses bundled synthetic data. It is not a screenshot of current
  production defects.

Relevant implementation fingerprints at validation:

| File | SHA256 |
|---|---|
| `hooks/scripts/board-demo.sh` | `dfcb0513c2e3ae88f349003779d50de8c75cb3410f7da0d1d0e24f473713372c` |
| `hooks/scripts/board_demo.py` | `6b27a63fea79bb70deba4f41ec99d8beca4e330c04d54cc046c173e70ba1d1a9` |
| `hooks/scripts/board-graph-build.py` | `a2414a57b8f458f52ce834524bdb57125bf2b96b5a98ca1daeecd2434a55678c` |
| `hooks/scripts/board-view.sh` | `b9eb56a59db05b0cae96f9c9154e03b83e54288c44ef0e331bf7b54b8f6b9368` |

## Automated validation

Observed on 2026-07-27:

| Gate | Result |
|---|---|
| `/board-demo` command contract | 10 pass, 0 fail |
| Deterministic graph engine | 6 pass, 0 fail |
| Hypothesis authority contract | 7 pass, 0 fail |
| Full first-win integration | 7 pass, 0 fail |
| Orchestration aggregate | 22 pass, 0 fail |
| Board-view aggregate | 50 pass, 0 fail |
| Permission aggregate | 29 pass, 0 fail |
| Cross-platform shell lint | 25 pass, 0 fail |
| Orchestrator untrusted-data framing | pass, 10/10 prompt files |
| Complete repository runner | 16 suites pass, 0 fail |
| MCP server suite inside full runner | pass |

The MCP bundle digest was reproducibly rebuilt and re-pinned because the bundle
contains the plugin hook-script tree. MCP tool behavior and schemas were not
changed, and no bundle was published.

## Documentation drift reconciliation

| Surface | Classification | Disposition |
|---|---|---|
| Central product spec | Behavioral/current-state drift | Gate 2 marked accepted; implementation and pending merge state recorded |
| README and quickstart | Product-writing drift | Pattern intelligence leads; `/board-demo` is the optional first win; verification is supporting feedback |
| Landing page and visual | Product-writing/visual drift | Real evidence → cluster → proposed-hypothesis output replaces the build-loop-first hero |
| Architecture | Structural/current-state drift | Commands, skills, scripts, graph/hypothesis layers, lifecycle, and 16-suite count aligned |
| Security | Security/current-version drift | Demo containment and cleanup refusal documented; supported minor corrected to 1.7.x; HTML-escaping claim repaired |
| Changelog | Unreleased behavior drift | Milestone A behavior and boundaries recorded without a release claim |
| Command/setup/permissions docs | Behavioral/configuration drift | New command, optional setup next step, internal renderer path, and permission manifest aligned |
| MCP documentation | Reviewed, unaffected | No MCP tool, schema, or setup behavior changed |
| Version manifests/releases | Reviewed, unaffected | No version bump, tag, release, upload, or deployment performed |
| Historical reports | Reviewed, preserved | Existing dated evidence was not rewritten; this report supersedes implementation-state observations |

Deterministic gates establish that required surfaces were not silently omitted.
Semantic review remains responsible for the meaning of the product and
epistemic-boundary claims.

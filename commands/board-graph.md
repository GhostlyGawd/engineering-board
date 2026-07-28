---
description: Build a deterministic structural graph (GRAPH.yml) of all open board entries. Same input always produces byte-identical output (modulo generated_at), with no LLM in the construction step. Downstream AI consumers read the structural facts and interpret them at point of use.
argument-hint: [project-name] [--full]
---

# /board-graph — build a deterministic structural graph of the live board

Generates `engineering-board/<project>/GRAPH.yml`: a **purely deterministic**
machine-readable graph of all open entries and canonical pattern records. Same
canonical Markdown produces the same structural facts. No LLM runs in the
construction step.

Downstream AI consumers read the structural facts and interpret them in their own context — interpretation happens at point of use, not at graph-build time.

## Trigger

- `/board-graph` — graph every project in BOARD-ROUTER.md (one GRAPH.yml per project)
- `/board-graph <project-name>` — graph just that project
- `/board-graph <project-name> --full` — bypass the disposable incremental cache

## Output schema

JSON-compatible YAML with these top-level keys:

1. `schema_version`
2. `generated_at`
3. `source_fingerprint`
4. `build_mode`
5. `project`
6. `entries_analyzed`
7. `nodes`
8. `edges`
9. `topology`
10. `unresolved_patterns`
11. `findings`
12. `read_order`, `drill_in`

Use entry IDs (B003, O002, F001) everywhere — never titles.

## Edge kinds — all deterministic

| kind | weight | source | LLM? |
|---|---|---|---|
| `blocked-by` | 3 | frontmatter `blocked_by:` | no |
| `superseded-by` | 3 | frontmatter `superseded_by:` | no |
| `merged-into` | 3 | frontmatter `merged_into:` | no |
| `contradicts` | 3 | frontmatter `contradicts:` | no |
| `shared-pattern` | 2 | same resolved `pattern_ids:` identity, with legacy label fallback | no |
| `shared-affects-prefix` | 2 | overlapping non-null `affects:` prefix | no |
| `shared-tag` | 1 | same non-universal `tag:` (skip tags on >50% of entries) | no |

**No `shared-topic`, no `claim-vs-bug` edges.** If the user wants a semantic connection captured, they add it as either an explicit frontmatter relationship (`contradicts: [F001]`) or a tag/pattern.

**Deduplication**: for the same `{from, to}` pair, keep the highest-weight edge per `kind`; emit multiple edges only if `kind` differs. If two edges of the same kind would be added (e.g. two shared patterns), keep one and concatenate values: `value: "hygiene, entry-lifecycle"`.

## Topology — deterministic graph theory only

- **Clusters** — connected components, treating all edges as undirected.
- **Density** — `internal_edges / (n*(n-1)/2)` for n cluster members, rounded to 2 decimals.
- **Bridge nodes (per cluster)** — cut vertices (articulation points). Removing the node disconnects the cluster. Found by depth-first scan: for each node, check whether removing it would split its cluster into 2+ components.
- **Cross-cluster bridges** — nodes that have edges in 2+ different clusters. (Mutually exclusive with single-cluster bridge nodes by construction.)
- **Isolated** — nodes with zero edges.

## Findings — structured facts only

Each finding is a typed record. No prose. No claims. No "this suggests..." commentary. The downstream consumer interprets.

Finding types:

```yaml
- type: dense-cluster
  members: [B003, O001, O002, O003, Q004]
  density: 0.6
  bridge_nodes: [B003]
  shared_dimensions:
    patterns: [plugin-fork-incomplete]
    tags: [stop-hook, v0.2.4-fork]
  internal_edges: 6

- type: cross-cluster-bridge
  node: B003
  connects_clusters: [cluster-id-1, cluster-id-2]

- type: isolated-node
  node: Q003

- type: pattern-recurrence
  pattern: hygiene
  count: 3
  members: [F003, F004, F006]

- type: contradiction
  from: B002
  to: F001
  via: contradicts-edge

- type: blocked-chain
  entry: B019
  chain: [Q008, Q012]
```

Emit only finding types where the conditions are met. If a board has no contradictions, no `contradiction` findings appear.

Thresholds:
- `dense-cluster` — any connected component with ≥2 nodes
- `cross-cluster-bridge` — any node with edges in 2+ clusters
- `isolated-node` — any node with zero edges
- `pattern-recurrence` — any pattern with count ≥2 across the analyzed corpus
- `contradiction` — any `contradicts` edge
- `blocked-chain` — any entry whose `blocked_by` references chain (depth ≥2 of unresolved blockers)

## Process

### Step 1 — Resolve target board(s)

Resolve the board router in this order (first hit wins): `$CLAUDE_PROJECT_DIR/engineering-board/BOARD-ROUTER.md` (default since 1.1.0), then `$CLAUDE_PROJECT_DIR/docs/boards/BOARD-ROUTER.md` (compat). Target either the named project or all listed. Fall back to `$CLAUDE_PROJECT_DIR/docs/board/` legacy layout if no router.

### Step 2 — Run the deterministic builder

For each target board, run:

```bash
bash "$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-graph-build.sh" \
  --board-dir "<board-dir>" \
  --project "<project-name>" \
  --output "<board-dir>/GRAPH.yml" [--full]
```

Do not reimplement graph parsing or edge construction in the command agent.

### Step 3 — Identify universal tags

Count tag frequency. Any tag appearing in >50% of entries is universal — exclude from `shared-tag` edge generation (zero signal).

### Step 4 — Build edge list

For each pair of entries, emit edges per the kind table above. Deduplicate per the rules. All steps deterministic — no LLM calls.

### Step 5 — Compute topology

Connected components (DFS or union-find). Density per cluster. Cut vertices per cluster. Cross-cluster bridges. Isolated nodes.

### Step 6 — Emit findings

For each finding type whose conditions are met, emit a structured record. No prose generation.

### Step 7 — Write GRAPH.yml

The builder atomically replaces `<board-dir>/GRAPH.yml` only if canonical
Markdown remains unchanged during the build. Its disposable cache is under
`.engineering-board/cache/` and is never authoritative.

### Step 8 — Report

Print to chat: node count, edge count, cluster count, finding count, file path. One sentence, no narrative.

## Notes

- **Determinism is the design.** No LLM in graph construction. Same input → same output. Trivially reproducible.
- **Cheap to regenerate.** Safe to run on every modifying command. Pairs with `/board-rebuild` (which calls it after BOARD.md regen).
- **Interpretation belongs downstream.** Future Claude sessions read `findings` and interpret in their own context. They have richer context than `/board-graph` does at build time.
- **For prioritized interpretation**, use `/board-insights`. It ranks the
  deterministic clusters and links durable H### records without changing graph
  facts. Agent interpretation remains an explicit `/board-hypothesis` step.
- **Staleness is impossible by construction** as long as `/board-rebuild` calls `/board-graph` after every entry change. The cache invalidation problem (B004) goes away.

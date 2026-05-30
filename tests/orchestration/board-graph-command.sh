#!/usr/bin/env bash
# tests/orchestration/board-graph-command.sh — Structural lint for
# commands/board-graph.md.
#
# NEXT-PHASE.md §1.4: "/board-graph: assert deterministic graph output;
# cluster/bridge/isolated-node correctness on fixture boards."
#
# Like /board-rebuild, /board-graph is a markdown command we cannot execute
# from a shell. This lint locks in the procedural contract: deterministic
# construction, the documented edge kinds, the topology vocabulary, the
# finding-type enum, and step ordering. The "correctness on fixture boards"
# half of §1.4 belongs to a future implementation test once the deterministic
# graph builder lands as a script (currently it lives only in the command
# prompt that Claude executes).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

CMD="$ROOT/commands/board-graph.md"

if [ ! -f "$CMD" ]; then
  echo "MISSING FILE: $CMD" >&2
  exit 1
fi

PASS=0
FAIL=0
report() {
  if [ "$1" = "0" ]; then
    printf "  [PASS] %s\n" "$2"
    PASS=$((PASS + 1))
  else
    printf "  [FAIL] %s%s\n" "$2" "${3:+ -- $3}"
    FAIL=$((FAIL + 1))
  fi
}

check() {
  local label="$1" needle="$2"
  if grep -qF -- "$needle" "$CMD"; then
    report 0 "$label"
  else
    report 1 "$label" "missing: $needle"
  fi
}

check_re() {
  local label="$1" pattern="$2"
  if grep -qE -- "$pattern" "$CMD"; then
    report 0 "$label"
  else
    report 1 "$label" "missing regex: $pattern"
  fi
}

# ── Trigger surface ─────────────────────────────────────────────────────────
check "trigger: /board-graph documented"                      "/board-graph"
check "trigger: per-project variant"                          "/board-graph <project-name>"
check "trigger: --include-archive flag"                       "--include-archive"

# ── Determinism is the central contract ─────────────────────────────────────
check "contract: purely deterministic"                        "purely deterministic"
check "contract: byte-identical output (modulo generated_at)" "byte-identical"
check "contract: no LLM in construction"                      "No LLM in graph construction"

# ── Output: GRAPH.yml with the documented top-level keys, in order ──────────
check "output path: GRAPH.yml"                                "GRAPH.yml"
for key in generated_at project entries_analyzed nodes edges topology findings; do
  check "schema: top-level key '$key'"                        "$key"
done

# ── Edge kinds — all 7 documented kinds must remain in the table ────────────
for kind in blocked-by superseded-by merged-into contradicts shared-pattern shared-affects-prefix shared-tag; do
  check "edge kind: $kind"                                    "$kind"
done

# ── Edge-kind weights (the deterministic-rule keys) ─────────────────────────
check "edge weights: 3 for hard relationships"                "| 3 |"
check "edge weights: 2 for shared-pattern / shared-affects"   "| 2 |"
check "edge weights: 1 for shared-tag"                        "| 1 |"

# ── Deduplication rule for same {from,to,kind} pairs ────────────────────────
check "edge dedup: same kind concatenates values"             "concatenate values"

# ── Topology vocabulary: clusters, density, bridge nodes, isolated ──────────
check "topology: clusters (connected components)"             "Clusters"
check "topology: density formula"                             "internal_edges"
check "topology: bridge nodes (cut vertices / articulation)"  "articulation points"
check "topology: cross-cluster bridges"                       "Cross-cluster bridges"
check "topology: isolated nodes"                              "Isolated"

# ── Universal-tag suppression: tags on >50% of entries are skipped ──────────
check "tag handling: universal tags excluded (>50% threshold)" ">50%"

# ── Findings vocabulary — all 6 typed records ───────────────────────────────
for ftype in dense-cluster cross-cluster-bridge isolated-node pattern-recurrence contradiction blocked-chain; do
  check "finding type: $ftype"                                "$ftype"
done

# ── Findings discipline: structured-only, no prose ──────────────────────────
check "findings: no prose, no claims, no implications"        "No prose"
check "findings: structured facts only"                       "structured facts"

# ── Step ordering: resolve boards -> parse -> tag freq -> edges -> topology
#    -> findings -> write -> report.
for step in "Step 1" "Step 2" "Step 3" "Step 4" "Step 5" "Step 6" "Step 7" "Step 8"; do
  check_re "procedure: $step heading present" "^### ${step} —"
done

# ── Findings come AFTER topology (step 6 after step 5) ──────────────────────
TOPO_LINE=$(grep -nE '^### Step 5 — Compute topology' "$CMD" | head -1 | cut -d: -f1)
FIND_LINE=$(grep -nE '^### Step 6 — Emit findings' "$CMD" | head -1 | cut -d: -f1)
if [ -n "$TOPO_LINE" ] && [ -n "$FIND_LINE" ] && [ "$TOPO_LINE" -lt "$FIND_LINE" ]; then
  report 0 "procedure: topology (Step 5) precedes findings (Step 6)"
else
  report 1 "procedure: topology (Step 5) precedes findings (Step 6)" \
    "topo=$TOPO_LINE find=$FIND_LINE"
fi

# ── Notes section: caches well + pairs with /board-rebuild ──────────────────
check "notes: cheap to regenerate"                            "Cheap to regenerate"
check "notes: pairs with /board-rebuild"                      "/board-rebuild"
check "notes: staleness impossible by construction"           "Staleness is impossible by construction"

# ── Interpretation belongs downstream, not in this command ──────────────────
check "scope: interpretation downstream"                      "Interpretation belongs downstream"

echo ""
echo "================================================================"
echo "board-graph-command: $PASS pass, $FAIL fail"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0

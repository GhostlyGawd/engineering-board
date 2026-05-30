#!/usr/bin/env bash
# tests/orchestration/subagent-fixtures.sh — v0.3.2 subagent contract lint.
#
# The substrate (claim scripts, consolidate, tidy, audit, registry, fallback)
# is covered end-to-end by tests/orchestration/{pm-loop,worker-*-loop,
# multi-worker-contention,active-workers-registry,pm-fallback-heartbeat,
# learnings-curator,board-migrate,pause-resume-registry}.sh — 12 sub-tests.
#
# The LLM-DISPATCHED layer (the actual subagent Task call) cannot be
# exercised from a shell harness — the model is not reachable. What we CAN
# pin is the CONTRACT: each dispatched subagent emits a JSON object with a
# specific shape, and the orchestrator (`hooks/stop-hook-procedure.md`)
# reads specific keys back. If an agent's documented output drops a
# load-bearing key, or the orchestrator starts consuming a key the agent
# never documents, the contract has silently regressed and downstream
# breaks at runtime instead of at the test boundary.
#
# This test pins three invariants per dispatched agent:
#
#   1. The agent body has an "## Output contract" heading. (Convention
#      shared by all 7 dispatched agents — the contract is the documented
#      source of truth the orchestrator reads against.)
#
#   2. The agent body documents every CONSUMER_KEYS entry — the keys the
#      orchestrator and PM-pipeline scripts actually read back from the
#      subagent's response. Adding a new consumed key WITHOUT documenting
#      it in the agent body is the regression this test catches.
#
#   3. Every fenced ```json``` code block in the agent body is parseable
#      after a deterministic placeholder substitution (e.g. `<integer>` →
#      `0`, `<entry-id from input>` → `"X"`). Catches typos in the
#      contract examples that look right but won't parse.
#
# Excluded: board-manager (router, not a JSON-emitting dispatched agent;
# it delegates to skills).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

AGENTS_DIR="$PLUGIN_ROOT/agents"
PROCEDURE="$PLUGIN_ROOT/hooks/stop-hook-procedure.md"

if [ ! -d "$AGENTS_DIR" ]; then
  echo "MISSING agents dir: $AGENTS_DIR" >&2
  exit 1
fi
if [ ! -f "$PROCEDURE" ]; then
  echo "MISSING $PROCEDURE" >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not on PATH" >&2
  exit 1
fi

PASS=0
FAIL=0
report() {
  if [ "$1" = "0" ]; then
    printf "  [PASS] %s\n" "$2"; PASS=$((PASS + 1))
  else
    printf "  [FAIL] %s%s\n" "$2" "${3:+ -- $3}"; FAIL=$((FAIL + 1))
  fi
}

# ── Per-agent CONSUMER_KEYS ─────────────────────────────────────────────────
# Each entry: "<agent-file-stem>|<space-separated load-bearing keys>"
# Sourced from:
#   - finding-extractor: stop-hook-procedure.md Section 3-EXTRACTOR step (d)
#     parses the returned JSON and appends to scratch; downstream
#     consolidator reads schema_version + findings + per-finding fields.
#   - consolidator: stop-hook-procedure.md Section 3-PM step (b) logs
#     promoted / archived_superseded / deferred.
#   - tidier: stop-hook-procedure.md Section 3-PM step (c) — actions_taken
#     is mentioned by name.
#   - learnings-curator: stop-hook-procedure.md Section 3-PM step (d)
#     reads status; v0.3.0 adds promoted / updated / skipped tracking.
#   - tdd-builder / code-reviewer / validator: stop-hook-procedure.md
#     Section 3-WORKER step (h) reads suggested_next_needs and status.
#     The agent body itself documents the full contract (entry_id,
#     discipline, test_command, etc.) which is the regression target.

AGENTS=(
  "finding-extractor|schema_version findings scratch_id type confidence title affects evidence_quote discovered tags schema_validation_result"
  "consolidator|schema_version session_file promoted archived_superseded deferred notes"
  "tidier|schema_version actions_taken board_md_rebuilt stale_claims_reclaimed archived_sessions_deleted patterns tdd_count review_count validate_count oscillating_count audit_unaccounted notes"
  "learnings-curator|schema_version board_dir min_recurrence resolved_scanned tag_counts promoted updated skipped notes"
  "tdd-builder|schema_version entry_id discipline status test_files_added impl_files_changed test_command test_output_excerpt suggested_next_needs notes"
  "code-reviewer|schema_version entry_id discipline status test_files_added impl_files_changed test_command test_output_excerpt suggested_next_needs notes"
  "validator|schema_version entry_id discipline status test_files_added impl_files_changed test_command test_output_excerpt suggested_next_needs notes"
)

# ── Invariant 1 + 2: each agent has Output contract + documents keys ────────
for entry in "${AGENTS[@]}"; do
  agent="${entry%%|*}"
  keys="${entry#*|}"
  file="$AGENTS_DIR/$agent.md"

  if [ ! -f "$file" ]; then
    report 1 "$agent.md exists" "missing file: $file"
    continue
  fi

  if grep -qE '^## Output contract' "$file"; then
    report 0 "$agent: has '## Output contract' heading"
  else
    report 1 "$agent: has '## Output contract' heading"
  fi

  missing=""
  for k in $keys; do
    if ! grep -qF "$k" "$file"; then
      missing="$missing $k"
    fi
  done
  if [ -z "$missing" ]; then
    report 0 "$agent: documents all $(echo $keys | wc -w | tr -d ' ') load-bearing keys"
  else
    report 1 "$agent: documents all load-bearing keys" "missing:$missing"
  fi
done

# ── Invariant 3: every ```json fenced block parses after placeholder subst ──
# Placeholders we deterministically substitute before parsing:
#   <integer>           → 0
#   <int>               → 0
#   <count>             → 0
#   "<anything>"        → "X" (string placeholders)
#   "..."               → (omitted — trailing-element marker, just drop)
# Anything else inside angle brackets stays as-is and may fail parse —
# that's the test catching a real typo.

parse_json_blocks_py='
import json, re, sys
path = sys.argv[1]
src = open(path, encoding="utf-8").read()

# Extract fenced ``` blocks (both ```json and plain ```), then filter to
# those whose first non-empty line looks like JSON (starts with "{" or "[").
# Agents use plain ``` fences for their contract examples.
raw_blocks = re.findall(r"```[a-zA-Z]*\s*\n(.*?)```", src, re.DOTALL)
blocks = []
for blk in raw_blocks:
    stripped = blk.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        blocks.append(blk)

errors = []
for i, blk in enumerate(blocks, 1):
    candidate = blk
    # Strip trailing-element marker lines: lines that are JUST "..." or "\"...\"".
    candidate = re.sub(r",\s*\n\s*\"?\.\.\.\"?\s*\n", "\n", candidate)
    candidate = re.sub(r"\n\s*\"?\.\.\.\"?\s*(?=\n|\})", "", candidate)
    # Strip mid-line ", ..." trailing-element markers before ] or }.
    # e.g. `["B001", ...]` → `["B001"]`,  `{"a": 1, ... }` → `{"a": 1 }`.
    candidate = re.sub(r",\s*\.\.\.(?=\s*[}\]])", "", candidate)
    # Substitute numeric placeholders.
    candidate = re.sub(r"<\s*(integer|int|count|n)\s*>", "0", candidate)
    # Substitute string placeholders inside double quotes:
    #   "<anything in here>" → "X"
    candidate = re.sub(r"\"<[^\">]*>\"", "\"X\"", candidate)
    # Bare angle-bracket placeholders that ended up where a value is expected
    # (e.g. `: <integer>,`) — coerce to 0.
    candidate = re.sub(r":\s*<[^>]*>", ": 0", candidate)
    # Substitute boolean placeholders.
    candidate = re.sub(r"<\s*(bool|boolean|true_or_false)\s*>", "false", candidate)
    # Inline comments are not valid JSON; strip "// ..." trailing comments.
    candidate = re.sub(r"//[^\n]*", "", candidate)
    # Trailing commas before } or ] are not valid JSON; clean them.
    candidate = re.sub(r",(\s*[}\]])", r"\1", candidate)
    try:
        json.loads(candidate)
    except Exception as e:
        errors.append((i, str(e)[:160]))
sys.stdout.write(f"BLOCKS={len(blocks)}\n")
for i, err in errors:
    sys.stdout.write(f"ERR_BLOCK_{i}={err}\n")
sys.exit(0)
'

for entry in "${AGENTS[@]}"; do
  agent="${entry%%|*}"
  file="$AGENTS_DIR/$agent.md"
  [ -f "$file" ] || continue
  out=$(python3 -c "$parse_json_blocks_py" "$file")
  if echo "$out" | grep -q "ERR_BLOCK_"; then
    errs="$(echo "$out" | grep ERR_BLOCK_ | tr '\n' '|')"
    report 1 "$agent: all fenced \`\`\`json blocks parse" "$errs"
  else
    blocks="$(echo "$out" | grep ^BLOCKS= | cut -d= -f2)"
    report 0 "$agent: all $blocks fenced \`\`\`json blocks parse"
  fi
done

# ── Cross-check: orchestrator references match contract keys ────────────────
# stop-hook-procedure.md mentions these per-agent keys; assert each is also
# documented in the corresponding agent file (this catches the inverse
# regression: orchestrator added a consumer for a key the agent dropped).
#
# Pairs: "<key>|<agent-file-stem>"
ORCHESTRATOR_REFS=(
  "promoted|consolidator"
  "archived_superseded|consolidator"
  "deferred|consolidator"
  "actions_taken|tidier"
  "status|learnings-curator"
  "suggested_next_needs|tdd-builder"
  "suggested_next_needs|code-reviewer"
  "suggested_next_needs|validator"
)

for pair in "${ORCHESTRATOR_REFS[@]}"; do
  key="${pair%%|*}"
  agent="${pair#*|}"
  file="$AGENTS_DIR/$agent.md"
  if ! grep -qF "$key" "$file"; then
    report 1 "orchestrator reads '$key' from $agent — $agent documents it" "key missing in agent file"
    continue
  fi
  if ! grep -qF "$key" "$PROCEDURE"; then
    report 1 "orchestrator-side ref to '$key' present in stop-hook-procedure.md"
    continue
  fi
  report 0 "orchestrator/contract sync: '$key' present in both $agent and stop-hook-procedure.md"
done

# ── board-manager exclusion — sanity check it IS a router, not dispatched ──
BM="$AGENTS_DIR/board-manager.md"
if [ -f "$BM" ]; then
  # board-manager should NOT be dispatched from stop-hook-procedure.md.
  if grep -qF "subagent_type=\`board-manager\`" "$PROCEDURE"; then
    report 1 "board-manager not in Stop pipeline" "found subagent_type=\`board-manager\` in $PROCEDURE"
  else
    report 0 "board-manager correctly excluded from Stop pipeline"
  fi
fi

echo ""
echo "subagent-fixtures: $PASS pass, $FAIL fail"
if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0

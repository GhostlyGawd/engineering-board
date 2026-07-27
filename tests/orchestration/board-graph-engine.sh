#!/usr/bin/env bash
# Executable graph-engine acceptance for positive, negative, singleton, and malformed input.
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
ENGINE="$ROOT/hooks/scripts/board-graph-build.py"
FIXTURE="$ROOT/references/demo/pattern-intelligence"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
PASS=0
FAIL=0

pass() { printf "  [PASS] %s\n" "$1"; PASS=$((PASS + 1)); }
fail() { printf "  [FAIL] %s\n" "$1"; FAIL=$((FAIL + 1)); }

python3 "$ENGINE" \
  --board-dir "$FIXTURE" \
  --project demo \
  --output "$TMP/GRAPH.yml" \
  --json-output "$TMP/graph.json" \
  --generated-at 2026-07-27T00:00:00Z >/dev/null

python3 - "$TMP/graph.json" <<'PY' && pass "positive: 3 nodes, 3 edges, one cluster" || fail "positive graph shape"
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
c = d["topology"]["clusters"]
assert len(d["nodes"]) == 3
assert len(d["edges"]) == 3
assert len(c) == 1
assert c[0]["id"] == "C001"
assert c[0]["members"] == ["B001", "B002", "B003"]
assert c[0]["affected_domains"] == ["board-view", "hooks", "mcp-server"]
assert c[0]["patterns"] == ["duplicated-state-contract"]
assert c[0]["density"] == 1.0
PY

cmp -s "$TMP/GRAPH.yml" "$TMP/graph.json" \
  && pass "GRAPH.yml is dependency-free JSON-compatible YAML" \
  || fail "GRAPH.yml/json logical source diverged"

FIRST="$(sha256sum "$TMP/GRAPH.yml" | awk '{print $1}')"
python3 "$ENGINE" \
  --board-dir "$FIXTURE" \
  --project demo \
  --output "$TMP/GRAPH.yml" \
  --json-output "$TMP/graph.json" \
  --generated-at 2026-07-27T00:00:00Z >/dev/null
SECOND="$(sha256sum "$TMP/GRAPH.yml" | awk '{print $1}')"
[ "$FIRST" = "$SECOND" ] && pass "same input is byte-deterministic" || fail "graph output changed"

make_entry() {
  local dir="$1" id="$2" pattern="$3" affects="$4"
  mkdir -p "$dir/bugs"
  cat > "$dir/bugs/$id.md" <<EOF
---
id: $id
type: bug
status: open
title: Similar lifecycle symptom $id
affects: $affects
discovered: 2026-07-27
pattern: [$pattern]
---

## Evidence

Control fixture.
EOF
}

NEG="$TMP/negative"
make_entry "$NEG" B001 cause-one domain-one/path
make_entry "$NEG" B002 cause-two domain-two/path
make_entry "$NEG" B003 cause-three domain-three/path
python3 "$ENGINE" --board-dir "$NEG" --project negative \
  --output "$TMP/negative.yml" --json-output "$TMP/negative.json" \
  --generated-at 2026-07-27T00:00:00Z >/dev/null
python3 - "$TMP/negative.json" <<'PY' && pass "negative: similar language does not force a cluster" || fail "negative fixture clustered"
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
assert d["edges"] == []
assert d["topology"]["clusters"] == []
assert d["topology"]["isolated"] == ["B001", "B002", "B003"]
PY

SINGLE="$TMP/singleton"
make_entry "$SINGLE" B001 singleton one-domain/path
python3 "$ENGINE" --board-dir "$SINGLE" --project singleton \
  --output "$TMP/singleton.yml" --json-output "$TMP/singleton.json" \
  --generated-at 2026-07-27T00:00:00Z >/dev/null
python3 - "$TMP/singleton.json" <<'PY' && pass "singleton remains isolated without systemic hypothesis facts" || fail "singleton contract"
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
assert d["topology"]["clusters"] == []
assert d["topology"]["isolated"] == ["B001"]
assert not any(f["type"] == "pattern-recurrence" for f in d["findings"])
PY

BAD="$TMP/malformed"
mkdir -p "$BAD/bugs"
cat > "$BAD/bugs/missing-id.md" <<'EOF'
---
type: bug
title: Missing id
discovered: 2026-07-27
---
EOF
RC=0
python3 "$ENGINE" --board-dir "$BAD" --project malformed \
  --output "$TMP/should-not-exist.yml" 2>"$TMP/error.json" || RC=$?
if [ "$RC" -eq 2 ] && grep -q "missing required field(s): id" "$TMP/error.json" \
  && [ ! -e "$TMP/should-not-exist.yml" ]; then
  pass "malformed input fails explicitly with no partial graph"
else
  fail "malformed input boundary"
fi

echo ""
echo "board-graph-engine: $PASS pass, $FAIL fail"
[ "$FAIL" -eq 0 ]

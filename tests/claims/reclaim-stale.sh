#!/usr/bin/env bash
# tests/claims/reclaim-stale.sh — Validate board-claim-reclaim-stale.sh
#
# Plants 3 fixture claims:
#   (i)   fresh heartbeat  (mtime = now)            → expect: kept
#   (ii)  stale heartbeat  (mtime = now - 200s)     → expect: reclaimed, reason stale_no_heartbeat
#   (iii) very stale       (mtime = now - 600s)     → expect: reclaimed, reason stale_no_heartbeat
#
# _reclaimed.log must have exactly 2 JSON-lines entries after the run.
#
# Usage:
#   bash tests/claims/reclaim-stale.sh [plugin-root]
#
# Exits 0 iff all assertions pass.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
RECLAIM="$PLUGIN_ROOT/hooks/scripts/board-claim-reclaim-stale.sh"

if [ ! -f "$RECLAIM" ]; then
  echo "MISSING: $RECLAIM" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 required" >&2
  exit 1
fi

TMP="$(python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="eb-reclaim-").replace(chr(92), "/"))')"
cleanup() { rm -rf "$TMP" 2>/dev/null || true; }
trap cleanup EXIT

BOARD_DIR="$TMP/project/docs/boards/test"
CLAIMS_DIR="$BOARD_DIR/_claims"
mkdir -p "$CLAIMS_DIR"

# ── Fixture helper ────────────────────────────────────────────────────────────
make_claim() {
  local name="$1" age_sec="$2"
  local dir="$CLAIMS_DIR/$name"
  mkdir -p "$dir"
  printf 'session-%s 2026-05-11T00:00:00Z %s\n' "$name" "$TMP" > "$dir/owner.txt"
  printf '2026-05-11T00:00:00Z\n' > "$dir/heartbeat.txt"
  # Back-date the heartbeat mtime via python3 (touch -d is not portable).
  python3 - "$dir/heartbeat.txt" "$age_sec" <<'PY'
import sys, os, time
path, age = sys.argv[1], float(sys.argv[2])
t = time.time() - age
os.utime(path, (t, t))
PY
}

make_claim "FRESH-001"   0      # (i)   fresh
make_claim "STALE-002"   200    # (ii)  stale  (> 180s default)
make_claim "VSTALE-003"  600    # (iii) very stale

# ── Run reclaim with default 180s threshold ───────────────────────────────────
STDOUT="$TMP/reclaim.stdout"
STDERR="$TMP/reclaim.stderr"
# Force non-cloud path (no OneDrive substring) so 180s threshold applies.
EB_STALE_SEC=180 bash "$RECLAIM" "$BOARD_DIR" > "$STDOUT" 2> "$STDERR"

# ── Assertion harness ─────────────────────────────────────────────────────────
PASS=0
FAIL=0
report() {
  if [ "$1" = "0" ]; then
    printf "  [PASS] %s\n" "$2"; PASS=$((PASS + 1))
  else
    printf "  [FAIL] %s%s\n" "$2" "${3:+ -- $3}"; FAIL=$((FAIL + 1))
  fi
}

# Helper: extract decision for a given scratch_id from stdout JSON-lines.
get_decision() {
  local id="$1"
  python3 - "$STDOUT" "$id" <<'PY'
import json, sys
path, target = sys.argv[1], sys.argv[2]
for line in open(path, encoding="utf-8"):
    line = line.strip()
    if not line: continue
    try:
        r = json.loads(line)
        if r.get("scratch_id") == target:
            print(r.get("decision",""))
            sys.exit(0)
    except Exception:
        pass
print("")
PY
}

get_reason() {
  local id="$1"
  python3 - "$STDOUT" "$id" <<'PY'
import json, sys
path, target = sys.argv[1], sys.argv[2]
for line in open(path, encoding="utf-8"):
    line = line.strip()
    if not line: continue
    try:
        r = json.loads(line)
        if r.get("scratch_id") == target:
            print(r.get("reason",""))
            sys.exit(0)
    except Exception:
        pass
print("")
PY
}

# 1. FRESH-001 → kept
D=$(get_decision "FRESH-001")
if [ "$D" = "kept" ]; then
  report 0 "FRESH-001 kept"
else
  report 1 "FRESH-001 kept" "got '$D'"
fi

# 2. STALE-002 → reclaimed
D=$(get_decision "STALE-002")
if [ "$D" = "reclaimed" ]; then
  report 0 "STALE-002 reclaimed"
else
  report 1 "STALE-002 reclaimed" "got '$D'"
fi

# 3. STALE-002 reason = stale_no_heartbeat
R=$(get_reason "STALE-002")
if [ "$R" = "stale_no_heartbeat" ]; then
  report 0 "STALE-002 reason=stale_no_heartbeat"
else
  report 1 "STALE-002 reason=stale_no_heartbeat" "got '$R'"
fi

# 4. VSTALE-003 → reclaimed
D=$(get_decision "VSTALE-003")
if [ "$D" = "reclaimed" ]; then
  report 0 "VSTALE-003 reclaimed"
else
  report 1 "VSTALE-003 reclaimed" "got '$D'"
fi

# 5. VSTALE-003 reason = stale_no_heartbeat
R=$(get_reason "VSTALE-003")
if [ "$R" = "stale_no_heartbeat" ]; then
  report 0 "VSTALE-003 reason=stale_no_heartbeat"
else
  report 1 "VSTALE-003 reason=stale_no_heartbeat" "got '$R'"
fi

# 6. _reclaimed.log has exactly 2 entries
RECLAIMED_LOG="$CLAIMS_DIR/_reclaimed.log"
if [ -f "$RECLAIMED_LOG" ]; then
  LOG_COUNT=$(grep -c '"reason"' "$RECLAIMED_LOG" 2>/dev/null || echo 0)
  if [ "$LOG_COUNT" -eq 2 ]; then
    report 0 "_reclaimed.log has 2 entries"
  else
    report 1 "_reclaimed.log has 2 entries" "got $LOG_COUNT"
  fi
else
  report 1 "_reclaimed.log has 2 entries" "file missing"
fi

# 7. Stale claim dirs actually removed from filesystem
if [ ! -d "$CLAIMS_DIR/STALE-002" ]; then
  report 0 "STALE-002 dir removed"
else
  report 1 "STALE-002 dir removed" "dir still present"
fi

if [ ! -d "$CLAIMS_DIR/VSTALE-003" ]; then
  report 0 "VSTALE-003 dir removed"
else
  report 1 "VSTALE-003 dir removed" "dir still present"
fi

# 8. Fresh claim dir still present
if [ -d "$CLAIMS_DIR/FRESH-001" ]; then
  report 0 "FRESH-001 dir preserved"
else
  report 1 "FRESH-001 dir preserved" "dir missing"
fi

echo ""
echo "================================================================"
echo "reclaim-stale: $PASS pass, $FAIL fail"
echo "================================================================"

[ "$FAIL" -eq 0 ]

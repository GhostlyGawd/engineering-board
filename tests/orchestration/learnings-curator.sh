#!/usr/bin/env bash
# tests/orchestration/learnings-curator.sh — v0.3.0 deterministic learning
# promotion via board-curate-learnings.sh.
#
# Covers:
#   1. Plant 3 resolved entries with shared pattern tag → promote 1 L###.
#   2. Plant 1 resolved entry with a different tag → skipped (below threshold).
#   3. Plant 1 OPEN entry with the shared tag → not counted in recurrence.
#   4. Idempotency: re-run produces byte-identical learnings/.
#   5. Update path: add a 4th source, recurrence and derived_from advance.
#   6. Confidence ladder: recurrence ≥ 5 → confidence=high.
#   7. Below-threshold tag is reported in `skipped`.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
CURATOR="$PLUGIN_ROOT/hooks/scripts/board-curate-learnings.sh"

if [ ! -f "$CURATOR" ]; then
  echo "MISSING: $CURATOR" >&2
  exit 1
fi

TMP="$(python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="eb-curate-"))')"
cleanup_tmp() { rm -rf "$TMP" 2>/dev/null || true; }
trap cleanup_tmp EXIT

BOARD_DIR="$TMP/docs/board"
mkdir -p "$BOARD_DIR/bugs" "$BOARD_DIR/features" "$BOARD_DIR/observations"

plant_resolved_bug() {
  local id="$1" tag="$2" disc="$3"
  cat > "$BOARD_DIR/bugs/$id-x.md" <<EOF
---
id: $id
type: bug
title: Bug $id
discovered: $disc
status: resolved
priority: P2
affects: foo/
pattern: [$tag]
---
## Done when
- [x] fixed
EOF
}

# Plant 4 resolved with shared, 1 with lonely, 1 OPEN (must not count).
plant_resolved_bug "B001" "shared" "2026-05-01"
plant_resolved_bug "B002" "shared" "2026-05-02"
plant_resolved_bug "B003" "shared" "2026-05-03"
plant_resolved_bug "B004" "lonely" "2026-05-04"
cat > "$BOARD_DIR/bugs/B005-x.md" <<EOF
---
id: B005
type: bug
title: Open bug shouldn't count
discovered: 2026-05-05
status: open
priority: P2
affects: foo/
pattern: [shared]
---
## Done when
- [ ] tbd
EOF

OUT="$(bash "$CURATOR" "$BOARD_DIR")"

PASS=0
FAIL=0
report() {
  if [ "$1" = "0" ]; then
    printf "  [PASS] %s\n" "$2"; PASS=$((PASS + 1))
  else
    printf "  [FAIL] %s%s\n" "$2" "${3:+ -- $3}"; FAIL=$((FAIL + 1))
  fi
}

json_q() {
  echo "$OUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
v = d
for k in sys.argv[1].split('.'):
    if k.isdigit():
        v = v[int(k)]
    else:
        v = v[k]
print(json.dumps(v))
"
}

# 1. Promote one learning for 'shared' tag.
PROMOTED_LEN="$(echo "$OUT" | python3 -c "import json, sys; print(len(json.load(sys.stdin)['promoted']))")"
[ "$PROMOTED_LEN" = "1" ] && report 0 "1 learning promoted" || report 1 "1 learning promoted" "got $PROMOTED_LEN"

PROMOTED_TAG="$(echo "$OUT" | python3 -c "import json, sys; d=json.load(sys.stdin); print(d['promoted'][0]['tag']) if d['promoted'] else print('none')")"
[ "$PROMOTED_TAG" = "shared" ] && report 0 "Promoted tag = 'shared'" || report 1 "Promoted tag = 'shared'" "got $PROMOTED_TAG"

PROMOTED_REC="$(echo "$OUT" | python3 -c "import json, sys; d=json.load(sys.stdin); print(d['promoted'][0]['recurrence']) if d['promoted'] else print(0)")"
[ "$PROMOTED_REC" = "3" ] && report 0 "Recurrence = 3 (open entry not counted)" || report 1 "Recurrence = 3 (open entry not counted)" "got $PROMOTED_REC"

DERIVED="$(echo "$OUT" | python3 -c "import json, sys; d=json.load(sys.stdin); print(','.join(d['promoted'][0]['derived_from'])) if d['promoted'] else print('')")"
[ "$DERIVED" = "B001,B002,B003" ] && report 0 "derived_from = B001,B002,B003" || report 1 "derived_from = B001,B002,B003" "got $DERIVED"

# 2. 'lonely' tag is skipped (below threshold).
LONELY_SKIPPED="$(echo "$OUT" | python3 -c "import json, sys; d=json.load(sys.stdin); [print(s['reason']) for s in d['skipped'] if s.get('tag')=='lonely']")"
case "$LONELY_SKIPPED" in
  recurrence_below_threshold*) report 0 "Lonely tag skipped: below threshold" ;;
  *) report 1 "Lonely tag skipped: below threshold" "got $LONELY_SKIPPED" ;;
esac

# 3. Learning file exists.
LEARNING_FILE=$(find "$BOARD_DIR/learnings" -name "L001-*.md" 2>/dev/null | head -1)
[ -n "$LEARNING_FILE" ] && report 0 "L001 file created" || report 1 "L001 file created"
grep -q "^confidence: medium$" "$LEARNING_FILE" 2>/dev/null && report 0 "L001 confidence=medium at 3" || report 1 "L001 confidence=medium at 3"

# 4. Idempotency.
SHA1=$(find "$BOARD_DIR/learnings" -type f -name "*.md" -exec sha256sum {} \; | sort)
bash "$CURATOR" "$BOARD_DIR" >/dev/null
SHA2=$(find "$BOARD_DIR/learnings" -type f -name "*.md" -exec sha256sum {} \; | sort)
[ "$SHA1" = "$SHA2" ] && report 0 "Re-run produces SHA-identical learnings" || report 1 "Re-run produces SHA-identical learnings"

# Second run's already-up-to-date reason recorded.
OUT2="$(bash "$CURATOR" "$BOARD_DIR")"
UPDATED2="$(echo "$OUT2" | python3 -c "import json, sys; print(len(json.load(sys.stdin)['updated']))")"
[ "$UPDATED2" = "0" ] && report 0 "Re-run: zero updates" || report 1 "Re-run: zero updates" "got $UPDATED2"
ALREADY_UP_TO_DATE="$(echo "$OUT2" | python3 -c "import json, sys; d=json.load(sys.stdin); [print(s['reason']) for s in d['skipped'] if s.get('tag')=='shared']")"
[ "$ALREADY_UP_TO_DATE" = "already_up_to_date" ] && report 0 "Re-run: shared tag already_up_to_date" || report 1 "Re-run: shared tag already_up_to_date" "got $ALREADY_UP_TO_DATE"

# 5. Update path: add 4th source.
plant_resolved_bug "B006" "shared" "2026-05-06"
OUT3="$(bash "$CURATOR" "$BOARD_DIR")"
UPDATED3="$(echo "$OUT3" | python3 -c "import json, sys; print(len(json.load(sys.stdin)['updated']))")"
[ "$UPDATED3" = "1" ] && report 0 "4th source -> 1 update" || report 1 "4th source -> 1 update" "got $UPDATED3"
NEW_REC="$(grep "^recurrence:" "$LEARNING_FILE" | awk '{print $2}')"
[ "$NEW_REC" = "4" ] && report 0 "Recurrence advances to 4" || report 1 "Recurrence advances to 4" "got $NEW_REC"

# 6. Confidence ladder: add 5th source → high.
plant_resolved_bug "B007" "shared" "2026-05-07"
bash "$CURATOR" "$BOARD_DIR" >/dev/null
NEW_CONF="$(grep "^confidence:" "$LEARNING_FILE" | awk '{print $2}')"
[ "$NEW_CONF" = "high" ] && report 0 "Confidence advances to high at recurrence=5" || report 1 "Confidence advances to high at recurrence=5" "got $NEW_CONF"

echo ""
echo "learnings-curator: $PASS pass, $FAIL fail"
if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0

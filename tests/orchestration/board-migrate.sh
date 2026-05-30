#!/usr/bin/env bash
# tests/orchestration/board-migrate.sh — v0.3.0 board-migrate.sh apply / rollback.
#
# Covers:
#   1. --apply creates learnings/ subdir with .gitkeep.
#   2. --apply back-fills needs:tdd on open bug/feature without needs.
#   3. --apply preserves existing needs: value on entries that have one.
#   4. --apply skips resolved entries (no needs added).
#   5. --apply is SHA256-idempotent (re-run produces identical tree).
#   6. --rollback restores SHA256-equal pre-migrate state.
#   7. --rollback after --apply --apply still SHA-equal pre-migrate.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
MIGRATE="$PLUGIN_ROOT/hooks/scripts/board-migrate.sh"

if [ ! -f "$MIGRATE" ]; then
  echo "MISSING: $MIGRATE" >&2
  exit 1
fi

TMP="$(python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="eb-mig-"))')"
cleanup_tmp() { rm -rf "$TMP" 2>/dev/null || true; }
trap cleanup_tmp EXIT

BOARD_DIR="$TMP/docs/board"
mkdir -p "$BOARD_DIR/bugs" "$BOARD_DIR/features" "$BOARD_DIR/questions" "$BOARD_DIR/observations"

cat > "$BOARD_DIR/BOARD.md" <<'EOF'
# board
## Open
- B001 P2 | [t](bugs/B001-x.md)
EOF
cat > "$BOARD_DIR/bugs/B001-x.md" <<'EOF'
---
id: B001
type: bug
title: Open bug no needs
discovered: 2026-05-01
status: open
priority: P2
affects: foo/
---
## Done when
- [ ] fix
EOF
cat > "$BOARD_DIR/features/F001-x.md" <<'EOF'
---
id: F001
type: feature
title: Open feature with needs
discovered: 2026-05-01
status: open
needs: review
priority: P2
affects: bar/
---
## Done when
- [ ] do
EOF
cat > "$BOARD_DIR/bugs/B002-x.md" <<'EOF'
---
id: B002
type: bug
title: Resolved bug
discovered: 2026-05-01
status: resolved
priority: P2
affects: foo/
---
## Done when
- [x] done
EOF

sha_live_tree() {
  python3 - "$BOARD_DIR" <<'PY'
import os, sys, hashlib
root = sys.argv[1]
h = hashlib.sha256()
files = []
for dp, dn, fn in os.walk(root):
    dn[:] = sorted(d for d in dn if d != "_migrate-snapshot")
    for f in sorted(fn):
        if f == ".migration-state.json": continue
        files.append(os.path.relpath(os.path.join(dp, f), root))
files.sort()
for r in files:
    h.update(r.encode()); h.update(b"\0")
    h.update(open(os.path.join(root, r), "rb").read()); h.update(b"\0")
print(h.hexdigest())
PY
}

PASS=0
FAIL=0
report() {
  if [ "$1" = "0" ]; then
    printf "  [PASS] %s\n" "$2"; PASS=$((PASS + 1))
  else
    printf "  [FAIL] %s%s\n" "$2" "${3:+ -- $3}"; FAIL=$((FAIL + 1))
  fi
}

PRE_SHA=$(sha_live_tree)

bash "$MIGRATE" --apply "$BOARD_DIR" >/dev/null

# 1. learnings/ + .gitkeep.
[ -d "$BOARD_DIR/learnings" ] && report 0 "learnings/ subdir created" || report 1 "learnings/ subdir created"
[ -f "$BOARD_DIR/learnings/.gitkeep" ] && report 0 "learnings/.gitkeep created" || report 1 "learnings/.gitkeep created"

# 2. needs:tdd back-filled on B001.
B001_NEEDS="$(grep "^needs:" "$BOARD_DIR/bugs/B001-x.md" | awk '{print $2}' || echo MISSING)"
[ "$B001_NEEDS" = "tdd" ] && report 0 "B001 (open, no needs) -> needs:tdd" || report 1 "B001 (open, no needs) -> needs:tdd" "got $B001_NEEDS"

# 3. F001 preserved.
F001_NEEDS="$(grep "^needs:" "$BOARD_DIR/features/F001-x.md" | awk '{print $2}')"
[ "$F001_NEEDS" = "review" ] && report 0 "F001 (open, has needs:review) preserved" || report 1 "F001 (open, has needs:review) preserved" "got $F001_NEEDS"

# 4. B002 resolved: no needs added.
B002_NEEDS="$(grep "^needs:" "$BOARD_DIR/bugs/B002-x.md" 2>/dev/null | awk '{print $2}' || echo MISSING)"
[ "$B002_NEEDS" = "MISSING" ] && report 0 "B002 (resolved) -> no needs added" || report 1 "B002 (resolved) -> no needs added" "got $B002_NEEDS"

# 5. Idempotency.
APPLY1_SHA=$(sha_live_tree)
bash "$MIGRATE" --apply "$BOARD_DIR" >/dev/null
APPLY2_SHA=$(sha_live_tree)
[ "$APPLY1_SHA" = "$APPLY2_SHA" ] && report 0 "--apply twice is SHA-idempotent" || report 1 "--apply twice is SHA-idempotent" "sha drift"

# 6. Rollback restores pre-migrate SHA.
bash "$MIGRATE" --rollback "$BOARD_DIR" >/dev/null
ROLLBACK_SHA=$(sha_live_tree)
[ "$ROLLBACK_SHA" = "$PRE_SHA" ] && report 0 "--rollback restores pre-migrate SHA" || report 1 "--rollback restores pre-migrate SHA" "drift"

# 7. Re-apply after rollback works (snapshot still exists from earlier).
bash "$MIGRATE" --apply "$BOARD_DIR" >/dev/null
REAPPLY_SHA=$(sha_live_tree)
[ "$REAPPLY_SHA" = "$APPLY1_SHA" ] && report 0 "--apply after --rollback reaches same post-apply SHA" || report 1 "--apply after --rollback reaches same post-apply SHA"

echo ""
echo "board-migrate: $PASS pass, $FAIL fail"
if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0

#!/usr/bin/env bash
# tests/orchestration/board-relocate.sh — board-relocate.sh (1.1.0 §6.7).
#
# Covers:
#   1. Full relocate (git work tree -> git mv): dirs + router moved, paths
#      rewritten, affects-prefix preserved, entry content intact, snapshot taken.
#   2. Idempotency: a second run is a no-op on the committed tree.
#   3. Legacy docs/board/ is reported as deferred and left in place (fallback).
#   4. Partial [project]: relocate one project, leave the other, finish later;
#      router carries mixed paths in between, docs/boards/ removed when empty.
#   5. Non-git dir -> plain mv fallback still moves + rewrites.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
RELOCATE="$PLUGIN_ROOT/hooks/scripts/board-relocate.sh"

if [ ! -f "$RELOCATE" ]; then
  echo "MISSING: $RELOCATE" >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not on PATH" >&2
  exit 1
fi

T1=""; T2=""; T3=""; T4=""
cleanup() { rm -rf "$T1" "$T2" "$T3" "$T4" 2>/dev/null || true; }
trap cleanup EXIT

PASS=0
FAIL=0
report() {
  if [ "$1" = "0" ]; then
    printf "  [PASS] %s\n" "$2"; PASS=$((PASS + 1))
  else
    printf "  [FAIL] %s%s\n" "$2" "${3:+ -- $3}"; FAIL=$((FAIL + 1))
  fi
}

mktmp() { python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="eb-reloc-"))'; }

# committed-tree SHA (excludes the gitignored .engineering-board/ runtime dir).
tree_sha() {
  python3 - "$1" <<'PY'
import os, sys, hashlib
root = sys.argv[1]
h = hashlib.sha256()
files = []
for dp, dn, fn in os.walk(root):
    dn[:] = sorted(d for d in dn if d != ".engineering-board")
    for f in sorted(fn):
        files.append(os.path.relpath(os.path.join(dp, f), root))
files.sort()
for r in files:
    h.update(r.encode()); h.update(b"\0")
    with open(os.path.join(root, r), "rb") as fh:
        h.update(fh.read())
    h.update(b"\0")
print(h.hexdigest())
PY
}

plant_boards() { # <root> : docs/boards with alpha (no trailing slash) + beta (trailing slash)
  local root="$1"
  mkdir -p "$root/docs/boards/alpha/bugs" "$root/docs/boards/beta/features"
  cat > "$root/docs/boards/BOARD-ROUTER.md" <<'EOF'
# Board Router

| project | path | affects prefix |
|---------|------|----------------|
| alpha | docs/boards/alpha | alpha/ |
| beta | docs/boards/beta/ | beta/ |
EOF
  printf 'id: B001\ntitle: keep me\n' > "$root/docs/boards/alpha/bugs/B001-x.md"
  printf 'id: F001\ntitle: keep me too\n' > "$root/docs/boards/beta/features/F001-y.md"
}

git_init() { ( cd "$1" && git init -q && git add -A && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init ); }

# ── 1. Full relocate (git mv) ───────────────────────────────────────────────
T1="$(mktmp)"; plant_boards "$T1"; git_init "$T1"
bash "$RELOCATE" "$T1" >/dev/null

[ -d "$T1/engineering-board/alpha" ] && report 0 "full: alpha moved to engineering-board/" || report 1 "full: alpha moved"
[ -d "$T1/engineering-board/beta" ]  && report 0 "full: beta moved to engineering-board/"  || report 1 "full: beta moved"
[ ! -e "$T1/docs/boards/alpha" ]     && report 0 "full: docs/boards/alpha gone"            || report 1 "full: docs/boards/alpha gone"
[ ! -d "$T1/docs/boards" ]           && report 0 "full: empty docs/boards/ removed"        || report 1 "full: docs/boards removed"
[ -f "$T1/engineering-board/BOARD-ROUTER.md" ] && report 0 "full: router at engineering-board/" || report 1 "full: router moved"
[ ! -f "$T1/docs/boards/BOARD-ROUTER.md" ]     && report 0 "full: compat router removed"        || report 1 "full: compat router removed"

ROUTER="$T1/engineering-board/BOARD-ROUTER.md"
grep -q "engineering-board/alpha" "$ROUTER"  && report 0 "full: alpha path rewritten"                 || report 1 "full: alpha path rewritten"
grep -q "engineering-board/beta/" "$ROUTER"  && report 0 "full: beta path rewritten (trailing slash kept)" || report 1 "full: beta path rewritten"
grep -q "docs/boards" "$ROUTER" && report 1 "full: no docs/boards left in router" "still present" || report 0 "full: no docs/boards left in router"
grep -q "| alpha/ |" "$ROUTER" && report 0 "full: alpha affects-prefix preserved" || report 1 "full: alpha affects-prefix preserved"
grep -q "B001" "$T1/engineering-board/alpha/bugs/B001-x.md" && report 0 "full: entry content preserved" || report 1 "full: entry content preserved"
compgen -G "$T1/.engineering-board/relocate-snapshot/*/docs-boards/BOARD-ROUTER.md" >/dev/null \
  && report 0 "full: pre-relocate snapshot created" || report 1 "full: snapshot created"
( cd "$T1" && git status --porcelain | grep -q "engineering-board/alpha" ) \
  && report 0 "full: move is staged in git (git mv path)" || report 1 "full: move staged in git"

# ── 2. Idempotency ──────────────────────────────────────────────────────────
SHA1="$(tree_sha "$T1")"
OUT2="$(bash "$RELOCATE" "$T1")"
SHA2="$(tree_sha "$T1")"
[ "$SHA1" = "$SHA2" ] && report 0 "idempotent: re-run leaves committed tree byte-stable" || report 1 "idempotent: re-run no-op" "sha drift"
echo "$OUT2" | grep -q "already-relocated: alpha" && report 0 "idempotent: re-run reports already-relocated" || report 1 "idempotent: reports already-relocated"

# ── 3. Legacy docs/board/ deferred ──────────────────────────────────────────
T2="$(mktmp)"; mkdir -p "$T2/docs/board/bugs"; printf 'id: B001\n' > "$T2/docs/board/bugs/B001.md"
OUT3="$(bash "$RELOCATE" "$T2")"
echo "$OUT3" | grep -qi "legacy" && report 0 "legacy: reported as deferred" || report 1 "legacy: reported deferred" "$OUT3"
[ -d "$T2/docs/board" ] && [ ! -d "$T2/engineering-board" ] && report 0 "legacy: left in place (fallback preserved)" || report 1 "legacy: not moved"

# ── 4. Partial [project] ────────────────────────────────────────────────────
T3="$(mktmp)"; plant_boards "$T3"; git_init "$T3"
bash "$RELOCATE" "$T3" alpha >/dev/null
[ -d "$T3/engineering-board/alpha" ] && report 0 "partial: alpha relocated" || report 1 "partial: alpha relocated"
[ -d "$T3/docs/boards/beta" ]        && report 0 "partial: beta left under docs/boards/" || report 1 "partial: beta left"
PR3="$T3/engineering-board/BOARD-ROUTER.md"
grep -q "engineering-board/alpha" "$PR3" && report 0 "partial: alpha row rewritten"        || report 1 "partial: alpha row rewritten"
grep -q "docs/boards/beta" "$PR3"        && report 0 "partial: beta row still docs/boards"  || report 1 "partial: beta row unchanged"
bash "$RELOCATE" "$T3" beta >/dev/null
[ -d "$T3/engineering-board/beta" ] && report 0 "partial: beta relocated on 2nd call" || report 1 "partial: beta relocated 2nd call"
grep -q "engineering-board/beta" "$PR3" && report 0 "partial: beta row rewritten" || report 1 "partial: beta row rewritten"
[ ! -d "$T3/docs/boards" ] && report 0 "partial: docs/boards/ removed after full relocation" || report 1 "partial: docs/boards removed"

# ── 5. Non-git mv fallback ──────────────────────────────────────────────────
T4="$(mktmp)"
mkdir -p "$T4/docs/boards/solo/questions"
cat > "$T4/docs/boards/BOARD-ROUTER.md" <<'EOF'
# Board Router

| project | path | affects prefix |
|---------|------|----------------|
| solo | docs/boards/solo | solo/ |
EOF
printf 'id: Q001\n' > "$T4/docs/boards/solo/questions/Q001.md"
OUT5="$(bash "$RELOCATE" "$T4")"
[ -d "$T4/engineering-board/solo" ] && report 0 "non-git: solo moved via mv fallback" || report 1 "non-git: solo moved"
echo "$OUT5" | grep -q "plain move" && report 0 "non-git: reports plain move method" || report 1 "non-git: reports plain move"
grep -q "engineering-board/solo" "$T4/engineering-board/BOARD-ROUTER.md" && report 0 "non-git: router rewritten" || report 1 "non-git: router rewritten"

echo ""
echo "================================================================"
echo "board-relocate: $PASS pass, $FAIL fail"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0

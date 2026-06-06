#!/usr/bin/env bash
# tests/paths/resolution-order.sh — unit tests for hooks/scripts/board-paths.sh
#
# Pins the §6.1 resolution order of the centralized path resolver introduced for
# the 1.1.0 board relocation (specs/board-relocation.md):
#   1. engineering-board/BOARD-ROUTER.md  (new default)  wins over
#   2. docs/boards/BOARD-ROUTER.md        (compat)       wins over
#   3. docs/board/                        (legacy single-board, no router)
#   4. none -> empty
# Also pins router row parsing (path + label columns, whitespace-trimmed, slash
# preserved) and the legacy fallback, so the helper is a faithful drop-in for the
# duplicated logic in board-consolidate.sh / board-index-check.sh /
# board-audit-scratch.sh / board-session-start.sh.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
HELPER="$ROOT/hooks/scripts/board-paths.sh"

PASS=0
FAIL=0
report_pass() { printf '  [PASS] %s\n' "$1"; PASS=$((PASS + 1)); }
report_fail() { printf '  [FAIL] %s\n     expected: %q\n     actual:   %q\n' "$1" "$2" "$3"; FAIL=$((FAIL + 1)); }
assert_eq() {
  local name="$1" expected="$2" actual="$3"
  if [ "$expected" = "$actual" ]; then report_pass "$name"; else report_fail "$name" "$expected" "$actual"; fi
}

if [ ! -f "$HELPER" ]; then
  echo "resolution-order: MISSING helper $HELPER" >&2
  exit 1
fi
# shellcheck source=/dev/null
. "$HELPER"

SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

# Write a router file: $1 = path, remaining args = data rows (verbatim).
make_router() {
  local rf="$1"; shift
  mkdir -p "$(dirname "$rf")"
  {
    printf '# Board Router\n\n'
    printf '| project | path | affects prefix |\n'
    printf '|---------|------|----------------|\n'
    local r
    for r in "$@"; do printf '%s\n' "$r"; done
  } > "$rf"
}

# --- T1: new default wins over compat when both exist --------------------
P="$SANDBOX/t1"; export CLAUDE_PROJECT_DIR="$P"
make_router "$P/engineering-board/BOARD-ROUTER.md" "| alpha | engineering-board/alpha | alpha/ |"
make_router "$P/docs/boards/BOARD-ROUTER.md"       "| alpha | docs/boards/alpha | alpha/ |"
assert_eq "T1 router: new default wins" "$P/engineering-board/BOARD-ROUTER.md" "$(eb_router_path)"
assert_eq "T1 board_dirs: from new root" "$P/engineering-board/alpha" "$(eb_board_dirs)"

# --- T2: compat resolves when only docs/boards exists --------------------
P="$SANDBOX/t2"; export CLAUDE_PROJECT_DIR="$P"
make_router "$P/docs/boards/BOARD-ROUTER.md" "| beta | docs/boards/beta | beta/ |"
assert_eq "T2 router: compat" "$P/docs/boards/BOARD-ROUTER.md" "$(eb_router_path)"
assert_eq "T2 board_dirs: compat" "$P/docs/boards/beta" "$(eb_board_dirs)"

# --- T3: legacy single-board (no router) ---------------------------------
P="$SANDBOX/t3"; export CLAUDE_PROJECT_DIR="$P"
mkdir -p "$P/docs/board"
assert_eq "T3 router: empty (legacy has none)" "" "$(eb_router_path)"
assert_eq "T3 board_dirs: legacy dir" "$P/docs/board" "$(eb_board_dirs)"
assert_eq "T3 board_rows: legacy labeled project" "$(printf 'project\t%s' "$P/docs/board")" "$(eb_board_rows)"

# --- T4: no board at all -------------------------------------------------
P="$SANDBOX/t4"; export CLAUDE_PROJECT_DIR="$P"; mkdir -p "$P"
assert_eq "T4 router: empty" "" "$(eb_router_path)"
assert_eq "T4 board_dirs: empty" "" "$(eb_board_dirs)"
assert_eq "T4 board_rows: empty" "" "$(eb_board_rows)"

# --- T5: multi-row router (row order + labels preserved) -----------------
P="$SANDBOX/t5"; export CLAUDE_PROJECT_DIR="$P"
make_router "$P/engineering-board/BOARD-ROUTER.md" \
  "| alpha | engineering-board/alpha | alpha/ |" \
  "| gamma | engineering-board/gamma | gamma/ |"
assert_eq "T5 board_dirs: two rows in order" \
  "$(printf '%s\n%s' "$P/engineering-board/alpha" "$P/engineering-board/gamma")" \
  "$(eb_board_dirs)"
assert_eq "T5 board_rows: label<TAB>path per row" \
  "$(printf 'alpha\t%s\ngamma\t%s' "$P/engineering-board/alpha" "$P/engineering-board/gamma")" \
  "$(eb_board_rows)"

# --- T6: whitespace trimmed, trailing slash in path preserved ------------
P="$SANDBOX/t6"; export CLAUDE_PROJECT_DIR="$P"
make_router "$P/engineering-board/BOARD-ROUTER.md" "|   delta   |   engineering-board/delta/   |  delta/  |"
assert_eq "T6 board_dirs: trimmed, slash kept" "$P/engineering-board/delta/" "$(eb_board_dirs)"
assert_eq "T6 board_rows: trimmed label+path" "$(printf 'delta\t%s' "$P/engineering-board/delta/")" "$(eb_board_rows)"

# --- T7: end-to-end — a real consumer (board-index-check.sh) resolves the new
#         engineering-board/ default and processes it cleanly ----------------
P="$SANDBOX/t7"; export CLAUDE_PROJECT_DIR="$P"
make_router "$P/engineering-board/BOARD-ROUTER.md" "| demo | engineering-board/demo | demo/ |"
mkdir -p "$P/engineering-board/demo/bugs"
printf '# Board\n\n## Open\n\n- B001: demo bug\n' > "$P/engineering-board/demo/BOARD.md"
printf -- '---\nid: B001\ntype: bug\ntitle: demo bug\ndiscovered: 2026-06-06\nstatus: open\npriority: P2\naffects: demo/\n---\n\n# demo bug\n\n## Done when\n\n- done\n' \
  > "$P/engineering-board/demo/bugs/B001-demo-bug.md"
rc=0
CLAUDE_PROJECT_DIR="$P" bash "$ROOT/hooks/scripts/board-index-check.sh" >/dev/null 2>&1 || rc=$?
if [ "$rc" -eq 0 ]; then
  report_pass "T7 board-index-check resolves engineering-board/ (exit 0)"
else
  report_fail "T7 board-index-check resolves engineering-board/ (exit 0)" "0" "$rc"
fi

echo ""
echo "resolution-order: $PASS pass, $FAIL fail"
[ "$FAIL" -eq 0 ]

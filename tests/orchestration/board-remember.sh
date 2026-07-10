#!/usr/bin/env bash
# tests/orchestration/board-remember.sh — C6 explicit learning capture.
#
# Covers:
#   1. Script-vs-MCP output equivalence: hooks/scripts/board-remember.sh and
#      the MCP board_remember tool produce byte-identical learning files
#      (modulo id/timestamp — here the fixtures are identical so ids match and
#      only dates are normalized) AND byte-identical BOARD.md treatment.
#   2. board-index-check.sh stays green after a script remember.
#   3. board-validate-entry.sh accepts the script-produced learning.
#   4. Id sequencing: second remember allocates the next L id.
#   5. --board-dir override works without CLAUDE_PROJECT_DIR.
#   6. Usage error (missing insight) -> exit 1; no board -> exit 2.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

REMEMBER="$PLUGIN_ROOT/hooks/scripts/board-remember.sh"
SERVER="$PLUGIN_ROOT/mcp-server/engineering_board_mcp.py"
INDEX_CHECK="$PLUGIN_ROOT/hooks/scripts/board-index-check.sh"
VALIDATE="$PLUGIN_ROOT/hooks/scripts/board-validate-entry.sh"

for f in "$REMEMBER" "$SERVER" "$INDEX_CHECK" "$VALIDATE"; do
  if [ ! -f "$f" ]; then
    echo "MISSING: $f" >&2
    exit 1
  fi
done
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not on PATH" >&2
  exit 1
fi

ROOT_A=""; ROOT_B=""
cleanup() { rm -rf "$ROOT_A" "$ROOT_B" 2>/dev/null || true; }
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

mktmp() { python3 -c 'import tempfile; print(tempfile.mkdtemp(prefix="eb-remember-"))'; }

# eb_tool <root> <tool> <json-args> — call one MCP tool handler in-process.
eb_tool() {
  python3 - "$SERVER" "$1" "$2" "$3" <<'PY'
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("eb_mcp", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
args = json.loads(sys.argv[4])
args["root"] = sys.argv[2]
handler = getattr(mod, "tool_" + sys.argv[3])
print(json.dumps(handler(args)))
PY
}

INSIGHT="Always flush the buffer before close"
CONTEXT="Applies to every buffered writer in exporters."

# ── Fixture: two identical boards, init'd through the same code path ────────
ROOT_A="$(mktmp)"   # MCP remember
ROOT_B="$(mktmp)"   # script remember
eb_tool "$ROOT_A" board_init '{"project":"demo"}' >/dev/null
eb_tool "$ROOT_B" board_init '{"project":"demo"}' >/dev/null

# ── 1. Equivalence: MCP on A, script on B ───────────────────────────────────
MCP_OUT="$(eb_tool "$ROOT_A" board_remember \
  "{\"project\":\"demo\",\"insight\":\"$INSIGHT\",\"context\":\"$CONTEXT\"}")"
echo "$MCP_OUT" | grep -q '"id": "L001"' && report 0 "mcp: remember allocated L001" \
  || report 1 "mcp: remember allocated L001" "$MCP_OUT"

SCRIPT_OUT="$(CLAUDE_PROJECT_DIR="$ROOT_B" bash "$REMEMBER" "$INSIGHT" "$CONTEXT")"
echo "$SCRIPT_OUT" | grep -q '"id": "L001"' && report 0 "script: remember allocated L001" \
  || report 1 "script: remember allocated L001" "$SCRIPT_OUT"
echo "$SCRIPT_OUT" | grep -q '"source": "remember"' && report 0 "script: JSON carries source=remember" \
  || report 1 "script: JSON carries source=remember" "$SCRIPT_OUT"

L_A="$(compgen -G "$ROOT_A/engineering-board/demo/learnings/L001-*.md" | head -1 || true)"
L_B="$(compgen -G "$ROOT_B/engineering-board/demo/learnings/L001-*.md" | head -1 || true)"
[ -n "$L_A" ] && [ -n "$L_B" ] && report 0 "both twins wrote an L001 learning file" \
  || report 1 "both twins wrote an L001 learning file" "A=$L_A B=$L_B"

[ "$(basename "$L_A")" = "$(basename "$L_B")" ] \
  && report 0 "equivalence: identical filename (same slug)" \
  || report 1 "equivalence: identical filename" "$(basename "$L_A") vs $(basename "$L_B")"

# Byte equivalence modulo timestamps: normalize YYYY-MM-DD dates on both sides.
norm() { sed -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}/DATE/g' "$1"; }
if diff <(norm "$L_A") <(norm "$L_B") >/dev/null; then
  report 0 "equivalence: learning file bytes identical (modulo date)"
else
  report 1 "equivalence: learning file bytes identical (modulo date)" \
    "$(diff <(norm "$L_A") <(norm "$L_B") | head -5)"
fi

grep -q "^source: remember$" "$L_B" && report 0 "script: frontmatter has source: remember" \
  || report 1 "script: frontmatter has source: remember"

# BOARD.md treatment equivalence: full-rebuild (MCP) vs row-insert (script)
# must land on identical bytes for identical fixtures.
if diff "$ROOT_A/engineering-board/demo/BOARD.md" "$ROOT_B/engineering-board/demo/BOARD.md" >/dev/null; then
  report 0 "equivalence: BOARD.md treatment byte-identical"
else
  report 1 "equivalence: BOARD.md treatment byte-identical" \
    "$(diff "$ROOT_A/engineering-board/demo/BOARD.md" "$ROOT_B/engineering-board/demo/BOARD.md" | head -5)"
fi
grep -q "^- L001 | \[" "$ROOT_B/engineering-board/demo/BOARD.md" \
  && report 0 "script: BOARD.md gained the L001 open row" \
  || report 1 "script: BOARD.md gained the L001 open row"

# ── 2. Index-check stays green post-remember ────────────────────────────────
if CLAUDE_PROJECT_DIR="$ROOT_B" bash "$INDEX_CHECK" >/dev/null 2>&1; then
  report 0 "board-index-check.sh green after script remember"
else
  report 1 "board-index-check.sh green after script remember"
fi

# ── 3. Validator accepts the script-produced learning ───────────────────────
VOUT="$(printf '{"tool_input":{"file_path":"%s"}}' "$L_B" \
  | CLAUDE_PROJECT_DIR="$ROOT_B" bash "$VALIDATE" 2>&1)" \
  && report 0 "board-validate-entry.sh accepts the script-produced learning" \
  || report 1 "board-validate-entry.sh accepts the script-produced learning" "$VOUT"

# ── 4. Id sequencing ─────────────────────────────────────────────────────────
OUT2="$(CLAUDE_PROJECT_DIR="$ROOT_B" bash "$REMEMBER" "Second durable insight")"
echo "$OUT2" | grep -q '"id": "L002"' && report 0 "second remember allocates L002" \
  || report 1 "second remember allocates L002" "$OUT2"
CLAUDE_PROJECT_DIR="$ROOT_B" bash "$INDEX_CHECK" >/dev/null 2>&1 \
  && report 0 "index-check still green after second remember" \
  || report 1 "index-check still green after second remember"

# ── 5. --board-dir override (no CLAUDE_PROJECT_DIR needed) ──────────────────
OUT3="$(env -u CLAUDE_PROJECT_DIR bash "$REMEMBER" --board-dir "$ROOT_B/engineering-board/demo" "Third insight via explicit dir")"
echo "$OUT3" | grep -q '"id": "L003"' && report 0 "--board-dir override works" \
  || report 1 "--board-dir override works" "$OUT3"

# ── 6. Error paths ───────────────────────────────────────────────────────────
if CLAUDE_PROJECT_DIR="$ROOT_B" bash "$REMEMBER" >/dev/null 2>&1; then
  report 1 "missing insight -> exit 1" "exited 0"
else
  rc=$?
  [ "$rc" = "1" ] && report 0 "missing insight -> exit 1" \
    || report 1 "missing insight -> exit 1" "exit=$rc"
fi
NOBOARD="$(mktmp)"
if CLAUDE_PROJECT_DIR="$NOBOARD" bash "$REMEMBER" "insight" >/dev/null 2>&1; then
  report 1 "no board -> exit 2" "exited 0"
else
  rc=$?
  [ "$rc" = "2" ] && report 0 "no board -> exit 2" \
    || report 1 "no board -> exit 2" "exit=$rc"
fi
rm -rf "$NOBOARD"

echo ""
echo "================================================================"
echo "board-remember: $PASS pass, $FAIL fail"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0

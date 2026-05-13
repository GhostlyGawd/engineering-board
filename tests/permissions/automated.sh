#!/usr/bin/env bash
# tests/permissions/automated.sh -- M2.2.c permissions test suite
#
# Covers:
#   - board-permission-self-check.sh (exit codes, output format, fixture variants)
#   - references/required-permissions.json (valid JSON, expected M2.2.c patterns)
#   - commands/board-install-permissions.md (frontmatter, interactive-only framing)
#   - commands/board-claim-release.md (frontmatter, --force docs)
#
# Usage:
#   bash tests/permissions/automated.sh                # auto-detect plugin root
#   bash tests/permissions/automated.sh <plugin-root>  # explicit root
#
# Exits 0 iff all tests pass.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PLUGIN_ROOT="${1:-$DEFAULT_ROOT}"

# On Windows Git Bash, normalize MSYS-style /c/foo paths to C:/foo so Python can open them.
# cygpath is bundled with Git Bash on Windows; absent on Linux/Mac (no conversion needed).
if command -v cygpath >/dev/null 2>&1; then
  PLUGIN_ROOT="$(cygpath -m "$PLUGIN_ROOT")"
fi

SELF_CHECK="$PLUGIN_ROOT/hooks/scripts/board-permission-self-check.sh"
MANIFEST="$PLUGIN_ROOT/references/required-permissions.json"
FIXTURES="$PLUGIN_ROOT/tests/permissions/fixtures"
CMD_INSTALL="$PLUGIN_ROOT/commands/board-install-permissions.md"
CMD_RELEASE="$PLUGIN_ROOT/commands/board-claim-release.md"

PASS=0
FAIL=0

pass() { printf "[PASS] %s\n" "$1"; PASS=$((PASS + 1)); }
fail() { printf "[FAIL] %s\n" "$1"; FAIL=$((FAIL + 1)); }

assert_exit() {
  local label="$1" expected="$2"
  shift 2
  local actual
  actual=0
  "$@" >/dev/null 2>&1 || actual=$?
  if [ "$actual" -eq "$expected" ]; then
    pass "$label"
  else
    fail "$label (expected exit $expected, got $actual)"
  fi
}

assert_output_contains() {
  local label="$1" needle="$2"
  shift 2
  local out
  out="$("$@" 2>&1 || true)"
  if echo "$out" | grep -qF "$needle"; then
    pass "$label"
  else
    fail "$label (expected output to contain: $needle)"
    echo "  actual output: $out" >&2
  fi
}

# ── Test 1: self-check script exists and is bash-invokable ───────────────────
if [ -f "$SELF_CHECK" ]; then
  pass "T01: board-permission-self-check.sh exists"
else
  fail "T01: board-permission-self-check.sh exists"
fi

if bash -n "$SELF_CHECK" 2>/dev/null; then
  pass "T02: board-permission-self-check.sh passes bash syntax check"
else
  fail "T02: board-permission-self-check.sh passes bash syntax check"
fi

# ── Test 2: empty settings -> 0 installed, N missing, exit 1 ─────────────────
TOTAL="$(python3 -c "import json; d=json.load(open('$MANIFEST')); print(len(d['patterns']))")"

run_selfcheck() {
  local home_dir="$1"
  CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" HOME="$home_dir" bash "$SELF_CHECK"
}

# Build a temp HOME that points .claude/settings.json to a fixture
make_home() {
  local fixture_src="$1"
  local tmpdir
  tmpdir="$(mktemp -d)"
  mkdir -p "$tmpdir/.claude"
  if [ -n "$fixture_src" ]; then
    cp "$fixture_src" "$tmpdir/.claude/settings.json"
  fi
  echo "$tmpdir"
}

T03_HOME="$(make_home "$FIXTURES/settings-empty.json")"
out="$(CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" HOME="$T03_HOME" bash "$SELF_CHECK" 2>&1 || true)"
ec=0; CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" HOME="$T03_HOME" bash "$SELF_CHECK" >/dev/null 2>&1 || ec=$?
if [ "$ec" -eq 1 ] && echo "$out" | grep -qF "0 installed, $TOTAL missing"; then
  pass "T03: empty settings -> 0 installed, $TOTAL missing, exit 1"
else
  fail "T03: empty settings -> 0 installed, $TOTAL missing, exit 1 (got exit=$ec, out=$out)"
fi
rm -rf "$T03_HOME"

# ── Test 3: all-patterns settings -> 0 missing, exit 0 ───────────────────────
T04_HOME="$(make_home "$FIXTURES/settings-all-patterns.json")"
out="$(CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" HOME="$T04_HOME" bash "$SELF_CHECK" 2>&1 || true)"
ec=0; CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" HOME="$T04_HOME" bash "$SELF_CHECK" >/dev/null 2>&1 || ec=$?
if [ "$ec" -eq 0 ] && echo "$out" | grep -qF "0 missing"; then
  pass "T04: all-patterns settings -> 0 missing, exit 0"
else
  fail "T04: all-patterns settings -> 0 missing, exit 0 (got exit=$ec, out=$out)"
fi
rm -rf "$T04_HOME"

# ── Test 4: partial settings -> correct missing count + MISSING: lines ────────
PARTIAL_INSTALLED="$(python3 -c "import json; d=json.load(open('$FIXTURES/settings-partial.json')); print(len(d['permissions']['allow']))")"
PARTIAL_MISSING=$((TOTAL - PARTIAL_INSTALLED))

T05_HOME="$(make_home "$FIXTURES/settings-partial.json")"
out="$(CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" HOME="$T05_HOME" bash "$SELF_CHECK" 2>&1 || true)"
ec=0; CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" HOME="$T05_HOME" bash "$SELF_CHECK" >/dev/null 2>&1 || ec=$?
if [ "$ec" -eq 1 ] && echo "$out" | grep -qF "$PARTIAL_INSTALLED installed, $PARTIAL_MISSING missing"; then
  pass "T05: partial settings -> $PARTIAL_MISSING missing, exit 1"
else
  fail "T05: partial settings -> $PARTIAL_MISSING missing, exit 1 (got exit=$ec, out=$out)"
fi
if echo "$out" | grep -qF "MISSING:"; then
  pass "T06: partial settings output contains MISSING: lines"
else
  fail "T06: partial settings output contains MISSING: lines (out=$out)"
fi
rm -rf "$T05_HOME"

# ── Test 5: missing settings.json -> treated as empty, exit 1 ────────────────
T07_HOME="$(make_home "")"
ec=0; CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" HOME="$T07_HOME" bash "$SELF_CHECK" >/dev/null 2>&1 || ec=$?
if [ "$ec" -eq 1 ]; then
  pass "T07: missing settings.json treated as empty -> exit 1"
else
  fail "T07: missing settings.json treated as empty -> exit 1 (got $ec)"
fi
rm -rf "$T07_HOME"

# ── Test 6: invalid settings.json -> exit 3 ──────────────────────────────────
T08_HOME="$(make_home "$FIXTURES/settings-invalid.json")"
ec=0; CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" HOME="$T08_HOME" bash "$SELF_CHECK" >/dev/null 2>&1 || ec=$?
if [ "$ec" -eq 3 ]; then
  pass "T08: invalid settings.json -> exit 3"
else
  fail "T08: invalid settings.json -> exit 3 (got $ec)"
fi
rm -rf "$T08_HOME"

# ── Test 7: invalid manifest -> exit 2 ───────────────────────────────────────
TMPROOT="$(mktemp -d)"
mkdir -p "$TMPROOT/references" "$TMPROOT/.claude"
echo "{{bad json" > "$TMPROOT/references/required-permissions.json"
ec=0; CLAUDE_PLUGIN_ROOT="$TMPROOT" HOME="$TMPROOT" bash "$SELF_CHECK" >/dev/null 2>&1 || ec=$?
if [ "$ec" -eq 2 ]; then
  pass "T09: invalid manifest -> exit 2"
else
  fail "T09: invalid manifest -> exit 2 (got $ec)"
fi
rm -rf "$TMPROOT"

# ── Test 8: required-permissions.json is valid JSON ──────────────────────────
if python3 -c "import json; json.load(open('$MANIFEST'))" 2>/dev/null; then
  pass "T10: required-permissions.json is valid JSON"
else
  fail "T10: required-permissions.json is valid JSON"
fi

# ── Test 9: manifest contains all expected M2.2.c patterns ───────────────────
check_pattern() {
  local label="$1" pattern="$2"
  if python3 -c "import json,sys; d=json.load(open('$MANIFEST')); patterns=[p['pattern'] for p in d['patterns']]; sys.exit(0 if '$pattern' in patterns else 1)" 2>/dev/null; then
    pass "$label"
  else
    fail "$label (pattern not found: $pattern)"
  fi
}

check_pattern "T11: manifest has /pm-start" "/pm-start"
check_pattern "T12: manifest has /worker-start --discipline tdd" "/worker-start --discipline tdd"
check_pattern "T13: manifest has /worker-start --discipline review" "/worker-start --discipline review"
check_pattern "T14: manifest has /worker-start --discipline validate" "/worker-start --discipline validate"
check_pattern "T15: manifest has /board-install-permissions" "/board-install-permissions"
check_pattern "T16: manifest has /board-claim-release" "/board-claim-release"

if python3 -c "import json,sys; d=json.load(open('$MANIFEST')); patterns=[p['pattern'] for p in d['patterns']]; sys.exit(0 if any('board-permission-self-check.sh' in p for p in patterns) else 1)" 2>/dev/null; then
  pass "T17: manifest has board-permission-self-check.sh pattern"
else
  fail "T17: manifest has board-permission-self-check.sh pattern"
fi

# ── Test 10: board-install-permissions.md frontmatter ────────────────────────
if [ -f "$CMD_INSTALL" ]; then
  pass "T18: board-install-permissions.md exists"
  if grep -q "^description:" "$CMD_INSTALL"; then
    pass "T19: board-install-permissions.md has description: field"
  else
    fail "T19: board-install-permissions.md has description: field"
  fi
  if grep -q "^argument-hint: (no arguments)" "$CMD_INSTALL"; then
    pass "T20: board-install-permissions.md has argument-hint: (no arguments)"
  else
    fail "T20: board-install-permissions.md has argument-hint: (no arguments)"
  fi
else
  fail "T18: board-install-permissions.md exists"
  fail "T19: board-install-permissions.md has description: field"
  fail "T20: board-install-permissions.md has argument-hint: (no arguments)"
fi

# ── Test 11: board-claim-release.md frontmatter ──────────────────────────────
if [ -f "$CMD_RELEASE" ]; then
  pass "T21: board-claim-release.md exists"
  if grep -q "^description:" "$CMD_RELEASE"; then
    pass "T22: board-claim-release.md has description: field"
  else
    fail "T22: board-claim-release.md has description: field"
  fi
  if grep -q "^argument-hint: <entry-id>" "$CMD_RELEASE"; then
    pass "T23: board-claim-release.md has argument-hint: <entry-id>"
  else
    fail "T23: board-claim-release.md has argument-hint: <entry-id>"
  fi
else
  fail "T21: board-claim-release.md exists"
  fail "T22: board-claim-release.md has description: field"
  fail "T23: board-claim-release.md has argument-hint: <entry-id>"
fi

# ── Test 12: board-install-permissions.md has interactive-only framing ───────
if grep -qiE "interactive.only|INTERACTIVE-ONLY" "$CMD_INSTALL" 2>/dev/null; then
  pass "T24: board-install-permissions.md contains interactive-only framing"
else
  fail "T24: board-install-permissions.md contains interactive-only framing"
fi

# ── Test 13: board-claim-release.md documents --force ────────────────────────
if grep -q "\-\-force" "$CMD_RELEASE" 2>/dev/null; then
  pass "T25: board-claim-release.md documents --force flag"
else
  fail "T25: board-claim-release.md documents --force flag"
fi

# ── Summary ──────────────────────────────────────────────────────────────────
TOTAL_TESTS=$((PASS + FAIL))
echo ""
echo "================================================================"
echo "RESULT: $PASS/$TOTAL_TESTS PASS"
echo "================================================================"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0

#!/usr/bin/env bash
# tests/session-start/automated.sh — board-session-start.sh correctness + perf.
#
# Covers eb-self B001 (the blocked_by dependency map was O(unique_blockers x
# files) via a per-line `grep -rl` — it exceeded the 10s SessionStart timeout on
# ~1000+ entry boards; measured 1200 entries = 15s) and B010 (an empty board
# rendered a garbled two-line "0\n0" open-count). The surface previously had no
# automated coverage.
#
# Usage: bash tests/session-start/automated.sh [plugin-root]

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
SESSION_START="$ROOT/hooks/scripts/board-session-start.sh"

PASS=0
FAIL=0
pass() { printf "  [PASS] %s\n" "$1"; PASS=$((PASS + 1)); }
fail() { printf "  [FAIL] %s\n" "$1"; FAIL=$((FAIL + 1)); }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

make_board() {
  # make_board <project-dir> — scaffold a minimal router + empty board.
  local proj="$1"
  mkdir -p "$proj/engineering-board/demo"/{bugs,features,questions,observations,learnings}
  cat > "$proj/engineering-board/BOARD-ROUTER.md" <<'EOF'
# Board Router

| project | path | affects prefix |
|---------|------|----------------|
| demo | engineering-board/demo | demo/ |
EOF
  cat > "$proj/engineering-board/demo/BOARD.md" <<'EOF'
# demo — Board

## Open

(none)
EOF
}

# ── Test 1: empty board renders a single clean open-count line (B010) ────────
P1="$TMP/empty"
make_board "$P1"
OUT1="$(CLAUDE_PROJECT_DIR="$P1" bash "$SESSION_START" 2>/dev/null || true)"
# The header line must be exactly "[ demo ] — 0 open item(s):" with no stray 0.
if printf '%s\n' "$OUT1" | grep -qE '^\[ demo \] — 0 open item\(s\):$'; then
  pass "T1: empty board open-count is a single clean 0"
else
  fail "T1: empty board open-count garbled: $(printf '%s' "$OUT1" | grep -n 'open item' || echo '<no header>')"
fi
# Guard against the D6 double-zero specifically: no bare "0" line on its own.
if printf '%s\n' "$OUT1" | grep -qxE '0'; then
  fail "T2: stray bare '0' line present (D6 double-zero regression)"
else
  pass "T2: no stray bare '0' line"
fi

# ── Test 3: blocking relationships are correct (functional preservation) ─────
P3="$TMP/blocking"
make_board "$P3"
BUGS="$P3/engineering-board/demo/bugs"
cat > "$BUGS/B012.md" <<'EOF'
---
id: B012
type: bug
title: dependent bug
discovered: 2026-07-04
status: open
priority: P1
affects: demo/x
blocked_by: [Q003]
---
## Done when
- x
EOF
cat > "$P3/engineering-board/demo/questions/Q003.md" <<'EOF'
---
id: Q003
type: question
title: blocking question
discovered: 2026-07-04
status: open
---
## Done when
- x
EOF
OUT3="$(CLAUDE_PROJECT_DIR="$P3" bash "$SESSION_START" 2>/dev/null || true)"
if printf '%s\n' "$OUT3" | grep -qF "Q003 blocks B012"; then
  pass "T3: blocking relationship 'Q003 blocks B012' rendered"
else
  fail "T3: blocking relationship missing from output"
fi

# ── Test 4: large board renders well under the 10s SessionStart timeout (B001) ─
PBIG="$TMP/big"
make_board "$PBIG"
python3 - "$PBIG/engineering-board/demo/bugs" <<'PY'
import os, sys
d = sys.argv[1]
N = 1200
for i in range(1, N + 1):
    bid = f"B{i:04d}"
    blk = f"Q{i:04d}"
    with open(os.path.join(d, f"{bid}.md"), "w") as f:
        f.write(
            f"---\nid: {bid}\ntype: bug\ntitle: entry {i}\ndiscovered: 2026-07-04\n"
            f"status: open\npriority: P2\naffects: demo/x\nblocked_by: [{blk}]\n---\n"
            "## Done when\n- x\n"
        )
PY
# Portable elapsed-time measurement via python3 (no `date -d`, crosscompat-safe).
START="$(python3 -c 'import time; print(time.time())')"
CLAUDE_PROJECT_DIR="$PBIG" bash "$SESSION_START" >/dev/null 2>&1 || true
END="$(python3 -c 'import time; print(time.time())')"
ELAPSED="$(python3 -c "print(f'{${END} - ${START}:.2f}')")"
UNDER="$(python3 -c "print(1 if (${END} - ${START}) < 10.0 else 0)")"
if [ "$UNDER" = "1" ]; then
  pass "T4: 1200-entry board renders in ${ELAPSED}s (< 10s SessionStart timeout)"
else
  fail "T4: 1200-entry board took ${ELAPSED}s (>= 10s SessionStart timeout — O(n^2) regression)"
fi

# ── Test 5-8: current session mode is surfaced in the banner (C13 observability) ─
# Passive (no mode file) prints the passive hint naming /pm-start.
P5="$TMP/mode-passive"
make_board "$P5"
OUT5="$(CLAUDE_PROJECT_DIR="$P5" bash "$SESSION_START" 2>/dev/null || true)"
if printf '%s\n' "$OUT5" | grep -qF "Mode: passive"; then
  pass "T5: passive mode surfaced (no session-mode.json)"
else
  fail "T5: passive mode line missing"
fi

# PM mode prints the PM line and the restart-to-switch guidance.
P6="$TMP/mode-pm"
make_board "$P6"
mkdir -p "$P6/.engineering-board"
printf '{"mode":"pm","session_id":"s1"}\n' > "$P6/.engineering-board/session-mode.json"
OUT6="$(CLAUDE_PROJECT_DIR="$P6" bash "$SESSION_START" 2>/dev/null || true)"
if printf '%s\n' "$OUT6" | grep -qF "Mode: PM" && printf '%s\n' "$OUT6" | grep -qiF "fresh session"; then
  pass "T6: PM mode surfaced with restart-to-switch guidance"
else
  fail "T6: PM mode line or restart guidance missing"
fi

# Worker mode reflects the discipline.
P7="$TMP/mode-worker"
make_board "$P7"
mkdir -p "$P7/.engineering-board"
printf '{"mode":"worker","discipline":"tdd","session_id":"s1"}\n' > "$P7/.engineering-board/session-mode.json"
OUT7="$(CLAUDE_PROJECT_DIR="$P7" bash "$SESSION_START" 2>/dev/null || true)"
if printf '%s\n' "$OUT7" | grep -qF "Mode: Worker (discipline=tdd)"; then
  pass "T7: worker mode surfaced with discipline"
else
  fail "T7: worker mode line missing or discipline wrong"
fi

# Corrupt mode file falls back to passive (fail-safe, not a crash).
P8="$TMP/mode-corrupt"
make_board "$P8"
mkdir -p "$P8/.engineering-board"
printf 'not json{' > "$P8/.engineering-board/session-mode.json"
OUT8="$(CLAUDE_PROJECT_DIR="$P8" bash "$SESSION_START" 2>/dev/null || true)"
if printf '%s\n' "$OUT8" | grep -qF "Mode: passive"; then
  pass "T8: corrupt session-mode.json falls back to passive line"
else
  fail "T8: corrupt session-mode.json did not fall back cleanly"
fi

echo ""
echo "================================================================"
echo "session-start: $PASS pass, $FAIL fail"
echo "================================================================"
[ "$FAIL" -eq 0 ]

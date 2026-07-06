#!/usr/bin/env bash
# tests/view/automated.sh — board-view.sh (HTML board viewer) — eb-self F001.
# Asserts: valid self-contained document, correct pipeline columns, cards for
# real entries, byte-determinism (safe to commit), and HTML-escaping of
# untrusted entry text (no markup injection into the view).

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
VIEW="$ROOT/hooks/scripts/board-view.sh"

PASS=0; FAIL=0
pass(){ printf "  [PASS] %s\n" "$1"; PASS=$((PASS+1)); }
fail(){ printf "  [FAIL] %s\n" "$1"; FAIL=$((FAIL+1)); }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
P="$TMP/proj"
mkdir -p "$P/engineering-board/demo"/{bugs,features,questions,observations,learnings}
cat > "$P/engineering-board/BOARD-ROUTER.md" <<'EOF'
# Board Router

| project | path | affects prefix |
|---------|------|----------------|
| demo | engineering-board/demo | demo/ |
EOF
cat > "$P/engineering-board/demo/BOARD.md" <<'EOF'
# demo — Board
## Open
EOF
# One card per pipeline column + an XSS attempt in a title.
mk(){ cat > "$P/engineering-board/demo/$1"; }
mk bugs/B001.md <<'EOF'
---
id: B001
type: bug
title: todo card <script>alert(1)</script>
discovered: 2026-07-04
status: open
priority: P1
affects: src/a.py
needs: tdd
pattern: [alpha]
---
## Done when
- x
EOF
mk bugs/B002.md <<'EOF'
---
id: B002
type: bug
title: review card
discovered: 2026-07-04
status: open
priority: P2
affects: src/b.py
needs: review
---
## Done when
- x
EOF
mk bugs/B003.md <<'EOF'
---
id: B003
type: bug
title: done card
discovered: 2026-07-04
status: resolved
priority: P2
affects: src/c.py
needs: validate
---
## Done when
- x
EOF
mk questions/Q001.md <<'EOF'
---
id: Q001
type: question
title: a question
discovered: 2026-07-04
status: open
---
## Done when
- x
EOF
mk learnings/L001.md <<'EOF'
---
id: L001
type: learning
title: durable lesson worth surfacing
discovered: 2026-07-04
status: open
confidence: high
recurrence: 4
applies_to: [src/]
pattern_tag: some-pattern
---
## Lesson
- x
EOF

OUT="$(CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo --stdout 2>/dev/null)"

echo "$OUT" | grep -q '<!doctype html>' && pass "emits a self-contained HTML document" || fail "no doctype"
echo "$OUT" | grep -q 'grep-safe' 2>/dev/null || true
for col in "To do" "Review" "Validate" "Done"; do
  echo "$OUT" | grep -qF ">$col " && pass "column present: $col" || fail "column missing: $col"
done
echo "$OUT" | grep -q 'B001' && echo "$OUT" | grep -q 'B003' && pass "renders real entry ids (B001 todo, B003 done)" || fail "entry ids missing"
# XSS: the raw <script> must NOT appear; it must be escaped.
if echo "$OUT" | grep -qF '<script>alert(1)</script>'; then
  fail "untrusted title injected raw <script> into the view (XSS)"
else
  pass "untrusted title is HTML-escaped (no markup injection)"
fi
echo "$OUT" | grep -qF '&lt;script&gt;' && pass "escaped entity present for the crafted title" || fail "no escaped entity"

# F003: learnings render in their own dedicated panel (not the Q/O lane), with
# confidence + recurrence surfaced.
echo "$OUT" | grep -qF 'Learnings · durable memory' && pass "learnings panel header present" || fail "learnings panel header missing"
echo "$OUT" | grep -qF 'lcard' && echo "$OUT" | grep -q 'L001' && pass "learning L001 rendered as a panel card" || fail "learning card missing"
echo "$OUT" | grep -qF 'durable lesson worth surfacing' && pass "learning title rendered" || fail "learning title missing"
if echo "$OUT" | grep -qF '>high<' && echo "$OUT" | grep -qF '×4'; then
  pass "learning confidence + recurrence surfaced"
else
  fail "learning confidence/recurrence not surfaced"
fi
# The Q/O lane header no longer claims to include Learnings.
echo "$OUT" | grep -qF 'Questions · Observations<' && pass "Q/O lane header no longer lists Learnings" || fail "Q/O lane header not updated"

# IMPROVEMENTS #2: the blocked badge uses the --eb-danger token, and the dark
# roots override it (the hardcoded #B23A2E measured 2.96:1 on the dark bg).
echo "$OUT" | grep -qF '.badge.blocked{color:var(--eb-danger)}' && pass "blocked badge uses --eb-danger token" || fail "blocked badge still hardcoded"
DARKS=$(echo "$OUT" | grep -o -- '--eb-danger:#E4685A' | wc -l | tr -d ' ')
[ "$DARKS" = "2" ] && pass "dark roots override --eb-danger (both blocks)" || fail "dark --eb-danger override missing (found $DARKS of 2)"

# Determinism: two renders are byte-identical.
A="$(CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo --stdout 2>/dev/null)"
B="$(CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo --stdout 2>/dev/null)"
[ "$A" = "$B" ] && pass "output is byte-deterministic (safe to commit)" || fail "non-deterministic output"

# Write-mode produces board.html in the board dir.
CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo >/dev/null 2>&1
[ -f "$P/engineering-board/demo/board.html" ] && pass "write mode creates board.html" || fail "board.html not written"

echo ""
echo "================================================================"
echo "board-view: $PASS pass, $FAIL fail"
echo "================================================================"
[ "$FAIL" -eq 0 ]

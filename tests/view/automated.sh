#!/usr/bin/env bash
# tests/view/automated.sh — board-view.sh (HTML board viewer) — eb-self F001.
# Asserts: valid self-contained document, correct pipeline columns, cards for
# real entries, byte-determinism (safe to commit), and HTML-escaping of
# untrusted entry text (no markup injection into the view).

# Do not use pipefail in this test. The grep -q checks close their input early.
# With pipefail, a successful match can report the writer's SIGPIPE as a test
# failure.
set -u
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
subtype: pattern
title: durable lesson worth surfacing
discovered: 2026-07-04
status: open
confidence: high
confidence_basis: Four resolved sources and one held fix outcome.
recurrence: 4
derived_from: [B001, B002, B003, B004]
applies_to: [src/]
pattern_ids: [P001]
pattern_tag: some-pattern
outcome_status: supported
outcome_refs: []
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
if echo "$OUT" | grep -qF '>supported<' &&
   echo "$OUT" | grep -qF 'Four resolved sources and one held fix outcome.'; then
  pass "Learning outcome state and confidence basis surfaced"
else
  fail "Learning outcome state or confidence basis missing"
fi
if echo "$OUT" | grep -qF 'useful resurfacing' &&
   echo "$OUT" | grep -qF 'confirmed systemic fixes'; then
  pass "canonical outcome-value strip surfaced"
else
  fail "outcome-value strip missing"
fi
# The Q/O lane header no longer claims to include Learnings.
echo "$OUT" | grep -qF 'Questions · Observations<' && pass "Q/O lane header no longer lists Learnings" || fail "Q/O lane header not updated"

# Graphite uses explicit state labels and shared semantic contrast in both themes.
echo "$OUT" | grep -qF '.badge.blocked{color:var(--eb-danger)}' && pass "blocked badge uses semantic danger token" || fail "blocked badge token missing"
printf '%s\n' "$OUT" > "$TMP/view.html"
python3 - "$TMP/view.html" "$ROOT" <<'PYSTYLE' && pass "Graphite: source tokens, embedded font, landmarks, contrast and offline assets" || fail "Graphite source/offline/accessibility contract"
import base64, re, sys
from html.parser import HTMLParser
from pathlib import Path
page = Path(sys.argv[1]).read_text()
root = Path(sys.argv[2])
source = (root / "brand/tokens.css").read_text()
font = (root / "brand/fonts/manrope-latin-wght-normal.woff2").read_bytes()
style = re.search(r'<style id="eb-brand-tokens">\n(.*?)</style>', page, re.S).group(1)
embedded = re.search(r'data:font/woff2;base64,([A-Za-z0-9+/=]+)', style)
assert embedded and base64.b64decode(embedded.group(1)) == font, "font differs from packaged bytes"
assert style.replace(embedded.group(0), 'fonts/manrope-latin-wght-normal.woff2').strip() == source.strip(), "shared CSS drift"
assert not re.search(r'url\([\s\'"]*(?!data:)[^\s\'"]', style), "nonembedded CSS resource"
assert '#9a5b00' not in page.lower() and '#e6a94e' not in page.lower(), "old amber palette"
class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]
    def handle_starttag(self, tag, attrs): self.tags.append((tag, dict(attrs)))
doc = Document(); doc.feed(page)
assert any(t == 'html' and a.get('data-theme') == 'dark' for t,a in doc.tags)
assert sum(t == 'main' and a.get('id') == 'main' for t,a in doc.tags) == 1
assert any(t == 'a' and a.get('href') == '#main' for t,a in doc.tags)
assert any(t == 'button' and a.get('id') == 'eb-theme' and 'hidden' in a and a.get('aria-pressed') == 'false' for t,a in doc.tags)
assert 'Static board · Read-only.' in page and 'Regenerate with <code>/board-view</code>' in page
assert 'Ranked investigations and their evidence remain visible.' in page
assert '[hidden]{display:none!important}' in page
assert all(not a.get('src') and not (t == 'link' and a.get('rel') == 'stylesheet') for t,a in doc.tags), "external render dependency"
assert not any(t in ('img','svg') for t,a in doc.tags), "viewer identity must be wordmark only"
def luminance(h):
    h=h.lstrip('#'); h=''.join(c*2 for c in h) if len(h)==3 else h
    rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    rgb=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in rgb]
    return sum(c*w for c,w in zip(rgb,[.2126,.7152,.0722]))
base=dict(re.findall(r'(--eb-[\w-]+):\s*(#[0-9A-Fa-f]+)',re.search(r':root\s*{(.*?)}',source,re.S).group(1)))
light=dict(base); light.update(re.findall(r'(--eb-[\w-]+):\s*(#[0-9A-Fa-f]+)',re.search(r':root\[data-theme="light"\]\s*{(.*?)}',source,re.S).group(1)))
for theme in (base,light):
    for fg in ('--eb-text','--eb-muted','--eb-danger'):
        for bg in ('--eb-bg','--eb-panel'):
            hi,lo=sorted([luminance(theme[fg]),luminance(theme[bg])],reverse=True)
            assert (hi+.05)/(lo+.05)>=4.5,(fg,bg,"contrast below 4.5")
PYSTYLE

# Script-only distributions retain a complete offline fallback, and token-only
# distributions must not leave a dangling font URL in generated HTML.
mkdir -p "$TMP/reduced/hooks/scripts" "$TMP/reduced/brand"
cp "$VIEW" "$ROOT/hooks/scripts/board-paths.sh" "$TMP/reduced/hooks/scripts/"
FALLBACK="$(CLAUDE_PROJECT_DIR="$P" bash "$TMP/reduced/hooks/scripts/board-view.sh" demo --stdout 2>/dev/null)"
if echo "$FALLBACK" | grep -q '<main id="main">' && echo "$FALLBACK" | grep -q 'B001' && ! echo "$FALLBACK" | grep -q 'url('; then
  pass "Graphite: script-only fallback renders entries without asset requests"
else
  fail "Graphite: script-only fallback broken"
fi
cp "$ROOT/brand/tokens.css" "$TMP/reduced/brand/tokens.css"
TOKEN_ONLY="$(CLAUDE_PROJECT_DIR="$P" bash "$TMP/reduced/hooks/scripts/board-view.sh" demo --stdout 2>/dev/null)"
if echo "$TOKEN_ONLY" | grep -q 'B001' && ! echo "$TOKEN_ONLY" | grep -q 'url('; then
  pass "Graphite: missing optional font falls back without a dangling URL"
else
  fail "Graphite: token-only font fallback broken"
fi

# The synthetic demo must consume the same exact theme and font as normal
# boards while retaining its explicit proposed-state, evidence and falsifier.
mkdir -p "$TMP/sample/hypotheses"
cat > "$TMP/sample/graph.json" <<'JSON'
{"nodes":{"B001":{"title":"Synthetic <finding>","source":"bugs/B001.md","affects":"src/a.py","pattern":["alpha"]}},"topology":{"clusters":[{"id":"C001","members":["B001"],"affected_domains":["src"],"patterns":["alpha"],"density":1}]}}
JSON
cat > "$TMP/sample/hypotheses/H001.md" <<'MD'
---
id: H001
title: A proposed explanation
status: proposed
---
## Proposed root cause
One shared rule may differ.
## Supporting evidence
- B001 records the symptom.
## Alternative explanations
- Independent local errors.
## Falsifier
All adapters use the same rule.
MD
CLAUDE_PROJECT_DIR="$P" bash "$VIEW" --demo-dir "$TMP/sample" --stdout > "$TMP/sample.html"
python3 - "$TMP/view.html" "$TMP/sample.html" <<'PYDEMO' && pass "Graphite: demo shares exact self-contained brand styles and preserves evidence states" || fail "Graphite demo contract"
from pathlib import Path
import re, sys
normal, demo = (Path(p).read_text() for p in sys.argv[1:])
def style(page): return re.search(r'<style id="eb-brand-tokens">\n(.*?)</style>',page,re.S).group(1)
assert style(normal) == style(demo)
for expected in ('<main id="main">', 'id="eb-theme"', 'Synthetic example · Read-only',
                 '&lt;finding&gt;', 'status: proposed', 'Supporting evidence', 'Alternative explanations',
                 'Falsifier', 'All adapters use the same rule.', '<code>/board-demo</code>'):
    assert expected in demo, expected
assert not re.search(r'#[0-9a-f]*[a-f0-9]',re.sub(r'<style id="eb-brand-tokens">.*?</style>','',demo,flags=re.S),re.I), 'demo duplicates palette'
PYDEMO

# IMPROVEMENTS #8: entry cards link to their markdown sources.
echo "$OUT" | grep -q '<a class="cid" href="bugs/B001.md">B001</a>' && pass "card id links to its entry file (relative)" || fail "card link missing"
LB="$(CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo --stdout --link-base "https://ex.test/base/" 2>/dev/null)"
echo "$LB" | grep -q 'href="https://ex.test/base/bugs/B001.md"' && pass "--link-base prefixes card links" || fail "--link-base not applied"

# IMPROVEMENTS #8: Done column collapses beyond 10 resolved entries.
for i in $(seq 10 22); do
  mk "bugs/B0${i}.md" <<EOF
---
id: B0${i}
type: bug
title: resolved filler ${i}
discovered: 2026-07-04
status: resolved
priority: P3
affects: src/f.py
needs: validate
---
## Done when
- x
EOF
done
BIG="$(CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo --stdout 2>/dev/null)"
echo "$BIG" | grep -q 'more resolved</summary>' && pass "Done column collapses beyond 10 (details/summary)" || fail "Done collapse missing"

# IMPROVEMENTS #8: --stamp adds a freshness line; default stays deterministic.
ST="$(CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo --stdout --stamp 2>/dev/null)"
echo "$ST" | grep -q 'Generated from <code>' && pass "--stamp adds a freshness footer" || fail "--stamp missing"
echo "$OUT" | grep -q 'Generated from <code>' && fail "default output leaks a stamp (breaks determinism)" || pass "default output has no stamp"

# Print styles exist.
echo "$OUT" | grep -q '@media print' && pass "print styles present" || fail "print styles missing"

# Determinism: two renders are byte-identical.
A="$(CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo --stdout 2>/dev/null)"
B="$(CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo --stdout 2>/dev/null)"
[ "$A" = "$B" ] && pass "output is byte-deterministic (safe to commit)" || fail "non-deterministic output"

# Write-mode produces board.html in the board dir.
CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo >/dev/null 2>&1
[ -f "$P/engineering-board/demo/board.html" ] && pass "write mode creates board.html" || fail "board.html not written"

# ---------------------------------------------------------------------------
# C4 — client-side search + filters (controls hidden without JS; vanilla JS).
# ---------------------------------------------------------------------------
echo "$OUT" | grep -q '<div class="controls" id="eb-controls" hidden>' && pass "C4: controls markup present and hidden in static HTML" || fail "C4: controls markup missing or not hidden"
echo "$OUT" | grep -q 'id="eb-search"' && pass "C4: search input present" || fail "C4: search input missing"
if echo "$OUT" | grep -q 'data-fgroup="type"' && echo "$OUT" | grep -q 'data-fval="p0"' && echo "$OUT" | grep -q 'data-fval="resolved"'; then
  pass "C4: type/priority/status filter chips present"
else
  fail "C4: filter chips missing"
fi
echo "$OUT" | grep -q '<script>' && pass "C4: embedded JS block present" || fail "C4: JS block missing"
echo "$OUT" | grep -qF "key === '/'" && pass "C4: '/' focuses search (keydown handler)" || fail "C4: slash-focus handler missing"
# Cards carry the data attributes the filter needs.
if echo "$OUT" | grep -q 'data-type="bug"' && echo "$OUT" | grep -q 'data-priority="p1"' && echo "$OUT" | grep -q 'data-status="open"'; then
  pass "C4: cards carry data-type/data-priority/data-status"
else
  fail "C4: card data attributes missing"
fi
echo "$OUT" | grep -q 'data-search="b001 todo card' && pass "C4: cards carry lowercase searchable text (id + title)" || fail "C4: data-search missing"
echo "$OUT" | grep -q 'class="no-match" hidden' && pass "C4: empty-state message present (hidden by default)" || fail "C4: empty-state div missing"
# The searchable text of the XSS title must still be escaped in the attribute.
echo "$OUT" | grep -qF 'data-search="b001 todo card &lt;script&gt;' && pass "C4: data-search escapes untrusted title text" || fail "C4: data-search not escaped"

# ---------------------------------------------------------------------------
# C7 (view part) — parent badge on child cards.
# ---------------------------------------------------------------------------
mk features/F001.md <<'EOF'
---
id: F001
type: feature
title: child feature under a bug
discovered: 2026-07-04
status: open
priority: P2
affects: src/d.py
needs: tdd
parent: B001
---
## Done when
- x
EOF
PARENT_OUT="$(CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo --stdout 2>/dev/null)"
echo "$PARENT_OUT" | grep -qF '<span class="badge parent">↳ B001</span>' && pass "C7: parent badge rendered on a parent-carrying card" || fail "C7: parent badge missing"
echo "$OUT" | grep -qF 'badge parent' && fail "C7: parent badge leaks onto cards without parent" || pass "C7: no parent badge without parent frontmatter"

# ---------------------------------------------------------------------------
# C12 — Stats panel (pure derivation from parsed entries).
# Fixture at this point: bugs = B001 open, B002 open, B003 + B010..B022 resolved
# (14 resolved); features = F001 open; questions = Q001 open; learnings = L001.
# ---------------------------------------------------------------------------
echo "$PARENT_OUT" | grep -qF '>Stats</h2>' && pass "C12: stats panel header present" || fail "C12: stats panel missing"
echo "$PARENT_OUT" | grep -qF 'bugs</span> <span class="stat-v">2 open · 14 resolved' && pass "C12: per-type bug counts correct" || fail "C12: bug counts wrong"
echo "$PARENT_OUT" | grep -qF 'features</span> <span class="stat-v">1 open · 0 resolved' && pass "C12: per-type feature counts correct" || fail "C12: feature counts wrong"
echo "$PARENT_OUT" | grep -qF 'learnings</span> <span class="stat-v">1</span>' && pass "C12: learnings total correct" || fail "C12: learnings total wrong"
echo "$PARENT_OUT" | grep -qF 'alpha ×1' && pass "C12: top pattern tags among open entries surfaced" || fail "C12: top pattern tags missing"

# ---------------------------------------------------------------------------
# C12 — Coordination panel: graceful empty states without runtime artifacts.
# ---------------------------------------------------------------------------
echo "$PARENT_OUT" | grep -qF '>Coordination</h2>' && pass "C12: coordination panel header present" || fail "C12: coordination panel missing"
if echo "$PARENT_OUT" | grep -qF 'no active claims' && echo "$PARENT_OUT" | grep -qF 'no recent reclaims' && echo "$PARENT_OUT" | grep -qF 'no active workers'; then
  pass "C12: coordination empty states (no _claims / log / registry)"
else
  fail "C12: coordination empty states missing"
fi

# Coordination with a real claim dir: owner + entry id shown, escaped.
mkdir -p "$P/engineering-board/demo/_claims/B001"
cat > "$P/engineering-board/demo/_claims/B001/owner.txt" <<'EOF'
session_id: sess-abc123 <b>evil</b>
timestamp: 2026-07-04T00:00:00Z
cwd: /tmp/x
EOF
# _reclaimed.log: one malformed line (skipped, not fatal) + one valid line.
cat > "$P/engineering-board/demo/_claims/_reclaimed.log" <<'EOF'
this is not json {{{
{"reclaimed_at": "2026-07-03T12:00:00Z", "entry_id": "B002", "reason": "stale_no_heartbeat", "age_sec": 999.0, "stale_threshold_sec": 600, "owner_info": "session_id: old-sess"}
EOF
# Active-workers registry (project-level runtime state).
mkdir -p "$P/.engineering-board"
cat > "$P/.engineering-board/active-workers.json" <<'EOF'
[{"session_id": "worker-1234567890", "started_at": "2026-07-04T00:00:00Z", "last_seen": "2026-07-04T00:05:00Z", "mode": "worker", "discipline": "tdd", "cwd": "/tmp/x", "claim_ids_held": ["B001"], "paused": false}]
EOF
COORD="$(CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo --stdout 2>/dev/null)"
[ -n "$COORD" ] && pass "C12: render survives runtime artifacts present" || fail "C12: render failed with runtime artifacts"
if echo "$COORD" | grep -qF 'B001' && echo "$COORD" | grep -qF 'sess-abc123'; then
  pass "C12: current claim shows entry id + owner"
else
  fail "C12: claim owner/id not rendered"
fi
echo "$COORD" | grep -qF '<b>evil</b>' && fail "C12: owner.txt content injected raw (XSS)" || pass "C12: claim owner content is HTML-escaped"
echo "$COORD" | grep -qF 'B002 · 2026-07-03T12:00:00Z' && pass "C12: valid reclaim line rendered (entry id + time)" || fail "C12: reclaim line missing"
echo "$COORD" | grep -qF 'this is not json' && fail "C12: malformed reclaim line leaked into output" || pass "C12: malformed reclaimed.log line skipped, not fatal"
if echo "$COORD" | grep -qF 'worker-1234' && echo "$COORD" | grep -qF '>worker' ; then
  pass "C12: active worker rendered (mode + session)"
else
  fail "C12: active worker missing"
fi

# Garbled runtime files must never fail the render.
echo 'garbage{{{' > "$P/.engineering-board/active-workers.json"
echo 'not even close' > "$P/engineering-board/demo/_claims/B001/owner.txt"
GARBLED="$(CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo --stdout 2>/dev/null)"; RC=$?
if [ "$RC" -eq 0 ] && echo "$GARBLED" | grep -q '<!doctype html>'; then
  pass "C12: garbled owner.txt + registry degrade gracefully (render still ok)"
else
  fail "C12: garbled runtime files broke the render (rc=$RC)"
fi
echo "$GARBLED" | grep -qF 'no active workers' && pass "C12: garbled registry falls back to empty state" || fail "C12: garbled registry not treated as empty"

# Byte-determinism holds with coordination data in the input tree.
C1="$(CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo --stdout 2>/dev/null)"
C2="$(CLAUDE_PROJECT_DIR="$P" bash "$VIEW" demo --stdout 2>/dev/null)"
[ "$C1" = "$C2" ] && pass "C12: byte-deterministic with claims/reclaims/workers present" || fail "C12: non-deterministic with coordination data"

echo ""
echo "================================================================"
echo "board-view: $PASS pass, $FAIL fail"
echo "================================================================"
[ "$FAIL" -eq 0 ]

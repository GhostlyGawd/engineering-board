#!/usr/bin/env bash
# tests/security/reject-filter.sh — Injection reject-filter corpus test.
#
# Feeds every adversarial-paste and benign-findings fixture through the
# canonical reject filter (hooks/scripts/board_reject_check.py — the same code
# board-consolidate.sh applies when promoting scratch findings to the live
# board) and asserts each fixture's declared `expect:` outcome (and, for
# adversarial fixtures, the `expect_reason:`).
#
# This is the suite whose absence let a trivially-bypassable filter ship: the
# 50 fixtures existed but no script consumed them (eb-self B003). It also pins
# the M2 hardening (eb-self B002): non-leading / mid-clause imperatives,
# broadened verb set, case-insensitive slash & subagent directives, and
# payloads smuggled through the `affects`/`tags` fields (not just title/quote).
# Board entries are read, never eval'd, so the filter targets instructions to
# the agent — not the mere presence of shell/HTML metacharacters, which recur in
# legitimate technical findings (benign-023/024 assert those still promote).
#
# Usage: bash tests/security/reject-filter.sh [plugin-root]
# Exits 0 iff every fixture classifies as declared.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
cd "$ROOT"

PASS=0
FAIL=0

pass() { printf "  [PASS] %s\n" "$1"; PASS=$((PASS + 1)); }
fail() { printf "  [FAIL] %s\n" "$1"; FAIL=$((FAIL + 1)); }

# Convert one fixture .md into a finding JSON and run it through the canonical
# CLI. Prints the classifier verdict ("accept" or "reject:<reason>").
classify_fixture() {
  python3 - "$1" <<'PY'
import json, re, sys, subprocess, os
path = sys.argv[1]
txt = open(path, encoding="utf-8").read()

def rx(pattern):
    m = re.search(pattern, txt, re.M)
    return m.group(1).strip() if m else ""

title = rx(r'^#\s*(.+)$')
quote = rx(r'evidence_quote:\s*"?(.*?)"?\s*$')
affects = rx(r'^-\s*affects:\s*(.+)$')
tags_raw = rx(r'^-\s*tags:\s*\[(.*)\]\s*$')
tags = []
for t in tags_raw.split(","):
    t = t.strip().strip('"').strip("'")
    if t:
        tags.append(t)

finding = {"title": title, "evidence_quote": quote, "affects": affects, "tags": tags}
proc = subprocess.run(
    ["python3", os.path.join("hooks", "scripts", "board_reject_check.py")],
    input=json.dumps(finding), capture_output=True, text=True,
)
sys.stdout.write(proc.stdout.strip())
PY
}

fixture_field() { grep -m1 "^$2:" "$1" | sed "s/^$2:[[:space:]]*//"; }

echo "== Adversarial corpus (must reject with declared reason) =="
adv_count=0
for f in tests/fixtures/adversarial-paste/adv-*.md; do
  [ -f "$f" ] || continue
  adv_count=$((adv_count + 1))
  id=$(fixture_field "$f" id)
  want_reason=$(fixture_field "$f" expect_reason)
  verdict=$(classify_fixture "$f")
  if [[ "$verdict" == reject:* ]]; then
    got_reason="${verdict#reject:}"
    if [ -z "$want_reason" ] || [ "$got_reason" = "$want_reason" ]; then
      pass "$id rejected ($got_reason)"
    else
      fail "$id rejected but reason mismatch: want '$want_reason' got '$got_reason'"
    fi
  else
    fail "$id NOT rejected (verdict: $verdict) — injection payload would promote to the board"
  fi
done

echo "== Benign corpus (must accept) =="
ben_count=0
for f in tests/fixtures/benign-findings/benign-*.md; do
  [ -f "$f" ] || continue
  ben_count=$((ben_count + 1))
  id=$(fixture_field "$f" id)
  verdict=$(classify_fixture "$f")
  if [ "$verdict" = "accept" ]; then
    pass "$id accepted"
  else
    fail "$id wrongly rejected ($verdict) — false positive on a legitimate finding"
  fi
done

# Guard the corpus can't silently shrink to nothing (the failure mode B003 was).
if [ "$adv_count" -lt 30 ]; then fail "adversarial corpus shrank: $adv_count < 30"; fi
if [ "$ben_count" -lt 20 ]; then fail "benign corpus shrank: $ben_count < 20"; fi

echo ""
echo "================================================================"
echo "reject-filter: $PASS pass, $FAIL fail (adversarial=$adv_count, benign=$ben_count)"
echo "================================================================"
[ "$FAIL" -eq 0 ]

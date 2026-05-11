#!/usr/bin/env bash
# tests/modes/command-frontmatter.sh — Structural lint for /pm-start and /worker-start slash command files.
#
# Slash commands in this plugin are markdown files Claude reads at runtime. There's no
# runtime to unit-test, so we lint the file structure: YAML frontmatter shape, required
# fields, and presence of the procedural steps the consensus plan locks in.
#
# Exits 0 iff all assertions pass.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

PASS=0
FAIL=0
report() {
  if [ "$1" = "0" ]; then
    printf "  [PASS] %s\n" "$2"
    PASS=$((PASS + 1))
  else
    printf "  [FAIL] %s%s\n" "$2" "${3:+ -- $3}"
    FAIL=$((FAIL + 1))
  fi
}

# ── /pm-start ────────────────────────────────────────────────────────────────
PM_START="$ROOT/commands/pm-start.md"
if [ ! -f "$PM_START" ]; then
  echo "MISSING FILE: $PM_START" >&2
  exit 1
fi

# Frontmatter must exist and contain description + argument-hint.
if head -1 "$PM_START" | grep -qF -- "---"; then
  report 0 "pm-start.md has frontmatter delimiter"
else
  report 1 "pm-start.md has frontmatter delimiter"
fi

grep -qE "^description:" "$PM_START" && report 0 "pm-start.md frontmatter: description" || report 1 "pm-start.md frontmatter: description"
grep -qE "^argument-hint:" "$PM_START" && report 0 "pm-start.md frontmatter: argument-hint" || report 1 "pm-start.md frontmatter: argument-hint"

# Body must reference the state file path, the mode value, and the idempotency check.
grep -qF '.engineering-board/session-mode.json' "$PM_START" && report 0 "pm-start.md references session-mode.json" || report 1 "pm-start.md references session-mode.json"
grep -qF '"mode": "pm"' "$PM_START" && report 0 "pm-start.md writes mode=pm" || report 1 "pm-start.md writes mode=pm"
grep -qF 'started_at' "$PM_START" && report 0 "pm-start.md writes started_at" || report 1 "pm-start.md writes started_at"
grep -qF 'session_id' "$PM_START" && report 0 "pm-start.md writes session_id" || report 1 "pm-start.md writes session_id"
grep -qF 'already in PM mode' "$PM_START" && report 0 "pm-start.md idempotent short-circuit" || report 1 "pm-start.md idempotent short-circuit"

# ── /worker-start ────────────────────────────────────────────────────────────
WORKER_START="$ROOT/commands/worker-start.md"
if [ ! -f "$WORKER_START" ]; then
  echo "MISSING FILE: $WORKER_START" >&2
  exit 1
fi

if head -1 "$WORKER_START" | grep -qF -- "---"; then
  report 0 "worker-start.md has frontmatter delimiter"
else
  report 1 "worker-start.md has frontmatter delimiter"
fi

grep -qE "^description:" "$WORKER_START" && report 0 "worker-start.md frontmatter: description" || report 1 "worker-start.md frontmatter: description"
grep -qE "^argument-hint:" "$WORKER_START" && report 0 "worker-start.md frontmatter: argument-hint" || report 1 "worker-start.md frontmatter: argument-hint"

grep -qF -- '--discipline' "$WORKER_START" && report 0 "worker-start.md mentions --discipline arg" || report 1 "worker-start.md mentions --discipline arg"
grep -qF '"mode": "worker"' "$WORKER_START" && report 0 "worker-start.md writes mode=worker" || report 1 "worker-start.md writes mode=worker"
grep -qF '"discipline":' "$WORKER_START" && report 0 "worker-start.md writes discipline field" || report 1 "worker-start.md writes discipline field"
grep -qF 'tdd' "$WORKER_START" && report 0 "worker-start.md mentions tdd discipline" || report 1 "worker-start.md mentions tdd discipline"

# Must reject unsupported disciplines (M2.2.b ships only tdd).
grep -qiE "unsupported discipline|only.*tdd|tdd.*only" "$WORKER_START" && report 0 "worker-start.md rejects non-tdd disciplines" || report 1 "worker-start.md rejects non-tdd disciplines"

grep -qF 'already in worker mode' "$WORKER_START" && report 0 "worker-start.md idempotent short-circuit" || report 1 "worker-start.md idempotent short-circuit"

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "command-frontmatter: $PASS pass, $FAIL fail"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0

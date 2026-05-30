#!/usr/bin/env bash
# tests/modes/command-frontmatter.sh — Structural lint for the four
# session-mode slash command files: /pm-start, /worker-start, /board-pause,
# /board-resume.
#
# Slash commands in this plugin are markdown files Claude reads at runtime.
# There's no runtime to unit-test, so we lint the file structure: YAML
# frontmatter shape, required fields, presence of the procedural steps the
# consensus plan locks in, and (since v0.3.1) that each command delegates
# its refusal-matrix decision to hooks/scripts/board-mode-guard.sh instead
# of re-implementing the matrix inline.
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

# v0.3.1: delegates to the mode-transition guard.
grep -qF 'board-mode-guard.sh' "$PM_START" && report 0 "pm-start.md invokes board-mode-guard.sh" || report 1 "pm-start.md invokes board-mode-guard.sh"
grep -qE 'board-mode-guard\.sh.* pm( |$)' "$PM_START" && report 0 "pm-start.md passes 'pm' target to guard" || report 1 "pm-start.md passes 'pm' target to guard"

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

# M2.2.c: all three disciplines must be present in the supported set.
grep -qF 'review' "$WORKER_START" && report 0 "worker-start.md mentions review discipline" || report 1 "worker-start.md mentions review discipline"
grep -qF 'validate' "$WORKER_START" && report 0 "worker-start.md mentions validate discipline" || report 1 "worker-start.md mentions validate discipline"

# argument-hint must reflect all three disciplines.
grep -qE 'argument-hint:.*tdd.*review.*validate|argument-hint:.*tdd\|review\|validate' "$WORKER_START" && report 0 "worker-start.md argument-hint includes tdd|review|validate" || report 1 "worker-start.md argument-hint includes tdd|review|validate"

# Must reject unsupported disciplines (M2.2.c ships tdd, review, validate).
grep -qiE 'unsupported discipline' "$WORKER_START" && report 0 "worker-start.md rejects unsupported disciplines" || report 1 "worker-start.md rejects unsupported disciplines"

# Rejection message must name all three valid disciplines.
grep -qiE 'ships disciplines: tdd, review, validate|disciplines.*tdd.*review.*validate' "$WORKER_START" && report 0 "worker-start.md rejection message names all three disciplines" || report 1 "worker-start.md rejection message names all three disciplines"

grep -qF 'already in worker mode' "$WORKER_START" && report 0 "worker-start.md idempotent short-circuit" || report 1 "worker-start.md idempotent short-circuit"

# v0.3.1: delegates to the mode-transition guard.
grep -qF 'board-mode-guard.sh' "$WORKER_START" && report 0 "worker-start.md invokes board-mode-guard.sh" || report 1 "worker-start.md invokes board-mode-guard.sh"
grep -qE 'board-mode-guard\.sh.* worker( |$)' "$WORKER_START" && report 0 "worker-start.md passes 'worker' target to guard" || report 1 "worker-start.md passes 'worker' target to guard"

# ── /board-pause ─────────────────────────────────────────────────────────────
BOARD_PAUSE="$ROOT/commands/board-pause.md"
if [ ! -f "$BOARD_PAUSE" ]; then
  echo "MISSING FILE: $BOARD_PAUSE" >&2
  exit 1
fi

if head -1 "$BOARD_PAUSE" | grep -qF -- "---"; then
  report 0 "board-pause.md has frontmatter delimiter"
else
  report 1 "board-pause.md has frontmatter delimiter"
fi

grep -qE "^description:" "$BOARD_PAUSE" && report 0 "board-pause.md frontmatter: description" || report 1 "board-pause.md frontmatter: description"
grep -qE "^argument-hint:" "$BOARD_PAUSE" && report 0 "board-pause.md frontmatter: argument-hint" || report 1 "board-pause.md frontmatter: argument-hint"

grep -qF '"mode": "paused"' "$BOARD_PAUSE" && report 0 "board-pause.md writes mode=paused" || report 1 "board-pause.md writes mode=paused"
grep -qF 'previous_mode' "$BOARD_PAUSE" && report 0 "board-pause.md preserves previous_mode" || report 1 "board-pause.md preserves previous_mode"
grep -qF 'previous_discipline' "$BOARD_PAUSE" && report 0 "board-pause.md preserves previous_discipline (matrix bit-exact resume)" || report 1 "board-pause.md preserves previous_discipline (matrix bit-exact resume)"
grep -qF 'already paused' "$BOARD_PAUSE" && report 0 "board-pause.md idempotent short-circuit" || report 1 "board-pause.md idempotent short-circuit"

# v0.3.1: delegates to the mode-transition guard.
grep -qF 'board-mode-guard.sh' "$BOARD_PAUSE" && report 0 "board-pause.md invokes board-mode-guard.sh" || report 1 "board-pause.md invokes board-mode-guard.sh"
grep -qE 'board-mode-guard\.sh.* paused( |$)' "$BOARD_PAUSE" && report 0 "board-pause.md passes 'paused' target to guard" || report 1 "board-pause.md passes 'paused' target to guard"

# ── /board-resume ────────────────────────────────────────────────────────────
BOARD_RESUME="$ROOT/commands/board-resume.md"
if [ ! -f "$BOARD_RESUME" ]; then
  echo "MISSING FILE: $BOARD_RESUME" >&2
  exit 1
fi

if head -1 "$BOARD_RESUME" | grep -qF -- "---"; then
  report 0 "board-resume.md has frontmatter delimiter"
else
  report 1 "board-resume.md has frontmatter delimiter"
fi

grep -qE "^description:" "$BOARD_RESUME" && report 0 "board-resume.md frontmatter: description" || report 1 "board-resume.md frontmatter: description"
grep -qE "^argument-hint:" "$BOARD_RESUME" && report 0 "board-resume.md frontmatter: argument-hint" || report 1 "board-resume.md frontmatter: argument-hint"

grep -qF 'not currently paused' "$BOARD_RESUME" && report 0 "board-resume.md NOOP message" || report 1 "board-resume.md NOOP message"
grep -qF 'RESTORE_DISCIPLINE' "$BOARD_RESUME" && report 0 "board-resume.md restores discipline (matrix bit-exact)" || report 1 "board-resume.md restores discipline (matrix bit-exact)"

# v0.3.1: delegates to the mode-transition guard.
grep -qF 'board-mode-guard.sh' "$BOARD_RESUME" && report 0 "board-resume.md invokes board-mode-guard.sh" || report 1 "board-resume.md invokes board-mode-guard.sh"
grep -qE 'board-mode-guard\.sh.* resumed( |$)' "$BOARD_RESUME" && report 0 "board-resume.md passes 'resumed' target to guard" || report 1 "board-resume.md passes 'resumed' target to guard"

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "command-frontmatter: $PASS pass, $FAIL fail"

if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
exit 0

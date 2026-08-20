#!/usr/bin/env bash
# tests/run-all.sh — Single CI runner for the entire engineering-board test
# suite.
#
# NEXT-PHASE.md Tier 4.1 (Single CI runner).
#
# Invokes every `automated.sh` under tests/ plus the standalone lints. Each
# sub-suite reports its own pass/fail; this runner exits 0 iff every
# sub-suite exits 0.
#
# The hooks.json regression caught in commit 52e99a4 lived in the tree for
# ~13 days because nobody ran all the suites together. This runner exists
# so "confirm green" is one command, not six.
#
# Usage:
#   bash tests/run-all.sh                # auto-detect plugin root
#   bash tests/run-all.sh <plugin-root>  # explicit root
#
# Exits 0 iff every sub-suite passes.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"

if [ -z "${ENGINEERING_BOARD_VALIDATOR_SESSION:-}" ]; then
  exec python3 "$ROOT/scripts/validator_resources.py" \
    --state-root "$ROOT/.engineering-board/validator-locks" \
    run --label legacy-run-all --exclusive aggregate -- \
    bash "$0" "$ROOT"
fi

# Sub-suite manifest. Each entry: "<label>|<command>".
# Commands are run from $ROOT with $ROOT passed as their argument.
SUITES=(
  "orchestration|bash tests/orchestration/automated.sh"
  "claims|bash tests/claims/automated.sh"
  "smoke|bash tests/smoke/automated.sh"
  "scratch-append|bash tests/scratch/append.sh"
  "paths|bash tests/paths/resolution-order.sh"
  "modes|bash tests/modes/automated.sh"
  "permissions|bash tests/permissions/automated.sh"
  "workflow-actions|bash tests/workflow-actions.sh"
  "lint-orchestrator-prompts|bash tests/lint-orchestrator-prompts.sh"
  "version-coherence|bash tests/version-coherence.sh"
  "codex-plugin|bash tests/codex-plugin.sh"
  "release-preparation|bash tests/release-preparation.sh"
  "docs-coherence|bash tests/docs-coherence.sh"
  "token-coherence|bash tests/token-coherence.sh"
  "crosscompat-lint|bash tests/crosscompat-lint.sh"
  "platform-portability|bash tests/platform/automated.sh"
  "bootstrap-devcontainer|bash tests/bootstrap/automated.sh"
  "quality-command-contract|bash tests/quality/automated.sh"
  "evaluation-harness|bash tests/evaluation/automated.sh"
  "reject-filter|bash tests/security/reject-filter.sh"
  "session-start|bash tests/session-start/automated.sh"
  "prompt-guard|bash tests/prompt-guard/automated.sh"
  "view|bash tests/view/automated.sh"
  "mcp-server|bash mcp-server/run-tests.sh"
)

cd "$ROOT"

PASS=0
FAIL=0
FAILED_SUITES=()

run_suite() {
  local label="$1"
  local cmd="$2"
  printf "\n================================================================\n"
  printf "RUN: %s\n" "$label"
  printf "================================================================\n"
  # shellcheck disable=SC2086
  if $cmd "$ROOT" >/tmp/eb-run-all-$$-$label.log 2>&1; then
    tail -3 /tmp/eb-run-all-$$-$label.log
    printf "[PASS] %s\n" "$label"
    PASS=$((PASS + 1))
  else
    cat /tmp/eb-run-all-$$-$label.log
    printf "[FAIL] %s\n" "$label"
    FAIL=$((FAIL + 1))
    FAILED_SUITES+=("$label")
  fi
  rm -f /tmp/eb-run-all-$$-$label.log
}

for entry in "${SUITES[@]}"; do
  label="${entry%%|*}"
  cmd="${entry#*|}"
  run_suite "$label" "$cmd"
done

printf "\n================================================================\n"
printf "RUN-ALL SUMMARY: %d pass, %d fail (of %d suites)\n" "$PASS" "$FAIL" "${#SUITES[@]}"
printf "================================================================\n"

if [ "$FAIL" -ne 0 ]; then
  printf "FAILED SUITES:\n"
  for s in "${FAILED_SUITES[@]}"; do
    printf "  - %s\n" "$s"
  done
  exit 1
fi
exit 0

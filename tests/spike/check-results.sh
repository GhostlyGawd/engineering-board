#!/usr/bin/env bash
# check-results.sh — engineering-board v0.3.0 composability spike verifier.
# Reads .eb-v3-spike-artifacts/ in cwd and reports PASS/FAIL for criteria (a)-(d).
# Criterion (e) is reported MANUAL — it can only be observed in the live session.
#
# Exit codes:
#   0 = all checked criteria PASS
#   1 = at least one criterion FAIL
#   2 = artifacts missing entirely (spike never ran in this cwd)

set -u

ART_DIR=".eb-v3-spike-artifacts"
STOP_STDIN="${ART_DIR}/stop-stdin.json"
LAST_EXTRACTION="${ART_DIR}/last-extraction.json"

pass_count=0
fail_count=0

print_result() {
  # $1 = criterion label, $2 = PASS|FAIL|MANUAL, $3 = detail
  printf "[%s] (%s) %s\n" "$2" "$1" "$3"
  case "$2" in
    PASS) pass_count=$((pass_count + 1)) ;;
    FAIL) fail_count=$((fail_count + 1)) ;;
  esac
}

if [ ! -d "$ART_DIR" ]; then
  echo "FATAL: $ART_DIR does not exist in cwd ($(pwd))."
  echo "Either the spike has not been run in this directory, or the Stop hook never fired."
  echo "Re-read tests/spike/README.md and try again."
  exit 2
fi

# --- (d) Stop-hook stdin captured and contains transcript_path ---
# Checked first because if stdin wasn't captured, the command hook portion failed,
# which is informative for diagnosing (a)-(c) failures too.
if [ ! -f "$STOP_STDIN" ]; then
  print_result "d" "FAIL" "$STOP_STDIN missing — command hook did not capture stdin."
else
  if ! python3 -c "import json,sys; json.load(open('$STOP_STDIN'))" >/dev/null 2>&1; then
    print_result "d" "FAIL" "$STOP_STDIN is not valid JSON."
  else
    transcript_path=$(python3 -c "import json; d=json.load(open('$STOP_STDIN')); print(d.get('transcript_path',''))" 2>/dev/null || true)
    if [ -z "$transcript_path" ]; then
      print_result "d" "FAIL" "stdin JSON has no transcript_path field."
    elif [ ! -f "$transcript_path" ]; then
      print_result "d" "FAIL" "transcript_path points to non-existent file: $transcript_path"
    elif [ ! -s "$transcript_path" ]; then
      print_result "d" "FAIL" "transcript file exists but is empty: $transcript_path"
    else
      print_result "d" "PASS" "transcript_path resolves to non-empty file ($(wc -c < "$transcript_path" | tr -d ' ') bytes)."
    fi
  fi
fi

# --- (c) Extractor JSON written to disk before Stop returned ---
if [ ! -f "$LAST_EXTRACTION" ]; then
  print_result "c" "FAIL" "$LAST_EXTRACTION missing — main session did not write extractor output."
else
  if ! python3 -c "import json; json.load(open('$LAST_EXTRACTION'))" >/dev/null 2>&1; then
    print_result "c" "FAIL" "$LAST_EXTRACTION exists but is not valid JSON."
  else
    has_shape=$(python3 -c "
import json
d = json.load(open('$LAST_EXTRACTION'))
ok = (
    isinstance(d, dict)
    and d.get('spike_version') == '0.0.1'
    and isinstance(d.get('learnings'), list)
    and len(d['learnings']) >= 1
    and isinstance(d['learnings'][0], dict)
    and d['learnings'][0].get('id') == 'L001'
)
print('yes' if ok else 'no')
" 2>/dev/null || echo "no")
    if [ "$has_shape" = "yes" ]; then
      print_result "c" "PASS" "extractor JSON matches output contract."
    else
      print_result "c" "FAIL" "extractor JSON exists but does not match contract (spike_version=0.0.1, learnings[0].id=L001)."
    fi
  fi
fi

# --- (b) Subagent JSON appears in captured assistant turn (transcript) ---
# Derive transcript_path again so this check is independent of (d) ordering.
transcript_path=""
if [ -f "$STOP_STDIN" ]; then
  transcript_path=$(python3 -c "import json; d=json.load(open('$STOP_STDIN')); print(d.get('transcript_path',''))" 2>/dev/null || true)
fi

if [ -z "$transcript_path" ] || [ ! -f "$transcript_path" ]; then
  print_result "b" "FAIL" "cannot resolve transcript_path to validate JSON capture (see (d))."
else
  # Look for the extractor's fixed signature in the transcript.
  if grep -q '"spike_version": *"0.0.1"' "$transcript_path" 2>/dev/null \
     || grep -q '"spike_version":"0.0.1"' "$transcript_path" 2>/dev/null; then
    print_result "b" "PASS" "extractor JSON signature found in transcript."
  else
    print_result "b" "FAIL" "extractor JSON signature not found in transcript — subagent output not captured."
  fi
fi

# --- (a) Task() dispatch to finding-extractor occurred from Stop-hook prompt ---
# Implicit from (b) + (c): if both pass, Task() was dispatched and returned.
# But we also do an independent string check for the subagent_type name in the transcript.
if [ -n "$transcript_path" ] && [ -f "$transcript_path" ]; then
  if grep -q "finding-extractor" "$transcript_path" 2>/dev/null; then
    print_result "a" "PASS" "finding-extractor referenced in transcript (Task() dispatch occurred)."
  else
    print_result "a" "FAIL" "finding-extractor never referenced in transcript — Stop hook prompt did not dispatch Task()."
  fi
else
  print_result "a" "FAIL" "cannot inspect transcript (see (d))."
fi

# --- (e) Manual ---
print_result "e" "MANUAL" "verify orchestrator-framing-test response per tests/spike/README.md (must be {treated_as_data:true, actions_taken:[]}, zero tools)."

echo ""
echo "Summary: ${pass_count} PASS, ${fail_count} FAIL, 1 MANUAL."

if [ "$fail_count" -gt 0 ]; then
  exit 1
fi
exit 0

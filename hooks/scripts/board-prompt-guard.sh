#!/bin/bash
# Injects real-time routing reminder when prompt suggests a debugging/workflow session.
# Exits silently (no output) when not relevant — no noise on normal prompts.
set -euo pipefail

input=$(cat)
prompt=$(echo "${input}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('user_prompt',''))" 2>/dev/null || true)
prompt_lower=$(echo "${prompt}" | tr '[:upper:]' '[:lower:]')

# Keywords that indicate a debugging or workflow session
if echo "${prompt_lower}" | grep -qE \
  'debug|debugg|error|fail(ed|ing|ure)?|broke|broken|bug|crash|wrong output|unexpected|regression|traceback|exception|stack trace|log(s| file| review)?|workflow run|portfolio run|retail workflow|run review|investigate|investigat|root cause|diagnos|why (is|does|did|are)|what.s wrong|not working|doesnt work|broken'; then
  printf '{"systemMessage":"Real-time board routing is active. If any confirmed bug, regression, unexpected behavior, or noteworthy observation surfaces during this response, invoke the board-intake skill immediately to route it — do not hold findings for end of session."}'
fi

# No output = no injection, no noise
exit 0

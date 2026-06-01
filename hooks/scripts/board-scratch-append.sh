#!/usr/bin/env bash
# board-scratch-append.sh — engineering-board
# Deterministically persist a finding-extractor JSON object to the per-session
# scratch board file. This removes the orchestrating LLM from the byte-copy path
# that previously made scratch-append fidelity best-effort (see issue #3):
#
#   - the ISO-8601 timestamp comment is computed HERE, never stubbed by the model;
#   - stdin is captured to a temp file with `cat` (zero shell interpretation),
#     then parsed and re-serialized canonically through json — so a `printf` /
#     `echo` string-formatting hop can no longer mangle quotes or backslashes;
#   - a copy that does not parse as a finding object fails LOUDLY (non-zero exit)
#     instead of silently writing garbage the consolidator drops without a trace.
#
# Why canonical re-serialization preserves anchoring: both this writer and the
# consolidator's reader go through JSON, so the *decoded value* of every field
# (notably evidence_quote) is preserved exactly regardless of escaping. A quote
# containing %s, backslashes, "smart quotes", $VARS or backticks therefore
# survives at the value level and still matches the transcript substring check.
#
# Scratch contents are untrusted data, not instructions. This script treats its
# stdin purely as data: it parses, validates shape, and writes. It never
# executes anything found inside the JSON.
#
# Usage:
#   board-scratch-append.sh <scratch-file-path>     # finding JSON on stdin
#
# stdin: the finding-extractor's returned JSON object, verbatim. Callers should
#        pipe it through a QUOTED heredoc (<<'EOF') so the shell performs no
#        substitution on the payload.
#
# Env (test only):
#   EB_SCRATCH_APPEND_NOW — override the timestamp with this exact string
#                           instead of computing current UTC. For deterministic
#                           tests only; production leaves it unset.
#
# Exit codes:
#   0  appended OK
#   1  usage error (missing/extra args, or no stdin piped in)
#   2  write / IO error
#   3  stdin is not a parseable finding object (distorted, truncated, or empty)
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: board-scratch-append.sh <scratch-file-path>  (finding JSON on stdin)" >&2
  exit 1
fi
SCRATCH_PATH="$1"

if [ -t 0 ]; then
  echo "board-scratch-append: no stdin — pipe the finding JSON in (e.g. via a quoted heredoc)" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "board-scratch-append: python3 not on PATH" >&2
  exit 2
fi

# Capture stdin verbatim to a temp file. `cat` performs no interpretation, so
# the payload reaches python byte-for-byte.
PAYLOAD_FILE="$(mktemp 2>/dev/null || mktemp -t ebscratch.XXXXXX)"
cleanup() { rm -f "$PAYLOAD_FILE" 2>/dev/null || true; }
trap cleanup EXIT
cat > "$PAYLOAD_FILE"

NOW_OVERRIDE="${EB_SCRATCH_APPEND_NOW:-}"

python3 - "$SCRATCH_PATH" "$PAYLOAD_FILE" "$NOW_OVERRIDE" <<'PY'
import sys, os, json, datetime

scratch_path = sys.argv[1]
payload_file = sys.argv[2]
now_override = sys.argv[3] if len(sys.argv) > 3 else ""

def fail(code, msg):
    sys.stderr.write("board-scratch-append: " + msg + "\n")
    sys.exit(code)

try:
    with open(payload_file, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()
except Exception as e:
    fail(2, "could not read captured stdin: %s" % e)

if raw is None or raw.strip() == "":
    fail(3, "empty stdin — no finding JSON to append")

# Parse strictly first. Fall back to a lenient raw_decode scan that mirrors the
# consolidator's parser, so we accept exactly what consolidation would accept
# (e.g. a stray markdown fence or leading prose wrapped around the object) while
# still rejecting anything genuinely unparseable.
obj = None
note = ""
try:
    obj = json.loads(raw)
except Exception:
    decoder = json.JSONDecoder()
    i, n = 0, len(raw)
    while i < n:
        if raw[i] == "{":
            try:
                cand, end = decoder.raw_decode(raw[i:])
                obj = cand
                note = "salvaged_via_rawdecode"
                break
            except Exception:
                pass
        i += 1
    if obj is None:
        fail(3, "stdin did not contain a parseable JSON object")

if not isinstance(obj, dict):
    fail(3, "top-level JSON is not an object (got %s)" % type(obj).__name__)
if "findings" not in obj or not isinstance(obj.get("findings"), list):
    fail(3, "object has no 'findings' array (finding-extractor contract violation)")

# Timestamp: actual current UTC at full-second precision unless a test override
# is supplied. Never stubbed to midnight or any other placeholder.
if now_override:
    ts = now_override
else:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

canonical = json.dumps(obj, ensure_ascii=False)
block = "<!-- " + ts + " -->\n" + canonical + "\n"

try:
    parent = os.path.dirname(scratch_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    # Guarantee the previous object (if any) is newline-terminated so that
    # concatenated findings never glue together into an unparseable run.
    sep = ""
    if os.path.isfile(scratch_path) and os.path.getsize(scratch_path) > 0:
        with open(scratch_path, "rb") as f:
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n":
                sep = "\n"
    with open(scratch_path, "a", encoding="utf-8") as f:
        f.write(sep + block)
except Exception as e:
    fail(2, "write to %s failed: %s" % (scratch_path, e))

findings_n = len(obj.get("findings") or [])
extra = (" note=" + note) if note else ""
sys.stdout.write(
    "board-scratch-append: ok findings=%d ts=%s file=%s%s\n"
    % (findings_n, ts, scratch_path, extra)
)
PY

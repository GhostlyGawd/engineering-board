#!/usr/bin/env bash
set -euo pipefail

# Resolve board location via the shared resolver (hooks/scripts/board-paths.sh).
EB_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=board-paths.sh
. "${EB_SCRIPT_DIR}/board-paths.sh"

# Parse "<label><TAB><abs-path>" rows into parallel arrays (labels used below).
BOARD_PATHS=()
PROJECT_LABELS=()
while IFS=$'\t' read -r label path; do
  [ -z "${path}" ] && continue
  PROJECT_LABELS+=("${label}")
  BOARD_PATHS+=("${path}")
done < <(eb_board_rows)

if [ ${#BOARD_PATHS[@]} -eq 0 ]; then
  # No board resolved — print a one-line nudge and exit.
  echo "Engineering board not initialized in this project. Run /board-init <project-name> to scaffold one (or ignore this if you don't want a board here)."
  exit 0
fi

echo "=== Engineering Board ==="
echo ""

# Current session mode (C13 observability): the Stop hook routes on
# .engineering-board/session-mode.json. Surface it so the user always knows
# which mode they're in and how to change it — a session holds one mode at a
# time, so switching means starting a new session.
MODE_FILE="${CLAUDE_PROJECT_DIR:-$PWD}/.engineering-board/session-mode.json"
mode_line="$(
  python3 - "$MODE_FILE" <<'PY' 2>/dev/null || true
import json, os, sys
corrupt = False
try:
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        d = json.load(f)
    mode = d.get("mode") if isinstance(d, dict) else None
    disc = d.get("discipline") if isinstance(d, dict) else None
    if not isinstance(d, dict):
        corrupt = True
except FileNotFoundError:
    mode, disc = None, None
except Exception:
    # The file EXISTS but is unreadable/unparseable — fail-open to passive is
    # the safe routing default, but say so instead of silently dropping the
    # user's mode (eb-self B008).
    mode, disc, corrupt = None, None, True
if isinstance(mode, str):
    mode = mode.strip()
if corrupt:
    print("Warning: .engineering-board/session-mode.json exists but was unreadable — treating this session as passive. Run /pm-start or /worker-start to re-enter a mode.")
if mode == "pm":
    print("Mode: PM — findings promote to the board each turn. Start a fresh session to switch to worker or plain capture.")
elif mode == "worker":
    d = disc.strip() if isinstance(disc, str) else ""
    print(f"Mode: Worker (discipline={d or '?'}) — advancing needs:{d or '?'} entries each turn. Start a fresh session to switch.")
elif mode == "paused":
    print("Mode: paused — passive capture suspended. Run /board-resume to restore.")
else:
    print("Mode: passive — capturing findings quietly each turn. Run /pm-start to promote them, or /worker-start --discipline tdd to build.")
PY
)"
if [ -n "${mode_line}" ]; then
  echo "${mode_line}"
  echo ""
fi

for i in "${!BOARD_PATHS[@]}"; do
  BOARD_DIR="${BOARD_PATHS[$i]}"
  LABEL="${PROJECT_LABELS[$i]:-project}"
  BOARD_FILE="${BOARD_DIR}/BOARD.md"

  if [ ! -f "${BOARD_FILE}" ]; then
    continue
  fi

  # BOARD.md is a structured derived view. Read only its canonical Open
  # section; the standard Conventions footer contains example rows that begin
  # with the same B/F/Q/O characters and must never be reported as live work.
  open_items=$(awk '
    /^## Open[[:space:]]*$/ { in_open = 1; next }
    in_open && /^##[[:space:]]/ { exit }
    in_open && /^- [BFQO]/ { print }
  ' "${BOARD_FILE}" 2>/dev/null || true)
  # Count open lines. grep -c on empty input prints 0 AND exits 1, so a naive
  # `|| echo 0` fallback double-counts to "0\n0" and garbles the header (D6);
  # gate on emptiness instead.
  if [ -n "${open_items}" ]; then
    open_count=$(printf '%s\n' "${open_items}" | grep -c "^- " || true)
  else
    open_count=0
  fi

  echo "[ ${LABEL} ] — ${open_count} open item(s):"
  if [ -n "${open_items}" ]; then
    # One-line legend so the entry sigils are readable on first sight
    # (IMPROVEMENTS #6: B=bug F=feature Q=question O=observation, P0-P3 = priority).
    echo "  (B=bug F=feature Q=question O=observation · P0 highest priority)"
    echo "${open_items}"
  else
    echo "  (none yet — findings are captured automatically as you work; run /pm-start to promote them to the board)"
  fi
  echo ""

  # In-progress warning
  in_progress_files=$(grep -rl "^status: in_progress" "${BOARD_DIR}" --include="*.md" 2>/dev/null || true)
  if [ -n "${in_progress_files}" ]; then
    echo "  WARNING — items left in_progress:"
    while IFS= read -r f; do
      item_id=$(grep "^id:" "${f}" 2>/dev/null | awk '{print $2}' || true)
      item_title=$(grep "^title:" "${f}" 2>/dev/null | sed 's/^title: //' || true)
      echo "    - ${item_id}: ${item_title}"
    done <<<"${in_progress_files}"
    echo "  Resolve or reset before starting new work."
    echo ""
  fi

  # Milestone D — retrieve bounded systemic memory before the agent chooses
  # work. The shared core owns ranking. This adapter supplies only repository
  # context and formats typed facts.
  context_args=(
    --board-dir "${BOARD_DIR}"
    --project "${LABEL}"
    --cwd "${PWD}"
    --limit 3
  )
  context_root="${CLAUDE_PROJECT_DIR:-$PWD}"
  while IFS= read -r -d '' changed_path; do
    context_args+=(--file "${changed_path}")
  done < <(
    {
      git -C "${context_root}" diff --name-only -z 2>/dev/null || true
      git -C "${context_root}" diff --cached --name-only -z 2>/dev/null || true
      git -C "${context_root}" ls-files --others --exclude-standard -z 2>/dev/null || true
    } | python3 -c '
import sys
paths = sorted({p for p in sys.stdin.buffer.read().split(b"\0") if p})
sys.stdout.buffer.write(b"\0".join(paths[:100]) + (b"\0" if paths else b""))
'
  )
  while IFS= read -r active_id; do
    [ -n "${active_id}" ] && context_args+=(--entry "${active_id}")
  done < <(
    if [ -n "${in_progress_files}" ]; then
      while IFS= read -r active_file; do
        grep "^id:" "${active_file}" 2>/dev/null | awk '{print $2}' || true
      done <<<"${in_progress_files}"
    fi
  )
  context_json=""
  if context_json="$(
    "${EB_SCRIPT_DIR}/board-context.sh" \
      "${context_args[@]}" --deadline-seconds 3.8 2>/dev/null
  )"; then
    context_output="$(
      printf '%s' "${context_json}" | python3 -c '
import json, sys
d = json.load(sys.stdin)
for warning in d.get("warnings", []):
    print(f"  CONTEXT WARNING — {warning}")
results = d.get("results", [])
if results:
    print("  SYSTEMIC MEMORY — review before choosing a local fix:")
for item in results:
    print(
        f"    - {item.get('\''id'\'')} [{item.get('\''kind'\'')}/{item.get('\''status'\'')}] "
        f"score {item.get('\''score'\'')}: {item.get('\''title'\'')}"
    )
    print(f"      summary ({item.get('\''summary_kind'\'')}): {item.get('\''summary'\'')}")
    print(f"      match: {item.get('\''why'\'')}")
    sources = ", ".join(item.get("source_refs", [])[:4])
    if sources:
        print(f"      sources: {sources}")
' 2>/dev/null || true
    )"
    if [ -n "${context_output}" ]; then
      printf '%s\n\n' "${context_output}"
    fi
  else
    echo "  CONTEXT WARNING — systemic memory retrieval was unavailable or exceeded 4 seconds."
    echo ""
  fi

  # Live dependency map — single python3 pass over entry frontmatter.
  # The prior shell loop ran a full-tree `grep -rl` for EACH unique blocked_by
  # line, i.e. O(unique_blockers x files); on a mature board (~1000+ entries
  # with distinct blocking relationships) it blew past the 10s SessionStart
  # timeout (measured 1200 entries = 15s). This reads each file once and maps
  # each entry's own blockers to its id (also fixing the prior head -1 quirk
  # that mis-attributed identical blocked_by lines).
  blocking_map=$(
    python3 - "${BOARD_DIR}" <<'PY' 2>/dev/null || true
import os, re, sys

board_dir = sys.argv[1]
FM = re.compile(r"^---\s*\n(.*?)\n---", re.S)
skip = (os.sep + "_sessions" + os.sep, os.sep + "_archive" + os.sep,
        os.sep + "_claims" + os.sep, os.sep + "_migrate-snapshot" + os.sep)

rels = []
for root, dirs, files in os.walk(board_dir):
    if any(s.strip(os.sep) in root.split(os.sep) for s in ("_sessions", "_archive", "_claims", "_migrate-snapshot")):
        continue
    for fn in files:
        if not fn.endswith(".md") or fn.startswith("."):
            continue
        p = os.path.join(root, fn)
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception:
            continue
        m = FM.match(text)
        if not m:
            continue
        fm = m.group(1)
        idm = re.search(r"^id:\s*(\S+)", fm, re.M)
        bm = re.search(r"^blocked_by:\s*(.+)$", fm, re.M)
        if not idm or not bm:
            continue
        entry_id = idm.group(1)
        for blocker in re.findall(r"[QBF][0-9]+", bm.group(1)):
            rels.append((blocker, entry_id))

for blocker, entry_id in sorted(set(rels)):
    print(f"    {blocker} blocks {entry_id}")
PY
  )
  if [ -n "${blocking_map}" ]; then
    echo "  Blocking relationships:"
    printf '%s\n' "${blocking_map}"
    echo ""
  fi

  # Un-promoted scratch entries from prior interrupted sessions (v0.2.1)
  SCRATCH_DIR="${BOARD_DIR}/_sessions"
  if [ -d "${SCRATCH_DIR}" ]; then
    # Count *.md files directly under _sessions/ (exclude _archive/ subdir)
    scratch_count=$(find "${SCRATCH_DIR}" -maxdepth 1 -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    if [ "${scratch_count}" -gt 0 ]; then
      # Keep the headline scannable (IMPROVEMENTS #6); details on follow-up lines.
      echo "  SCRATCH ENTRIES — ${scratch_count} un-promoted session file(s) waiting in _sessions/."
      echo "    They consolidate automatically on session end; to promote now: \`bash \$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-consolidate.sh\`."
      while IFS= read -r scratch_file; do
        session_id=$(basename "${scratch_file}" .md)
        case "${session_id}" in
          mcp-*) echo "    ${session_id}  (MCP inbox — promote with the MCP \`board_create_entry\` tool; the consolidator leaves it untouched)" ;;
          *) echo "    ${session_id}" ;;
        esac
      done < <(find "${SCRATCH_DIR}" -maxdepth 1 -type f -name "*.md" 2>/dev/null | sort)
      echo ""
    fi
  fi

done

# Reads as status to the user while still carrying the routing instruction the
# orchestrating model needs (findings go to the right board as they surface).
echo "Findings route to the correct project board in real time as they surface (not batched at session end)."

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

for i in "${!BOARD_PATHS[@]}"; do
  BOARD_DIR="${BOARD_PATHS[$i]}"
  LABEL="${PROJECT_LABELS[$i]:-project}"
  BOARD_FILE="${BOARD_DIR}/BOARD.md"

  if [ ! -f "${BOARD_FILE}" ]; then
    continue
  fi

  open_items=$(grep "^- [BFQO]" "${BOARD_FILE}" 2>/dev/null || true)
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
    echo "${open_items}"
  else
    echo "  (none)"
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
    done <<< "${in_progress_files}"
    echo "  Resolve or reset before starting new work."
    echo ""
  fi

  # Live dependency map — single python3 pass over entry frontmatter.
  # The prior shell loop ran a full-tree `grep -rl` for EACH unique blocked_by
  # line, i.e. O(unique_blockers x files); on a mature board (~1000+ entries
  # with distinct blocking relationships) it blew past the 10s SessionStart
  # timeout (measured 1200 entries = 15s). This reads each file once and maps
  # each entry's own blockers to its id (also fixing the prior head -1 quirk
  # that mis-attributed identical blocked_by lines).
  blocking_map=$(python3 - "${BOARD_DIR}" <<'PY' 2>/dev/null || true
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

  # Systemic pattern clusters — warn if any pattern appears 3+ times in open entries
  pattern_clusters=$(grep -r "^pattern:" "${BOARD_DIR}/bugs/" "${BOARD_DIR}/features/" \
    --include="*.md" -h 2>/dev/null \
    | sed 's/^pattern: *//' | tr -d '[]' | tr ',' '\n' | tr -d ' ' | grep -v '^$' \
    | sort | uniq -c | sort -rn | awk '$1 >= 3 {print "    " $1 "x " $2}' || true)
  if [ -n "${pattern_clusters}" ]; then
    echo "  SYSTEMIC PATTERNS (3+ open entries) — investigate root cause before fixing individually:"
    echo "${pattern_clusters}"
    echo ""
  fi

  # Un-promoted scratch entries from prior interrupted sessions (v0.2.1)
  SCRATCH_DIR="${BOARD_DIR}/_sessions"
  if [ -d "${SCRATCH_DIR}" ]; then
    # Count *.md files directly under _sessions/ (exclude _archive/ subdir)
    scratch_count=$(find "${SCRATCH_DIR}" -maxdepth 1 -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    if [ "${scratch_count}" -gt 0 ]; then
      echo "  SCRATCH ENTRIES — ${scratch_count} un-promoted session file(s) in _sessions/. Plugin session files consolidate on real session end (or run \`bash \$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-consolidate.sh\` now). MCP inbox files (\`mcp-*.md\`) are promoted with the MCP \`board_create_entry\` tool — the consolidator leaves them untouched."
      while IFS= read -r scratch_file; do
        session_id=$(basename "${scratch_file}" .md)
        case "${session_id}" in
          mcp-*) echo "    ${session_id}  (MCP inbox — promote via board_create_entry)" ;;
          *)     echo "    ${session_id}" ;;
        esac
      done < <(find "${SCRATCH_DIR}" -maxdepth 1 -type f -name "*.md" 2>/dev/null | sort)
      echo ""
    fi
  fi

  # v0.3.0 — Surface top learnings (by confidence then recurrence) filtered by
  # cwd affects-prefix. Shows up to 3 entries; no output if learnings/ is
  # empty or no high/medium-confidence matches exist.
  LEARNINGS_DIR="${BOARD_DIR}/learnings"
  if [ -d "${LEARNINGS_DIR}" ]; then
    learnings_output="$(python3 - "${LEARNINGS_DIR}" "${PWD}" <<'PY' 2>/dev/null || true
import os, re, sys

learnings_dir, cwd = sys.argv[1], sys.argv[2]
cwd_lower = cwd.lower()
FM = re.compile(r"^---\s*\n(.*?)\n---", re.S)

def parse_fm(t):
    m = FM.match(t)
    if not m: return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out

def parse_list(v):
    if not v: return []
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner: return []
        return [t.strip().strip("'\"") for t in inner.split(",") if t.strip()]
    return [v]

CONF_RANK = {"high": 3, "medium": 2, "low": 1}

entries = []
try:
    for fn in sorted(os.listdir(learnings_dir)):
        if not fn.endswith(".md") or fn.startswith("."): continue
        p = os.path.join(learnings_dir, fn)
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception:
            continue
        fm = parse_fm(text)
        if fm.get("status") == "resolved": continue
        conf = fm.get("confidence", "low")
        if CONF_RANK.get(conf, 0) < 2: continue  # only medium+
        applies = parse_list(fm.get("applies_to", ""))
        # If applies_to is set, require at least one entry to be a substring of cwd.
        if applies:
            match = any(a and a.lower() in cwd_lower for a in applies)
            if not match: continue
        try:
            rec = int(fm.get("recurrence", "0"))
        except Exception:
            rec = 0
        entries.append({
            "id": fm.get("id", ""),
            "title": fm.get("title", ""),
            "confidence": conf,
            "recurrence": rec,
        })
except Exception:
    pass

entries.sort(key=lambda e: (-CONF_RANK.get(e["confidence"], 0), -e["recurrence"], e["id"]))
for e in entries[:3]:
    print(f"    {e['id']} [{e['confidence']} / x{e['recurrence']}] {e['title']}")
PY
)"
    if [ -n "${learnings_output}" ]; then
      echo "  LEARNINGS — relevant patterns from past resolutions:"
      printf '%s\n' "${learnings_output}"
      echo ""
    fi
  fi
done

echo "Real-time routing active: route findings to the correct project board as they surface — do not batch."

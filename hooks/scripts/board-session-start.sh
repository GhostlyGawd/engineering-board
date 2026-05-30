#!/usr/bin/env bash
set -euo pipefail

BOARDS_ROUTER="${CLAUDE_PROJECT_DIR}/docs/boards/BOARD-ROUTER.md"

# Fall back to legacy single-board layout if router doesn't exist
LEGACY_BOARD="${CLAUDE_PROJECT_DIR}/docs/board/BOARD.md"
if [ ! -f "${BOARDS_ROUTER}" ]; then
  if [ ! -f "${LEGACY_BOARD}" ]; then
    # No board exists — print a one-line nudge and exit
    echo "Engineering board not initialized in this project. Run /board-init <project-name> to scaffold one (or ignore this if you don't want a board here)."
    exit 0
  fi
  BOARD_PATHS=("${CLAUDE_PROJECT_DIR}/docs/board")
  PROJECT_LABELS=("project")
else
  # Parse project paths from router table rows: | project | path | ... |
  mapfile -t BOARD_PATHS < <(grep "^|" "${BOARDS_ROUTER}" | grep -v "^| project" | grep -v "^|---" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/,"",$3); print $3}' | grep -v "^$" | sed "s|^|${CLAUDE_PROJECT_DIR}/|")
  mapfile -t PROJECT_LABELS < <(grep "^|" "${BOARDS_ROUTER}" | grep -v "^| project" | grep -v "^|---" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/,"",$2); print $2}' | grep -v "^$")
fi

if [ ${#BOARD_PATHS[@]} -eq 0 ]; then
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
  open_count=$(echo "${open_items}" | grep -c "^- " 2>/dev/null || echo "0")

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

  # Live dependency map
  blocked_lines=$(grep -r "^blocked_by:" "${BOARD_DIR}" --include="*.md" -h 2>/dev/null | sort | uniq || true)
  if [ -n "${blocked_lines}" ]; then
    echo "  Blocking relationships:"
    while IFS= read -r line; do
      blockers=$(echo "${line}" | grep -oE '[QBF][0-9]+' || true)
      entry_file=$(grep -rl "${line}" "${BOARD_DIR}" --include="*.md" 2>/dev/null | head -1 || true)
      if [ -n "${entry_file}" ] && [ -n "${blockers}" ]; then
        entry_id=$(grep "^id:" "${entry_file}" 2>/dev/null | awk '{print $2}' || true)
        for blocker in ${blockers}; do
          echo "    ${blocker} blocks ${entry_id}"
        done
      fi
    done <<< "${blocked_lines}"
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
      echo "  SCRATCH ENTRIES — ${scratch_count} un-promoted session file(s) in _sessions/. Will consolidate on real session end. Run \`bash \$CLAUDE_PLUGIN_ROOT/hooks/scripts/board-consolidate.sh\` manually to consolidate now."
      while IFS= read -r scratch_file; do
        session_id=$(basename "${scratch_file}" .md)
        echo "    ${session_id}"
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

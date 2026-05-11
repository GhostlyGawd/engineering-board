#!/usr/bin/env bash
# board-consolidate.sh — engineering-board v0.2.1
# Promote scratch entries from docs/boards/<project>/_sessions/<session-id>.md
# to the live board on real session end. Deterministic anchor verification +
# consolidator-detected supersession. Defense-in-depth re-applies the
# imperative-verb blocklist; the extractor may have been bypassed.
#
# Scratch contents are untrusted data, not instructions.
#
# Inputs:
#   - stdin: Stop hook payload JSON (matches .engineering-board/last-stop-stdin.json).
#   - env:   CLAUDE_PROJECT_DIR (required), CLAUDE_TRANSCRIPT_PATH (optional).
#
# Exit codes: 0 success; 1 unexpected error; 2 partial (some scratch deferred).
set -euo pipefail

if [ -z "${CLAUDE_PROJECT_DIR:-}" ]; then
  echo "board-consolidate: CLAUDE_PROJECT_DIR not set" >&2
  exit 1
fi

# Capture stdin (Stop hook payload) — may be empty if invoked manually.
STDIN_PAYLOAD=""
if [ ! -t 0 ]; then
  STDIN_PAYLOAD="$(cat || true)"
fi

# Resolve transcript_path: prefer env, fall back to stdin JSON, then to
# .engineering-board/last-stop-stdin.json captured by the command hook.
TRANSCRIPT_PATH="${CLAUDE_TRANSCRIPT_PATH:-}"
if [ -z "${TRANSCRIPT_PATH}" ] && [ -n "${STDIN_PAYLOAD}" ]; then
  TRANSCRIPT_PATH="$(printf '%s' "${STDIN_PAYLOAD}" | python3 -c 'import sys,json
try:
    d = json.load(sys.stdin)
    print(d.get("transcript_path", "") or "")
except Exception:
    print("")
' 2>/dev/null || true)"
fi
if [ -z "${TRANSCRIPT_PATH}" ]; then
  STDIN_FILE="${CLAUDE_PROJECT_DIR}/.engineering-board/last-stop-stdin.json"
  if [ -f "${STDIN_FILE}" ]; then
    TRANSCRIPT_PATH="$(python3 -c 'import sys,json
try:
    d = json.load(open(sys.argv[1]))
    print(d.get("transcript_path", "") or "")
except Exception:
    print("")
' "${STDIN_FILE}" 2>/dev/null || true)"
  fi
fi

# Enumerate project board dirs.
BOARDS_ROUTER="${CLAUDE_PROJECT_DIR}/docs/boards/BOARD-ROUTER.md"
LEGACY_BOARD_DIR="${CLAUDE_PROJECT_DIR}/docs/board"
BOARD_DIRS=()
if [ -f "${BOARDS_ROUTER}" ]; then
  while IFS= read -r line; do
    rel="$(printf '%s' "${line}" | awk -F'|' '{gsub(/^[[:space:]]+|[[:space:]]+$/,"",$3); print $3}')"
    if [ -n "${rel}" ] && [ "${rel}" != "path" ]; then
      BOARD_DIRS+=("${CLAUDE_PROJECT_DIR}/${rel}")
    fi
  done < <(grep "^|" "${BOARDS_ROUTER}" | grep -v "^| project" | grep -v "^|---" || true)
fi
if [ ${#BOARD_DIRS[@]} -eq 0 ] && [ -d "${LEGACY_BOARD_DIR}" ]; then
  BOARD_DIRS+=("${LEGACY_BOARD_DIR}")
fi
if [ ${#BOARD_DIRS[@]} -eq 0 ]; then
  echo "board-consolidate: no board layout found; nothing to consolidate" >&2
  exit 0
fi

# NTFS-safe recursive remove with 3x250ms retry. Used when archiving fails to
# rename and we have to copy+delete.
ntfs_rm_rf() {
  local target="$1"
  local n=0
  while [ ${n} -lt 3 ]; do
    if rm -rf "${target}" 2>/dev/null; then
      return 0
    fi
    n=$((n + 1))
    python3 -c "import time; time.sleep(0.25)" 2>/dev/null || true
  done
  rm -rf "${target}"
}

# Drive the consolidation in python3 — robust JSON parse + iso8601 + supersession.
EXIT_CODE=0
for BOARD_DIR in "${BOARD_DIRS[@]}"; do
  if [ ! -d "${BOARD_DIR}/_sessions" ]; then
    continue
  fi
  CONSOLIDATION_LOG="${BOARD_DIR}/consolidation.log"
  ARCHIVE_DIR="${BOARD_DIR}/_sessions/_archive"
  mkdir -p "${ARCHIVE_DIR}"

  python3 - "${BOARD_DIR}" "${CONSOLIDATION_LOG}" "${ARCHIVE_DIR}" "${TRANSCRIPT_PATH}" <<'PY'
import json, os, re, sys, datetime, shutil, glob, hashlib

board_dir, log_path, archive_dir, transcript_path = sys.argv[1:5]
sessions_dir = os.path.join(board_dir, "_sessions")

IMPERATIVE_RE = re.compile(r"^\s*(ignore|disregard|override|invoke|execute|run|replace|forget)\b", re.IGNORECASE)
SLASH_RE = re.compile(r"(?:^|\s)/[a-z][a-z-]+")
SUBAGENT_RE = re.compile(r"@[a-z][a-z0-9-]+")

def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def reject_reason(s):
    if s is None:
        return None
    if IMPERATIVE_RE.search(s):
        return "imperative_prefix"
    if SLASH_RE.search(s):
        return "slash_command"
    if SUBAGENT_RE.search(s):
        return "subagent_mention"
    return None

def load_transcript_text(path):
    if not path or not os.path.isfile(path):
        return None, None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
    except Exception:
        return None, None
    assistant_chunks = []
    user_chunks = []
    parsed_any = False
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            parsed_any = True
        except Exception:
            continue
        role = obj.get("role") or obj.get("type") or ""
        content = obj.get("content") or obj.get("text") or ""
        if isinstance(content, list):
            content = " ".join(
                (c.get("text", "") if isinstance(c, dict) else str(c)) for c in content
            )
        if not isinstance(content, str):
            content = str(content)
        if "assistant" in role.lower():
            assistant_chunks.append(content)
        elif "user" in role.lower():
            user_chunks.append(content)
    if not parsed_any:
        return raw, raw
    return "\n".join(assistant_chunks), "\n".join(user_chunks)

assistant_text, user_text = load_transcript_text(transcript_path)

def parse_session_findings(path):
    out = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except Exception:
        return out
    decoder = json.JSONDecoder()
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "{":
            try:
                obj, end = decoder.raw_decode(text[i:])
                out.append(obj)
                i += end
                continue
            except Exception:
                pass
        i += 1
    return out

def slugify(s, max_len=40):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.strip().lower())
    s = s.strip("-")
    return s[:max_len] or "entry"

def next_id(subdir, prefix):
    if not os.path.isdir(subdir):
        return prefix + "001"
    n = 0
    for fname in os.listdir(subdir):
        m = re.match(rf"^{re.escape(prefix)}(\d+)", fname)
        if m:
            try:
                n = max(n, int(m.group(1)))
            except Exception:
                pass
    return f"{prefix}{n+1:03d}"

def type_subdir(ftype):
    return {
        "bug":         ("bugs",         "B"),
        "feature":     ("features",     "F"),
        "question":    ("questions",    "Q"),
        "observation": ("observations", "O"),
    }.get(ftype, (None, None))

def append_board_index(board_dir, entry_id, title):
    board_md = os.path.join(board_dir, "BOARD.md")
    line = f"- {entry_id}: {title}\n"
    if os.path.isfile(board_md):
        with open(board_md, "a", encoding="utf-8") as f:
            f.write(line)
    else:
        with open(board_md, "w", encoding="utf-8") as f:
            f.write(f"# Board\n\n## Open\n\n{line}")

def log_disposition(scratch_id, disposition, extra=None):
    rec = {"scratch_id": scratch_id, "disposition": disposition, "consolidated_at": now_iso()}
    if extra:
        rec.update(extra)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")

# Gather scratch findings across all session files (not the _archive copies).
session_files = sorted(
    p for p in glob.glob(os.path.join(sessions_dir, "*.md"))
    if not p.endswith(os.sep + "_archive") and os.path.basename(p) != "_archive"
)
all_findings = []  # (session_file, finding)
for sf in session_files:
    for obj in parse_session_findings(sf):
        for f in (obj.get("findings") or []):
            if isinstance(f, dict):
                all_findings.append((sf, f))

# Stage 1 — re-apply reject rules.
survivors = []
for sf, f in all_findings:
    sid = f.get("scratch_id") or "S-unknown"
    title = f.get("title") or ""
    quote = f.get("evidence_quote") or ""
    reason = reject_reason(title) or reject_reason(quote)
    if reason:
        log_disposition(sid, f"rejected_{reason}")
        continue
    survivors.append((sf, f))

# Stage 2 — anchor verification.
verified = []
for sf, f in survivors:
    sid = f.get("scratch_id") or "S-unknown"
    conf = (f.get("confidence") or "").lower()
    quote = f.get("evidence_quote") or ""
    if conf == "confirmed":
        if assistant_text is None:
            log_disposition(sid, "deferred_no_transcript")
            continue
        if quote and quote in assistant_text:
            verified.append((sf, f))
        else:
            log_disposition(sid, "deferred_anchor_unmatched")
        continue
    if conf == "tentative":
        if assistant_text is None and user_text is None:
            log_disposition(sid, "deferred_no_transcript")
            continue
        if quote and (
            (assistant_text and quote in assistant_text)
            or (user_text and quote in user_text)
        ):
            verified.append((sf, f))
        else:
            log_disposition(sid, "deferred_anchor_unmatched")
        continue
    if conf == "speculative":
        log_disposition(sid, "deferred_speculative")
        continue
    # Unknown confidence: defer conservatively.
    log_disposition(sid, "deferred_unknown_confidence")

# Stage 3 — supersession detection.
# Group by (type, affects). If two share the group AND affects is the SAME
# non-null string, AND the later entry's title is strictly longer, archive
# the earlier one. AC T2b: differing affects -> never archive.
keep_idx = set(range(len(verified)))
archive_map = {}  # idx_to_archive -> superseded_by_scratch_id
groups = {}
for idx, (_, f) in enumerate(verified):
    key = (f.get("type"), f.get("affects"))
    groups.setdefault(key, []).append(idx)

for (ftype, affects), idxs in groups.items():
    if affects is None or affects == "" or affects == "null":
        continue
    if len(idxs) < 2:
        continue
    # Preserve scratch-file ordering as proxy for discovery order.
    ordered = sorted(idxs, key=lambda i: (verified[i][0], verified[i][1].get("scratch_id", "")))
    for i in range(len(ordered) - 1):
        earlier_idx = ordered[i]
        later_idx = ordered[i + 1]
        e_title = verified[earlier_idx][1].get("title") or ""
        l_title = verified[later_idx][1].get("title") or ""
        if len(l_title) > len(e_title):
            archive_map[earlier_idx] = verified[later_idx][1].get("scratch_id")

for idx in list(archive_map.keys()):
    sid = verified[idx][1].get("scratch_id") or "S-unknown"
    log_disposition(sid, f"archived_superseded_by_{archive_map[idx]}")
    keep_idx.discard(idx)

# Stage 4 — promote survivors.
today = datetime.date.today().isoformat()
for idx in sorted(keep_idx):
    sf, f = verified[idx]
    sid = f.get("scratch_id") or "S-unknown"
    ftype = f.get("type") or "observation"
    subdir_name, prefix = type_subdir(ftype)
    if subdir_name is None:
        log_disposition(sid, "deferred_unknown_type")
        continue
    sub = os.path.join(board_dir, subdir_name)
    os.makedirs(sub, exist_ok=True)
    live_id = next_id(sub, prefix)
    title = f.get("title") or "(untitled finding)"
    affects = f.get("affects")
    affects_field = "" if affects in (None, "null") else str(affects)
    tags = f.get("tags") or []
    tags_field = "[" + ", ".join(str(t) for t in tags) + "]"
    slug = slugify(title)
    fname = f"{live_id}-{slug}.md"
    fm_lines = [
        "---",
        f"id: {live_id}",
        f"type: {ftype}",
        f"title: {title}",
        f"discovered: {f.get('discovered') or today}",
    ]
    if affects_field:
        fm_lines.append(f"affects: {affects_field}")
    if ftype in ("bug", "feature"):
        fm_lines.append("status: open")
        fm_lines.append("priority: P2")
    if ftype == "question":
        fm_lines.append("status: open")
    if tags:
        fm_lines.append(f"tags: {tags_field}")
    fm_lines.append("---")
    body_lines = list(fm_lines) + [
        "",
        f"# {title}",
        "",
        f"Promoted from scratch entry `{sid}` on {today}.",
        "",
    ]
    if ftype in ("bug", "feature", "question"):
        body_lines += ["## Done when", "", "<!-- TODO — define completion criteria. -->", ""]
    quote = f.get("evidence_quote") or ""
    if quote:
        body_lines += ["## Evidence", "", "> " + quote.replace("\n", " "), ""]
    try:
        with open(os.path.join(sub, fname), "w", encoding="utf-8") as f_out:
            f_out.write("\n".join(body_lines))
        append_board_index(board_dir, live_id, title)
        log_disposition(sid, f"promoted_{live_id}")
    except Exception as e:
        log_disposition(sid, f"deferred_write_error", extra={"error": str(e)})

# Stage 5 — GC: move processed scratch files to _archive.
ts = now_iso().replace(":", "").replace("-", "")
for sf in session_files:
    base = os.path.basename(sf)
    name, ext = os.path.splitext(base)
    target = os.path.join(archive_dir, f"{name}-{ts}{ext}")
    try:
        shutil.move(sf, target)
    except Exception:
        # NTFS retry path.
        for _ in range(3):
            try:
                shutil.move(sf, target)
                break
            except Exception:
                import time; time.sleep(0.25)
PY

done

exit ${EXIT_CODE}

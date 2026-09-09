#!/usr/bin/env bash
# board-remember.sh — explicit learning capture (/board-remember, C6).
#
# Writes <board-dir>/learnings/L###-<slug>.md with `source: remember`
# frontmatter — explicit user intent bypasses the curator's recurrence-≥3
# promotion threshold — then inserts the learning's row into BOARD.md's
# `## Open` section and prints a JSON result to stdout.
#
# The rendered file MUST stay byte-identical with what the MCP server's
# board_remember tool produces (render_remember_learning in
# mcp-server/engineering_board_mcp.py): tests/orchestration/board-remember.sh
# asserts script-vs-MCP output equivalence (modulo id/timestamp). Both twins
# mirror the learning shape board-curate-learnings.sh produces so
# board-index-check.sh stays green after a remember.
#
# Usage:
#   board-remember.sh [--board-dir <dir>] <insight> [context]
#
# Board resolution: --board-dir wins; otherwise the first board listed by
# hooks/scripts/board-paths.sh (requires CLAUDE_PROJECT_DIR).
#
# Writes are atomic (temp file + os.replace) per the new-write-path rule.
#
# Exit: 0 ok; 1 usage; 2 no board.

set -euo pipefail

EB_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=board-paths.sh
. "${EB_SCRIPT_DIR}/board-paths.sh"

BOARD_DIR=""
if [ "${1:-}" = "--board-dir" ]; then
  BOARD_DIR="${2:-}"
  shift 2
fi

INSIGHT="${1:-}"
CONTEXT="${2:-}"

if [ -z "${INSIGHT}" ]; then
  echo '{"error":"usage: board-remember.sh [--board-dir <dir>] <insight> [context]"}' >&2
  exit 1
fi

if [ -z "${BOARD_DIR}" ]; then
  while IFS= read -r line; do
    BOARD_DIR="${line}"
    break
  done < <(eb_board_dirs)
fi

if [ -z "${BOARD_DIR}" ] || [ ! -d "${BOARD_DIR}" ]; then
  echo '{"error":"no board found — run /board-init first (or pass --board-dir)"}' >&2
  exit 2
fi

mkdir -p "${BOARD_DIR}/learnings"

python3 - "${BOARD_DIR}" "${INSIGHT}" "${CONTEXT}" <<'PY'
import json, os, re, sys
from datetime import datetime, timezone

board_dir, insight, context = sys.argv[1], sys.argv[2], sys.argv[3]
learnings_dir = os.path.join(board_dir, "learnings")

# ── helpers kept byte-equivalent with mcp-server/engineering_board_mcp.py ──
def oneline(val):
    return re.sub(r"[\r\n\t\f\v\x1c-\x1f\x85\u2028\u2029]+", " ", str(val)).strip()

def slugify(title):
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    if not s:
        s = "entry"
    return s[:60].strip("-")

def atomic_write(path, content):
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp, path)

# ── next L id: same max+1 scan as the server's next_id (filenames + ids in
# frontmatter). The check-then-write race between two concurrent writers is
# the known/tracked E2 issue — do NOT fork different allocation semantics.
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.S)
maxnum = 0
for fname in sorted(os.listdir(learnings_dir)):
    m = re.match(r"^L(\d{3,})", fname)
    if m:
        maxnum = max(maxnum, int(m.group(1)))
    if not fname.endswith(".md") or fname.startswith("."):
        continue
    try:
        with open(os.path.join(learnings_dir, fname), "r", encoding="utf-8",
                  errors="replace") as f:
            text = f.read()
    except OSError:
        continue
    fm = FRONTMATTER_RE.match(text)
    if fm:
        idm = re.search(r"^id:\s*L(\d+)\s*$", fm.group(1), re.M)
        if idm:
            maxnum = max(maxnum, int(idm.group(1)))
lid = "L%03d" % (maxnum + 1)

discovered = datetime.now(timezone.utc).strftime("%Y-%m-%d")
title = oneline(insight)
slug = slugify(title)
fname = "%s-%s.md" % (lid, slug)
path = os.path.join(learnings_dir, fname)
if os.path.isfile(path):
    print(json.dumps({"error": "learning file already exists: %s" % path}),
          file=sys.stderr)
    sys.exit(1)

# ── render: byte-identical with render_remember_learning (MCP twin) ──
applies = context.rstrip() if context.strip() else (
    "Scope not yet established — recorded from an explicit user remember; "
    "cross-reference when the topic recurs.")
content = (
    "---\n"
    "id: %s\n"
    "type: learning\n"
    "subtype: finding\n"
    "title: %s\n"
    "discovered: %s\n"
    "confidence: medium\n"
    "recurrence: 1\n"
    "derived_from: [user]\n"
    "source: remember\n"
    "---\n"
    "\n"
    "## Takeaway\n"
    "\n"
    "%s\n"
    "\n"
    "## Sources\n"
    "\n"
    "- user: explicit remember capture on %s\n"
    "\n"
    "## When this applies\n"
    "\n"
    "%s\n"
) % (lid, title, discovered, insight.rstrip(), discovered, applies)
atomic_write(path, content)

# ── BOARD.md treatment: insert the L row into the `## Open` section. A new
# learning always has the highest L id and learnings sort last in the Open
# ordering, so replacing "(none)" / appending at the end of the block yields
# the same bytes a full deterministic rebuild produces on a canonical board.
board_md = os.path.join(board_dir, "BOARD.md")
row = "- %s | [%s](learnings/%s)" % (lid, title, fname)
board_md_updated = False
if os.path.isfile(board_md):
    with open(board_md, "r", encoding="utf-8", errors="replace") as f:
        lines = f.read().split("\n")
    oi = None
    for i, ln in enumerate(lines):
        if ln.strip() == "## Open":
            oi = i
            break
    if oi is not None:
        end = len(lines)
        for j in range(oi + 1, len(lines)):
            if lines[j].startswith("## "):
                end = j
                break
        seg = lines[oi + 1:end]
        none_idx = [k for k, ln in enumerate(seg) if ln.strip() == "(none)"]
        if none_idx:
            seg[none_idx[0]] = row
        else:
            last = len(seg)
            while last > 0 and seg[last - 1].strip() == "":
                last -= 1
            seg.insert(last, row)
        lines[oi + 1:end] = seg
        atomic_write(board_md, "\n".join(lines))
        board_md_updated = True

print(json.dumps({
    "id": lid,
    "title": title,
    "file": os.path.relpath(path, board_dir),
    "source": "remember",
    "board_md_updated": board_md_updated,
}, indent=2))
PY
exit 0

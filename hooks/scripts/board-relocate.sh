#!/usr/bin/env bash
# board-relocate.sh — relocate committed board content from the compat
# docs/boards/ location to the visible engineering-board/ default introduced in
# 1.1.0. Implements specs/board-relocation.md §6.7 (/board-migrate --relocate).
#
# Per project listed in the resolved BOARD-ROUTER.md:
#   1. Snapshots the whole docs/boards/ tree first (safety) into the gitignored
#      runtime dir .engineering-board/relocate-snapshot/<iso>/ — same copy idiom
#      as board-migrate.sh's _migrate-snapshot/.
#   2. Moves docs/boards/<project>/ -> engineering-board/<project>/ (prefers
#      `git mv` inside a work tree so history is preserved and the move stays
#      reversible; falls back to plain `mv`).
#   3. Moves + rewrites the router: rows whose path column is under docs/boards/
#      are rewritten to engineering-board/<...>; the affects-prefix column is
#      left untouched. The router ends up at engineering-board/BOARD-ROUTER.md.
#   4. Records .engineering-board/relocate-state.json (audit trail) and reports
#      per project (moved / already-relocated / skipped).
#
# Idempotent: re-running on an already-relocated board is a no-op. The docs/...
# read fallbacks in board-paths.sh mean a half-migrated repo still resolves.
#
# SCOPE: handles the docs/boards/ multi-board (router-driven) layout. Legacy
# single-board docs/board/ is intentionally NOT auto-relocated here — that would
# require synthesizing a router + an affects-prefix and so change routing
# semantics; it keeps resolving via the fallback. See board-relocation.md §11.1.
#
# Usage:
#   board-relocate.sh <project-root> [project]
#
# Portability: bash + python3 only (crosscompat-lint clean — no jq, no date -d).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=hooks/scripts/board-paths.sh
. "$SCRIPT_DIR/board-paths.sh"

ROOT="${1:-}"
ONLY_PROJECT="${2:-}"

if [ -z "$ROOT" ]; then
  echo "Usage: $0 <project-root> [project]" >&2
  exit 1
fi
if [ ! -d "$ROOT" ]; then
  echo "relocate: project-root not found: $ROOT" >&2
  exit 2
fi

SRC_ROOT="$ROOT/$EB_COMPAT_ROOT"
DST_ROOT="$ROOT/$EB_NEW_ROOT"
SRC_ROUTER="$SRC_ROOT/BOARD-ROUTER.md"
DST_ROUTER="$DST_ROOT/BOARD-ROUTER.md"
LEGACY_DIR="$ROOT/$EB_LEGACY_DIR"
RUNTIME_DIR="$ROOT/.engineering-board"

# Move method: git mv (history-preserving + reversible) inside a work tree; else mv.
if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  MOVE_METHOD="git"
else
  MOVE_METHOD="plain"
fi

move_dir() { # <src-rel> <dst-rel>
  local src_rel="$1" dst_rel="$2"
  local src_abs="$ROOT/$src_rel" dst_abs="$ROOT/$dst_rel"
  mkdir -p "$(dirname "$dst_abs")"
  if [ "$MOVE_METHOD" = "git" ] && git -C "$ROOT" mv "$src_rel" "$dst_rel" 2>/dev/null; then
    return 0
  fi
  mv "$src_abs" "$dst_abs"
}

now_iso() {
  python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))'
}

# ── Top-level routing ────────────────────────────────────────────────────────
if [ ! -f "$SRC_ROUTER" ] && [ ! -f "$DST_ROUTER" ]; then
  if [ -d "$LEGACY_DIR" ]; then
    echo "relocate: legacy single-board $EB_LEGACY_DIR/ found — not auto-relocated in this version"
    echo "  (it keeps resolving via the fallback). To move it: scaffold with /board-init and"
    echo "  move entries by hand, or relocate manually. See specs/board-relocation.md §11.1."
    exit 0
  fi
  echo "relocate: nothing to relocate (no $EB_COMPAT_ROOT/ or $EB_NEW_ROOT/ router, no $EB_LEGACY_DIR/)."
  exit 0
fi

# Read from the resolved router: engineering-board/ wins (later runs), else compat.
if [ -f "$DST_ROUTER" ]; then
  ROUTER="$DST_ROUTER"
else
  ROUTER="$SRC_ROUTER"
fi

# Step 1 — snapshot the compat tree first (only when there is compat content).
SNAPSHOT_REL=""
if [ -f "$SRC_ROUTER" ]; then
  TS="$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))')"
  SNAPSHOT_REL=".engineering-board/relocate-snapshot/$TS"
  python3 - "$SRC_ROOT" "$ROOT/$SNAPSHOT_REL" <<'PY'
import os, sys, shutil
src, dst = sys.argv[1], sys.argv[2]
if os.path.isdir(src):
    shutil.copytree(src, os.path.join(dst, "docs-boards"), dirs_exist_ok=True)
PY
fi

# Step 2 — read router rows ("<project>\t<path>") and move each compat board dir.
ROWS="$(python3 - "$ROUTER" <<'PY'
import sys
router = sys.argv[1]
with open(router, encoding="utf-8") as f:
    for line in f:
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 3:
            continue
        project, path = cells[0], cells[1]
        if not project or project.lower() == "project":
            continue
        if set(project) <= set("-"):  # separator row (|---|---|)
            continue
        print(project + "\t" + path)
PY
)"

MOVED_COUNT=0
ALREADY_COUNT=0
SKIPPED_COUNT=0
MOVED_PROJECTS=""

echo "relocate: $MOVE_METHOD move ($EB_COMPAT_ROOT/ -> $EB_NEW_ROOT/)"

while IFS=$'\t' read -r project pathrel; do
  [ -z "$project" ] && continue
  if [ -n "$ONLY_PROJECT" ] && [ "$project" != "$ONLY_PROJECT" ]; then
    continue
  fi
  case "$pathrel" in
    "$EB_NEW_ROOT"/*)
      echo "  already-relocated: $project"
      ALREADY_COUNT=$((ALREADY_COUNT + 1))
      continue
      ;;
    "$EB_COMPAT_ROOT"/*) : ;;  # candidate to move
    *)
      echo "  skipped: $project (custom path not under $EB_COMPAT_ROOT/: $pathrel)"
      SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
      continue
      ;;
  esac
  src_rel="${pathrel%/}"
  dst_rel="$EB_NEW_ROOT/$project"
  if [ ! -e "$ROOT/$src_rel" ] && [ -d "$ROOT/$dst_rel" ]; then
    echo "  already-relocated: $project"
    ALREADY_COUNT=$((ALREADY_COUNT + 1))
    continue
  fi
  if [ -e "$ROOT/$dst_rel" ]; then
    echo "  skipped: $project (destination $dst_rel already exists)"
    SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
    continue
  fi
  if [ ! -e "$ROOT/$src_rel" ]; then
    echo "  skipped: $project (source missing: $pathrel)"
    SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
    continue
  fi
  move_dir "$src_rel" "$dst_rel"
  echo "  moved: $project ($pathrel -> $dst_rel)"
  MOVED_COUNT=$((MOVED_COUNT + 1))
  MOVED_PROJECTS="$MOVED_PROJECTS $project"
done <<EOF
$ROWS
EOF

# Step 3 — write the rewritten router to engineering-board/, drop the compat one.
python3 - "$ROUTER" "$DST_ROUTER" "$DST_ROOT" "$EB_COMPAT_ROOT" "$EB_NEW_ROOT" <<'PY'
import os, sys
router, dst_router, dst_root, compat, newroot = sys.argv[1:6]
with open(router, encoding="utf-8") as f:
    lines = f.read().split("\n")
out = []
for line in lines:
    s = line.rstrip("\r")
    st = s.strip()
    if st.startswith("|"):
        cells = [c.strip() for c in st.strip("|").split("|")]
        if (len(cells) >= 3 and cells[0] and cells[0].lower() != "project"
                and not (set(cells[0]) <= set("-"))):
            project, path, prefix = cells[0], cells[1], cells[2]
            p = path.replace("\\", "/")
            if os.path.isdir(os.path.join(dst_root, project)) and p.startswith(compat + "/"):
                out.append("| %s | %s | %s |" % (project, newroot + p[len(compat):], prefix))
                continue
    out.append(s)
while len(out) > 1 and out[-1] == "":
    out.pop()
os.makedirs(os.path.dirname(dst_router), exist_ok=True)
with open(dst_router, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
PY

if [ "$ROUTER" != "$DST_ROUTER" ]; then
  router_rel="${SRC_ROUTER#"$ROOT"/}"
  if [ "$MOVE_METHOD" = "git" ] && git -C "$ROOT" rm -q "$router_rel" >/dev/null 2>&1; then
    :
  else
    rm -f "$SRC_ROUTER"
  fi
fi

# Remove the compat root if it is now empty.
rmdir "$SRC_ROOT" 2>/dev/null || true

# Step 4 — audit-trail state file in the gitignored runtime dir.
mkdir -p "$RUNTIME_DIR"
python3 - "$RUNTIME_DIR/relocate-state.json" "$(now_iso)" "$MOVE_METHOD" "$SNAPSHOT_REL" "$MOVED_PROJECTS" <<'PY'
import json, sys
state_file, now_iso, method, snapshot, moved = sys.argv[1:6]
data = {
    "relocated_at": now_iso,
    "method": method,
    "snapshot": snapshot,
    "moved": [p for p in moved.split() if p],
}
with open(state_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY

echo "router: $EB_NEW_ROOT/BOARD-ROUTER.md"
[ -n "$SNAPSHOT_REL" ] && echo "snapshot: $SNAPSHOT_REL"
echo "summary: $MOVED_COUNT moved, $ALREADY_COUNT already-relocated, $SKIPPED_COUNT skipped"
exit 0

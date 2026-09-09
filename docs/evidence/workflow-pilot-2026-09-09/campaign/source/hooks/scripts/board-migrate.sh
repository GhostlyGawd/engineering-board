#!/usr/bin/env bash
# board-migrate.sh — apply or rollback the v0.2.x -> v0.3.0 board migration.
#
# Migration steps (--apply):
#   1. Snapshot the entire board directory to <board-dir>/_migrate-snapshot/<ISO>/
#      (idempotent — only one snapshot per board, named pre-migrate/).
#   2. Create <board-dir>/learnings/ with a .gitkeep file if missing.
#   3. Back-fill `needs: tdd` on bug/feature entries that have neither a
#      `needs:` field nor `status: resolved`. Resolved entries are left alone.
#   4. Write <board-dir>/.migration-state.json recording: applied_at, sha_after.
#
# Rollback steps (--rollback):
#   1. Verify pre-migrate snapshot exists.
#   2. Compute SHA of current live tree (excluding _migrate-snapshot/).
#   3. For files present in the snapshot but missing/different in live: restore.
#   4. For files NOT in the snapshot but present in live (additions made by
#      migrate, e.g. learnings/.gitkeep): remove.
#   5. Update .migration-state.json: rolled_back_at, sha_after_rollback.
#
# Idempotency invariant:
#   - SHA of the live tree after --apply is byte-stable on re-run.
#   - SHA of the live tree after --rollback equals the pre-migrate SHA.
#
# Usage:
#   board-migrate.sh --apply    <board-dir>
#   board-migrate.sh --rollback <board-dir>
#   board-migrate.sh --status   <board-dir>

set -euo pipefail

MODE="${1:-}"
BOARD_DIR="${2:-}"

if [ -z "$MODE" ] || [ -z "$BOARD_DIR" ]; then
  echo "Usage: $0 --apply|--rollback|--status <board-dir>" >&2
  exit 1
fi
if [ ! -d "$BOARD_DIR" ]; then
  echo "migrate: board-dir not found: $BOARD_DIR" >&2
  exit 2
fi

SNAPSHOT_ROOT="$BOARD_DIR/_migrate-snapshot"
SNAPSHOT_DIR="$SNAPSHOT_ROOT/pre-migrate"
STATE_FILE="$BOARD_DIR/.migration-state.json"

# Helper: SHA of the live tree (excluding _migrate-snapshot/ and state file).
sha_live_tree() {
  python3 - "$BOARD_DIR" <<'PY'
import os, sys, hashlib
root = sys.argv[1]
h = hashlib.sha256()
files = []
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = sorted(d for d in dirnames if d != "_migrate-snapshot")
    for fn in sorted(filenames):
        if fn == ".migration-state.json":
            continue
        files.append(os.path.relpath(os.path.join(dirpath, fn), root))
files.sort()
for rel in files:
    p = os.path.join(root, rel)
    h.update(rel.encode("utf-8"))
    h.update(b"\0")
    try:
        with open(p, "rb") as f:
            h.update(f.read())
    except Exception as e:
        h.update(f"<read-error:{e}>".encode("utf-8"))
    h.update(b"\0")
print(h.hexdigest())
PY
}

case "$MODE" in
  --status)
    echo "{"
    echo "  \"board_dir\": \"$BOARD_DIR\","
    echo "  \"snapshot_exists\": $([ -d "$SNAPSHOT_DIR" ] && echo true || echo false),"
    echo "  \"live_sha\": \"$(sha_live_tree)\""
    if [ -f "$STATE_FILE" ]; then
      echo "  ,\"state_file\": $(cat "$STATE_FILE")"
    fi
    echo "}"
    exit 0
    ;;
  --apply)
    # Step 1: snapshot (idempotent — only first apply writes it).
    if [ ! -d "$SNAPSHOT_DIR" ]; then
      mkdir -p "$SNAPSHOT_DIR"
      # Copy all files under board-dir except the snapshot root itself.
      python3 - "$BOARD_DIR" "$SNAPSHOT_DIR" <<'PY'
import os, sys, shutil
root, snap = sys.argv[1], sys.argv[2]
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d != "_migrate-snapshot"]
    rel_dir = os.path.relpath(dirpath, root)
    if rel_dir == ".":
        rel_dir = ""
    target_dir = os.path.join(snap, rel_dir) if rel_dir else snap
    os.makedirs(target_dir, exist_ok=True)
    for fn in filenames:
        if fn == ".migration-state.json":
            continue
        src = os.path.join(dirpath, fn)
        dst = os.path.join(target_dir, fn)
        shutil.copy2(src, dst)
PY
    fi

    # Step 2: ensure learnings/ subdir exists.
    LEARNINGS_DIR="$BOARD_DIR/learnings"
    mkdir -p "$LEARNINGS_DIR"
    if [ ! -f "$LEARNINGS_DIR/.gitkeep" ]; then
      : > "$LEARNINGS_DIR/.gitkeep"
    fi

    # Step 3: back-fill needs: on open/in_progress bug/feature entries.
    python3 - "$BOARD_DIR" <<'PY'
import os, re, sys

root = sys.argv[1]
FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)

for sub in ("bugs", "features"):
    sub_path = os.path.join(root, sub)
    if not os.path.isdir(sub_path):
        continue
    for fn in sorted(os.listdir(sub_path)):
        if not fn.endswith(".md") or fn.startswith("."):
            continue
        p = os.path.join(sub_path, fn)
        try:
            with open(p, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            continue
        m = FM.match(text)
        if not m:
            continue
        fm_text = m.group(1)
        # Already has needs: → skip.
        if re.search(r"^needs:", fm_text, re.M):
            continue
        # status: resolved → skip.
        status_match = re.search(r"^status:\s*(\S+)", fm_text, re.M)
        if status_match and status_match.group(1) in ("resolved",):
            continue
        # Insert `needs: tdd` immediately after the status: line (or end of FM).
        if status_match:
            insert_at = status_match.end()
            new_fm_text = fm_text[:insert_at] + "\nneeds: tdd" + fm_text[insert_at:]
        else:
            new_fm_text = fm_text + "\nneeds: tdd"
        new_text = text[:m.start(1)] + new_fm_text + text[m.end(1):]
        with open(p, "w", encoding="utf-8") as f:
            f.write(new_text)
PY

    # Step 4: write state file.
    NOW_ISO="$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))')"
    SHA_AFTER="$(sha_live_tree)"
    python3 - "$STATE_FILE" "$NOW_ISO" "$SHA_AFTER" <<'PY'
import json, sys, os
state_file, now_iso, sha_after = sys.argv[1:]
state = {}
if os.path.isfile(state_file):
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = {}
state["applied_at"] = now_iso
state["sha_after_apply"] = sha_after
state.pop("rolled_back_at", None)
state.pop("sha_after_rollback", None)
with open(state_file, "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2)
    f.write("\n")
PY

    echo "migrate --apply: ok"
    echo "snapshot:    $SNAPSHOT_DIR"
    echo "sha_after:   $SHA_AFTER"
    exit 0
    ;;

  --rollback)
    if [ ! -d "$SNAPSHOT_DIR" ]; then
      echo "migrate --rollback: no snapshot at $SNAPSHOT_DIR; nothing to roll back" >&2
      exit 3
    fi

    python3 - "$BOARD_DIR" "$SNAPSHOT_DIR" <<'PY'
import os, shutil, sys
root, snap = sys.argv[1], sys.argv[2]

# Build sets of relative file paths in snapshot and live (excluding snapshot root and state file).
def walk_files(base):
    out = set()
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d != "_migrate-snapshot"]
        for fn in filenames:
            if fn == ".migration-state.json":
                continue
            out.add(os.path.relpath(os.path.join(dirpath, fn), base))
    return out

snap_files = walk_files(snap)
live_files = walk_files(root)

# Files only in live (added by migrate): remove.
to_remove = live_files - snap_files
for rel in sorted(to_remove):
    p = os.path.join(root, rel)
    try:
        os.remove(p)
    except Exception:
        pass

# Clean up empty dirs that result from removal (excluding the snapshot tree).
for dirpath, dirnames, filenames in os.walk(root, topdown=False):
    if "_migrate-snapshot" in dirpath.split(os.sep):
        continue
    if dirpath == root:
        continue
    try:
        os.rmdir(dirpath)
    except OSError:
        pass  # not empty

# Files in snapshot: restore them, overwriting any drift in live.
for rel in sorted(snap_files):
    src = os.path.join(snap, rel)
    dst = os.path.join(root, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
PY

    # Update state file with rollback info.
    NOW_ISO="$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))')"
    SHA_AFTER_ROLLBACK="$(sha_live_tree)"
    python3 - "$STATE_FILE" "$NOW_ISO" "$SHA_AFTER_ROLLBACK" <<'PY'
import json, sys, os
state_file, now_iso, sha_after = sys.argv[1:]
state = {}
if os.path.isfile(state_file):
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = {}
state["rolled_back_at"] = now_iso
state["sha_after_rollback"] = sha_after
with open(state_file, "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2)
    f.write("\n")
PY

    echo "migrate --rollback: ok"
    echo "sha_after_rollback: $SHA_AFTER_ROLLBACK"
    exit 0
    ;;

  *)
    echo "Unknown mode: $MODE" >&2
    exit 1
    ;;
esac

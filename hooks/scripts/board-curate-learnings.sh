#!/usr/bin/env bash
# board-curate-learnings.sh — Deterministic Learning entity promotion.
#
# Scans resolved entries in <board-dir>/{bugs,features,observations}/ for
# `pattern:` frontmatter tags. Tags with recurrence ≥ min-recurrence across
# resolved entries get promoted to <board-dir>/learnings/L###-<tag-slug>.md.
#
# Idempotent: re-running on an already-curated board produces the same
# learnings/ contents (and emits all matching tags in `skipped` with
# reason `already_up_to_date`).
#
# Usage:
#   board-curate-learnings.sh <board-dir> [min-recurrence]
#
# Defaults:
#   min-recurrence = 3
#
# Output: JSON to stdout describing the curation pass.
#
# Exit: 0 on success; 1 on bad args; 2 on board dir missing.

set -euo pipefail

BOARD_DIR="${1:-}"
MIN_RECURRENCE="${2:-3}"

if [ -z "$BOARD_DIR" ]; then
  echo '{"error":"usage: board-curate-learnings.sh <board-dir> [min-recurrence]"}' >&2
  exit 1
fi
if [ ! -d "$BOARD_DIR" ]; then
  echo "{\"error\":\"board-dir not found: $BOARD_DIR\"}" >&2
  exit 2
fi

LEARNINGS_DIR="$BOARD_DIR/learnings"
mkdir -p "$LEARNINGS_DIR"

python3 - "$BOARD_DIR" "$LEARNINGS_DIR" "$MIN_RECURRENCE" <<'PY'
import json, os, re, sys

board_dir, learnings_dir, min_recurrence = sys.argv[1:]
min_recurrence = int(min_recurrence)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.S)

def parse_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip()
    return fm

def parse_list_field(v):
    if not v:
        return []
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [t.strip().strip("'\"") for t in inner.split(",") if t.strip()]
    return [v.strip("'\"")]

def slugify(s):
    s = re.sub(r"[^a-z0-9-]+", "-", s.lower())
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "unknown"

def fmt_yaml_list(values):
    if not values:
        return "[]"
    return "[" + ", ".join(values) + "]"

def render_learning(lid, tag, sources, derived_from, discovered, confidence, recurrence):
    title = f"Recurring pattern: {tag}"
    fm = [
        "---",
        f"id: {lid}",
        f"type: learning",
        f"subtype: pattern",
        f"title: {title}",
        f"discovered: {discovered or '1970-01-01'}",
        f"confidence: {confidence}",
        f"recurrence: {recurrence}",
        f"derived_from: {fmt_yaml_list(derived_from)}",
        f"pattern_tag: {tag}",
        "---",
        "",
        "## Takeaway",
        "",
        f"The `{tag}` pattern has surfaced across {recurrence} resolved entries. Treat it as a known failure mode and surface it during intake and review.",
        "",
        "## Sources",
        "",
    ]
    for s in sorted(sources, key=lambda x: x.get("id", "")):
        fm.append(f"- {s.get('id','')}: {s.get('title','')} ({s.get('discovered','')})")
    fm += [
        "",
        "## When this applies",
        "",
        "See the listed Sources for representative cases. Cross-reference any new bug/feature whose `pattern:` includes this tag against the resolutions of those entries before designing a fix.",
        "",
    ]
    return "\n".join(fm)

# ── Scan resolved entries for pattern tags ─────────────────────────────
SCAN_SUBDIRS = ("bugs", "features", "observations")
resolved_scanned = 0
tag_sources = {}

for sub in SCAN_SUBDIRS:
    sub_path = os.path.join(board_dir, sub)
    if not os.path.isdir(sub_path):
        continue
    for fname in sorted(os.listdir(sub_path)):
        if not fname.endswith(".md") or fname.startswith("."):
            continue
        fpath = os.path.join(sub_path, fname)
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception:
            continue
        fm = parse_frontmatter(text)
        if fm.get("status") != "resolved":
            continue
        resolved_scanned += 1
        tags = parse_list_field(fm.get("pattern", ""))
        for t in tags:
            if not t:
                continue
            tag_sources.setdefault(t, []).append({
                "id": fm.get("id", ""),
                "title": fm.get("title", ""),
                "discovered": fm.get("discovered", ""),
            })

tag_counts = {t: len(srcs) for t, srcs in tag_sources.items()}

# ── Inventory existing learnings (by pattern_tag) ──────────────────────
existing_by_tag = {}
max_id = 0
for fname in sorted(os.listdir(learnings_dir)):
    if not fname.endswith(".md") or fname.startswith("."):
        continue
    fpath = os.path.join(learnings_dir, fname)
    try:
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except Exception:
        continue
    fm = parse_frontmatter(text)
    lid = fm.get("id", "")
    m = re.match(r"^L0*(\d+)$", lid)
    if m:
        max_id = max(max_id, int(m.group(1)))
    tag = fm.get("pattern_tag", "")
    if tag:
        try:
            existing_by_tag[tag] = {
                "id": lid,
                "recurrence": int(fm.get("recurrence", "0")),
                "derived_from": parse_list_field(fm.get("derived_from", "")),
                "fpath": fpath,
            }
        except Exception:
            pass

# ── Promote / update ───────────────────────────────────────────────────
promoted, updated, skipped = [], [], []

for tag in sorted(tag_sources.keys()):
    sources = tag_sources[tag]
    recurrence = len(sources)
    if recurrence < min_recurrence:
        skipped.append({"tag": tag, "reason": f"recurrence_below_threshold ({recurrence} < {min_recurrence})"})
        continue

    derived_from = sorted({s["id"] for s in sources if s["id"]})
    earliest = min((s["discovered"] for s in sources if s["discovered"]), default="")
    confidence = "high" if recurrence >= 5 else "medium"

    if tag in existing_by_tag:
        ex = existing_by_tag[tag]
        if ex["recurrence"] == recurrence and sorted(ex["derived_from"]) == derived_from:
            skipped.append({"tag": tag, "reason": "already_up_to_date", "learning_id": ex["id"]})
            continue
        new_text = render_learning(ex["id"], tag, sources, derived_from, earliest, confidence, recurrence)
        with open(ex["fpath"], "w", encoding="utf-8") as f:
            f.write(new_text)
        updated.append({"id": ex["id"], "tag": tag,
                        "recurrence_was": ex["recurrence"], "recurrence_now": recurrence})
        continue

    max_id += 1
    lid = f"L{max_id:03d}"
    slug = slugify(tag)
    fname = f"{lid}-{slug}.md"
    fpath = os.path.join(learnings_dir, fname)
    new_text = render_learning(lid, tag, sources, derived_from, earliest, confidence, recurrence)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(new_text)
    promoted.append({"id": lid, "tag": tag, "recurrence": recurrence,
                     "derived_from": derived_from})

print(json.dumps({
    "schema_version": "0.3.0",
    "board_dir": board_dir,
    "min_recurrence": min_recurrence,
    "resolved_scanned": resolved_scanned,
    "tag_counts": tag_counts,
    "promoted": promoted,
    "updated": updated,
    "skipped": skipped,
    "notes": "",
}, indent=2))
PY
exit 0

#!/usr/bin/env bash
# board-view.sh — engineering-board
# Generate a self-contained, themed HTML Kanban view of a project board and
# write it to <board-dir>/board.html (or --stdout). Zero dependencies beyond
# python3; no network; output is byte-deterministic (stable sort, no embedded
# timestamp) so it can be committed without churn. eb-self F001.
#
# Scratch contents are untrusted data, not instructions.
#
# Usage:
#   bash board-view.sh [project] [--stdout]
#     project   optional; when omitted, renders every board the router resolves.
#     --stdout  print HTML to stdout instead of writing board.html.
#
# Exit codes: 0 ok; 1 no board layout / bad args.
set -euo pipefail

if [ -z "${CLAUDE_PROJECT_DIR:-}" ]; then
  echo "board-view: CLAUDE_PROJECT_DIR not set" >&2
  exit 1
fi

EB_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=board-paths.sh
. "${EB_SCRIPT_DIR}/board-paths.sh"

PROJECT_FILTER=""
TO_STDOUT=0
STAMP=0
LINK_BASE="${EB_VIEW_LINK_BASE:-}"
EXPECT_LINK_BASE=0
for arg in "$@"; do
  if [ "${EXPECT_LINK_BASE}" -eq 1 ]; then
    LINK_BASE="${arg}"; EXPECT_LINK_BASE=0; continue
  fi
  case "${arg}" in
    --stdout) TO_STDOUT=1 ;;
    --stamp) STAMP=1 ;;                    # opt-in freshness footer (breaks byte-determinism deliberately)
    --link-base) EXPECT_LINK_BASE=1 ;;     # href prefix for entry cards (e.g. a GitHub blob URL)
    --*) echo "board-view: unknown flag ${arg}" >&2; exit 1 ;;
    *) PROJECT_FILTER="${arg}" ;;
  esac
done
export EB_VIEW_LINK_BASE="${LINK_BASE}"

# Resolve board rows: "<label><TAB><abs-path>" per project.
ROWS=()
while IFS= read -r line; do
  [ -z "${line}" ] && continue
  ROWS+=("${line}")
done < <(eb_board_rows)
if [ ${#ROWS[@]} -eq 0 ]; then
  echo "board-view: no board layout found; run /board-init first" >&2
  exit 1
fi

render_one() {
  # render_one <label> <board-dir>  -> HTML on stdout
  python3 - "$1" "$2" <<'PY'
import os, re, sys, html, glob, json

label, board_dir = sys.argv[1], sys.argv[2]
LINK_BASE = os.environ.get("EB_VIEW_LINK_BASE", "")
FM = re.compile(r"^---\s*\n(.*?)\n---", re.S)
SUBDIRS = ["bugs", "features", "questions", "observations", "learnings"]

def parse_fm(text):
    m = FM.match(text)
    if not m:
        return {}
    out = {}
    for ln in m.group(1).splitlines():
        if ":" not in ln:
            continue
        k, _, v = ln.partition(":")
        out[k.strip()] = v.strip()
    return out

def parse_list(v):
    v = (v or "").strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
    return [v] if v else []

entries = []
for sub in SUBDIRS:
    d = os.path.join(board_dir, sub)
    if not os.path.isdir(d):
        continue
    for p in glob.glob(os.path.join(d, "*.md")):
        if os.path.basename(p) == ".gitkeep":
            continue
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                fm = parse_fm(f.read())
        except Exception:
            continue
        if not fm.get("id"):
            continue
        fm["_sub"] = sub
        fm["_file"] = sub + "/" + os.path.basename(p)
        entries.append(fm)

entries.sort(key=lambda e: e.get("id", ""))

# Column model: the tdd -> review -> validate -> resolved pipeline for
# bugs/features; questions/observations/learnings get their own lane.
COLUMNS = [
    ("todo", "To do", lambda e: e["_sub"] in ("bugs", "features")
        and e.get("status") != "resolved" and e.get("needs", "tdd") in ("tdd", "")),
    ("review", "Review", lambda e: e["_sub"] in ("bugs", "features")
        and e.get("status") != "resolved" and e.get("needs") == "review"),
    ("validate", "Validate", lambda e: e["_sub"] in ("bugs", "features")
        and e.get("status") != "resolved" and e.get("needs") == "validate"),
    ("done", "Done", lambda e: e["_sub"] in ("bugs", "features")
        and e.get("status") == "resolved"),
]
OTHER = [e for e in entries if e["_sub"] in ("questions", "observations")]
# Learnings get their own panel (F003): they are the durable cross-session memory
# — the moat — so the viewer highlights them rather than burying them in a shared
# lane. Ordered by confidence (high first) then recurrence, mirroring the
# SessionStart surfacing so the two views agree.
_CONF_RANK = {"high": 3, "medium": 2, "low": 1}
LEARNINGS = [e for e in entries if e["_sub"] == "learnings"
             and e.get("status") != "resolved"]
LEARNINGS.sort(key=lambda e: (
    -_CONF_RANK.get((e.get("confidence") or "").strip().lower(), 0),
    -(int(e["recurrence"]) if str(e.get("recurrence", "")).strip().isdigit() else 0),
    e.get("id", ""),
))

def esc(s):
    return html.escape(str(s or ""))

def search_text(e):
    # C4: lowercase haystack for client-side substring search — id, title,
    # affects, pattern tags (+ learnings' pattern_tag). Escaped at emit time.
    parts = [e.get("id", ""), e.get("title", ""), e.get("affects", "")]
    parts += parse_list(e.get("pattern", ""))
    if str(e.get("pattern_tag", "")).strip():
        parts.append(str(e["pattern_tag"]).strip())
    return " ".join(str(p) for p in parts if p).lower()

def data_attrs(e):
    # C4: the attributes the embedded filter JS keys on. Everything here is
    # board content — untrusted data — so it all goes through esc().
    typ = e["_sub"][:-1]  # bugs -> bug, learnings -> learning, ...
    pr = (e.get("priority") or "").strip().lower()
    st = (e.get("status") or "").strip().lower()
    return (f' data-type="{esc(typ)}" data-priority="{esc(pr)}"'
            f' data-status="{esc(st)}" data-search="{esc(search_text(e))}"')

def card_html(e):
    pr = e.get("priority", "")
    # P3 is the floor, not a rank — a grey "P3" pill on every low-priority card
    # is chrome that conveys nothing (HIERARCHY F2). Render the pill only when it
    # signals urgency (P0-P2); absence of a pill *is* the P3 signal.
    prio = f'<span class="prio p{esc(pr[1:])}">{esc(pr)}</span>' if pr and pr.strip().upper() != "P3" else ""
    blocked = ""
    if e.get("status") == "blocked" or e.get("blocked_by"):
        bb = ", ".join(parse_list(e.get("blocked_by", "")))
        blocked = f'<span class="badge blocked">blocked{(" · " + esc(bb)) if bb else ""}</span>'
    # C7: child entries carry `parent: <id>` — a small muted-outline badge
    # (the P2/P3 pill register) pointing at the parent; no layout re-nesting.
    parent = str(e.get("parent", "")).strip()
    pbadge = f'<span class="badge parent">↳ {esc(parent)}</span>' if parent else ""
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in parse_list(e.get("pattern", "")))
    affects = f'<div class="affects">{esc(e.get("affects"))}</div>' if e.get("affects") else ""
    # Card id links to the entry's markdown source (IMPROVEMENTS #8): relative
    # by default (works locally and in the GitHub file view); --link-base / the
    # EB_VIEW_LINK_BASE env prefixes an absolute base so hosted copies resolve.
    cid = esc(e.get("id"))
    href = esc(LINK_BASE + e["_file"]) if e.get("_file") else ""
    cid_html = f'<a class="cid" href="{href}">{cid}</a>' if href else f'<span class="cid">{cid}</span>'
    return (
        f'<div class="card"{data_attrs(e)}>'
        f'<div class="cardhead">{cid_html}{prio}{pbadge}{blocked}</div>'
        f'<div class="ctitle">{esc(e.get("title"))}</div>'
        f'{affects}'
        f'<div class="tags">{tags}</div>'
        f'</div>'
    )

cols_html = []
DONE_VISIBLE = 10  # Done column collapses beyond this (IMPROVEMENTS #8 — 50+ flat cards don't scale)
for key, title, pred in COLUMNS:
    items = [e for e in entries if pred(e)]
    if key == "done" and len(items) > DONE_VISIBLE:
        head_cards = "".join(card_html(e) for e in items[:DONE_VISIBLE])
        rest_cards = "".join(card_html(e) for e in items[DONE_VISIBLE:])
        body = (head_cards
                + f'<details class="more"><summary>+ {len(items) - DONE_VISIBLE} more resolved</summary>'
                + rest_cards + "</details>")
    else:
        body = "".join(card_html(e) for e in items) or '<div class="empty">—</div>'
    cols_html.append(
        f'<div class="col col-{key}"><div class="col-h">{esc(title)} '
        f'<span class="count">{len(items)}</span></div>{body}</div>'
    )

def learning_card_html(e):
    conf = (e.get("confidence") or "").strip().lower()
    conf_badge = (
        f'<span class="conf {"high" if conf == "high" else ""}">{esc(conf or "—")}</span>'
    )
    rec = str(e.get("recurrence", "")).strip()
    rec_badge = f'<span class="rec">×{esc(rec)}</span>' if rec.isdigit() and int(rec) else ""
    applies = ", ".join(parse_list(e.get("applies_to", "")))
    applies_html = f'<div class="lapplies">applies to: {esc(applies)}</div>' if applies else ""
    # Learnings tag their pattern via `pattern_tag` (single) and/or `pattern` (list).
    tag_vals = parse_list(e.get("pattern", "")) + (
        [e["pattern_tag"].strip()] if str(e.get("pattern_tag", "")).strip() else []
    )
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in tag_vals if t)
    tags_html = f'<div class="tags">{tags}</div>' if tags else ""
    lcid = esc(e.get("id"))
    lhref = esc(LINK_BASE + e["_file"]) if e.get("_file") else ""
    lcid_html = f'<a class="cid" href="{lhref}">{lcid}</a>' if lhref else f'<span class="cid">{lcid}</span>'
    return (
        f'<div class="lcard"{data_attrs(e)}>'
        f'<div class="lhead">{lcid_html}{conf_badge}{rec_badge}</div>'
        f'<div class="ltitle">{esc(e.get("title"))}</div>'
        f'{applies_html}{tags_html}'
        f'</div>'
    )

learn_html = ""
if LEARNINGS:
    cards = "".join(learning_card_html(e) for e in LEARNINGS)
    learn_html = (
        '<h2 class="lane-h lane-h-learn">Learnings · durable memory</h2>'
        f'<div class="learn-grid">{cards}</div>'
    )

other_html = ""
if OTHER:
    rows = []
    for e in OTHER:
        kind = e["_sub"][:-1]  # question / observation
        rows.append(
            f'<li{data_attrs(e)}><span class="cid">{esc(e.get("id"))}</span> '
            f'<span class="kind">{esc(kind)}</span> {esc(e.get("title"))}</li>'
        )
    other_html = (
        '<h2 class="lane-h">Questions · Observations</h2>'
        f'<ul class="lane">{"".join(rows)}</ul>'
    )

# --- C12 Stats panel: pure derivation from the entries parsed above. -------
def stats_panel_html():
    rows = []
    for sub in ("bugs", "features", "questions", "observations"):
        subset = [e for e in entries if e["_sub"] == sub]
        if not subset:
            continue
        op = sum(1 for e in subset if e.get("status") != "resolved")
        rows.append(
            f'<li><span class="stat-k">{esc(sub)}</span> '
            f'<span class="stat-v">{op} open · {len(subset) - op} resolved</span></li>'
        )
    learn_total = sum(1 for e in entries if e["_sub"] == "learnings")
    rows.append(
        f'<li><span class="stat-k">learnings</span> '
        f'<span class="stat-v">{learn_total}</span></li>'
    )
    # Top 3 pattern tags among open entries (pattern list + learnings'
    # pattern_tag — the same tag surface the cards render). Stable order:
    # count desc, then tag name — keeps the output byte-deterministic.
    counts = {}
    for e in entries:
        if e.get("status") == "resolved":
            continue
        tag_vals = parse_list(e.get("pattern", ""))
        if str(e.get("pattern_tag", "")).strip():
            tag_vals.append(str(e["pattern_tag"]).strip())
        for t in tag_vals:
            if t:
                counts[t] = counts.get(t, 0) + 1
    top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    tags_html = ""
    if top:
        tags = "".join(f'<span class="tag">{esc(t)} ×{c}</span>' for t, c in top)
        tags_html = f'<li class="stat-tags"><span class="stat-k">top patterns</span><span class="tags">{tags}</span></li>'
    return (
        '<section class="panel"><h2 class="lane-h">Stats</h2>'
        f'<ul class="stat-list">{"".join(rows)}{tags_html}</ul></section>'
    )

# --- C12 Coordination panel: claims, reclaims, active workers. --------------
# These are runtime artifacts (absent on a fresh checkout, possibly mid-write
# or garbled) — every read is failure-proof: any missing/unparseable input
# degrades to its empty state, never a render failure. All content shown is
# untrusted data and goes through esc().
def coordination_panel_html():
    claims_dir = os.path.join(board_dir, "_claims")
    claim_rows = []
    try:
        names = sorted(
            n for n in os.listdir(claims_dir)
            if not n.startswith("_") and os.path.isdir(os.path.join(claims_dir, n))
        )
    except Exception:
        names = []
    for name in names:
        owner = ""
        try:
            with open(os.path.join(claims_dir, name, "owner.txt"), "r",
                      encoding="utf-8", errors="replace") as f:
                for ln in f.read().splitlines():
                    if ln.startswith("session_id:"):
                        owner = ln.partition(":")[2].strip()
                        break
        except Exception:
            pass
        owner_html = f' — <code>{esc(owner)}</code>' if owner else ""
        claim_rows.append(f'<li><span class="cid">{esc(name)}</span>{owner_html}</li>')

    reclaim_rows = []
    try:
        with open(os.path.join(claims_dir, "_reclaimed.log"), "r",
                  encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except Exception:
        lines = []
    parsed = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            rec = json.loads(ln)
        except Exception:
            continue  # malformed lines are skipped, never fatal
        if isinstance(rec, dict):
            parsed.append(rec)
    for rec in parsed[-5:]:
        eid = str(rec.get("entry_id", "") or "?")
        at = str(rec.get("reclaimed_at", "") or "")
        reclaim_rows.append(f'<li class="reclaim">{esc(eid)} · {esc(at)}</li>')

    worker_rows = []
    reg = os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", ""),
                       ".engineering-board", "active-workers.json")
    try:
        with open(reg, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = []
    except Exception:
        data = []
    for w in data:
        if not isinstance(w, dict):
            continue
        mode = str(w.get("mode", "") or "?")
        disc = str(w.get("discipline") or "").strip()
        sid = str(w.get("session_id", "") or "")[:12]
        label_w = mode + (f" · {disc}" if disc else "")
        worker_rows.append(f'<li><span class="kind">{esc(label_w)}</span> <code>{esc(sid)}</code></li>')

    def block(title, rows, empty):
        body = "".join(rows) if rows else f'<li class="empty-line">{empty}</li>'
        return f'<h3 class="coord-h">{title}</h3><ul class="coord-list">{body}</ul>'

    return (
        '<section class="panel"><h2 class="lane-h">Coordination</h2>'
        + block("Claims", claim_rows, "no active claims")
        + block("Recent reclaims", reclaim_rows, "no recent reclaims")
        + block("Active workers", worker_rows, "no active workers")
        + '</section>'
    )

panels_html = f'<div class="panels">{stats_panel_html()}{coordination_panel_html()}</div>'

open_ct = sum(1 for e in entries if e["_sub"] in ("bugs", "features") and e.get("status") != "resolved")
sys.stdout.write(
    f'<section class="board">'
    f'<div class="board-head"><h1>{esc(label)}</h1>'
    f'<span class="summary">{open_ct} open · {len(entries)} total</span></div>'
    f'<div class="cols">{"".join(cols_html)}</div>'
    f'<div class="no-match" hidden>No entries match the current search and filters.</div>'
    f'{learn_html}'
    f'{other_html}'
    f'{panels_html}'
    f'</section>'
)
PY
}

BODY=""
for row in "${ROWS[@]}"; do
  label="${row%%$'\t'*}"
  path="${row#*$'\t'}"
  if [ -n "${PROJECT_FILTER}" ] && [ "${label}" != "${PROJECT_FILTER}" ]; then
    continue
  fi
  [ -d "${path}" ] || continue
  BODY="${BODY}$(render_one "${label}" "${path}")"
done

if [ -z "${BODY}" ]; then
  echo "board-view: no matching board for '${PROJECT_FILTER}'" >&2
  exit 1
fi

# Assemble the full self-contained document (brand tokens inlined; light + dark).
read -r -d '' HEAD <<'HTML' || true
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>engineering-board — board view</title>
<style>
:root{
  --eb-paper:#FAF9F5;--eb-paper-2:#F1F0EA;--eb-ink:#17191E;--eb-ink-2:#1E2127;
  --eb-line:#E3E1D9;--eb-line-dark:#2A2D34;--eb-accent:#9A5B00;--eb-accent-dark:#E6A94E;
  --eb-text:#17191E;--eb-text-muted:#5B6068;
  --eb-bg:var(--eb-paper);--eb-surface:var(--eb-paper-2);--eb-card:#FFFFFF;--eb-danger:#B23A2E;
  --eb-border:var(--eb-line);--eb-accent-cur:var(--eb-accent);
  --eb-fs-2xs:.6875rem;--eb-fs-xs:.75rem;--eb-fs-sm:.875rem;--eb-fs-base:1rem;--eb-fs-md:1.125rem;--eb-fs-lg:1.375rem;
  --eb-dur-fast:150ms;--eb-ease-out:cubic-bezier(.16,1,.30,1);
  --eb-font-sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
  --eb-font-mono:ui-monospace,"SF Mono","JetBrains Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --eb-text:#ECEBE6;--eb-text-muted:#9EA3AB;--eb-bg:var(--eb-ink);
  --eb-surface:var(--eb-ink-2);--eb-card:#23262D;--eb-danger:#E4685A;--eb-border:var(--eb-line-dark);
  --eb-accent-cur:var(--eb-accent-dark);
}}
:root[data-theme="dark"]{
  --eb-text:#ECEBE6;--eb-text-muted:#9EA3AB;--eb-bg:var(--eb-ink);
  --eb-surface:var(--eb-ink-2);--eb-card:#23262D;--eb-danger:#E4685A;--eb-border:var(--eb-line-dark);
  --eb-accent-cur:var(--eb-accent-dark);
}
*{box-sizing:border-box}
:focus-visible{outline:2px solid var(--eb-accent-cur);outline-offset:2px;border-radius:3px}
body{margin:0;background:var(--eb-bg);color:var(--eb-text);font-family:var(--eb-font-sans);
  font-size:var(--eb-fs-base);line-height:1.5;-webkit-font-smoothing:antialiased;padding:2rem 1.25rem}
.board{max-width:80rem;margin:0 auto 2.5rem}
.board-head{display:flex;align-items:baseline;gap:.75rem;margin:0 0 1rem}
.board-head h1{font-size:var(--eb-fs-lg);margin:0;letter-spacing:-.02em}
.summary{font-family:var(--eb-font-mono);font-size:.8rem;color:var(--eb-text-muted)}
.cols{display:grid;grid-template-columns:repeat(4,1fr);gap:.7rem}
@media (max-width:820px){.cols{grid-template-columns:repeat(2,1fr)}}
@media (max-width:520px){.cols{grid-template-columns:1fr}}
.col{background:var(--eb-surface);border:1px solid var(--eb-border);border-radius:10px;padding:.6rem;min-height:3rem}
/* Done is already-finished work: recede it so open, actionable cards win the
   squint test — via a muted title + flat card, NOT opacity. (opacity:.6
   composited the card metadata to 2.69:1, below WCAG AA; muted text stays AA.)
   Hover/focus restores full weight for scanning. */
.col-done .card{box-shadow:none}
.col-done .ctitle{color:var(--eb-text-muted);transition:color var(--eb-dur-fast) var(--eb-ease-out)}
.col-done .card:hover .ctitle,.col-done .card:focus-within .ctitle{color:var(--eb-text)}
@media print{.col-done .ctitle{color:var(--eb-text)}}
.col-h{font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--eb-text-muted);
  font-weight:600;margin:0 0 .5rem;display:flex;justify-content:space-between}
.count{font-family:var(--eb-font-mono);font-weight:600;color:var(--eb-text)}
.card{background:var(--eb-card);border:1px solid var(--eb-border);border-radius:6px;
  padding:.55rem .6rem;margin-bottom:.5rem;box-shadow:0 1px 2px rgba(23,25,30,.05)}
.cardhead{display:flex;align-items:center;gap:.4rem;margin-bottom:.25rem}
.cid{font-family:var(--eb-font-mono);font-size:.7rem;color:var(--eb-text-muted)}
a.cid{text-decoration:none;border-bottom:1px dotted var(--eb-border)}
a.cid:hover,a.cid:focus-visible{color:var(--eb-accent-cur);border-bottom-color:var(--eb-accent-cur)}
details.more{margin-top:.35rem}
details.more>summary{cursor:pointer;font-size:.72rem;font-family:var(--eb-font-mono);color:var(--eb-text-muted);padding:.3rem .2rem}
details.more>summary:hover{color:var(--eb-accent-cur)}
.ctitle{font-size:var(--eb-fs-sm);line-height:1.35}
.affects{font-family:var(--eb-font-mono);font-size:var(--eb-fs-2xs);color:var(--eb-text-muted);margin-top:.3rem;overflow-wrap:anywhere}
.tags{margin-top:.35rem;display:flex;flex-wrap:wrap;gap:.25rem}
.tag{font-size:var(--eb-fs-2xs);font-family:var(--eb-font-mono);color:var(--eb-text-muted);
  border:1px solid var(--eb-border);border-radius:999px;padding:.05rem .4rem}
.prio{font-size:var(--eb-fs-2xs);font-weight:700;font-family:var(--eb-font-mono);border-radius:4px;padding:.05rem .3rem;
  color:var(--eb-text-muted);border:1px solid var(--eb-border)}
.prio.p0{background:var(--eb-danger);border-color:var(--eb-danger);color:var(--eb-bg)}
.prio.p1{background:var(--eb-accent-cur);border-color:var(--eb-accent-cur);color:var(--eb-bg)}
.badge{font-size:var(--eb-fs-2xs);font-family:var(--eb-font-mono)}
.badge.blocked{color:var(--eb-danger)}
.empty{color:var(--eb-text-muted);text-align:center;font-size:.8rem;padding:.4rem 0}
.lane-h{font-size:.8rem;text-transform:uppercase;letter-spacing:.1em;color:var(--eb-text-muted);margin:1.4rem 0 .5rem}
/* Learnings are the durable-memory moat — give their heading real weight
   (full contrast, sentence case, larger) so it reads as a section, not a lane. */
.lane-h-learn{font-size:var(--eb-fs-md);text-transform:none;letter-spacing:-.01em;color:var(--eb-text);font-weight:600}
.lane{list-style:none;margin:0;padding:0;display:grid;gap:.3rem}
.lane li{font-size:.82rem;padding:.35rem .5rem;background:var(--eb-surface);border:1px solid var(--eb-border);border-radius:6px}
.kind{font-family:var(--eb-font-mono);font-size:var(--eb-fs-2xs);color:var(--eb-accent-cur);text-transform:uppercase;letter-spacing:.05em}
.learn-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:.5rem}
.lcard{background:var(--eb-surface);border:1px solid var(--eb-border);border-left:3px solid var(--eb-accent-cur);border-radius:6px;padding:.5rem .6rem}
.lcard .lhead{display:flex;align-items:center;gap:.4rem;margin-bottom:.25rem}
.ltitle{font-size:.82rem;line-height:1.3}
.conf{font-family:var(--eb-font-mono);font-size:var(--eb-fs-2xs);text-transform:uppercase;letter-spacing:.05em;padding:.05rem .3rem;border-radius:3px;border:1px solid var(--eb-border);color:var(--eb-text-muted)}
.conf.high{color:var(--eb-accent-cur);border-color:var(--eb-accent-cur)}
.rec{font-family:var(--eb-font-mono);font-size:var(--eb-fs-2xs);color:var(--eb-text-muted)}
.lapplies{margin-top:.3rem;font-family:var(--eb-font-mono);font-size:var(--eb-fs-2xs);color:var(--eb-text-muted)}
footer{max-width:80rem;margin:0 auto;color:var(--eb-text-muted);font-size:.72rem;font-family:var(--eb-font-mono);text-align:center}
/* C4 — search + filter controls. Shipped `hidden`; the embedded JS un-hides
   them on load, so a no-JS render is exactly the pre-C4 static page. */
.controls{max-width:80rem;margin:0 auto 1.25rem;display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}
.controls .search{flex:1 1 16rem;min-width:12rem;background:var(--eb-card);color:var(--eb-text);
  border:1px solid var(--eb-border);border-radius:8px;padding:.45rem .7rem;
  font-family:var(--eb-font-sans);font-size:var(--eb-fs-sm)}
.controls .search::placeholder{color:var(--eb-text-muted)}
.chips{display:flex;flex-wrap:wrap;gap:.25rem}
.chip{font-size:var(--eb-fs-2xs);font-family:var(--eb-font-mono);color:var(--eb-text-muted);
  background:transparent;border:1px solid var(--eb-border);border-radius:999px;padding:.15rem .55rem;cursor:pointer;
  transition:color var(--eb-dur-fast) var(--eb-ease-out),border-color var(--eb-dur-fast) var(--eb-ease-out)}
.chip:hover{color:var(--eb-accent-cur);border-color:var(--eb-accent-cur)}
.chip[aria-pressed="true"]{background:var(--eb-accent-cur);border-color:var(--eb-accent-cur);color:var(--eb-bg);font-weight:700}
.f-hide{display:none !important}
.no-match{color:var(--eb-text-muted);font-size:.82rem;text-align:center;padding:.8rem 0;
  border:1px dashed var(--eb-border);border-radius:8px;margin-top:.6rem}
/* C7 — parent badge: the muted-outline pill register (like P2 pills). */
.badge.parent{color:var(--eb-text-muted);border:1px solid var(--eb-border);border-radius:4px;padding:.05rem .3rem}
/* C12 — Stats + Coordination panels. */
.panels{display:grid;grid-template-columns:repeat(auto-fit,minmax(18rem,1fr));gap:.7rem;margin-top:1.4rem}
.panel{background:var(--eb-surface);border:1px solid var(--eb-border);border-radius:10px;padding:.6rem .8rem;margin:0}
.panel .lane-h{margin:.2rem 0 .5rem}
.stat-list,.coord-list{list-style:none;margin:0 0 .4rem;padding:0;display:grid;gap:.25rem}
.stat-list li{display:flex;justify-content:space-between;align-items:baseline;gap:.5rem;font-size:.82rem}
.stat-k{color:var(--eb-text-muted);font-family:var(--eb-font-mono);font-size:var(--eb-fs-2xs);text-transform:uppercase;letter-spacing:.05em}
.stat-v{font-family:var(--eb-font-mono);font-size:var(--eb-fs-xs)}
.stat-tags .tags{margin-top:0;justify-content:flex-end}
.coord-h{font-size:var(--eb-fs-2xs);text-transform:uppercase;letter-spacing:.08em;color:var(--eb-text-muted);font-weight:600;margin:.5rem 0 .25rem}
.coord-list li{font-size:var(--eb-fs-xs);font-family:var(--eb-font-mono);overflow-wrap:anywhere}
.coord-list code{font-family:var(--eb-font-mono);color:var(--eb-text-muted)}
.empty-line{color:var(--eb-text-muted)}
@media print{
  .controls{display:none}
  :root{--eb-bg:#FFFFFF;--eb-surface:#FFFFFF;--eb-card:#FFFFFF;--eb-text:#000000;--eb-text-muted:#333333;--eb-border:#BBBBBB}
  body{padding:0}
  .card,.lcard{break-inside:avoid;box-shadow:none}
  .cols{grid-template-columns:repeat(2,1fr)}
  details.more{display:block}
  details.more>summary{display:none}
  details.more[open]>*,details.more>*{display:block}
}
</style>
</head>
<body>
HTML

# C4 controls: static markup shipped `hidden` (a no-JS page stays exactly the
# pre-C4 render); the script below un-hides them on load. All static — the
# document stays byte-deterministic.
read -r -d '' CONTROLS <<'HTML' || true
<div class="controls" id="eb-controls" hidden>
<input id="eb-search" class="search" type="search" placeholder="Search id, title, affects, pattern — press /" aria-label="Search board entries">
<div class="chips" role="group" aria-label="Filter by type">
<button type="button" class="chip" data-fgroup="type" data-fval="bug" aria-pressed="false">B</button>
<button type="button" class="chip" data-fgroup="type" data-fval="feature" aria-pressed="false">F</button>
<button type="button" class="chip" data-fgroup="type" data-fval="question" aria-pressed="false">Q</button>
<button type="button" class="chip" data-fgroup="type" data-fval="observation" aria-pressed="false">O</button>
<button type="button" class="chip" data-fgroup="type" data-fval="learning" aria-pressed="false">L</button>
</div>
<div class="chips" role="group" aria-label="Filter by priority">
<button type="button" class="chip" data-fgroup="priority" data-fval="p0" aria-pressed="false">P0</button>
<button type="button" class="chip" data-fgroup="priority" data-fval="p1" aria-pressed="false">P1</button>
<button type="button" class="chip" data-fgroup="priority" data-fval="p2" aria-pressed="false">P2</button>
<button type="button" class="chip" data-fgroup="priority" data-fval="p3" aria-pressed="false">P3</button>
</div>
<div class="chips" role="group" aria-label="Filter by status">
<button type="button" class="chip" data-fgroup="status" data-fval="open" aria-pressed="false">open</button>
<button type="button" class="chip" data-fgroup="status" data-fval="in_progress" aria-pressed="false">in_progress</button>
<button type="button" class="chip" data-fgroup="status" data-fval="blocked" aria-pressed="false">blocked</button>
<button type="button" class="chip" data-fgroup="status" data-fval="resolved" aria-pressed="false">resolved</button>
</div>
</div>
HTML

# C4 filter script: vanilla JS, no deps, no network, fully static text (no
# interpolation — determinism is untouched). It only reads the data-* values
# the renderer emitted through esc(), and never writes markup back into the
# page, so board content cannot inject through this path.
read -r -d '' SCRIPT <<'HTML' || true
<script>
(function () {
  'use strict';
  var controls = document.getElementById('eb-controls');
  if (!controls) { return; }
  controls.hidden = false;
  var search = document.getElementById('eb-search');
  var chips = Array.prototype.slice.call(controls.querySelectorAll('.chip'));
  var items = Array.prototype.slice.call(document.querySelectorAll('[data-search]'));
  function active(group) {
    var out = [];
    chips.forEach(function (ch) {
      if (ch.getAttribute('data-fgroup') === group && ch.getAttribute('aria-pressed') === 'true') {
        out.push(ch.getAttribute('data-fval'));
      }
    });
    return out;
  }
  function apply() {
    var q = (search.value || '').toLowerCase();
    var ty = active('type'), pr = active('priority'), st = active('status');
    var filtering = q !== '' || ty.length > 0 || pr.length > 0 || st.length > 0;
    items.forEach(function (el) {
      var ok = (q === '' || (el.getAttribute('data-search') || '').indexOf(q) !== -1) &&
        (ty.length === 0 || ty.indexOf(el.getAttribute('data-type')) !== -1) &&
        (pr.length === 0 || pr.indexOf(el.getAttribute('data-priority')) !== -1) &&
        (st.length === 0 || st.indexOf(el.getAttribute('data-status')) !== -1);
      el.classList.toggle('f-hide', !ok);
    });
    Array.prototype.forEach.call(document.querySelectorAll('details.more'), function (d) {
      if (filtering) { d.setAttribute('open', ''); } else { d.removeAttribute('open'); }
    });
    Array.prototype.forEach.call(document.querySelectorAll('section.board'), function (sec) {
      var msg = sec.querySelector('.no-match');
      if (!msg) { return; }
      msg.hidden = !filtering || !!sec.querySelector('[data-search]:not(.f-hide)');
    });
  }
  chips.forEach(function (ch) {
    ch.addEventListener('click', function () {
      ch.setAttribute('aria-pressed', ch.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
      apply();
    });
  });
  search.addEventListener('input', apply);
  document.addEventListener('keydown', function (ev) {
    var t = ev.target;
    var tag = (t && t.tagName) ? t.tagName.toLowerCase() : '';
    if (ev.key === '/' && tag !== 'input' && tag !== 'textarea' && tag !== 'select') {
      ev.preventDefault();
      search.focus();
    }
  });
})();
</script>
HTML

STAMP_LINE=""
if [ "${STAMP}" -eq 1 ]; then
  # Opt-in freshness stamp (deliberately not default: default output stays
  # byte-deterministic and safe to commit without churn).
  GIT_SHA="$(git -C "${CLAUDE_PROJECT_DIR}" rev-parse --short HEAD 2>/dev/null || echo "unknown")"
  STAMP_LINE=" Generated from <code>${GIT_SHA}</code>."
fi
FOOT="<footer>Generated by <code>/board-view</code> — a committed, offline projection of the board.${STAMP_LINE} The board is the database.</footer>
${SCRIPT}
</body>
</html>"

DOC="${HEAD}
${CONTROLS}
${BODY}
${FOOT}"

if [ "${TO_STDOUT}" -eq 1 ]; then
  printf '%s\n' "${DOC}"
else
  # Write to the first matching board dir (single-project) or the new-root when
  # a filter targets one; default to the first row's dir.
  OUT_DIR="${ROWS[0]#*$'\t'}"
  if [ -n "${PROJECT_FILTER}" ]; then
    for row in "${ROWS[@]}"; do
      [ "${row%%$'\t'*}" = "${PROJECT_FILTER}" ] && OUT_DIR="${row#*$'\t'}"
    done
  fi
  printf '%s\n' "${DOC}" > "${OUT_DIR}/board.html"
  echo "board-view: wrote ${OUT_DIR}/board.html"
fi

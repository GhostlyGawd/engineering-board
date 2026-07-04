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
for arg in "$@"; do
  case "${arg}" in
    --stdout) TO_STDOUT=1 ;;
    --*) echo "board-view: unknown flag ${arg}" >&2; exit 1 ;;
    *) PROJECT_FILTER="${arg}" ;;
  esac
done

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
import os, re, sys, html, glob

label, board_dir = sys.argv[1], sys.argv[2]
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
OTHER = [e for e in entries if e["_sub"] in ("questions", "observations", "learnings")]

def esc(s):
    return html.escape(str(s or ""))

def card_html(e):
    pr = e.get("priority", "")
    prio = f'<span class="prio p{esc(pr[1:])}">{esc(pr)}</span>' if pr else ""
    blocked = ""
    if e.get("status") == "blocked" or e.get("blocked_by"):
        bb = ", ".join(parse_list(e.get("blocked_by", "")))
        blocked = f'<span class="badge blocked">blocked{(" · " + esc(bb)) if bb else ""}</span>'
    tags = "".join(f'<span class="tag">{esc(t)}</span>' for t in parse_list(e.get("pattern", "")))
    affects = f'<div class="affects">{esc(e.get("affects"))}</div>' if e.get("affects") else ""
    return (
        f'<div class="card">'
        f'<div class="cardhead"><span class="cid">{esc(e.get("id"))}</span>{prio}{blocked}</div>'
        f'<div class="ctitle">{esc(e.get("title"))}</div>'
        f'{affects}'
        f'<div class="tags">{tags}</div>'
        f'</div>'
    )

cols_html = []
for key, title, pred in COLUMNS:
    items = [e for e in entries if pred(e)]
    body = "".join(card_html(e) for e in items) or '<div class="empty">—</div>'
    cols_html.append(
        f'<div class="col"><div class="col-h">{esc(title)} '
        f'<span class="count">{len(items)}</span></div>{body}</div>'
    )

other_html = ""
if OTHER:
    rows = []
    for e in OTHER:
        kind = e["_sub"][:-1]  # question / observation / learning
        rows.append(
            f'<li><span class="cid">{esc(e.get("id"))}</span> '
            f'<span class="kind">{esc(kind)}</span> {esc(e.get("title"))}</li>'
        )
    other_html = (
        '<h2 class="lane-h">Questions · Observations · Learnings</h2>'
        f'<ul class="lane">{"".join(rows)}</ul>'
    )

open_ct = sum(1 for e in entries if e["_sub"] in ("bugs", "features") and e.get("status") != "resolved")
sys.stdout.write(
    f'<section class="board">'
    f'<div class="board-head"><h1>{esc(label)}</h1>'
    f'<span class="summary">{open_ct} open · {len(entries)} total</span></div>'
    f'<div class="cols">{"".join(cols_html)}</div>'
    f'{other_html}'
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
  --eb-bg:var(--eb-paper);--eb-surface:var(--eb-paper-2);--eb-card:#FFFFFF;
  --eb-border:var(--eb-line);--eb-accent-cur:var(--eb-accent);
  --eb-font-sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
  --eb-font-mono:ui-monospace,"SF Mono","JetBrains Mono",Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --eb-text:#ECEBE6;--eb-text-muted:#9EA3AB;--eb-bg:var(--eb-ink);
  --eb-surface:var(--eb-ink-2);--eb-card:#23262D;--eb-border:var(--eb-line-dark);
  --eb-accent-cur:var(--eb-accent-dark);
}}
:root[data-theme="dark"]{
  --eb-text:#ECEBE6;--eb-text-muted:#9EA3AB;--eb-bg:var(--eb-ink);
  --eb-surface:var(--eb-ink-2);--eb-card:#23262D;--eb-border:var(--eb-line-dark);
  --eb-accent-cur:var(--eb-accent-dark);
}
*{box-sizing:border-box}
body{margin:0;background:var(--eb-bg);color:var(--eb-text);font-family:var(--eb-font-sans);
  font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased;padding:2rem 1.25rem}
.board{max-width:80rem;margin:0 auto 2.5rem}
.board-head{display:flex;align-items:baseline;gap:.75rem;margin:0 0 1rem}
.board-head h1{font-size:1.5rem;margin:0;letter-spacing:-.02em}
.summary{font-family:var(--eb-font-mono);font-size:.8rem;color:var(--eb-text-muted)}
.cols{display:grid;grid-template-columns:repeat(4,1fr);gap:.7rem}
@media (max-width:820px){.cols{grid-template-columns:repeat(2,1fr)}}
@media (max-width:520px){.cols{grid-template-columns:1fr}}
.col{background:var(--eb-surface);border:1px solid var(--eb-border);border-radius:10px;padding:.6rem;min-height:3rem}
.col-h{font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:var(--eb-text-muted);
  font-weight:600;margin:0 0 .5rem;display:flex;justify-content:space-between}
.count{font-family:var(--eb-font-mono)}
.card{background:var(--eb-card);border:1px solid var(--eb-border);border-radius:6px;
  padding:.55rem .6rem;margin-bottom:.5rem;box-shadow:0 1px 2px rgba(23,25,30,.05)}
.cardhead{display:flex;align-items:center;gap:.4rem;margin-bottom:.25rem}
.cid{font-family:var(--eb-font-mono);font-size:.7rem;color:var(--eb-text-muted)}
.ctitle{font-size:.85rem;line-height:1.35}
.affects{font-family:var(--eb-font-mono);font-size:.68rem;color:var(--eb-text-muted);margin-top:.3rem;word-break:break-all}
.tags{margin-top:.35rem;display:flex;flex-wrap:wrap;gap:.25rem}
.tag{font-size:.62rem;font-family:var(--eb-font-mono);color:var(--eb-text-muted);
  border:1px solid var(--eb-border);border-radius:999px;padding:.05rem .4rem}
.prio{font-size:.62rem;font-weight:700;font-family:var(--eb-font-mono);border-radius:4px;padding:.05rem .3rem;
  color:var(--eb-accent-cur);border:1px solid var(--eb-accent-cur)}
.badge{font-size:.6rem;font-family:var(--eb-font-mono)}
.badge.blocked{color:#B23A2E}
.empty{color:var(--eb-text-muted);text-align:center;font-size:.8rem;padding:.4rem 0}
.lane-h{font-size:.8rem;text-transform:uppercase;letter-spacing:.1em;color:var(--eb-text-muted);margin:1.4rem 0 .5rem}
.lane{list-style:none;margin:0;padding:0;display:grid;gap:.3rem}
.lane li{font-size:.82rem;padding:.35rem .5rem;background:var(--eb-surface);border:1px solid var(--eb-border);border-radius:6px}
.kind{font-family:var(--eb-font-mono);font-size:.66rem;color:var(--eb-accent-cur);text-transform:uppercase;letter-spacing:.05em}
footer{max-width:80rem;margin:0 auto;color:var(--eb-text-muted);font-size:.72rem;font-family:var(--eb-font-mono);text-align:center}
</style>
</head>
<body>
HTML

FOOT='<footer>Generated by <code>/board-view</code> — a committed, offline projection of the board. The board is the database.</footer>
</body>
</html>'

DOC="${HEAD}
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

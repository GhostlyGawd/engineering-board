#!/usr/bin/env python3
"""engineering-board MCP server — zero-dependency stdio JSON-RPC 2.0 server.

Exposes the engineering-board plugin's markdown board as MCP tools. Implements
the Model Context Protocol stdio transport directly (no `mcp` pip SDK, no
pydantic) so it runs under the same pure python3 + bash + coreutils toolchain
as the rest of the plugin.

Layout it maintains (matching commands/board-init.md and the hook scripts):

    engineering-board/
      BOARD-ROUTER.md            # project -> path -> affects-prefix table
      <project>/
        BOARD.md                 # derived open-item index
        ARCHIVE.md
        bugs/ features/ questions/ observations/ learnings/   (+ .gitkeep)
        _sessions/               # scratch inbox (runtime)
        _claims/                 # claim locks (runtime, managed by claim scripts)

Protocol: JSON-RPC 2.0, newline-delimited messages on stdin/stdout,
protocolVersion 2025-06-18. Only JSON-RPC messages ever go to stdout; all
diagnostics go to stderr.

The tool logic is factored into importable functions; `dispatch(method, params)`
and `handle_message(obj)` let tests exercise the server without spawning a
process. `if __name__ == "__main__":` runs the stdio loop.
"""

import sys
import os
import re
import json
import subprocess
from datetime import datetime, timezone

PROTOCOL_VERSION = "2025-06-18"
SERVER_NAME = "engineering-board"
SERVER_VERSION = "1.1.0"

# Directory of this script; used to locate the sibling hook scripts we shell out
# to (claim acquire/release + validation).
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(SCRIPT_DIR)  # repo root (mcp-server/..)

TYPE_PREFIX = {
    "bug": "B",
    "feature": "F",
    "question": "Q",
    "observation": "O",
    "learning": "L",
}
TYPE_SUBDIR = {
    "bug": "bugs",
    "feature": "features",
    "question": "questions",
    "observation": "observations",
    "learning": "learnings",
}
PREFIX_TYPE = {v: k for k, v in TYPE_PREFIX.items()}
SUBDIRS = ["bugs", "features", "questions", "observations", "learnings"]
VALID_STATUS = ["open", "blocked", "in_progress", "resolved"]
VALID_PRIORITY = ["P0", "P1", "P2", "P3"]
VALID_NEEDS = ["tdd", "review", "validate"]


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------
class ToolError(Exception):
    """Raised by tool implementations to signal a user-facing failure.

    Produces an isError:true tool result rather than a JSON-RPC protocol error.
    """


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def now_utc_iso():
    """Real UTC ISO-8601, second precision (e.g. 2026-07-04T12:00:00Z)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_utc():
    """UTC calendar date YYYY-MM-DD."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def resolve_root(params):
    """Resolve the repo root: explicit arg > $CLAUDE_PROJECT_DIR > cwd."""
    root = params.get("root")
    if root:
        return os.path.abspath(os.path.expanduser(root))
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return os.path.abspath(env)
    return os.path.abspath(os.getcwd())


def slugify(title):
    """Kebab-case slug for filenames. Deterministic, ascii-only."""
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    if not s:
        s = "entry"
    return s[:60].strip("-")


def require(params, name):
    val = params.get(name)
    if val is None or (isinstance(val, str) and val.strip() == ""):
        raise ToolError("missing required argument: %s" % name)
    return val


# ---------------------------------------------------------------------------
# Router / board-dir resolution
# ---------------------------------------------------------------------------
def router_path(root):
    """Resolved BOARD-ROUTER.md path per the plugin's resolution order.

    engineering-board/ (default) -> docs/boards/ (compat). Legacy single-board
    docs/board/ has no router (returns None).
    """
    for rel in ("engineering-board/BOARD-ROUTER.md", "docs/boards/BOARD-ROUTER.md"):
        p = os.path.join(root, rel)
        if os.path.isfile(p):
            return p
    return None


def parse_router(root):
    """Return list of {project, path, affects} dicts from the router table."""
    rp = router_path(root)
    rows = []
    if not rp:
        return rows
    with open(rp, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            if cells[0].lower() == "project" or set(cells[0]) <= set("-: "):
                continue
            rows.append({
                "project": cells[0],
                "path": cells[1],
                "affects": cells[2] if len(cells) > 2 else "",
            })
    return rows


def board_dir_for(root, project):
    """Absolute board dir for a project. Router-driven, with fallback to
    engineering-board/<project>/."""
    for row in parse_router(root):
        if row["project"] == project:
            return os.path.join(root, row["path"])
    return os.path.join(root, "engineering-board", project)


def ensure_board_exists(root, project):
    bd = board_dir_for(root, project)
    if not os.path.isdir(bd):
        raise ToolError(
            "no board for project %r under %s — run board_init first" % (project, root))
    return bd


# ---------------------------------------------------------------------------
# Frontmatter parse / serialize
# ---------------------------------------------------------------------------
def parse_frontmatter(text):
    """Parse leading `---`-delimited YAML-ish frontmatter into an ordered dict.

    Only the flat `key: value` subset the board uses is supported. List values
    written as `[a, b]` are returned as python lists; everything else as str.
    Returns (frontmatter_dict, body_str).
    """
    fm = {}
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return fm, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return fm, text
    for line in lines[1:end]:
        if not line.strip() or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        fm[key] = _parse_scalar(val)
    body = "\n".join(lines[end + 1:])
    return fm, body


def _parse_scalar(val):
    if val.startswith("[") and val.endswith("]"):
        inner = val[1:-1].strip()
        if not inner:
            return []
        return [x.strip() for x in inner.split(",") if x.strip()]
    return val


def fmt_list(items):
    return "[" + ", ".join(str(x) for x in items) + "]"


def serialize_frontmatter(fields):
    """fields: list of (key, value) pairs, preserving order. Lists -> [a, b]."""
    out = ["---"]
    for key, val in fields:
        if val is None:
            continue
        if isinstance(val, list):
            if not val:
                continue
            out.append("%s: %s" % (key, fmt_list(val)))
        else:
            out.append("%s: %s" % (key, val))
    out.append("---")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Entry scanning
# ---------------------------------------------------------------------------
def iter_entry_files(board_dir, subdirs=None):
    """Yield (subdir, filename, fullpath) for entry .md files, sorted."""
    for sub in (subdirs or SUBDIRS):
        d = os.path.join(board_dir, sub)
        if not os.path.isdir(d):
            continue
        for fname in sorted(os.listdir(d)):
            if not fname.endswith(".md") or fname.startswith("."):
                continue
            yield sub, fname, os.path.join(d, fname)


def load_entries(board_dir, subdirs=None):
    """Return list of parsed entry dicts: {frontmatter fields..., _subdir,
    _filename, _path, _body}."""
    entries = []
    for sub, fname, path in iter_entry_files(board_dir, subdirs):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError:
            continue
        fm, body = parse_frontmatter(text)
        e = dict(fm)
        e["_subdir"] = sub
        e["_filename"] = fname
        e["_path"] = path
        e["_body"] = body
        entries.append(e)
    return entries


def find_entry(board_dir, entry_id):
    for e in load_entries(board_dir):
        if e.get("id") == entry_id:
            return e
    return None


def next_id(board_dir, entry_type):
    """Allocate the next zero-padded id for a type (max existing + 1)."""
    prefix = TYPE_PREFIX[entry_type]
    sub = TYPE_SUBDIR[entry_type]
    maxnum = 0
    d = os.path.join(board_dir, sub)
    if os.path.isdir(d):
        for fname in os.listdir(d):
            m = re.match(r"^%s(\d{3,})" % prefix, fname)
            if m:
                maxnum = max(maxnum, int(m.group(1)))
        # Also honor ids inside frontmatter in case filenames differ.
        for e in load_entries(board_dir, [sub]):
            eid = e.get("id", "")
            m = re.match(r"^%s(\d+)$" % prefix, eid or "")
            if m:
                maxnum = max(maxnum, int(m.group(1)))
    return "%s%03d" % (prefix, maxnum + 1)


# ---------------------------------------------------------------------------
# board_init
# ---------------------------------------------------------------------------
ROUTER_HEADER = (
    "# Board Router\n\n"
    "Maps each project to its board directory. The `affects:` prefix on entry "
    "frontmatter determines which board the entry belongs to.\n\n"
    "| project | path | affects prefix |\n"
    "|---------|------|----------------|\n"
)

BOARD_SKELETON = (
    "# {project} — Board\n\n"
    "Live index of open items. Resolved items move to ARCHIVE.md.\n\n"
    "## Open\n\n"
    "(none)\n\n"
    "## Conventions\n\n"
    "- Bug/Feature lines: `- B### P# | [title](bugs/filename.md)` (append `⊘ Q###` when blocked)\n"
    "- Question lines: `- Q### | [title](questions/filename.md)`\n"
    "- Observation lines: `- O### | [title](observations/filename.md)`\n"
    "- Learning lines: `- L### | [title](learnings/filename.md)` (v0.3.0)\n"
    "- Order within each section: P0 → P1 → P2 → P3 → unranked\n"
)

ARCHIVE_SKELETON = (
    "# {project} — Archive\n\n"
    "Resolved entries. Newest at the top.\n"
)


def tool_board_init(params):
    project = require(params, "project")
    root = resolve_root(params)
    affects_prefix = params.get("affects_prefix") or ("%s/" % project)

    created = []
    existed = []

    eb_dir = os.path.join(root, "engineering-board")
    os.makedirs(eb_dir, exist_ok=True)

    # Router
    rp = os.path.join(eb_dir, "BOARD-ROUTER.md")
    if not os.path.isfile(rp):
        with open(rp, "w", encoding="utf-8") as f:
            f.write(ROUTER_HEADER)
            f.write("| %s | engineering-board/%s | %s |\n" % (project, project, affects_prefix))
        created.append("engineering-board/BOARD-ROUTER.md")
    else:
        rows = parse_router(root)
        if any(r["project"] == project for r in rows):
            existed.append("engineering-board/BOARD-ROUTER.md (row present)")
        else:
            with open(rp, "a", encoding="utf-8") as f:
                f.write("| %s | engineering-board/%s | %s |\n" % (project, project, affects_prefix))
            created.append("engineering-board/BOARD-ROUTER.md (added row)")

    bd = os.path.join(eb_dir, project)
    os.makedirs(bd, exist_ok=True)

    # Subdirs + .gitkeep
    for sub in SUBDIRS:
        sd = os.path.join(bd, sub)
        os.makedirs(sd, exist_ok=True)
        gk = os.path.join(sd, ".gitkeep")
        if not os.path.isfile(gk):
            with open(gk, "w", encoding="utf-8") as f:
                f.write("")
            created.append("engineering-board/%s/%s/.gitkeep" % (project, sub))

    # BOARD.md
    bp = os.path.join(bd, "BOARD.md")
    if not os.path.isfile(bp):
        with open(bp, "w", encoding="utf-8") as f:
            f.write(BOARD_SKELETON.format(project=project))
        created.append("engineering-board/%s/BOARD.md" % project)
    else:
        existed.append("engineering-board/%s/BOARD.md" % project)

    # ARCHIVE.md
    ap = os.path.join(bd, "ARCHIVE.md")
    if not os.path.isfile(ap):
        with open(ap, "w", encoding="utf-8") as f:
            f.write(ARCHIVE_SKELETON.format(project=project))
        created.append("engineering-board/%s/ARCHIVE.md" % project)
    else:
        existed.append("engineering-board/%s/ARCHIVE.md" % project)

    return {
        "project": project,
        "board_dir": os.path.relpath(bd, root),
        "affects_prefix": affects_prefix,
        "created": created,
        "existed": existed,
    }


# ---------------------------------------------------------------------------
# board_list_projects
# ---------------------------------------------------------------------------
def tool_board_list_projects(params):
    root = resolve_root(params)
    rows = parse_router(root)
    projects = [{
        "id": r["project"],
        "path": r["path"],
        "affects_prefix": r["affects"],
    } for r in rows]
    return {"router": os.path.relpath(router_path(root), root) if router_path(root) else None,
            "projects": projects}


# ---------------------------------------------------------------------------
# board_create_entry
# ---------------------------------------------------------------------------
def _body_from_done_when(done_when, body):
    """Build a `## Done when` section from a list or an explicit body string."""
    parts = ["## Done when", ""]
    if done_when:
        if isinstance(done_when, str):
            done_when = [done_when]
        for item in done_when:
            parts.append("- [ ] %s" % item)
    elif body:
        parts.append(body.rstrip())
    else:
        parts.append("- [ ] (define verification criteria)")
    return "\n".join(parts)


def tool_board_create_entry(params):
    project = require(params, "project")
    entry_type = require(params, "type")
    title = require(params, "title")
    if entry_type not in TYPE_PREFIX:
        raise ToolError("invalid type %r (allowed: %s)" % (entry_type, ", ".join(TYPE_PREFIX)))
    root = resolve_root(params)
    bd = ensure_board_exists(root, project)

    eid = next_id(bd, entry_type)
    discovered = params.get("discovered") or today_utc()
    slug = slugify(title)
    filename = "%s-%s.md" % (eid, slug)
    sub = TYPE_SUBDIR[entry_type]
    path = os.path.join(bd, sub, filename)

    fields = [("id", eid), ("type", entry_type), ("title", title),
              ("discovered", discovered)]
    body = ""

    if entry_type in ("bug", "feature"):
        status = params.get("status", "open")
        if status not in VALID_STATUS:
            raise ToolError("invalid status %r" % status)
        priority = require(params, "priority")
        if priority not in VALID_PRIORITY:
            raise ToolError("invalid priority %r (allowed: %s)" % (priority, ", ".join(VALID_PRIORITY)))
        affects = require(params, "affects")
        needs = params.get("needs", "tdd")
        if needs is not None and needs not in VALID_NEEDS:
            raise ToolError("invalid needs %r (allowed: %s)" % (needs, ", ".join(VALID_NEEDS)))
        blocked_by = params.get("blocked_by")
        pattern = params.get("pattern")
        fields += [("status", status), ("priority", priority), ("affects", affects)]
        if needs:
            fields.append(("needs", needs))
        if blocked_by:
            fields.append(("blocked_by", blocked_by if isinstance(blocked_by, list) else [blocked_by]))
        if pattern:
            fields.append(("pattern", pattern if isinstance(pattern, list) else [pattern]))
        body = _body_from_done_when(params.get("done_when"), params.get("body"))

    elif entry_type == "question":
        status = params.get("status", "open")
        if status not in VALID_STATUS:
            raise ToolError("invalid status %r" % status)
        fields.append(("status", status))
        if params.get("source"):
            fields.append(("source", params.get("source")))
        if params.get("affects"):
            fields.append(("affects", params.get("affects")))
        if params.get("pattern"):
            p = params.get("pattern")
            fields.append(("pattern", p if isinstance(p, list) else [p]))
        body = _body_from_done_when(params.get("done_when"), params.get("body"))

    elif entry_type == "observation":
        if params.get("status"):
            if params["status"] not in VALID_STATUS:
                raise ToolError("invalid status %r" % params["status"])
            fields.append(("status", params["status"]))
        if params.get("pattern"):
            p = params.get("pattern")
            fields.append(("pattern", p if isinstance(p, list) else [p]))
        b = params.get("body") or "(observation details)"
        body = b.rstrip()

    elif entry_type == "learning":
        subtype = require(params, "subtype")
        if subtype not in ("pattern", "finding", "principle"):
            raise ToolError("invalid subtype %r (allowed: pattern, finding, principle)" % subtype)
        confidence = require(params, "confidence")
        if confidence not in ("low", "medium", "high"):
            raise ToolError("invalid confidence %r (allowed: low, medium, high)" % confidence)
        recurrence = require(params, "recurrence")
        derived_from = require(params, "derived_from")
        if not isinstance(derived_from, list):
            derived_from = [derived_from]
        fields = [("id", eid), ("type", "learning"), ("subtype", subtype),
                  ("title", title), ("discovered", discovered),
                  ("confidence", confidence), ("recurrence", recurrence),
                  ("derived_from", derived_from)]
        if params.get("applies_to"):
            a = params.get("applies_to")
            fields.append(("applies_to", a if isinstance(a, list) else [a]))
        if params.get("pattern_tag"):
            fields.append(("pattern_tag", params.get("pattern_tag")))
        if params.get("status"):
            fields.append(("status", params.get("status")))
        takeaway = params.get("takeaway") or params.get("body") or "(durable lesson)"
        sources = params.get("sources")
        src_lines = []
        if sources:
            if isinstance(sources, str):
                sources = [sources]
            src_lines = ["- %s" % s for s in sources]
        else:
            src_lines = ["- %s" % s for s in derived_from]
        body = "## Takeaway\n\n%s\n\n## Sources\n\n%s" % (takeaway.rstrip(), "\n".join(src_lines))

    content = serialize_frontmatter(fields) + "\n\n" + body.rstrip() + "\n"

    if os.path.isfile(path):
        raise ToolError("entry file already exists: %s" % path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    # Rebuild the index so the new id appears in BOARD.md (validation requires it).
    rebuild_board(bd, project)

    return {
        "id": eid,
        "type": entry_type,
        "title": title,
        "file": os.path.relpath(path, root),
        "status": dict(fields).get("status", "(none)"),
    }


# ---------------------------------------------------------------------------
# board_list_entries
# ---------------------------------------------------------------------------
def _public_fm(entry):
    return {k: v for k, v in entry.items() if not k.startswith("_")}


def tool_board_list_entries(params):
    root = resolve_root(params)
    want_project = params.get("project")
    want_type = params.get("type")
    want_status = params.get("status")
    want_needs = params.get("needs")

    if want_project:
        targets = [(want_project, ensure_board_exists(root, want_project))]
    else:
        rows = parse_router(root)
        targets = [(r["project"], os.path.join(root, r["path"])) for r in rows]

    result = []
    for project, bd in targets:
        if not os.path.isdir(bd):
            continue
        for e in load_entries(bd):
            etype = e.get("type", "")
            if want_type and etype != want_type:
                continue
            if want_status and e.get("status") != want_status:
                continue
            if want_needs and e.get("needs") != want_needs:
                continue
            fm = _public_fm(e)
            fm["project"] = project
            fm["file"] = os.path.relpath(e["_path"], root)
            result.append(fm)
    return {"count": len(result), "entries": result}


# ---------------------------------------------------------------------------
# board_get_entry
# ---------------------------------------------------------------------------
def tool_board_get_entry(params):
    project = require(params, "project")
    entry_id = require(params, "entry_id")
    root = resolve_root(params)
    bd = ensure_board_exists(root, project)
    e = find_entry(bd, entry_id)
    if not e:
        raise ToolError("entry %r not found in project %r" % (entry_id, project))
    with open(e["_path"], "r", encoding="utf-8", errors="replace") as f:
        markdown = f.read()
    return {
        "id": entry_id,
        "project": project,
        "file": os.path.relpath(e["_path"], root),
        "frontmatter": _public_fm(e),
        "markdown": markdown,
    }


# ---------------------------------------------------------------------------
# board_update_entry
# ---------------------------------------------------------------------------
# Minimal legal status transitions (schema §"Status Transitions").
LEGAL_TRANSITIONS = {
    "open": {"in_progress", "blocked", "resolved"},
    "in_progress": {"resolved", "blocked", "open"},
    "blocked": {"open", "in_progress", "resolved"},
    "resolved": {"open"},
}


def tool_board_update_entry(params):
    project = require(params, "project")
    entry_id = require(params, "entry_id")
    root = resolve_root(params)
    bd = ensure_board_exists(root, project)
    e = find_entry(bd, entry_id)
    if not e:
        raise ToolError("entry %r not found in project %r" % (entry_id, project))

    with open(e["_path"], "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    fm, body = parse_frontmatter(text)

    # Preserve frontmatter field order; update in place, append new keys.
    order = []
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if ":" in line and line.strip():
                order.append(line.partition(":")[0].strip())

    changes = []

    new_status = params.get("status")
    if new_status is not None:
        if new_status not in VALID_STATUS:
            raise ToolError("invalid status %r" % new_status)
        cur = fm.get("status")
        if cur and cur != new_status and new_status not in LEGAL_TRANSITIONS.get(cur, set()):
            raise ToolError("illegal status transition %s -> %s" % (cur, new_status))
        fm["status"] = new_status
        changes.append("status=%s" % new_status)

    new_needs = params.get("needs")
    if new_needs is not None:
        if new_needs not in VALID_NEEDS:
            raise ToolError("invalid needs %r (allowed: %s)" % (new_needs, ", ".join(VALID_NEEDS)))
        fm["needs"] = new_needs
        changes.append("needs=%s" % new_needs)

    new_priority = params.get("priority")
    if new_priority is not None:
        if new_priority not in VALID_PRIORITY:
            raise ToolError("invalid priority %r" % new_priority)
        fm["priority"] = new_priority
        changes.append("priority=%s" % new_priority)

    new_blocked = params.get("blocked_by")
    if new_blocked is not None:
        fm["blocked_by"] = new_blocked if isinstance(new_blocked, list) else [new_blocked]
        changes.append("blocked_by=%s" % fmt_list(fm["blocked_by"]))

    # Rebuild frontmatter preserving order then appending any new keys.
    field_pairs = []
    seen = set()
    for k in order:
        if k in fm:
            field_pairs.append((k, fm[k]))
            seen.add(k)
    for k, v in fm.items():
        if k not in seen:
            field_pairs.append((k, v))

    append_section = params.get("append_section")
    if append_section:
        heading = append_section.get("heading") if isinstance(append_section, dict) else None
        section_body = append_section.get("body", "") if isinstance(append_section, dict) else str(append_section)
        if not heading:
            raise ToolError("append_section requires a 'heading'")
        if not heading.startswith("#"):
            heading = "## " + heading
        body = body.rstrip() + "\n\n" + heading + "\n\n" + section_body.rstrip() + "\n"
        changes.append("appended section %r" % heading)

    new_text = serialize_frontmatter(field_pairs) + "\n\n" + body.strip("\n") + "\n"
    with open(e["_path"], "w", encoding="utf-8") as f:
        f.write(new_text)

    rebuild_board(bd, project)

    return {
        "id": entry_id,
        "project": project,
        "file": os.path.relpath(e["_path"], root),
        "changes": changes,
    }


# ---------------------------------------------------------------------------
# board_rebuild — deterministic BOARD.md regeneration
# ---------------------------------------------------------------------------
def _priority_rank(p):
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    return order.get(p, 4)


def _open_line_bug_feature(e):
    eid = e.get("id", "")
    prio = e.get("priority", "")
    title = e.get("title", "")
    sub = e["_subdir"]
    fname = e["_filename"]
    line = "- %s %s | [%s](%s/%s)" % (eid, prio, title, sub, fname)
    blocked_by = e.get("blocked_by")
    if blocked_by:
        if isinstance(blocked_by, str):
            blocked_by = [blocked_by]
        line += " ⊘ " + ", ".join(blocked_by)
    status = e.get("status")
    if status == "in_progress":
        line += " (in_progress)"
    elif status == "blocked":
        line += " (blocked)"
    return line


def _open_line_simple(e):
    eid = e.get("id", "")
    title = e.get("title", "")
    sub = e["_subdir"]
    fname = e["_filename"]
    return "- %s | [%s](%s/%s)" % (eid, title, sub, fname)


def build_open_section(board_dir):
    """Return the sorted list of Open-section lines (may be empty)."""
    entries = load_entries(board_dir)
    bugs, feats, questions, observations, learnings = [], [], [], [], []
    for e in entries:
        etype = e.get("type", "")
        status = e.get("status")
        if etype in ("bug", "feature"):
            if status == "resolved":
                continue
            (bugs if etype == "bug" else feats).append(e)
        elif etype == "question":
            if status == "resolved":
                continue
            questions.append(e)
        elif etype == "observation":
            if status == "resolved":
                continue
            observations.append(e)
        elif etype == "learning":
            if status == "resolved":
                continue
            learnings.append(e)

    def by_prio_id(lst):
        return sorted(lst, key=lambda e: (_priority_rank(e.get("priority", "")), e.get("id", "")))

    def by_id(lst):
        return sorted(lst, key=lambda e: e.get("id", ""))

    lines = []
    for e in by_prio_id(bugs):
        lines.append(_open_line_bug_feature(e))
    for e in by_prio_id(feats):
        lines.append(_open_line_bug_feature(e))
    for e in by_id(questions):
        lines.append(_open_line_simple(e))
    for e in by_id(observations):
        lines.append(_open_line_simple(e))
    for e in by_id(learnings):
        lines.append(_open_line_simple(e))
    return lines


def rebuild_board(board_dir, project):
    """Regenerate BOARD.md deterministically from entry files. Returns line count."""
    lines = build_open_section(board_dir)
    open_block = "\n".join(lines) if lines else "(none)"
    content = (
        "# %s — Board\n\n"
        "Live index of open items. Resolved items move to ARCHIVE.md.\n\n"
        "## Open\n\n"
        "%s\n\n"
        "## Conventions\n\n"
        "- Bug/Feature lines: `- B### P# | [title](bugs/filename.md)` (append `⊘ Q###` when blocked)\n"
        "- Question lines: `- Q### | [title](questions/filename.md)`\n"
        "- Observation lines: `- O### | [title](observations/filename.md)`\n"
        "- Learning lines: `- L### | [title](learnings/filename.md)` (v0.3.0)\n"
        "- Order within each section: P0 → P1 → P2 → P3 → unranked\n"
    ) % (project, open_block)
    bp = os.path.join(board_dir, "BOARD.md")
    with open(bp, "w", encoding="utf-8") as f:
        f.write(content)
    return len(lines)


def tool_board_rebuild(params):
    root = resolve_root(params)
    want_project = params.get("project")
    if want_project:
        targets = [(want_project, ensure_board_exists(root, want_project))]
    else:
        rows = parse_router(root)
        targets = [(r["project"], os.path.join(root, r["path"])) for r in rows]
    results = []
    for project, bd in targets:
        if not os.path.isdir(bd):
            continue
        n = rebuild_board(bd, project)
        results.append({"project": project, "open_lines": n,
                        "board_md": os.path.relpath(os.path.join(bd, "BOARD.md"), root)})
    return {"rebuilt": results}


# ---------------------------------------------------------------------------
# board_capture_finding — append to scratch inbox
# ---------------------------------------------------------------------------
def scratch_file_path(board_dir):
    return os.path.join(board_dir, "_sessions", "mcp-%s.md" % today_utc())


def tool_board_capture_finding(params):
    project = require(params, "project")
    kind = require(params, "kind")
    title = require(params, "title")
    root = resolve_root(params)
    bd = ensure_board_exists(root, project)

    evidence = params.get("evidence")
    affects = params.get("affects")
    ts = now_utc_iso()

    sp = scratch_file_path(bd)
    os.makedirs(os.path.dirname(sp), exist_ok=True)
    is_new = not os.path.isfile(sp)

    block = ["## %s — %s: %s" % (ts, kind, title), ""]
    block.append("- kind: %s" % kind)
    if affects:
        block.append("- affects: %s" % affects)
    if evidence:
        block += ["", evidence.rstrip()]
    block.append("")
    text = "\n".join(block) + "\n"

    with open(sp, "a", encoding="utf-8") as f:
        if is_new:
            f.write("# MCP scratch inbox — %s\n\n" % today_utc())
            f.write("Un-promoted findings captured via the MCP server. "
                    "Promote to entries with board_create_entry.\n\n")
        f.write(text)

    return {
        "project": project,
        "scratch_file": os.path.relpath(sp, root),
        "kind": kind,
        "title": title,
        "captured_at": ts,
    }


def count_scratch_findings(board_dir):
    """Count un-promoted scratch findings across _sessions/*.md.

    Counts `## ` finding headers written by board_capture_finding plus
    `<!-- ts -->` JSON blocks written by the plugin's board-scratch-append.sh.
    """
    sess = os.path.join(board_dir, "_sessions")
    if not os.path.isdir(sess):
        return 0
    total = 0
    for fname in sorted(os.listdir(sess)):
        if not fname.endswith(".md"):
            continue
        try:
            with open(os.path.join(sess, fname), "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if line.startswith("## "):
                        total += 1
                    elif line.startswith("<!-- ") and line.rstrip().endswith("-->"):
                        total += 1
        except OSError:
            continue
    return total


# ---------------------------------------------------------------------------
# board_claim / board_release — shell out to the existing scripts
# ---------------------------------------------------------------------------
CLAIM_ACQUIRE = os.path.join(PLUGIN_ROOT, "hooks", "scripts", "board-claim-acquire.sh")
CLAIM_RELEASE = os.path.join(PLUGIN_ROOT, "hooks", "scripts", "board-claim-release.sh")

ACQUIRE_MEANING = {0: "acquired", 1: "contended", 2: "stale"}
RELEASE_MEANING = {0: "released", 3: "owner_mismatch_or_missing", 4: "retries_exhausted"}


def tool_board_claim(params):
    project = require(params, "project")
    entry_id = require(params, "entry_id")
    session_id = require(params, "session_id")
    root = resolve_root(params)
    bd = ensure_board_exists(root, project)
    if not os.path.isfile(CLAIM_ACQUIRE):
        raise ToolError("claim script not found: %s" % CLAIM_ACQUIRE)
    proc = subprocess.run(
        ["bash", CLAIM_ACQUIRE, bd, entry_id, session_id],
        capture_output=True, text=True)
    rc = proc.returncode
    return {
        "action": "claim",
        "entry_id": entry_id,
        "exit_code": rc,
        "result": ACQUIRE_MEANING.get(rc, "error"),
        "acquired": rc == 0,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def tool_board_release(params):
    project = require(params, "project")
    entry_id = require(params, "entry_id")
    session_id = require(params, "session_id")
    root = resolve_root(params)
    bd = ensure_board_exists(root, project)
    if not os.path.isfile(CLAIM_RELEASE):
        raise ToolError("release script not found: %s" % CLAIM_RELEASE)
    proc = subprocess.run(
        ["bash", CLAIM_RELEASE, bd, entry_id, session_id],
        capture_output=True, text=True)
    rc = proc.returncode
    return {
        "action": "release",
        "entry_id": entry_id,
        "exit_code": rc,
        "result": RELEASE_MEANING.get(rc, "error"),
        "released": rc == 0,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


# ---------------------------------------------------------------------------
# board_status
# ---------------------------------------------------------------------------
def status_for_board(project, board_dir):
    entries = load_entries(board_dir)
    open_counts = {"bug": 0, "feature": 0, "question": 0, "observation": 0, "learning": 0}
    in_progress = []
    blocked = []
    for e in entries:
        etype = e.get("type", "")
        status = e.get("status")
        if etype not in open_counts:
            continue
        if status == "resolved":
            continue
        if status not in ("resolved",):
            open_counts[etype] += 1
        if status == "in_progress":
            in_progress.append(e.get("id", ""))
        elif status == "blocked":
            blocked.append(e.get("id", ""))
    return {
        "project": project,
        "open_counts": open_counts,
        "in_progress": sorted(in_progress),
        "blocked": sorted(blocked),
        "unpromoted_scratch": count_scratch_findings(board_dir),
    }


def tool_board_status(params):
    root = resolve_root(params)
    want_project = params.get("project")
    if want_project:
        targets = [(want_project, ensure_board_exists(root, want_project))]
    else:
        rows = parse_router(root)
        targets = [(r["project"], os.path.join(root, r["path"])) for r in rows]
    boards = []
    for project, bd in targets:
        if not os.path.isdir(bd):
            continue
        boards.append(status_for_board(project, bd))
    return {"boards": boards}


# ---------------------------------------------------------------------------
# Tool registry + JSON schemas
# ---------------------------------------------------------------------------
_ROOT_PROP = {"type": "string",
              "description": "Repo root that contains the board. Defaults to $CLAUDE_PROJECT_DIR or the current working directory."}

TOOLS = [
    {
        "name": "board_init",
        "description": "Scaffold a project board: create engineering-board/BOARD-ROUTER.md (or append a row), the project board dir, BOARD.md, ARCHIVE.md, and the five entry-type subdirs with .gitkeep. Idempotent — never clobbers an existing file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project name (kebab-case), e.g. 'navigator'."},
                "affects_prefix": {"type": "string", "description": "affects: prefix routed to this board. Defaults to '<project>/'."},
                "root": _ROOT_PROP,
            },
            "required": ["project"],
        },
        "handler": tool_board_init,
    },
    {
        "name": "board_list_projects",
        "description": "List projects registered in engineering-board/BOARD-ROUTER.md with their board path and affects prefix.",
        "inputSchema": {
            "type": "object",
            "properties": {"root": _ROOT_PROP},
        },
        "handler": tool_board_list_projects,
    },
    {
        "name": "board_create_entry",
        "description": "Create a valid board entry file with correct frontmatter and required body sections, allocating the next zero-padded id for its type, then rebuild BOARD.md. Produces a file that passes board-validate-entry.sh.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Target project (must already be board_init'd)."},
                "type": {"type": "string", "enum": ["bug", "feature", "question", "observation", "learning"],
                         "description": "Entry type. Determines the id prefix (B/F/Q/O/L) and required fields."},
                "title": {"type": "string", "description": "Short title. Present-tense for bug/feature; interrogative for question; one-line takeaway for learning."},
                "priority": {"type": "string", "enum": VALID_PRIORITY, "description": "Required for bug/feature. P0=production down/data loss … P3=cosmetic."},
                "affects": {"type": "string", "description": "Relative file path the fix/answer lands in. Required for bug/feature; optional for question."},
                "needs": {"type": "string", "enum": VALID_NEEDS, "description": "Workflow state for bug/feature. Defaults to 'tdd' on intake."},
                "status": {"type": "string", "enum": VALID_STATUS, "description": "Initial status. Defaults to 'open' for bug/feature/question."},
                "blocked_by": {"type": "array", "items": {"type": "string"}, "description": "Question ids (e.g. ['Q001']) blocking a bug/feature."},
                "pattern": {"type": "array", "items": {"type": "string"}, "description": "Root-cause pattern tags (kebab-case)."},
                "done_when": {"type": "array", "items": {"type": "string"}, "description": "Verification criteria — become the required '## Done when' checklist for bug/feature/question."},
                "source": {"type": "string", "description": "Question only: what surfaced this question."},
                "subtype": {"type": "string", "enum": ["pattern", "finding", "principle"], "description": "Learning only. Required."},
                "confidence": {"type": "string", "enum": ["low", "medium", "high"], "description": "Learning only. Required."},
                "recurrence": {"type": "integer", "description": "Learning only. Number of resolved entries this is derived from. Required."},
                "derived_from": {"type": "array", "items": {"type": "string"}, "description": "Learning only. Resolved entry ids that surfaced this pattern. Required."},
                "takeaway": {"type": "string", "description": "Learning only: the durable lesson (becomes '## Takeaway')."},
                "sources": {"type": "array", "items": {"type": "string"}, "description": "Learning only: source lines for '## Sources' (defaults to derived_from)."},
                "applies_to": {"type": "array", "items": {"type": "string"}, "description": "Learning only: paths/components where this applies."},
                "pattern_tag": {"type": "string", "description": "Learning only: original pattern: tag retained for cross-reference."},
                "body": {"type": "string", "description": "Free-form body (used as the section content when done_when/takeaway are not given)."},
                "discovered": {"type": "string", "description": "Discovery date YYYY-MM-DD. Defaults to today (UTC)."},
                "root": _ROOT_PROP,
            },
            "required": ["project", "type", "title"],
        },
        "handler": tool_board_create_entry,
    },
    {
        "name": "board_list_entries",
        "description": "List board entries with parsed frontmatter. Filters: project, type, status, needs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Restrict to one project (default: all projects in the router)."},
                "type": {"type": "string", "enum": ["bug", "feature", "question", "observation", "learning"]},
                "status": {"type": "string", "enum": VALID_STATUS},
                "needs": {"type": "string", "enum": VALID_NEEDS},
                "root": _ROOT_PROP,
            },
        },
        "handler": tool_board_list_entries,
    },
    {
        "name": "board_get_entry",
        "description": "Return the full markdown of one entry by id, plus its parsed frontmatter.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string"},
                "entry_id": {"type": "string", "description": "Entry id, e.g. B001, Q003."},
                "root": _ROOT_PROP,
            },
            "required": ["project", "entry_id"],
        },
        "handler": tool_board_get_entry,
    },
    {
        "name": "board_update_entry",
        "description": "Update frontmatter fields (status, needs, priority, blocked_by) and/or append a body section to an entry, then rebuild BOARD.md. Validates status transitions minimally.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string"},
                "entry_id": {"type": "string"},
                "status": {"type": "string", "enum": VALID_STATUS},
                "needs": {"type": "string", "enum": VALID_NEEDS},
                "priority": {"type": "string", "enum": VALID_PRIORITY},
                "blocked_by": {"type": "array", "items": {"type": "string"}},
                "append_section": {
                    "type": "object",
                    "description": "Append a markdown section to the body.",
                    "properties": {
                        "heading": {"type": "string", "description": "Section heading (## added if absent)."},
                        "body": {"type": "string", "description": "Section body markdown."},
                    },
                    "required": ["heading"],
                },
                "root": _ROOT_PROP,
            },
            "required": ["project", "entry_id"],
        },
        "handler": tool_board_update_entry,
    },
    {
        "name": "board_rebuild",
        "description": "Deterministically regenerate BOARD.md from entry files for a project (or all projects). Open section: bugs/features P0→P3 then features, questions/observations/learnings by id; resolved omitted; ⊘ Q### when blocked.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Project to rebuild (default: all projects in the router)."},
                "root": _ROOT_PROP,
            },
        },
        "handler": tool_board_rebuild,
    },
    {
        "name": "board_capture_finding",
        "description": "Append a finding to the scratch inbox _sessions/mcp-<UTC-date>.md for a project (creating the dir if missing). For quick capture before promotion to a real entry.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string"},
                "kind": {"type": "string", "description": "Finding kind, e.g. bug, feature, question, observation."},
                "title": {"type": "string", "description": "One-line finding summary."},
                "evidence": {"type": "string", "description": "Optional supporting evidence / quote."},
                "affects": {"type": "string", "description": "Optional relative path the finding concerns."},
                "root": _ROOT_PROP,
            },
            "required": ["project", "kind", "title"],
        },
        "handler": tool_board_capture_finding,
    },
    {
        "name": "board_claim",
        "description": "Acquire the claim lock on an entry by shelling out to board-claim-acquire.sh. Returns exit_code 0=acquired, 1=contended, 2=stale.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string"},
                "entry_id": {"type": "string"},
                "session_id": {"type": "string", "description": "Caller's session id (claim owner)."},
                "root": _ROOT_PROP,
            },
            "required": ["project", "entry_id", "session_id"],
        },
        "handler": tool_board_claim,
    },
    {
        "name": "board_release",
        "description": "Release the claim lock on an entry by shelling out to board-claim-release.sh. Only the owning session may release. Returns exit_code 0=released, 3=owner mismatch/missing, 4=retries exhausted.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string"},
                "entry_id": {"type": "string"},
                "session_id": {"type": "string"},
                "root": _ROOT_PROP,
            },
            "required": ["project", "entry_id", "session_id"],
        },
        "handler": tool_board_release,
    },
    {
        "name": "board_status",
        "description": "Board overview: per-type open counts, in_progress ids, blocked ids, and un-promoted scratch count. Optionally scoped to one project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "Restrict to one project (default: all)."},
                "root": _ROOT_PROP,
            },
        },
        "handler": tool_board_status,
    },
]

TOOLS_BY_NAME = {t["name"]: t for t in TOOLS}


def public_tools():
    """Tool list for tools/list (without the internal 'handler' key)."""
    return [{"name": t["name"], "description": t["description"], "inputSchema": t["inputSchema"]} for t in TOOLS]


# ---------------------------------------------------------------------------
# JSON-RPC plumbing
# ---------------------------------------------------------------------------
class RpcError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def call_tool(name, arguments):
    """Run a tool by name. Returns the tools/call result dict."""
    tool = TOOLS_BY_NAME.get(name)
    if not tool:
        raise RpcError(-32602, "unknown tool: %s" % name)
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        raise RpcError(-32602, "tool arguments must be an object")
    try:
        result = tool["handler"](arguments)
        text = json.dumps(result, ensure_ascii=False, indent=2)
        return {"content": [{"type": "text", "text": text}], "isError": False}
    except ToolError as e:
        return {"content": [{"type": "text", "text": "Error: %s" % e}], "isError": True}
    except Exception as e:  # pragma: no cover - defensive
        return {"content": [{"type": "text", "text": "Internal error: %s: %s" % (type(e).__name__, e)}],
                "isError": True}


def dispatch(method, params):
    """Dispatch a JSON-RPC method to its result payload. Raises RpcError on
    protocol-level failures (unknown method, bad params)."""
    if params is None:
        params = {}
    if method == "initialize":
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "instructions": "Maintains the engineering-board markdown board: init projects, "
                            "create/list/update/get entries, rebuild the index, capture scratch "
                            "findings, and claim/release entry locks.",
        }
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": public_tools()}
    if method == "tools/call":
        name = params.get("name")
        if not name:
            raise RpcError(-32602, "tools/call requires 'name'")
        return call_tool(name, params.get("arguments"))
    raise RpcError(-32601, "method not found: %s" % method)


def handle_message(obj):
    """Handle one parsed JSON-RPC message object. Returns a response dict, or
    None for notifications (no reply)."""
    if not isinstance(obj, dict):
        return {"jsonrpc": "2.0", "id": None,
                "error": {"code": -32600, "message": "invalid request: not an object"}}

    method = obj.get("method")
    msg_id = obj.get("id")
    is_notification = "id" not in obj

    # Notifications (no id) get no response.
    if is_notification:
        # notifications/initialized and any other notification: no reply.
        return None

    if not method:
        return {"jsonrpc": "2.0", "id": msg_id,
                "error": {"code": -32600, "message": "invalid request: missing method"}}

    try:
        result = dispatch(method, obj.get("params"))
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}
    except RpcError as e:
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": e.code, "message": e.message}}
    except Exception as e:  # pragma: no cover - defensive
        return {"jsonrpc": "2.0", "id": msg_id,
                "error": {"code": -32603, "message": "internal error: %s: %s" % (type(e).__name__, e)}}


def serve_stdio(stdin=None, stdout=None):
    """Run the newline-delimited JSON-RPC stdio loop."""
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            resp = {"jsonrpc": "2.0", "id": None,
                    "error": {"code": -32700, "message": "parse error"}}
            stdout.write(json.dumps(resp) + "\n")
            stdout.flush()
            continue
        resp = handle_message(obj)
        if resp is not None:
            stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            stdout.flush()


if __name__ == "__main__":
    try:
        serve_stdio()
    except (BrokenPipeError, KeyboardInterrupt):
        pass

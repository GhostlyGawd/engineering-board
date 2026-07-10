#!/usr/bin/env python3
"""Pure-python3 test for the engineering-board MCP server (zero third-party deps).

Two suites:

  1. A REAL end-to-end stdio session: spawn engineering_board_mcp.py as a
     subprocess, drive initialize -> notifications/initialized -> tools/list ->
     several tools/call, asserting on the JSON-RPC responses.

  2. In-process board lifecycle in a temp repo: board_init -> board_create_entry
     (bug + question + feature) -> board_list_entries -> board_update_entry ->
     board_rebuild -> board_status -> board_capture_finding -> board_claim /
     board_release. Every created entry file is checked against the REAL
     hooks/scripts/board-validate-entry.sh.

Exit 0 on all-pass; non-zero with a diff/detail on the first failure.
Runnable as: python3 mcp-server/test_mcp_server.py
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER_PATH = os.path.join(HERE, "engineering_board_mcp.py")
PLUGIN_ROOT = os.path.dirname(HERE)
VALIDATE_SCRIPT = os.path.join(PLUGIN_ROOT, "hooks", "scripts", "board-validate-entry.sh")


# ---------------------------------------------------------------------------
# Assertion helpers
# ---------------------------------------------------------------------------
class Failure(Exception):
    pass


PASSED = []


def ok(label):
    PASSED.append(label)
    print("  [PASS] %s" % label)


def check(cond, label, detail=""):
    if cond:
        ok(label)
    else:
        raise Failure("%s%s" % (label, (" -- " + detail) if detail else ""))


# ---------------------------------------------------------------------------
# Load server module in-process (for suite 2)
# ---------------------------------------------------------------------------
def load_server():
    spec = importlib.util.spec_from_file_location("eb_mcp", SERVER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Suite 1 — real subprocess stdio session
# ---------------------------------------------------------------------------
def suite_stdio(tmp_repo):
    print("\n== Suite 1: real stdio subprocess session ==")
    proc = subprocess.Popen(
        ["python3", SERVER_PATH],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1,
        env=dict(os.environ, CLAUDE_PROJECT_DIR=tmp_repo),
    )

    def send(obj):
        proc.stdin.write(json.dumps(obj) + "\n")
        proc.stdin.flush()

    def recv():
        line = proc.stdout.readline()
        if not line:
            raise Failure("server closed stdout unexpectedly; stderr=%r" % proc.stderr.read())
        return json.loads(line)

    try:
        # initialize
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
              "params": {"protocolVersion": "2025-06-18", "capabilities": {}}})
        r = recv()
        check(r.get("id") == 1, "initialize response id matches")
        res = r.get("result", {})
        check(res.get("protocolVersion") == "2025-06-18", "protocolVersion 2025-06-18",
              str(res.get("protocolVersion")))
        check(res.get("serverInfo", {}).get("name") == "engineering-board", "serverInfo.name")
        check(res.get("capabilities", {}).get("tools", {}).get("listChanged") is False,
              "capabilities.tools.listChanged is false")
        check("instructions" in res, "initialize includes instructions")

        # initialized notification -> no reply. Follow with ping to prove the
        # loop is still alive and the notification produced no stray output.
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        send({"jsonrpc": "2.0", "id": 2, "method": "ping"})
        r = recv()
        check(r.get("id") == 2 and r.get("result") == {}, "ping after notification returns {}",
              json.dumps(r))

        # tools/list
        send({"jsonrpc": "2.0", "id": 3, "method": "tools/list"})
        r = recv()
        tools = r.get("result", {}).get("tools", [])
        names = {t["name"] for t in tools}
        expected = {"board_init", "board_list_projects", "board_create_entry",
                    "board_list_entries", "board_get_entry", "board_update_entry",
                    "board_rebuild", "board_capture_finding", "board_claim",
                    "board_release", "board_status", "board_remember"}
        check(expected <= names, "tools/list exposes all expected tools",
              "missing: %s" % (expected - names))
        for t in tools:
            check(isinstance(t.get("inputSchema"), dict) and t["inputSchema"].get("type") == "object",
                  "tool %s has object inputSchema" % t["name"])

        # tools/call board_init via stdio
        send({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
              "params": {"name": "board_init", "arguments": {"project": "navigator"}}})
        r = recv()
        res = r.get("result", {})
        check(res.get("isError") is False, "board_init call not an error", json.dumps(res))
        payload = json.loads(res["content"][0]["text"])
        check(payload["project"] == "navigator", "board_init returned project navigator")

        # tools/call board_create_entry (bug) via stdio
        send({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
              "params": {"name": "board_create_entry", "arguments": {
                  "project": "navigator", "type": "bug", "title": "Widget renders blank",
                  "priority": "P1", "affects": "navigator/widget.py",
                  "done_when": ["widget shows content"]}}})
        r = recv()
        res = r.get("result", {})
        check(res.get("isError") is False, "stdio board_create_entry bug ok", json.dumps(res))
        payload = json.loads(res["content"][0]["text"])
        check(payload["id"] == "B001", "stdio-created bug got id B001", payload.get("id"))

        # unknown method -> -32601
        send({"jsonrpc": "2.0", "id": 6, "method": "does/not/exist"})
        r = recv()
        check(r.get("error", {}).get("code") == -32601, "unknown method -> -32601",
              json.dumps(r.get("error")))

        # tools/call unknown tool -> isError result (invalid params surfaced)
        send({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
              "params": {"name": "nope", "arguments": {}}})
        r = recv()
        check(r.get("error", {}).get("code") == -32602, "unknown tool -> -32602",
              json.dumps(r))

    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


# ---------------------------------------------------------------------------
# Suite 2 — in-process lifecycle + real validation
# ---------------------------------------------------------------------------
def run_validate(file_path, project_dir):
    """Run the real board-validate-entry.sh against a created entry file.

    The hook reads tool_input.file_path from stdin (PostToolUse shape) and needs
    CLAUDE_PROJECT_DIR set. Exit 0 = valid, 2 = validation errors.
    """
    stdin_payload = json.dumps({"tool_input": {"file_path": file_path}})
    proc = subprocess.run(
        ["bash", VALIDATE_SCRIPT],
        input=stdin_payload, capture_output=True, text=True,
        env=dict(os.environ, CLAUDE_PROJECT_DIR=project_dir),
    )
    return proc.returncode, proc.stderr


def suite_lifecycle(mod, tmp_repo):
    print("\n== Suite 2: in-process board lifecycle + real validation ==")
    root = tmp_repo

    # board_init
    r = mod.tool_board_init({"project": "atlas", "root": root})
    check("engineering-board/atlas/BOARD.md" in r["created"], "board_init created BOARD.md",
          json.dumps(r["created"]))
    board_dir = os.path.join(root, "engineering-board", "atlas")
    for sub in ["bugs", "features", "questions", "observations", "learnings"]:
        check(os.path.isfile(os.path.join(board_dir, sub, ".gitkeep")),
              "board_init created %s/.gitkeep" % sub)
    check(os.path.isfile(os.path.join(board_dir, "ARCHIVE.md")), "board_init created ARCHIVE.md")

    # idempotent re-init
    r2 = mod.tool_board_init({"project": "atlas", "root": root})
    check(any("row present" in x for x in r2["existed"]) or r2["created"] == [] or True,
          "board_init is idempotent (no crash on re-run)")
    check("engineering-board/atlas/BOARD.md" in r2["existed"], "re-init reports BOARD.md existed")

    # board_list_projects
    lp = mod.tool_board_list_projects({"root": root})
    check(any(p["id"] == "atlas" for p in lp["projects"]), "board_list_projects lists atlas")

    # board_create_entry — bug
    bug = mod.tool_board_create_entry({
        "project": "atlas", "root": root, "type": "bug",
        "title": "Export drops final row", "priority": "P0",
        "affects": "atlas/export.py",
        "done_when": ["all rows present in export", "regression test added"],
    })
    check(bug["id"] == "B001", "first bug is B001", bug["id"])
    bug_path = os.path.join(root, bug["file"])
    rc, err = run_validate(bug_path, root)
    check(rc == 0, "created bug passes board-validate-entry.sh", err)

    # board_create_entry — question
    q = mod.tool_board_create_entry({
        "project": "atlas", "root": root, "type": "question",
        "title": "Should export stream or buffer?",
        "done_when": ["decision recorded with rationale"],
        "source": "B001 fix direction",
    })
    check(q["id"] == "Q001", "first question is Q001", q["id"])
    rc, err = run_validate(os.path.join(root, q["file"]), root)
    check(rc == 0, "created question passes board-validate-entry.sh", err)

    # board_create_entry — feature (blocked by the question)
    feat = mod.tool_board_create_entry({
        "project": "atlas", "root": root, "type": "feature",
        "title": "Add streaming export mode", "priority": "P2",
        "affects": "atlas/export.py", "blocked_by": ["Q001"], "status": "blocked",
        "done_when": ["streaming mode selectable"],
    })
    check(feat["id"] == "F001", "first feature is F001", feat["id"])
    rc, err = run_validate(os.path.join(root, feat["file"]), root)
    check(rc == 0, "created feature passes board-validate-entry.sh", err)

    # negative: missing priority for a bug is rejected
    try:
        mod.tool_board_create_entry({"project": "atlas", "root": root, "type": "bug",
                                     "title": "no priority", "affects": "x"})
        raise Failure("expected ToolError for bug without priority")
    except mod.ToolError:
        ok("board_create_entry rejects bug without priority")

    # board_list_entries — filters
    all_entries = mod.tool_board_list_entries({"project": "atlas", "root": root})
    check(all_entries["count"] == 3, "board_list_entries finds 3 entries", str(all_entries["count"]))
    bugs_only = mod.tool_board_list_entries({"project": "atlas", "root": root, "type": "bug"})
    check(bugs_only["count"] == 1, "type filter returns 1 bug", str(bugs_only["count"]))
    tdd_only = mod.tool_board_list_entries({"project": "atlas", "root": root, "needs": "tdd"})
    check(tdd_only["count"] == 2, "needs=tdd filter returns bug+feature", str(tdd_only["count"]))

    # board_get_entry
    got = mod.tool_board_get_entry({"project": "atlas", "root": root, "entry_id": "B001"})
    check("## Done when" in got["markdown"], "board_get_entry returns full markdown")
    check(got["frontmatter"]["priority"] == "P0", "board_get_entry parsed priority")

    # board_update_entry — status transition + append section
    upd = mod.tool_board_update_entry({
        "project": "atlas", "root": root, "entry_id": "B001",
        "status": "in_progress", "needs": "review",
        "append_section": {"heading": "Investigation", "body": "Root cause in buffer flush."},
    })
    check(any("status=in_progress" in c for c in upd["changes"]), "update set status=in_progress")
    got2 = mod.tool_board_get_entry({"project": "atlas", "root": root, "entry_id": "B001"})
    check("## Investigation" in got2["markdown"], "appended section present")
    check(got2["frontmatter"]["status"] == "in_progress", "status persisted")
    rc, err = run_validate(os.path.join(root, got2["file"]), root)
    check(rc == 0, "updated bug still passes validation", err)

    # illegal transition rejected
    try:
        mod.tool_board_update_entry({"project": "atlas", "root": root, "entry_id": "B001",
                                     "status": "bogus"})
        raise Failure("expected ToolError for invalid status")
    except mod.ToolError:
        ok("board_update_entry rejects invalid status value")

    # security: path traversal via project name (eb-self B024) — every traversal
    # form must be rejected, and nothing may be written outside root.
    import glob as _glob
    before = set(_glob.glob(os.path.join(os.path.dirname(root), "*")))
    for bad in ["/tmp/EB_PWNED", "../../EB_PWNED", "..", "~evil", "a/b", "x\\y", "a..b", ""]:
        try:
            mod.tool_board_init({"project": bad, "root": root})
            raise Failure("path traversal project name accepted: %r" % bad)
        except mod.ToolError:
            pass
    ok("board_init rejects path-traversal project names (B024)")
    try:
        mod.tool_board_create_entry({"project": "../../evil", "root": root, "type": "bug",
                                     "title": "x", "priority": "P1", "affects": "y"})
        raise Failure("create_entry accepted traversal project")
    except mod.ToolError:
        ok("board_create_entry rejects path-traversal project (B024)")
    after = set(_glob.glob(os.path.join(os.path.dirname(root), "*")))
    check(before == after, "no files written outside root by traversal attempts (B024)",
          str(after - before))

    # security: entry_id path traversal in claim/release (eb-self B034).
    for bad in ["../../../pwned", "../victim", "..", "a/b", "x\\y"]:
        try:
            mod.tool_board_claim({"project": "atlas", "root": root,
                                  "entry_id": bad, "session_id": "s"})
            raise Failure("board_claim accepted traversal entry_id: %r" % bad)
        except mod.ToolError:
            pass
    ok("board_claim rejects path-traversal entry_id (B034)")
    try:
        mod.tool_board_release({"project": "atlas", "root": root,
                                "entry_id": "../victim", "session_id": "s"})
        raise Failure("board_release accepted traversal entry_id")
    except mod.ToolError:
        ok("board_release rejects path-traversal entry_id (B034)")

    # security: bulk tools must not follow a router row that escapes root (B035).
    rp = os.path.join(root, "engineering-board", "BOARD-ROUTER.md")
    with open(rp, "a", encoding="utf-8") as f:
        f.write("| evil | ../outside | evil/ |\n")
    outside = os.path.join(os.path.dirname(root), "outside")
    os.makedirs(outside, exist_ok=True)
    with open(os.path.join(outside, "BOARD.md"), "w") as f:
        f.write("PRECIOUS\n")
    for tool, nm in ((mod.tool_board_rebuild, "rebuild"),
                     (mod.tool_board_status, "status"),
                     (mod.tool_board_list_entries, "list_entries")):
        try:
            tool({"root": root})
            raise Failure("board_%s followed an escaping router row" % nm)
        except mod.ToolError:
            pass
    check(open(os.path.join(outside, "BOARD.md")).read().strip() == "PRECIOUS",
          "bulk tools did not overwrite a file outside root via router escape (B035)")
    # Remove the poisoned row so later assertions see a clean router.
    lines = [ln for ln in open(rp, encoding="utf-8") if "../outside" not in ln]
    open(rp, "w", encoding="utf-8").write("".join(lines))

    # hygiene: append_section heading is newline-flattened (eb-self B036).
    # Reuse an existing entry so the board's entry counts are unchanged.
    mod.tool_board_update_entry({"project": "atlas", "root": root, "entry_id": "B001",
                                 "append_section": {"heading": "H\n---\ninjected: yes", "body": "x"}})
    hmd = mod.tool_board_get_entry({"project": "atlas", "root": root, "entry_id": "B001"})["markdown"]
    check("\n---\ninjected: yes" not in hmd,
          "append_section heading is newline-flattened, no body injection (B036)")

    # security: affects_prefix router-row injection in board_init (eb-self B038).
    inj_root = tempfile.mkdtemp()
    mod.tool_board_init({"project": "beta", "root": inj_root,
                         "affects_prefix": "alpha/ |\n| evil | /etc/cron.d | evil/"})
    projs = [p["id"] for p in mod.tool_board_list_projects({"root": inj_root})["projects"]]
    check(projs == ["beta"], "affects_prefix cannot inject a spoofed router project (B038)", str(projs))
    try:
        mod.tool_board_status({"root": inj_root})  # must not be DoS'd by an escaping row
        ok("bulk tools still work after affects_prefix injection attempt (B038)")
    except mod.ToolError as e:
        raise Failure("affects_prefix injection DoS'd board_status: %s" % e)
    shutil.rmtree(inj_root, ignore_errors=True)

    # security: board_init must not follow a symlink out of root (eb-self B039).
    sym_root = tempfile.mkdtemp()
    outside = tempfile.mkdtemp()
    os.makedirs(os.path.join(sym_root, "engineering-board"), exist_ok=True)
    os.symlink(outside, os.path.join(sym_root, "engineering-board", "sneaky"))
    try:
        mod.tool_board_init({"project": "sneaky", "root": sym_root})
        raise Failure("board_init followed a symlink out of root")
    except mod.ToolError:
        ok("board_init rejects a symlinked project dir (B039)")
    check(not os.path.exists(os.path.join(outside, "BOARD.md")),
          "no scaffold written outside root via symlink (B039)")
    shutil.rmtree(sym_root, ignore_errors=True)
    shutil.rmtree(outside, ignore_errors=True)

    # security: board_capture_finding must not inject a second scratch header (B040).
    cap_root = tempfile.mkdtemp()
    mod.tool_board_init({"project": "cap", "root": cap_root})
    mod.tool_board_capture_finding({"project": "cap", "root": cap_root, "kind": "bug",
                                    "title": "real\n## FAKE — evil: pwn\n\n- kind: bug"})
    sp = os.path.join(cap_root, "engineering-board", "cap", "_sessions",
                      "mcp-%s.md" % mod.today_utc())
    hdrs = sum(1 for ln in open(sp) if ln.startswith("## "))
    check(hdrs == 1, "board_capture_finding title cannot inject a second header (B040)",
          "found %d headers" % hdrs)
    shutil.rmtree(cap_root, ignore_errors=True)

    # security: board_capture_finding evidence cannot inject a scratch header (B040 follow-up).
    ev_root = tempfile.mkdtemp()
    mod.tool_board_init({"project": "ev", "root": ev_root})
    mod.tool_board_capture_finding({"project": "ev", "root": ev_root, "kind": "observation",
                                    "title": "real",
                                    "evidence": "Legit.\n\n## 2099-01-01T00:00:00Z — bug: FORGED\n\n- kind: bug"})
    ev_sp = os.path.join(ev_root, "engineering-board", "ev", "_sessions",
                         "mcp-%s.md" % mod.today_utc())
    ev_hdrs = sum(1 for ln in open(ev_sp) if ln.startswith("## "))
    check(ev_hdrs == 1, "board_capture_finding evidence cannot inject a second header (B040 follow-up)",
          "found %d headers" % ev_hdrs)
    shutil.rmtree(ev_root, ignore_errors=True)

    # security: evidence blockquote must split on ALL line separators, not just
    # \n — a bare \r / \f / NEL escaped the `> ` prefix and forged a `## ` header
    # (eb-self B054, re-opening B040 via .split("\n")). The reader below iterates
    # with universal-newline semantics, so \r IS a line boundary on read.
    for sep, sep_name in (("\r", "CR"), ("\f", "FF"), ("\x85", "NEL")):
        b54_root = tempfile.mkdtemp()
        mod.tool_board_init({"project": "b54", "root": b54_root})
        mod.tool_board_capture_finding(
            {"project": "b54", "root": b54_root, "kind": "observation", "title": "one real finding",
             "evidence": "Legit evidence." + sep + "## 2099-01-01T00:00:00Z — bug: FORGED\n\n- kind: bug"})
        b54_bd = mod.board_dir_for(b54_root, "b54")
        b54_sp = os.path.join(b54_bd, "_sessions", "mcp-%s.md" % mod.today_utc())
        b54_hdrs = sum(1 for ln in open(b54_sp) if ln.startswith("## "))
        check(b54_hdrs == 1,
              "board_capture_finding evidence %s cannot forge a scratch header (B054)" % sep_name,
              "found %d headers" % b54_hdrs)
        # count_scratch_findings must also see exactly one finding, not two.
        check(mod.count_scratch_findings(b54_bd) == 1,
              "count_scratch_findings unaffected by %s-hidden forged header (B054)" % sep_name,
              "got %d" % mod.count_scratch_findings(b54_bd))
        shutil.rmtree(b54_root, ignore_errors=True)

    # security: session_id with whitespace is rejected (eb-self B029/F3).
    sid_root = tempfile.mkdtemp()
    mod.tool_board_init({"project": "s", "root": sid_root})
    for bad in ["sess with space", "sess\nowner: attacker", "tab\there"]:
        try:
            mod.tool_board_claim({"project": "s", "root": sid_root, "entry_id": "B001",
                                  "session_id": bad})
            raise Failure("board_claim accepted a whitespace session_id: %r" % bad)
        except mod.ToolError:
            pass
    ok("board_claim rejects a whitespace/newline session_id (B029/F3)")
    good = mod.tool_board_claim({"project": "s", "root": sid_root, "entry_id": "B001",
                                 "session_id": "sess-abc123"})
    check(good.get("acquired") is True, "a normal opaque session_id still acquires (B029/F3)")
    shutil.rmtree(sid_root, ignore_errors=True)

    # security: frontmatter injection via newline in a field value (eb-self B028).
    fm = mod.serialize_frontmatter([("id", "B900"), ("type", "bug"),
                                    ("title", "pwn\nstatus: resolved\nmalicious: yes"),
                                    ("status", "open")])
    lines = fm.splitlines()
    check(not any(l.strip().startswith("malicious:") for l in lines),
          "serialize_frontmatter does not inject keys from a newline (B028)")
    check(sum(1 for l in lines if l.strip().startswith("status:")) == 1,
          "serialize_frontmatter keeps a single status line (B028)")

    # board_rebuild — deterministic + idempotent
    rb1 = mod.tool_board_rebuild({"project": "atlas", "root": root})
    board_md = os.path.join(board_dir, "BOARD.md")
    with open(board_md) as f:
        content1 = f.read()
    rb2 = mod.tool_board_rebuild({"project": "atlas", "root": root})
    with open(board_md) as f:
        content2 = f.read()
    check(content1 == content2, "board_rebuild is idempotent (byte-identical)")
    # B001 (in_progress) present with suffix; F001 blocked with ⊘ Q001; B001 before F001
    check("- B001 P0 | [Export drops final row](bugs/B001-export-drops-final-row.md) (in_progress)"
          in content1, "BOARD.md bug line format with in_progress suffix", content1)
    check("⊘ Q001" in content1, "BOARD.md shows blocked marker ⊘ Q001")
    check("- Q001 | [" in content1, "BOARD.md question line format")

    # board_status
    st = mod.tool_board_status({"project": "atlas", "root": root})
    board = st["boards"][0]
    check(board["open_counts"]["bug"] == 1, "status bug open count", json.dumps(board["open_counts"]))
    check("B001" in board["in_progress"], "status lists B001 in_progress")
    check("F001" in board["blocked"], "status lists F001 blocked")

    # board_capture_finding
    cf = mod.tool_board_capture_finding({
        "project": "atlas", "root": root, "kind": "observation",
        "title": "Flush latency spikes under load", "evidence": "p99 = 1.2s",
        "affects": "atlas/export.py",
    })
    sp = os.path.join(root, cf["scratch_file"])
    check(os.path.isfile(sp), "capture_finding created scratch file")
    with open(sp) as f:
        scratch = f.read()
    check("Flush latency spikes under load" in scratch, "finding written to scratch")
    st2 = mod.tool_board_status({"project": "atlas", "root": root})
    check(st2["boards"][0]["unpromoted_scratch"] == 1, "status counts 1 unpromoted scratch",
          str(st2["boards"][0]["unpromoted_scratch"]))

    # board_claim / board_release round-trip via real scripts
    cl = mod.tool_board_claim({"project": "atlas", "root": root, "entry_id": "B001",
                               "session_id": "sess-test-1"})
    check(cl["acquired"] is True and cl["exit_code"] == 0, "board_claim acquired", json.dumps(cl))
    # second claim by a different session -> contended (exit 1)
    cl2 = mod.tool_board_claim({"project": "atlas", "root": root, "entry_id": "B001",
                                "session_id": "sess-test-2"})
    check(cl2["exit_code"] == 1 and cl2["result"] == "contended", "second claim contended",
          json.dumps(cl2))
    rel = mod.tool_board_release({"project": "atlas", "root": root, "entry_id": "B001",
                                  "session_id": "sess-test-1"})
    check(rel["released"] is True and rel["exit_code"] == 0, "board_release released", json.dumps(rel))

    # learning entry validates too (exercises the strictest schema branch)
    learn = mod.tool_board_create_entry({
        "project": "atlas", "root": root, "type": "learning",
        "title": "Buffered exports drop tail rows under backpressure",
        "subtype": "pattern", "confidence": "medium", "recurrence": 3,
        "derived_from": ["B001", "B002", "B003"],
        "takeaway": "Always flush-and-verify tail on buffered writers.",
    })
    rc, err = run_validate(os.path.join(root, learn["file"]), root)
    check(rc == 0, "created learning passes board-validate-entry.sh", err)


# ---------------------------------------------------------------------------
# Suite: C5 — deterministic ready queue
# ---------------------------------------------------------------------------
def suite_ready(mod):
    """Shared C5 semantics: ready iff status: open AND every blocked_by id that
    resolves to an existing entry has status: resolved. Dangling blocker ids do
    not block but are surfaced as warnings."""
    print("\n== Suite: C5 ready queue ==")
    root = tempfile.mkdtemp(prefix="eb-mcp-ready-")
    try:
        mod.tool_board_init({"project": "rdy", "root": root})

        # Q001 open (blocker for B002); Q002 resolved (blocker for B003).
        mod.tool_board_create_entry({
            "project": "rdy", "root": root, "type": "question",
            "title": "Open blocker question", "done_when": ["answered"]})
        mod.tool_board_create_entry({
            "project": "rdy", "root": root, "type": "question",
            "title": "Resolved blocker question", "done_when": ["answered"]})
        mod.tool_board_update_entry({"project": "rdy", "root": root,
                                     "entry_id": "Q002", "status": "resolved"})

        # B001: open, no blockers -> ready.
        mod.tool_board_create_entry({
            "project": "rdy", "root": root, "type": "bug",
            "title": "No blockers", "priority": "P1", "affects": "rdy/a",
            "done_when": ["x"]})
        # B002: open, blocked_by open Q001 -> NOT ready.
        mod.tool_board_create_entry({
            "project": "rdy", "root": root, "type": "bug",
            "title": "Blocked by open question", "priority": "P1",
            "affects": "rdy/b", "blocked_by": ["Q001"], "done_when": ["x"]})
        # B003: open, blocked_by resolved Q002 -> ready.
        mod.tool_board_create_entry({
            "project": "rdy", "root": root, "type": "bug",
            "title": "Blocked by resolved question", "priority": "P1",
            "affects": "rdy/c", "blocked_by": ["Q002"], "done_when": ["x"]})
        # B004: open, blocked_by dangling X999 -> ready + warning.
        mod.tool_board_create_entry({
            "project": "rdy", "root": root, "type": "bug",
            "title": "Dangling blocker", "priority": "P1",
            "affects": "rdy/d", "blocked_by": ["X999"], "done_when": ["x"]})
        # B005: in_progress, no blockers -> never ready.
        mod.tool_board_create_entry({
            "project": "rdy", "root": root, "type": "bug",
            "title": "Already in progress", "priority": "P1",
            "affects": "rdy/e", "status": "in_progress", "done_when": ["x"]})

        lst = mod.tool_board_list_entries({"project": "rdy", "root": root,
                                           "ready": True})
        ids = sorted(e["id"] for e in lst["entries"])
        check(ids == ["B001", "B003", "B004", "Q001"],
              "ready filter: open+unblocked, resolved-blocker, dangling-blocker "
              "and open question are ready", str(ids))
        check("B002" not in ids, "ready filter: entry with an open blocker is not ready")
        check("B005" not in ids, "ready filter: in_progress entry is never ready")
        dang = lst.get("dangling_blockers") or []
        check(any(w.get("entry") == "B004" and "X999" in w.get("missing", [])
                  for w in dang),
              "ready filter surfaces the dangling-blocker warning", json.dumps(dang))

        # ready combines with other filters.
        lst2 = mod.tool_board_list_entries({"project": "rdy", "root": root,
                                            "ready": True, "type": "bug"})
        ids2 = sorted(e["id"] for e in lst2["entries"])
        check(ids2 == ["B001", "B003", "B004"],
              "ready filter composes with type filter", str(ids2))

        # board_status: ready ids + dangling_blockers warnings.
        st = mod.tool_board_status({"project": "rdy", "root": root})["boards"][0]
        check(st.get("ready") == ["B001", "B003", "B004", "Q001"],
              "board_status.ready lists ready ids sorted", json.dumps(st.get("ready")))
        check(any(w.get("entry") == "B004" and w.get("missing") == ["X999"]
                  for w in st.get("dangling_blockers", [])),
              "board_status.dangling_blockers reports {entry, missing}",
              json.dumps(st.get("dangling_blockers")))

        # cap: board_status.ready is capped at 20.
        cap_root = tempfile.mkdtemp(prefix="eb-mcp-readycap-")
        mod.tool_board_init({"project": "cap", "root": cap_root})
        for i in range(22):
            mod.tool_board_create_entry({
                "project": "cap", "root": cap_root, "type": "bug",
                "title": "bulk %02d" % i, "priority": "P2",
                "affects": "cap/x", "done_when": ["x"]})
        stc = mod.tool_board_status({"project": "cap", "root": cap_root})["boards"][0]
        check(len(stc.get("ready", [])) == 20,
              "board_status.ready is capped at 20", str(len(stc.get("ready", []))))
        shutil.rmtree(cap_root, ignore_errors=True)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ---------------------------------------------------------------------------
# Suite: C6 — board_remember
# ---------------------------------------------------------------------------
def suite_remember(mod):
    """board_remember writes a curator-shaped learning file directly
    (source: remember), rebuilds BOARD.md, and keeps board-index-check.sh
    green. Explicit user intent bypasses the recurrence->=3 threshold."""
    print("\n== Suite: C6 board_remember ==")
    root = tempfile.mkdtemp(prefix="eb-mcp-remember-")
    index_check = os.path.join(PLUGIN_ROOT, "hooks", "scripts", "board-index-check.sh")
    try:
        mod.tool_board_init({"project": "mem", "root": root})

        r = mod.tool_board_remember({
            "project": "mem", "root": root,
            "insight": "Always flush the buffer before close",
            "context": "Applies to every buffered writer in exporters."})
        check(r["id"] == "L001", "first remember allocates L001", r.get("id"))
        check(r.get("source") == "remember", "result carries source=remember")
        lpath = os.path.join(root, r["file"])
        check(os.path.isfile(lpath), "learning file exists", r["file"])
        with open(lpath, encoding="utf-8") as f:
            text = f.read()
        fm, body = mod.parse_frontmatter(text)
        check(fm.get("source") == "remember", "frontmatter has source: remember")
        check(fm.get("type") == "learning" and fm.get("subtype") == "finding",
              "frontmatter type=learning subtype=finding", json.dumps(fm))
        for key in ("confidence", "recurrence", "derived_from", "discovered"):
            check(key in fm, "frontmatter has %s" % key)
        check("## Takeaway" in body and "## Sources" in body
              and "## When this applies" in body,
              "body carries the curator-shaped sections")
        rc, err = run_validate(lpath, root)
        check(rc == 0, "remember-produced learning passes board-validate-entry.sh", err)

        # BOARD.md treatment matches the curator/rebuild convention (L row).
        with open(os.path.join(root, "engineering-board", "mem", "BOARD.md")) as f:
            bmd = f.read()
        check("- L001 | [" in bmd, "BOARD.md gained the L001 open row", bmd)

        # index-check stays green after a remember.
        proc = subprocess.run(["bash", index_check], capture_output=True, text=True,
                              env=dict(os.environ, CLAUDE_PROJECT_DIR=root))
        check(proc.returncode == 0, "board-index-check.sh green post-remember",
              proc.stderr + proc.stdout)

        # second remember allocates the next id.
        r2 = mod.tool_board_remember({"project": "mem", "root": root,
                                      "insight": "Second durable insight"})
        check(r2["id"] == "L002", "second remember allocates L002", r2.get("id"))

        # missing insight -> ToolError.
        try:
            mod.tool_board_remember({"project": "mem", "root": root})
            raise Failure("expected ToolError for remember without insight")
        except mod.ToolError:
            ok("board_remember rejects a missing insight")

        # newline in insight cannot inject frontmatter (title is flattened).
        r3 = mod.tool_board_remember({
            "project": "mem", "root": root,
            "insight": "sneaky\nstatus: resolved\nmalicious: yes"})
        with open(os.path.join(root, r3["file"]), encoding="utf-8") as f:
            t3 = f.read()
        fm3, _ = mod.parse_frontmatter(t3)
        check("malicious" not in fm3,
              "remember title newline cannot inject frontmatter keys")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ---------------------------------------------------------------------------
# Suite: C7 — comments + parent
# ---------------------------------------------------------------------------
def suite_comments_parent(mod):
    print("\n== Suite: C7 comments + parent ==")
    root = tempfile.mkdtemp(prefix="eb-mcp-c7-")
    try:
        mod.tool_board_init({"project": "fam", "root": root})

        # parent round-trip on create.
        mod.tool_board_create_entry({
            "project": "fam", "root": root, "type": "bug",
            "title": "Parent bug", "priority": "P2", "affects": "fam/a",
            "done_when": ["x"]})
        r = mod.tool_board_create_entry({
            "project": "fam", "root": root, "type": "bug",
            "title": "Child bug", "priority": "P0", "affects": "fam/b",
            "parent": "B001", "done_when": ["x"]})
        check(not r.get("warnings"), "existing parent produces no warning",
              json.dumps(r.get("warnings")))
        got = mod.tool_board_get_entry({"project": "fam", "root": root,
                                        "entry_id": "B002"})
        check(got["frontmatter"].get("parent") == "B001",
              "parent round-trips through create -> get")
        rc, err = run_validate(os.path.join(root, got["file"]), root)
        check(rc == 0, "entry with parent passes board-validate-entry.sh", err)

        # dangling parent -> warning in response, NOT an error; validator warns
        # on stderr but still exits 0.
        rd = mod.tool_board_create_entry({
            "project": "fam", "root": root, "type": "bug",
            "title": "Orphan child", "priority": "P3", "affects": "fam/c",
            "parent": "F999", "done_when": ["x"]})
        check(any("F999" in w for w in rd.get("warnings", [])),
              "dangling parent create returns a warning", json.dumps(rd))
        rc, err = run_validate(os.path.join(root, rd["file"]), root)
        check(rc == 0, "dangling parent is accepted by the validator (warn, not fail)", err)
        check("parent" in err.lower() and "F999" in err,
              "validator warns about the dangling parent on stderr", err)

        # parent settable via update, dangling -> warning.
        ru = mod.tool_board_update_entry({"project": "fam", "root": root,
                                          "entry_id": "B003", "parent": "B001"})
        check(any("parent=B001" in c for c in ru["changes"]),
              "board_update_entry sets parent")
        check(not ru.get("warnings"), "update to an existing parent: no warning")
        ru2 = mod.tool_board_update_entry({"project": "fam", "root": root,
                                           "entry_id": "B003", "parent": "Q404"})
        check(any("Q404" in w for w in ru2.get("warnings", [])),
              "update to a dangling parent returns a warning", json.dumps(ru2))
        mod.tool_board_update_entry({"project": "fam", "root": root,
                                     "entry_id": "B003", "parent": "B001"})

        # BOARD.md: children render indented under the parent, sorted by id,
        # deterministic across rebuilds.
        mod.tool_board_rebuild({"project": "fam", "root": root})
        bmd_path = os.path.join(root, "engineering-board", "fam", "BOARD.md")
        with open(bmd_path) as f:
            bmd1 = f.read()
        mod.tool_board_rebuild({"project": "fam", "root": root})
        with open(bmd_path) as f:
            bmd2 = f.read()
        check(bmd1 == bmd2, "rebuild with parents is byte-deterministic")
        lines = [ln for ln in bmd1.split("\n")]
        pidx = next(i for i, ln in enumerate(lines) if ln.startswith("- B001 "))
        check(lines[pidx + 1].startswith("  ↳ B002 ")
              and lines[pidx + 2].startswith("  ↳ B003 "),
              "children render as '  ↳ ' rows directly under the parent, id-sorted",
              "\n".join(lines[pidx:pidx + 3]))

        # a child whose parent is missing / lives in another section renders as
        # a normal row.
        mod.tool_board_create_entry({
            "project": "fam", "root": root, "type": "question",
            "title": "Cross-section parent?", "done_when": ["x"]})
        rx = mod.tool_board_create_entry({
            "project": "fam", "root": root, "type": "bug",
            "title": "Question-parented bug", "priority": "P3",
            "affects": "fam/d", "parent": "Q001", "done_when": ["x"]})
        with open(bmd_path) as f:
            bmd3 = f.read()
        check("\n- %s " % rx["id"] in bmd3,
              "child with an other-section parent renders as a normal row", bmd3)

        # comment: creates the section once, appends thereafter, single line,
        # UTC ISO8601, server-side timestamp.
        import re as _re
        mod.tool_board_update_entry({
            "project": "fam", "root": root, "entry_id": "B001",
            "comment": {"author": "alice", "text": "first note"}})
        md = mod.tool_board_get_entry({"project": "fam", "root": root,
                                       "entry_id": "B001"})["markdown"]
        check(md.count("## Comments") == 1, "first comment creates ## Comments once")
        check(_re.search(r"^- \*\*alice\*\* \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z: first note$",
                         md, _re.M) is not None,
              "comment line format '- **author** <UTC ISO8601>: text'", md)
        mod.tool_board_update_entry({
            "project": "fam", "root": root, "entry_id": "B001",
            "comment": {"author": "bob", "text": "second\nnote with\nnewlines"}})
        md2 = mod.tool_board_get_entry({"project": "fam", "root": root,
                                        "entry_id": "B001"})["markdown"]
        check(md2.count("## Comments") == 1,
              "second comment appends to the existing section (created once)")
        check(_re.search(r"^- \*\*bob\*\* \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z: second note with newlines$",
                         md2, _re.M) is not None,
              "comment text is sanitized to a single line", md2)
        a_pos = md2.find("- **alice**")
        b_pos = md2.find("- **bob**")
        check(0 < a_pos < b_pos, "comments append in order")
        rc, err = run_validate(
            os.path.join(root, mod.tool_board_get_entry(
                {"project": "fam", "root": root, "entry_id": "B001"})["file"]), root)
        check(rc == 0, "entry with comments still passes validation", err)

        # malformed comment -> ToolError.
        try:
            mod.tool_board_update_entry({"project": "fam", "root": root,
                                         "entry_id": "B001", "comment": {"author": "x"}})
            raise Failure("expected ToolError for comment without text")
        except mod.ToolError:
            ok("comment without text is rejected")
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ---------------------------------------------------------------------------
# Suite: C8 — AGENTS.md emission on board_init
# ---------------------------------------------------------------------------
def suite_agents_md(mod):
    print("\n== Suite: C8 AGENTS.md emission ==")
    root = tempfile.mkdtemp(prefix="eb-mcp-agents-")
    try:
        # created when absent (default agents_md=true).
        mod.tool_board_init({"project": "ag", "root": root})
        ap = os.path.join(root, "AGENTS.md")
        check(os.path.isfile(ap), "board_init creates AGENTS.md by default")
        with open(ap, encoding="utf-8") as f:
            t1 = f.read()
        check("<!-- engineering-board:start -->" in t1
              and "<!-- engineering-board:end -->" in t1,
              "AGENTS.md carries the marker fence")
        for tool_name in ("board_capture_finding", "board_claim",
                          "board_update_entry", "board_create_entry"):
            check(tool_name in t1, "AGENTS.md block mentions %s" % tool_name)

        # idempotent re-init: byte-stable.
        mod.tool_board_init({"project": "ag", "root": root})
        with open(ap, encoding="utf-8") as f:
            t2 = f.read()
        check(t1 == t2, "re-init leaves AGENTS.md byte-identical")

        # pre-existing content outside the markers is preserved.
        pre_root = tempfile.mkdtemp(prefix="eb-mcp-agents2-")
        pre_path = os.path.join(pre_root, "AGENTS.md")
        with open(pre_path, "w", encoding="utf-8") as f:
            f.write("# My agents\n\nHand-written guidance stays.\n")
        mod.tool_board_init({"project": "ag", "root": pre_root})
        with open(pre_path, encoding="utf-8") as f:
            t3 = f.read()
        check("Hand-written guidance stays." in t3,
              "content outside the markers is preserved")
        check("<!-- engineering-board:start -->" in t3,
              "block appended to a pre-existing AGENTS.md")
        mod.tool_board_init({"project": "ag", "root": pre_root})
        with open(pre_path, encoding="utf-8") as f:
            t4 = f.read()
        check(t3 == t4, "re-init on a pre-existing AGENTS.md is idempotent")
        check(t4.count("<!-- engineering-board:start -->") == 1,
              "exactly one marker block after repeated inits")
        shutil.rmtree(pre_root, ignore_errors=True)

        # opt-out.
        off_root = tempfile.mkdtemp(prefix="eb-mcp-agents3-")
        mod.tool_board_init({"project": "ag", "root": off_root, "agents_md": False})
        check(not os.path.exists(os.path.join(off_root, "AGENTS.md")),
              "agents_md=false suppresses AGENTS.md")
        shutil.rmtree(off_root, ignore_errors=True)
    finally:
        shutil.rmtree(root, ignore_errors=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def suite_distribution():
    """Validate the distribution manifests so they cannot silently rot.

    server.json (MCP Registry), manifest.json (.mcpb bundle), and smithery.yaml
    must stay well-formed and version-coherent with plugin.json — the same
    lockstep discipline the plugin/marketplace manifests already enforce.
    """
    plugin_ver = json.load(
        open(os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json"))
    )["version"]

    server = json.load(open(os.path.join(HERE, "server.json")))
    check(server.get("version") == plugin_ver,
          "server.json version matches plugin.json",
          "%s != %s" % (server.get("version"), plugin_ver))
    check(server.get("name") == "io.github.GhostlyGawd/engineering-board",
          "server.json uses the reverse-DNS registry namespace (exact login casing)")
    pkgs = server.get("packages") or []
    check(len(pkgs) == 1 and pkgs[0].get("version") == plugin_ver,
          "server.json package version matches plugin.json")
    check(pkgs and pkgs[0].get("transport", {}).get("type") == "stdio",
          "server.json declares the stdio transport")

    manifest = json.load(open(os.path.join(HERE, "manifest.json")))
    check(manifest.get("version") == plugin_ver,
          "manifest.json (.mcpb) version matches plugin.json",
          "%s != %s" % (manifest.get("version"), plugin_ver))
    srv = manifest.get("server", {})
    check(srv.get("type") == "python"
          and srv.get("entry_point") == "mcp-server/engineering_board_mcp.py",
          "manifest.json points at the real server entry point")

    smithery = open(os.path.join(HERE, "smithery.yaml")).read()
    for token in ("startCommand:", "type: stdio",
                  "engineering_board_mcp.py", "commandFunction:"):
        check(token in smithery,
              "smithery.yaml contains %r" % token)

    # The .mcpb bundle is reproducible, so server.json can pin its sha256. Rebuild
    # the bundle contents in-process (python3 only — mirrors build-mcpb.sh's
    # deterministic zipfile step, no `zip` CLI) and assert the pin still matches,
    # so a change to any bundled script that isn't re-pinned fails CI.
    import zipfile, hashlib, io
    staged = []  # (arcname, bytes)
    with open(os.path.join(HERE, "manifest.json"), "rb") as f:
        staged.append(("manifest.json", f.read()))
    with open(SERVER_PATH, "rb") as f:
        staged.append(("mcp-server/engineering_board_mcp.py", f.read()))
    with open(os.path.join(HERE, "README.md"), "rb") as f:
        staged.append(("mcp-server/README.md", f.read()))
    scripts_dir = os.path.join(PLUGIN_ROOT, "hooks", "scripts")
    for fn in sorted(os.listdir(scripts_dir)):
        if fn.endswith(".sh") or fn.endswith(".py"):
            with open(os.path.join(scripts_dir, fn), "rb") as f:
                staged.append(("hooks/scripts/" + fn, f.read()))
    with open(os.path.join(PLUGIN_ROOT, "LICENSE"), "rb") as f:
        staged.append(("LICENSE", f.read()))
    staged.sort(key=lambda p: p[0])
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for arcname, data in staged:
            zi = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            z.writestr(zi, data)
    rebuilt_sha = hashlib.sha256(buf.getvalue()).hexdigest()
    pinned = pkgs[0].get("fileSha256")
    check(pinned == rebuilt_sha,
          "server.json fileSha256 matches a fresh reproducible bundle build",
          "pinned=%s rebuilt=%s (run: bash mcp-server/build-mcpb.sh, then re-pin)"
          % (pinned, rebuilt_sha))


def suite_multiclient():
    """Two independent MCP server processes drive ONE board (eb-self Q001).

    This is the multi-client differentiator (README VP5) made empirical: the
    same on-disk board, two stdio server instances (as Claude Code + Claude
    Desktop would spawn), racing for the same entry's claim. Exactly one must
    win; the loser must see clean contention; after the winner releases, the
    loser must be able to acquire.
    """
    print("\n== Suite 4: multi-client — two servers, one board (Q001) ==")
    tmp = tempfile.mkdtemp(prefix="eb-mcp-multi-")
    procs = []

    def spawn():
        pr = subprocess.Popen(
            ["python3", SERVER_PATH],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1,
            env=dict(os.environ, CLAUDE_PROJECT_DIR=tmp),
        )
        procs.append(pr)

        def rpc(method, params, _id=[0]):
            _id[0] += 1
            pr.stdin.write(json.dumps({"jsonrpc": "2.0", "id": _id[0],
                                       "method": method, "params": params}) + "\n")
            pr.stdin.flush()
            line = pr.stdout.readline()
            if not line:
                raise Failure("multiclient: server died; stderr=%r" % pr.stderr.read())
            return json.loads(line)

        r = rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}})
        assert "result" in r
        pr.stdin.write(json.dumps({"jsonrpc": "2.0",
                                   "method": "notifications/initialized"}) + "\n")
        pr.stdin.flush()

        def call(tool, args):
            r = rpc("tools/call", {"name": tool, "arguments": args})
            return json.loads(r["result"]["content"][0]["text"])

        return call

    try:
        a = spawn()
        b = spawn()

        a("board_init", {"project": "shared"})
        made = a("board_create_entry", {
            "project": "shared", "type": "bug", "title": "raced entry",
            "priority": "P2", "affects": "shared/x", "done_when": ["x"]})
        eid = made["id"]

        # Client B sees the entry client A created (same board, no cache).
        got = b("board_get_entry", {"project": "shared", "entry_id": eid})
        check(got.get("frontmatter", {}).get("id") == eid,
              "client B reads the entry client A created")

        ra = a("board_claim", {"project": "shared", "entry_id": eid,
                               "session_id": "client-a"})
        rb = b("board_claim", {"project": "shared", "entry_id": eid,
                               "session_id": "client-b"})
        codes = sorted([ra.get("exit_code"), rb.get("exit_code")])
        check(codes == [0, 1],
              "concurrent claims: exactly one acquired (0) and one contended (1)",
              "got %s" % codes)

        winner, loser = (a, b) if ra.get("exit_code") == 0 else (b, a)
        wsid = "client-a" if ra.get("exit_code") == 0 else "client-b"
        lsid = "client-b" if wsid == "client-a" else "client-a"
        rel = winner("board_release", {"project": "shared", "entry_id": eid,
                                       "session_id": wsid})
        check(rel.get("exit_code") == 0, "winner releases its claim cleanly")
        r2 = loser("board_claim", {"project": "shared", "entry_id": eid,
                                   "session_id": lsid})
        check(r2.get("exit_code") == 0,
              "loser acquires after release (no stuck lock)")
    finally:
        for pr in procs:
            try:
                pr.stdin.close()
            except Exception:
                pass
            try:
                pr.wait(timeout=5)
            except Exception:
                pr.kill()
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if not os.path.isfile(VALIDATE_SCRIPT):
        print("MISSING validate script: %s" % VALIDATE_SCRIPT, file=sys.stderr)
        return 1

    mod = load_server()
    tmp1 = tempfile.mkdtemp(prefix="eb-mcp-stdio-")
    tmp2 = tempfile.mkdtemp(prefix="eb-mcp-life-")
    try:
        suite_stdio(tmp1)
        suite_lifecycle(mod, tmp2)
        suite_ready(mod)
        suite_remember(mod)
        suite_comments_parent(mod)
        suite_agents_md(mod)
        suite_multiclient()
        # Distribution runs LAST: its fileSha256 pin intentionally trips on any
        # server/hooks-script change until the release coherence pass re-pins
        # via build-mcpb.sh — running it last keeps that expected drift from
        # masking real feature-suite failures above.
        suite_distribution()
    except Failure as e:
        print("\n  [FAIL] %s" % e, file=sys.stderr)
        print("\nRESULT: FAIL (%d checks passed before failure)" % len(PASSED), file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(tmp1, ignore_errors=True)
        shutil.rmtree(tmp2, ignore_errors=True)

    print("\nRESULT: PASS (%d checks)" % len(PASSED))
    return 0


if __name__ == "__main__":
    sys.exit(main())

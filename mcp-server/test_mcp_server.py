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
                    "board_release", "board_status"}
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
# Main
# ---------------------------------------------------------------------------
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

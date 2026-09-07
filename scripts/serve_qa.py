#!/usr/bin/env python3
"""Stage and serve the landing and generated board on 127.0.0.1:4173."""

from __future__ import annotations

import argparse
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple

import validator_resources


ADDRESS = "127.0.0.1"
PORT = 4173
ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".engineering-board" / "qa"
RECEIPT = RUNTIME / "server.json"
LOCK_ROOT = ROOT / ".engineering-board" / "validator-locks"


class QAError(RuntimeError):
    """A local QA lifecycle operation failed safely."""

    def __init__(self, code: str, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code


class QuietHandler(SimpleHTTPRequestHandler):
    """Serve only the staged directory and keep stdout/stderr deterministic."""

    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".md": "text/plain; charset=utf-8",
        ".txt": "text/plain; charset=utf-8",
    }

    def log_message(self, format: str, *args: object) -> None:
        return


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_json(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, sort_keys=True, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(str(temporary), str(path))
        reread = json.loads(path.read_text(encoding="utf-8"))
        if reread != value:
            raise QAError("E_RECEIPT", "server receipt read-back differed", 4)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _read_receipt() -> Optional[Dict[str, Any]]:
    try:
        value = json.loads(RECEIPT.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return value if isinstance(value, dict) else None


def _command_matches(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        return validator_resources._pid_is_alive(pid)
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    command = result.stdout.strip()
    return result.returncode == 0 and "serve_qa.py" in command


def _process_is_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        return validator_resources._pid_is_alive(pid)
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "stat="],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    state = result.stdout.strip()
    return result.returncode == 0 and bool(state) and not state.startswith("Z")


def stop() -> int:
    receipt = _read_receipt()
    if receipt is None:
        raise QAError(
            "E_NOT_RUNNING",
            "no readable QA server receipt exists; nothing was stopped",
            4,
        )
    pid = receipt.get("pid")
    if not isinstance(pid, int) or not _command_matches(pid):
        raise QAError(
            "E_OWNER_MISMATCH",
            "recorded PID is not the Engineering Board QA server; no process was stopped",
            4,
        )
    os.kill(pid, signal.SIGTERM)
    deadline = time.monotonic() + 8.0
    while time.monotonic() < deadline and _process_is_running(pid):
        time.sleep(0.05)
    if _process_is_running(pid):
        raise QAError(
            "E_STOP_TIMEOUT",
            f"recorded QA server PID {pid} did not stop; inspect it before retrying",
            4,
        )
    print(f"qa-server: STOPPED pid={pid}", file=sys.stderr)
    return 0


def _acquire_locks() -> Tuple[str, List[Path]]:
    token = os.urandom(16).hex()
    owner = validator_resources._owner_record("serve-qa", token)
    acquired: List[Path] = []
    for slot in range(1, validator_resources.MAX_SESSIONS + 1):
        candidate = LOCK_ROOT / "sessions" / f"slot-{slot}"
        if validator_resources._acquire_directory(candidate, owner):
            acquired.append(candidate)
            break
    if not acquired:
        raise QAError(
            "E_LOCK",
            "global validator capacity is occupied; stop another validator and retry",
            75,
        )
    try:
        for resource in ("browser", "port-4173"):
            directory = LOCK_ROOT / "exclusive" / resource
            if not validator_resources._acquire_directory(directory, owner):
                occupant = validator_resources._read_owner(directory) or {}
                label = occupant.get("label", "unknown")
                raise QAError(
                    "E_LOCK",
                    f"exclusive {resource} lock is occupied by {label}; retry after it exits",
                    75,
                )
            acquired.append(directory)
    except BaseException:
        for directory in reversed(acquired):
            validator_resources._remove_owned_lock(directory, token)
        raise
    return token, acquired


def _stage_site() -> Tuple[Path, Dict[str, str]]:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".site-", dir=str(RUNTIME)))
    try:
        shutil.copy2(str(ROOT / "docs" / "index.html"), str(temporary / "index.html"))
        shutil.copytree(str(ROOT / "docs" / "assets"), str(temporary / "assets"))
        for optional in (".nojekyll", "llms.txt"):
            source = ROOT / "docs" / optional
            if source.is_file():
                shutil.copy2(str(source), str(temporary / optional))
        environment = os.environ.copy()
        environment["CLAUDE_PROJECT_DIR"] = str(ROOT)
        board_source = ROOT / "engineering-board" / "eb-self"
        canonical_root = temporary / "engineering-board"
        canonical_root.mkdir(parents=True, exist_ok=True)
        for relative in (
            "bugs",
            "features",
            "questions",
            "observations",
            "learnings",
            "hypotheses",
        ):
            source_directory = board_source / relative
            if source_directory.is_dir():
                shutil.copytree(
                    str(source_directory),
                    str(temporary / relative),
                )
                shutil.copytree(
                    str(source_directory),
                    str(canonical_root / relative),
                )
        generated = subprocess.run(
            [
                "bash",
                str(ROOT / "hooks" / "scripts" / "board-view.sh"),
                "eb-self",
                "--stdout",
            ],
            cwd=ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if generated.returncode != 0:
            diagnostic = generated.stderr.decode("utf-8", errors="replace").strip()
            raise QAError(
                "E_GENERATION",
                f"board generation failed without replacing staged output: {diagnostic}",
                3,
            )
        (temporary / "board.html").write_bytes(generated.stdout)
        canonical_board = canonical_root / "board.html"
        canonical_board.write_bytes(generated.stdout)
        hashes = {
            "landing_sha256": _sha256(temporary / "index.html"),
            "board_sha256": _sha256(temporary / "board.html"),
        }
        return temporary, hashes
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def serve() -> int:
    token, locks = _acquire_locks()
    server: Optional[ThreadingHTTPServer] = None
    site: Optional[Path] = None
    try:
        try:
            server = ThreadingHTTPServer(
                (ADDRESS, PORT),
                lambda *args, **kwargs: QuietHandler(*args, directory=str(site), **kwargs),
            )
        except OSError as exc:
            raise QAError(
                "E_PORT_CONFLICT",
                f"{ADDRESS}:{PORT} is occupied; stop the existing listener and retry, no fallback was used ({exc.__class__.__name__})",
                75,
            )
        site, hashes = _stage_site()
        receipt = {
            "schema_version": "1",
            "pid": os.getpid(),
            "token": token,
            "address": ADDRESS,
            "port": PORT,
            "site": str(site.relative_to(ROOT)),
            **hashes,
        }
        _atomic_json(RECEIPT, receipt)

        def terminate(_signum: int, _frame: object) -> None:
            raise KeyboardInterrupt

        if os.name != "nt":
            signal.signal(signal.SIGTERM, terminate)
            signal.signal(signal.SIGINT, terminate)
        print(
            "qa-server: READY "
            f"pid={os.getpid()} address={ADDRESS}:{PORT} "
            f"landing_sha256={hashes['landing_sha256']} "
            f"board_sha256={hashes['board_sha256']}",
            file=sys.stderr,
            flush=True,
        )
        try:
            server.serve_forever(poll_interval=0.1)
        except KeyboardInterrupt:
            pass
        return 0
    finally:
        if server is not None:
            server.server_close()
        current = _read_receipt()
        if current is not None and current.get("token") == token:
            try:
                RECEIPT.unlink()
            except FileNotFoundError:
                pass
        if site is not None:
            shutil.rmtree(site, ignore_errors=True)
        for directory in reversed(locks):
            validator_resources._remove_owned_lock(directory, token)
        try:
            RUNTIME.rmdir()
        except OSError:
            pass


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "The server binds only 127.0.0.1:4173 and owns the browser and "
            "port-4173 locks. Stop only the recorded PID with --stop."
        ),
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="stop and wait for only the PID in .engineering-board/qa/server.json",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    try:
        args = parse_args(sys.argv[1:] if argv is None else argv)
        return stop() if args.stop else serve()
    except QAError as exc:
        print(f"qa-server: {exc.code} {exc}", file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())

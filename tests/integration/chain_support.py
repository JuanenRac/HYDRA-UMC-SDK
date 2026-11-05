# =============================================================================
# HYDRA-UMC-SDK - tests/integration/chain_support.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Helpers of the safety-chain simulation: where the other repositories are, the local servers it starts and the stand-ins it needs.

Everything runs on the loopback address and on ports that the operating system gives at that moment. The other repositories are only
read: their packages are imported from their source folders and their programs are started as they are, nothing is installed and
nothing is written in them. A program that is not built, or a repository that is not next to this one, makes the scenario that needs
it skip (the runner turns a skip into a failure with `--require`).

Stand-ins, named as such wherever they are used:
  * `OrchestratorDouble` follows the contract of the global stop of HYDRA-UMC-ORCHESTRATOR (`POST /estop`, `POST /estop/release`,
    423 while engaged, a latch that survives a restart and a state file that cannot be read counts as engaged). The real program is
    written in Rust and is not built here (a build of it is heavy), so this file does not run the real one.
  * `CellDouble` is the cell that confirms (or does not confirm) that the robots of a failed node are stopped.
"""
from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

SDK_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SDK_ROOT / "tools"))
from local_build import local_build_refusal  # noqa: E402  (the lock on builds that compile on this PC)
WORKSPACE = Path(os.environ.get("HYDRA_CHAIN_SIM_WORKSPACE", str(SDK_ROOT.parent))).resolve()
EXE = ".exe" if os.name == "nt" else ""


def repo(name: str) -> Path:
    return WORKSPACE / f"HYDRA-UMC-{name}"


def add_python_package(name: str) -> bool:
    """Puts the `src` folder of a sibling repository on the import path (read only). False when it is not there."""
    src = repo(name) / "src"
    if not src.is_dir():
        return False
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    return True


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def random_secret(nbytes: int = 24) -> str:
    return secrets.token_hex(nbytes)


# --- small HTTP client --------------------------------------------------------------------------------------------------------


def http(method: str, url: str, body: object | None = None, token: str = "", timeout: float = 6.0) -> tuple[int, Any]:
    """(status, parsed JSON or text). A refused connection raises OSError, as a real client would see it."""
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - loopback only
            status, raw = response.status, response.read()
    except urllib.error.HTTPError as error:
        status, raw = error.code, error.read()
    try:
        return status, json.loads(raw)
    except ValueError:
        return status, raw.decode("utf-8", "replace")


class LocalServer:
    """A ThreadingHTTPServer in a thread of this process, on a port of the system."""

    def __init__(self, handler: type[BaseHTTPRequestHandler]) -> None:
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.httpd.daemon_threads = True
        self.port = int(self.httpd.server_address[1])
        self.url = f"http://127.0.0.1:{self.port}"
        self._thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def start(self) -> "LocalServer":
        self._thread.start()
        return self

    def stop(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()


def _reply(handler: BaseHTTPRequestHandler, status: int, payload: object, headers: dict[str, str] | None = None) -> None:
    body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    for name, value in (headers or {}).items():
        handler.send_header(name, value)
    handler.end_headers()
    handler.wfile.write(body)


def _body(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length") or 0)
    raw = handler.rfile.read(length) if length else b""
    try:
        value = json.loads(raw or b"{}")
    except ValueError:
        return {}
    return value if isinstance(value, dict) else {}


# --- stand-in of the verdict channel: replays or alters what the real safety service said ----------------------------------------


class VerdictProxy:
    """Sits between the planner and the real safety service so a scenario can hand the planner a changed or an older verdict.

    `mutate(answer)` receives the real answer of `GET /state` and returns what the planner sees; `None` returns it as it is.
    """

    def __init__(self, upstream: str) -> None:
        self.upstream = upstream
        self.mutate: Callable[[dict], dict] | None = None
        self.replay: dict | None = None
        proxy = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args: object) -> None:  # noqa: D102
                return

            def do_GET(self) -> None:  # noqa: N802
                if proxy.replay is not None:
                    _reply(self, 200, proxy.replay)
                    return
                status, answer = http("GET", proxy.upstream + "/state")
                if status == 200 and isinstance(answer, dict) and proxy.mutate is not None:
                    answer = proxy.mutate(answer)
                _reply(self, status, answer)

        self.server = LocalServer(Handler)

    @property
    def url(self) -> str:
        return self.server.url

    def start(self) -> "VerdictProxy":
        self.server.start()
        return self

    def stop(self) -> None:
        self.server.stop()


# --- stand-in of the global stop of the orchestrator ------------------------------------------------------------------------------


class OrchestratorDouble:
    """The contract of HYDRA-UMC-ORCHESTRATOR around the global stop, as a small server (see the module note).

    Routes: GET /health (liveness, always ok), GET /health-report (what the HealthService of the orchestrator says: DEGRADED while the
    stop is engaged), GET /estop, POST /estop (operator or admin), POST /estop/release (admin only), POST /missions/{id}/dispatch,
    /auto-dispatch and /start (423 while engaged), POST /nodes/{node}/recover (recorded).
    """

    def __init__(self, token: str, admin_token: str, state_file: Path) -> None:
        self.token, self.admin_token, self.state_file = token, admin_token, state_file
        self.engaged = False
        self.latch: dict[str, Any] = {"by": "", "reason": "", "triggers": 0}
        self.recoveries: list[str] = []
        self.dispatched: list[str] = []
        self._lock = threading.Lock()
        self._load()
        double = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args: object) -> None:  # noqa: D102
                return

            def _role(self) -> str | None:
                given = self.headers.get("Authorization", "").removeprefix("Bearer ").strip()
                if given and given == double.admin_token:
                    return "admin"
                if given and given == double.token:
                    return "operator"
                return None

            def do_GET(self) -> None:  # noqa: N802
                if self.path == "/health":
                    _reply(self, 200, {"status": "ok", "name": "HYDRA-UMC-ORCHESTRATOR"})
                elif self.path == "/health-report":
                    state = "degraded" if double.engaged else "ok"
                    detail = "the global stop is engaged: no mission moves until it is released" if double.engaged else "ready"
                    _reply(self, 200, {"name": "HYDRA-UMC-ORCHESTRATOR", "status": state, "detail": detail})
                elif self.path == "/estop":
                    if self._role() is None:
                        _reply(self, 401, {"error": "missing or wrong bearer token"})
                    else:
                        _reply(self, 200, {"engaged": double.engaged, **double.latch})
                else:
                    _reply(self, 404, {"error": "not found"})

            def do_POST(self) -> None:  # noqa: N802
                role = self._role()
                body = _body(self)
                if self.path == "/estop":
                    if role is None:
                        _reply(self, 401, {"error": "missing or wrong bearer token"})
                    else:
                        _reply(self, 200, double.trigger(str(body.get("by", "")), str(body.get("reason", ""))))
                elif self.path == "/estop/release":
                    if role is None:
                        _reply(self, 401, {"error": "missing or wrong bearer token"})
                    elif role != "admin":
                        _reply(self, 403, {"error": "only an administrator may release the global stop", "engaged": double.engaged})
                    else:
                        _reply(self, 200, double.release())
                elif re.fullmatch(r"/missions/[^/]+/(dispatch|auto-dispatch|start)", self.path):
                    if role is None:
                        _reply(self, 401, {"error": "missing or wrong bearer token"})
                    elif double.engaged:
                        _reply(self, 423, {"error": "the global stop is engaged: nothing is dispatched or started until an administrator releases it", "estop": True})
                    else:
                        double.dispatched.append(self.path)
                        _reply(self, 200, {"ok": True})
                elif re.fullmatch(r"/nodes/[^/]+/recover", self.path):
                    double.recoveries.append(self.path.split("/")[2])
                    _reply(self, 200, {"requeuedMissions": []})
                else:
                    _reply(self, 404, {"error": "not found"})

        self.server = LocalServer(Handler)

    def _load(self) -> None:
        try:
            text = self.state_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            return
        except OSError:
            self.engaged, self.latch = True, {"by": "startup", "reason": "the saved state could not be opened", "triggers": 1}
            return
        try:
            saved = json.loads(text)
            self.engaged = bool(saved["engaged"])
            self.latch = {"by": saved.get("by", ""), "reason": saved.get("reason", ""), "triggers": int(saved.get("triggers", 0))}
        except (ValueError, KeyError, TypeError):
            # an unreadable record of a stop must not become "no stop"
            self.engaged, self.latch = True, {"by": "startup", "reason": "the saved state could not be read", "triggers": 1}

    def _save(self) -> None:
        self.state_file.write_text(json.dumps({"engaged": self.engaged, **self.latch}), encoding="utf-8")

    def trigger(self, by: str, reason: str) -> dict:
        with self._lock:
            repeat = self.engaged
            self.engaged = True
            if not repeat:
                self.latch = {"by": by or "unknown", "reason": reason, "triggers": 0}
            self.latch["triggers"] += 1
            self._save()
            return {"engaged": True, "already_engaged": repeat or self.latch["triggers"] > 1, "by": self.latch["by"]}

    def release(self) -> dict:
        with self._lock:
            was = self.engaged
            self.engaged = False
            self._save()
            return {"engaged": False, "was_engaged": was}

    @property
    def url(self) -> str:
        return self.server.url

    def start(self) -> "OrchestratorDouble":
        self.server.start()
        return self

    def stop(self) -> None:
        self.server.stop()


class OrchestratorEStopRequester:
    """Glue of the scenario: the E-STOP request that SAFETY-ZONES produces (it never cuts power itself) becomes `POST /estop`.

    In the real installation the request goes over the CAN bus to the firmware; this glue stands for the part of the chain that tells
    the orchestrator. A request that cannot be delivered raises, so the zone service reports the failed delivery.
    """

    def __init__(self, base: str, token: str) -> None:
        self.base, self.token = base, token
        self.sent: list[str] = []

    def send(self, request: Any) -> None:
        self.sent.append(request.reason)
        status, _ = http("POST", self.base + "/estop", {"by": "safety-zones", "reason": request.reason}, self.token)
        if status != 200:
            raise OSError(f"the orchestrator answered {status}")


# --- stand-in of the cell that confirms that the robots are stopped -----------------------------------------------------------------


class CellDouble:
    """The cell the fencing asks: `POST /robots/{node}/hold` and `GET /robots/{node}/state` -> {"state": ...}."""

    def __init__(self, state: str) -> None:
        self.state = state
        self.holds: list[str] = []
        cell = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args: object) -> None:  # noqa: D102
                return

            def do_POST(self) -> None:  # noqa: N802
                cell.holds.append(self.path)
                _reply(self, 200, {"held": True})

            def do_GET(self) -> None:  # noqa: N802
                _reply(self, 200, {"state": cell.state})

        self.server = LocalServer(Handler)

    @property
    def url(self) -> str:
        return self.server.url

    def start(self) -> "CellDouble":
        self.server.start()
        return self

    def stop(self) -> None:
        self.server.stop()


class NodeDouble:
    """A node whose health route answers what the scenario says; `answer` is (status, body bytes, extra headers) or None to hang."""

    def __init__(self, answer: tuple[int, bytes, dict[str, str]] | None) -> None:
        self.answer = answer
        node = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args: object) -> None:  # noqa: D102
                return

            def do_GET(self) -> None:  # noqa: N802
                if node.answer is None:
                    time.sleep(8)
                    return
                status, body, headers = node.answer
                _reply(self, status, body, headers)

        self.server = LocalServer(Handler)

    @property
    def url(self) -> str:
        return self.server.url

    def start(self) -> "NodeDouble":
        self.server.start()
        return self

    def stop(self) -> None:
        self.server.stop()


# --- the programs of the other repositories, started as they are ----------------------------------------------------------------------


def build_node_healing(out_dir: Path) -> Path | None:
    """The watchdog program: HYDRA_UMC_NODE_HEALING_BIN, or a build of the repository next to this one (go build, light) in `out_dir`."""
    given = os.environ.get("HYDRA_UMC_NODE_HEALING_BIN")
    if given and Path(given).is_file():
        return Path(given)
    source = repo("NODE-HEALING")
    if not (source / "main.go").is_file() or shutil.which("go") is None or local_build_refusal() is not None:
        return None
    target = out_dir / f"node-healing{EXE}"
    result = subprocess.run(["go", "build", "-o", str(target), "."], cwd=source, capture_output=True, text=True, timeout=300)
    return target if result.returncode == 0 and target.is_file() else None


class Process:
    """A program started by the scenario; only this process is ever stopped, and its output is kept for the failure message."""

    def __init__(self, argv: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
        self.argv = argv
        self.output_path = Path(tempfile.mkstemp(prefix="chain-sim-", suffix=".log")[1])
        self._log = open(self.output_path, "wb")  # noqa: SIM115 - closed in stop()
        self.proc = subprocess.Popen(argv, cwd=cwd, stdout=self._log, stderr=subprocess.STDOUT, env=env)  # noqa: S603

    def text(self) -> str:
        self._log.flush()
        try:
            return self.output_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    def wait_for(self, pattern: str, seconds: float) -> re.Match[str] | None:
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            found = re.search(pattern, self.text())
            if found:
                return found
            if self.proc.poll() is not None:
                return re.search(pattern, self.text())
            time.sleep(0.2)
        return None

    def stop(self) -> None:
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=10)
        self._log.close()
        try:
            self.output_path.unlink(missing_ok=True)
        except OSError:
            pass  # Windows may still hold the file for a moment; it is a throw-away log in the temp folder

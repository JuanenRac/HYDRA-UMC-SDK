# =============================================================================
# HYDRA-UMC-SDK - tests/integration/test_safety_chain_sim.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Safety chain in simulation: zones -> planner gate -> orchestrator stop -> operator dead-man -> watchdog.

Real parts (the other repositories are only read, nothing is installed): the zone service and its signed verdicts
(HYDRA-UMC-SAFETY-ZONES), the planner and its safety gate (HYDRA-UMC-SEMANTIC-PLANNER), the dead-man of the presence of the operator
(HYDRA-UMC-SERVER, run with its own TypeScript runner) and the watchdog program (HYDRA-UMC-NODE-HEALING, built with `go build`).
Stand-ins: the global stop of the orchestrator (the Rust program is not built here), the cell that confirms the robots are stopped
and the nodes the watchdog looks at. Every server listens on loopback on a port of the system. A pass means "passed in simulation":
nothing here ran on hardware.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from chain_support import (
    SDK_ROOT,
    CellDouble,
    NodeDouble,
    OrchestratorDouble,
    OrchestratorEStopRequester,
    Process,
    VerdictProxy,
    add_python_package,
    build_node_healing,
    free_port,
    http,
    random_secret,
    repo,
)

if not (add_python_package("SAFETY-ZONES") and add_python_package("SEMANTIC-PLANNER")):
    pytest.skip("HYDRA-UMC-SAFETY-ZONES and HYDRA-UMC-SEMANTIC-PLANNER must be next to this repository", allow_module_level=True)

from hydra_umc_safety_zones.api import SafetyZonesServer  # noqa: E402
from hydra_umc_safety_zones.signing import StateSigner  # noqa: E402
from hydra_umc_semantic_planner.api import SemanticPlannerServer  # noqa: E402
from hydra_umc_semantic_planner.safety_gate import (  # noqa: E402
    ClosedGate,
    SafetyGate,
    SafetyGateConfigError,
    SafetyGatePolicy,
)

GOAL = "assemble the housing"
KEY_ID = "line1"


# --- scaffolding -----------------------------------------------------------------------------------------------------------------


def _serve(server: object) -> str:
    threading.Thread(target=server.serve_forever, daemon=True).start()  # type: ignore[attr-defined]
    return f"http://127.0.0.1:{server.server_address[1]}"  # type: ignore[attr-defined]


def _stop(server: object) -> None:
    server.shutdown()  # type: ignore[attr-defined]
    server.server_close()  # type: ignore[attr-defined]


def _check_body(position: float) -> dict:
    """A request for a verdict: one danger zone (0..2 on every axis), one detected person at `position`, a fresh observer."""
    today = datetime.now(timezone.utc).date().isoformat()
    return {
        "zones": {
            "zones": [{"id": "cell", "level": "danger", "min": {"x": 0, "y": 0, "z": 0}, "max": {"x": 2, "y": 2, "z": 2}}],
            "calibration": {"version": "c", "source": "manual", "calibrated_at": today, "max_age_days": 30},
        },
        "detections": {"objects": [{"id": "person1", "position": {"x": position, "y": position, "z": position}}]},
        "observation": {"active": True, "observedAt": datetime.now(timezone.utc).isoformat(), "maxAgeSeconds": 3600, "error": None},
    }


def _verdict(base: str, position: float) -> dict:
    status, body = http("POST", base + "/check", _check_body(position))
    assert status == 200, body
    return body


def _planner(gate: SafetyGate | None) -> tuple[SemanticPlannerServer, str]:
    server = SemanticPlannerServer(("127.0.0.1", 0), "chain-sim", safety_gate=gate)
    return server, _serve(server)


def _release(base: str) -> dict:
    status, proposal = http("POST", base + "/decompose", {"goal": GOAL})
    assert status == 200, proposal
    status, body = http("POST", base + "/release", {"goal": GOAL, "approved_by": "ana", "plan_fingerprint": proposal["fingerprint"]})
    assert status == 200, body
    return body


@pytest.fixture(scope="module")
def workdir() -> Path:
    path = Path(tempfile.mkdtemp(prefix="chain-sim-"))
    yield path
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture(scope="module")
def key_file(workdir: Path) -> Path:
    path = workdir / "state.key"
    path.write_text(random_secret(32), encoding="utf-8")
    return path


@pytest.fixture()
def zones(key_file: Path):
    """The real zone service, signing its verdicts with the key of `key_file`."""
    server = SafetyZonesServer(("127.0.0.1", 0), "chain-sim", signer=StateSigner(key_file.read_text().strip().encode(), KEY_ID))
    base = _serve(server)
    yield server, base
    _stop(server)


def _gate(url: str, key_file: Path | str, **overrides: object) -> SafetyGate:
    policy = SafetyGatePolicy(enabled=True, url=url, key_file=str(key_file), key_id=KEY_ID, **overrides)  # type: ignore[arg-type]
    gate = SafetyGate.from_policy(policy)
    assert gate is not None
    return gate


# --- (a) a valid signed state releases; (b) every doubt refuses with the reason -----------------------------------------------------


def test_a_valid_signed_ready_state_releases_the_plan(zones, key_file: Path) -> None:
    _, base = zones
    assert _verdict(base, 50)["sdkSafetyState"]["state"] == "READY"
    planner, planner_url = _planner(_gate(base, key_file))
    try:
        body = _release(planner_url)
        assert body["released"] is True and body["safety_gate"] == {"allowed": True, "state": "READY"}
    finally:
        _stop(planner)


def test_without_a_gate_nothing_changes_and_with_a_closed_gate_nothing_is_released(workdir: Path, zones) -> None:
    """The switch is off by default (the planner behaves as before); with the switch on and no usable key the gate refuses everything."""
    _, base = zones
    _verdict(base, 50)
    plain, plain_url = _planner(None)
    try:
        assert _release(plain_url)["released"] is True
    finally:
        _stop(plain)
    # key file absent, start_without_key on: the planner starts, every release is refused with the reason
    policy = SafetyGatePolicy(enabled=True, url=base, key_file=str(workdir / "absent.key"), key_id=KEY_ID, start_without_key=True)
    closed = SafetyGate.from_policy(policy)
    assert isinstance(closed, ClosedGate)
    planner, planner_url = _planner(closed)
    try:
        body = _release(planner_url)
        assert body["released"] is False and "cannot verify verdicts" in body["reason"]
    finally:
        _stop(planner)
    # key file absent, start_without_key off (the default): the planner does not even start
    with pytest.raises(SafetyGateConfigError):
        SafetyGate.from_policy(SafetyGatePolicy(enabled=True, url=base, key_file=str(workdir / "absent.key"), key_id=KEY_ID))
    # a key that is too short is refused too
    short = workdir / "short.key"
    short.write_text("abc", encoding="utf-8")
    with pytest.raises(SafetyGateConfigError):
        SafetyGate.from_policy(SafetyGatePolicy(enabled=True, url=base, key_file=str(short), key_id=KEY_ID))


def test_a_state_that_is_unsigned_forged_old_replayed_or_from_another_key_is_refused(workdir: Path, zones, key_file: Path) -> None:
    server, base = zones
    good = _verdict(base, 50)
    assert good["sdkSafetyState"]["state"] == "READY"
    proxy = VerdictProxy(base).start()
    planner, planner_url = _planner(_gate(proxy.url, key_file, max_age_ms=60_000))
    try:
        assert _release(planner_url)["released"] is True

        # manipulated: the real verdict is DANGER (SAFE_STOP), the state is rewritten to READY and the signature is left as it was
        _verdict(base, 1)
        proxy.mutate = lambda answer: {**answer, "sdkSafetyState": {**answer["sdkSafetyState"], "state": "READY"}}
        body = _release(planner_url)
        assert body["released"] is False and "signature does not match" in body["reason"]
        proxy.mutate = None

        # signature removed
        proxy.mutate = lambda answer: {k: v for k, v in answer.items() if k != "sdkSafetyStateSignature"}
        _verdict(base, 50)
        body = _release(planner_url)
        assert body["released"] is False and "not signed" in body["reason"]

        # signature of another key id
        proxy.mutate = lambda answer: {**answer, "sdkSafetyStateSignature": {**answer["sdkSafetyStateSignature"], "key_id": "other"}}
        body = _release(planner_url)
        assert body["released"] is False and "another key id" in body["reason"]

        # signature with another algorithm than the one configured
        proxy.mutate = lambda answer: {**answer, "sdkSafetyStateSignature": {**answer["sdkSafetyStateSignature"], "alg": "Ed25519"}}
        body = _release(planner_url)
        assert body["released"] is False and "another algorithm" in body["reason"]
        proxy.mutate = None

        # replayed: a newer verdict was seen, then an older one is shown again
        older = _verdict(base, 50)
        time.sleep(0.01)
        newer = _verdict(base, 50)
        assert newer["sdkSafetyStateSignature"]["counter"] > older["sdkSafetyStateSignature"]["counter"]
        assert _release(planner_url)["released"] is True
        proxy.replay = {"sdkSafetyState": older["sdkSafetyState"], "sdkSafetyStateSignature": older["sdkSafetyStateSignature"]}
        body = _release(planner_url)
        assert body["released"] is False and "replay" in body["reason"]
    finally:
        _stop(planner)
        proxy.stop()

    # signed by a service that holds another key
    other_key = workdir / "other.key"
    other_key.write_text(random_secret(32), encoding="utf-8")
    planner, planner_url = _planner(_gate(base, other_key))
    try:
        _verdict(base, 50)
        body = _release(planner_url)
        assert body["released"] is False and "signature does not match" in body["reason"]
    finally:
        _stop(planner)

    # a service that does not sign at all
    unsigned = SafetyZonesServer(("127.0.0.1", 0), "chain-sim")
    unsigned_url = _serve(unsigned)
    planner, planner_url = _planner(_gate(unsigned_url, key_file))
    try:
        assert _verdict(unsigned_url, 50)["sdkSafetyState"]["state"] == "READY"
        body = _release(planner_url)
        assert body["released"] is False and "not signed" in body["reason"]
    finally:
        _stop(planner)
        _stop(unsigned)


def test_an_expired_verdict_is_refused(zones, key_file: Path) -> None:
    _, base = zones
    _verdict(base, 50)
    planner, planner_url = _planner(_gate(base, key_file, max_age_ms=150))
    try:
        time.sleep(0.5)
        body = _release(planner_url)
        assert body["released"] is False and "ms old" in body["reason"]
    finally:
        _stop(planner)


def test_no_verdict_a_silent_service_and_a_non_ready_state_refuse(zones, key_file: Path) -> None:
    server, base = zones
    planner, planner_url = _planner(_gate(base, key_file))
    try:
        # the service is up but has not reached a verdict yet: not confirmed safe
        body = _release(planner_url)
        assert body["released"] is False and "did not answer" in body["reason"]
        # a person inside the danger zone: SAFE_STOP, with the state in the answer
        assert _verdict(base, 1)["sdkSafetyState"]["state"] == "SAFE_STOP"
        body = _release(planner_url)
        assert body["released"] is False and body["safety_gate"] == {"allowed": False, "state": "SAFE_STOP"}
        # back to clear: it releases again (a refusal is not latched here: the latch is the orchestrator's)
        _verdict(base, 50)
        assert _release(planner_url)["released"] is True
    finally:
        _stop(planner)
    # a service that is not there at all
    dead_port = free_port()
    planner, planner_url = _planner(_gate(f"http://127.0.0.1:{dead_port}", key_file))
    try:
        body = _release(planner_url)
        assert body["released"] is False and "did not answer" in body["reason"]
    finally:
        _stop(planner)


# --- (c) the global stop: orchestrator DEGRADED, nothing dispatched, planner refuses, watchdog sees it -----------------------------


@pytest.fixture()
def orchestrator(workdir: Path):
    double = OrchestratorDouble("operator-" + random_secret(8), "admin-" + random_secret(8), workdir / f"estop-{random_secret(4)}.json").start()
    yield double
    double.stop()


def test_a_danger_verdict_engages_the_stop_that_blocks_dispatch_and_degrades_the_orchestrator(zones, orchestrator: OrchestratorDouble, key_file: Path) -> None:
    server, base = zones
    requester = OrchestratorEStopRequester(orchestrator.url, orchestrator.token)
    server.estop_requester = requester
    planner, planner_url = _planner(_gate(base, key_file))
    try:
        _verdict(base, 50)
        assert _release(planner_url)["released"] is True
        status, _ = http("POST", orchestrator.url + "/missions/m1/dispatch", {}, orchestrator.token)
        assert status == 200

        # a person walks into the danger zone: the zone service asks for the stop, the orchestrator latches it
        assert _verdict(base, 1)["sdkSafetyState"]["state"] == "SAFE_STOP"
        assert requester.sent and "person1" in requester.sent[0]
        status, latch = http("GET", orchestrator.url + "/estop", token=orchestrator.token)
        assert status == 200 and latch["engaged"] is True and latch["by"] == "safety-zones"

        # nothing is dispatched or started, whatever the route; the planner releases nothing either
        for route in ("dispatch", "auto-dispatch", "start"):
            status, body = http("POST", f"{orchestrator.url}/missions/m1/{route}", {}, orchestrator.token)
            assert status == 423 and body["estop"] is True, route
        assert _release(planner_url)["released"] is False
        # the orchestrator reports DEGRADED (its liveness stays "ok": it is alive, it is not moving missions)
        assert http("GET", orchestrator.url + "/health")[1]["status"] == "ok"
        report = http("GET", orchestrator.url + "/health-report")[1]
        assert report["status"] == "degraded" and "global stop" in report["detail"]

        # clearing the zone does not clear the stop: only an administrator does, an operator is refused
        _verdict(base, 50)
        assert http("POST", orchestrator.url + "/missions/m1/dispatch", {}, orchestrator.token)[0] == 423
        status, body = http("POST", orchestrator.url + "/estop/release", {"by": "ana"}, orchestrator.token)
        assert status == 403 and body["engaged"] is True
        assert http("POST", orchestrator.url + "/estop/release", {"by": "ana"})[0] == 401
        status, body = http("POST", orchestrator.url + "/estop/release", {"by": "ana"}, orchestrator.admin_token)
        assert status == 200 and body["engaged"] is False
        assert http("POST", orchestrator.url + "/missions/m1/dispatch", {}, orchestrator.token)[0] == 200
        assert http("GET", orchestrator.url + "/health-report")[1]["status"] == "ok"
    finally:
        _stop(planner)


def test_the_stop_survives_a_restart_and_an_unreadable_record_counts_as_engaged(workdir: Path) -> None:
    state = workdir / "estop-restart.json"
    first = OrchestratorDouble("t" * 20, "a" * 20, state)
    first.trigger("ana", "test")
    assert OrchestratorDouble("t" * 20, "a" * 20, state).engaged is True
    state.write_text("{ not json", encoding="utf-8")
    broken = OrchestratorDouble("t" * 20, "a" * 20, state)
    assert broken.engaged is True and broken.latch["by"] == "startup"
    state.write_text('{"engaged": "yes please", "triggers": "x"}', encoding="utf-8")
    assert OrchestratorDouble("t" * 20, "a" * 20, state).engaged is True


def test_a_stop_that_cannot_be_delivered_is_reported_not_swallowed(zones) -> None:
    server, base = zones
    server.estop_requester = OrchestratorEStopRequester(f"http://127.0.0.1:{free_port()}", "x")
    status, body = http("POST", base + "/check", _check_body(1))
    # the verdict stays a stop and says that the delivery failed: it never reads as "all clear"
    assert status == 200 and body["sdkSafetyState"]["state"] == "SAFE_STOP"
    assert "estopTransportError" in body and body["estopRequests"] == []


# --- (d) the dead-man of the presence of the operator ---------------------------------------------------------------------------------


def _run_presence(action: str) -> dict | None:
    server = repo("SERVER")
    runner = server / "node_modules" / "tsx" / "dist" / "cli.mjs"
    module = server / "src" / "operatorPresence.ts"
    if not runner.is_file() or not module.is_file() or shutil.which("node") is None:
        return None
    env = {"PRESENCE_MODULE": module.as_uri(), "PRESENCE_ACTION": action, "PATH": os.environ.get("PATH", ""), "SystemRoot": os.environ.get("SystemRoot", "")}
    result = subprocess.run(["node", str(runner), str(SDK_ROOT / "tests" / "integration" / "presence_driver.mts")], cwd=server, env=env, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr[-2000:]
    return json.loads(result.stdout.strip().splitlines()[-1])


def test_a_lost_operator_heartbeat_lowers_the_speed_and_warns() -> None:
    out = _run_presence("slow")
    if out is None:
        pytest.skip("HYDRA-UMC-SERVER with its node_modules and node are needed")
    steps = out["steps"]
    assert steps["alive"]["state"] == steps["stillAlive"]["state"] == "present" and steps["stillAlive"]["speedA"] == 100
    assert steps["lost"]["state"] == "lost" and steps["lost"]["speedA"] < 100, "the speed of the robot of that operator is lowered"
    assert steps["lost"]["playingA"] is True, "slow does not stop the robot"
    assert steps["lost"]["speedB"] == 80, "a robot held by another operator is not touched"
    assert out["warned"] == [["robot-a"]] and out["logHasLoss"] and "operator-presence-lost" in out["auditTypes"]
    assert steps["afterRaise"]["speedA"] == steps["lost"]["speedA"], "a speed raised by hand while lost goes back to the cap"
    assert steps["afterOneBeat"]["state"] == "recovering" and steps["afterOneBeat"]["speedA"] == steps["lost"]["speedA"], "one beat is not trust"
    assert steps["recovered"]["state"] == "present" and "operator-presence-restored" in out["auditTypes"]
    ramp = out["ramp"]
    assert ramp == sorted(ramp) and ramp[-1] == 100, "the speed returns along a ramp, never above what it was"


def test_the_notify_action_only_warns() -> None:
    out = _run_presence("notify")
    if out is None:
        pytest.skip("HYDRA-UMC-SERVER with its node_modules and node are needed")
    assert out["steps"]["lost"]["speedA"] == 100 and out["steps"]["lost"]["state"] == "lost" and out["warned"] == [["robot-a"]]


# --- (e) the watchdog: UNHEALTHY / UNREACHABLE and never an error read as healthy -----------------------------------------------------


@pytest.fixture(scope="module")
def watchdog_binary(workdir: Path) -> Path:
    binary = build_node_healing(workdir)
    if binary is None:
        pytest.skip("the watchdog program needs go and HYDRA-UMC-NODE-HEALING next to this repository (or HYDRA_UMC_NODE_HEALING_BIN)")
    return binary


def _transitions(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for name, state in re.findall(r"\[node-healing\] (\S+): \S+ -> (\S+)", text):
        found[name] = state
    return found


def test_the_watchdog_marks_failures_and_never_turns_an_error_into_healthy(workdir: Path, watchdog_binary: Path) -> None:
    ok = b'{"status":"ok"}'
    nodes = {
        "N-OK": NodeDouble((200, ok, {})),
        "N-DEGRADED": NodeDouble((200, b'{"status":"degraded","detail":"x"}', {})),
        "N-PERSIST": NodeDouble((200, b'{"status":"ok","persistenceHealthy":false}', {})),
        "N-ERRORBODY": NodeDouble((200, b'{"status":"error"}', {})),
        "N-503": NodeDouble((503, b'{"status":"ok"}', {})),
        "N-500": NodeDouble((500, b"boom", {})),
        "N-OTHER": NodeDouble((200, b'{"name":"SOMETHING-ELSE","status":"ok"}', {})),
        "N-REDIRECT": NodeDouble((302, b"", {"Location": "http://127.0.0.1:9/"})),
        "N-HANG": NodeDouble(None),
    }
    registry = [{"name": name, "healthUrl": node.url + "/health"} for name, node in nodes.items()]
    registry.append({"name": "N-DOWN", "healthUrl": f"http://127.0.0.1:{free_port()}/health"})
    path = workdir / "watch-nodes.json"
    path.write_text(json.dumps(registry), encoding="utf-8")
    for node in nodes.values():
        node.start()
    process = Process([str(watchdog_binary), "-nodes", str(path)], cwd=workdir)
    try:
        deadline = time.monotonic() + 40
        seen: dict[str, str] = {}
        while time.monotonic() < deadline:
            seen = _transitions(process.text())
            if len(seen) >= len(registry):
                break
            time.sleep(0.5)
        log = process.text()
    finally:
        process.stop()
        for node in nodes.values():
            node.stop()
    assert seen.get("N-OK") == "HEALTHY", log
    assert seen.get("N-DEGRADED") == "DEGRADED", log
    assert seen.get("N-PERSIST") == "DEGRADED", log
    assert seen.get("N-ERRORBODY") == "UNHEALTHY", log
    assert seen.get("N-503") == "UNHEALTHY", log
    assert seen.get("N-500") == "UNHEALTHY", log
    assert seen.get("N-OTHER") == "INVALID", log
    assert seen.get("N-REDIRECT") == "MISCONFIGURED", log
    assert seen.get("N-HANG") == "UNREACHABLE", log
    assert seen.get("N-DOWN") == "UNREACHABLE", log
    healthy = {name for name, state in seen.items() if state == "HEALTHY"}
    assert healthy == {"N-OK"}, f"only the node that answered ok is healthy, got {sorted(healthy)}"


def test_the_watchdog_sees_the_global_stop_as_degraded_and_the_release_as_healthy(workdir: Path, watchdog_binary: Path, orchestrator: OrchestratorDouble) -> None:
    """The orchestrator is watched through the route that stands for its HealthService (the gRPC probe is not exercised here)."""
    path = workdir / "watch-orch.json"
    path.write_text(json.dumps([{"name": "HYDRA-UMC-ORCHESTRATOR", "healthUrl": orchestrator.url + "/health-report"}]), encoding="utf-8")
    process = Process([str(watchdog_binary), "-nodes", str(path)], cwd=workdir)

    def wait_state(state: str, seconds: float = 20) -> bool:
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if _transitions(process.text()).get("HYDRA-UMC-ORCHESTRATOR") == state:
                return True
            time.sleep(0.5)
        return False

    try:
        assert wait_state("HEALTHY"), process.text()
        http("POST", orchestrator.url + "/estop", {"by": "test", "reason": "chain"}, orchestrator.token)
        assert wait_state("DEGRADED"), process.text()
        http("POST", orchestrator.url + "/estop/release", {"by": "ana"}, orchestrator.admin_token)
        assert wait_state("HEALTHY"), process.text()
    finally:
        process.stop()


@pytest.mark.parametrize("cell_state,expect_recovery", [("moving", False), ("stopped", True)])
def test_a_failed_node_is_not_requeued_unless_the_cell_confirms_the_robots_are_stopped(workdir: Path, watchdog_binary: Path, orchestrator: OrchestratorDouble, cell_state: str, expect_recovery: bool) -> None:
    cell = CellDouble(cell_state).start()
    fencing = workdir / f"fencing-{cell_state}.json"
    fencing.write_text(json.dumps({
        "enabled": True, "mode": "confirm", "holdUrl": cell.url + "/robots/{node}/hold", "statusUrl": cell.url + "/robots/{node}/state",
        "safeStates": ["stopped"], "confirmTimeoutSeconds": 1, "pollMillis": 100,
    }), encoding="utf-8")
    nodes = workdir / f"fence-nodes-{cell_state}.json"
    nodes.write_text(json.dumps([{"name": "NODE-A", "healthUrl": f"http://127.0.0.1:{free_port()}/health", "dispatchNode": "robot-1"}]), encoding="utf-8")
    process = Process([
        str(watchdog_binary), "-nodes", str(nodes), "-orchestrator-url", orchestrator.url, "-orchestrator-token", orchestrator.token,
        "-fencing-config", str(fencing), "-recover-confirm-after", "0s", "-startup-grace", "0s",
    ], cwd=workdir)
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            text = process.text()
            if expect_recovery and orchestrator.recoveries:
                break
            if not expect_recovery and "NOT requested" in text:
                break
            time.sleep(0.3)
        log = process.text()
    finally:
        process.stop()
        cell.stop()
    assert cell.holds, "the cell was asked to hold the robot first\n" + log
    if expect_recovery:
        assert orchestrator.recoveries == ["robot-1"], log
    else:
        assert orchestrator.recoveries == [], "no mission is requeued while the robots are not confirmed stopped\n" + log
        assert "not confirmed safe" in log


def test_without_a_fencing_file_no_recovery_is_requested(workdir: Path, watchdog_binary: Path, orchestrator: OrchestratorDouble) -> None:
    nodes = workdir / "nofence-nodes.json"
    nodes.write_text(json.dumps([{"name": "NODE-B", "healthUrl": f"http://127.0.0.1:{free_port()}/health", "dispatchNode": "robot-2"}]), encoding="utf-8")
    process = Process([
        str(watchdog_binary), "-nodes", str(nodes), "-orchestrator-url", orchestrator.url, "-orchestrator-token", orchestrator.token,
        "-recover-confirm-after", "0s", "-startup-grace", "0s",
    ], cwd=workdir)
    try:
        assert process.wait_for(r"fencing is MANDATORY", 15), process.text()
        process.wait_for(r"NODE-B: \S+ -> UNREACHABLE", 20)
        time.sleep(2)
        log = process.text()
    finally:
        process.stop()
    assert orchestrator.recoveries == [], log

# =============================================================================
# HYDRA-UMC-SDK - tests/integration/test_fake_server.py
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The stand-in server keeps state: sessions, reservations, revisions, the jog that must be armed, the global STOP."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance" / "fake-server"))
import hydra_fake_server as fake  # noqa: E402


@pytest.fixture()
def server():
    state = fake.FakeHydra(robots=2)
    httpd, _ = fake.start(state)
    yield state, f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def call(base, method, path, body=None, token=None, headers=None):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(base + path, data=data, method=method)
    request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    for key, value in (headers or {}).items():
        request.add_header(key, value)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read() or b"{}")


def sign_in(base):
    status, answer = call(base, "POST", "/api/login", {"username": "admin", "password": "admin"})
    assert status == 200
    return answer


def test_routes_need_a_session_but_the_open_ones_do_not(server):
    _, base = server
    assert call(base, "GET", "/api/hydra-info")[0] == 200
    assert call(base, "GET", "/api/settings")[0] == 401
    assert call(base, "POST", "/api/login", {"username": "admin", "password": "wrong"})[0] == 401


def test_the_refresh_token_turns_over(server):
    _, base = server
    first = sign_in(base)
    status, second = call(base, "POST", "/api/refresh", {"refreshToken": first["refreshToken"]})
    assert status == 200 and second["refreshToken"] != first["refreshToken"]
    assert call(base, "POST", "/api/refresh", {"refreshToken": first["refreshToken"]})[0] == 401
    assert call(base, "POST", "/api/logout", {"refreshToken": second["refreshToken"]})[0] == 200
    assert call(base, "POST", "/api/refresh", {"refreshToken": second["refreshToken"]})[0] == 401


def test_a_reservation_belongs_to_the_account_and_the_controller(server):
    state, base = server
    token = sign_in(base)["token"]
    status, claimed = call(base, "POST", "/api/robot/1/claim", {"controllerId": "ios-a"}, token)
    assert status == 200 and claimed["reservation"]["controllerId"] == "ios-a"
    assert call(base, "POST", "/api/robot/1/claim", {"controllerId": "ios-b"}, token)[1]["code"] == "other-controller"
    assert call(base, "POST", "/api/robot/1/claim", {}, token)[1]["code"] == "controller-id-required"
    assert [c["robotId"] for c in call(base, "GET", "/api/claims", None, token)[1]["claims"]] == [1]
    assert call(base, "POST", "/api/robot/1/release", {"controllerId": "ios-a"}, token)[0] == 200
    assert call(base, "GET", "/api/claims", None, token)[1]["claims"] == []
    state.now_ms += 1  # the clock only moves when a test moves it


def test_a_reservation_runs_out_with_the_clock(server):
    state, base = server
    token = sign_in(base)["token"]
    call(base, "POST", "/api/robot/1/claim", {"controllerId": "dsi-a"}, token)
    state.now_ms += fake.CLAIM_TTL_MS + 1
    assert call(base, "GET", "/api/claims", None, token)[1]["claims"] == []


def test_a_write_with_an_old_revision_is_refused(server):
    _, base = server
    token = sign_in(base)["token"]
    revision = call(base, "GET", "/api/robot/1", None, token)[1]["revision"]
    assert call(base, "POST", "/api/robot/1/command", {"command": "play"}, token, {"If-Match": f'"{revision}"'})[0] == 200
    status, refused = call(base, "POST", "/api/robot/1/command", {"command": "play"}, token, {"If-Match": f'"{revision}"'})
    assert status == 412 and refused["code"] == "revision-mismatch"
    # the continuous commands carry no revision, and STOP is never refused for one
    assert call(base, "POST", "/api/robot/1/jog-arm", {"armed": True}, token)[0] == 200
    assert call(base, "POST", "/api/robot/1/command", {"command": "jog"}, token, {"If-Match": f'"{revision}"'})[0] == 200
    assert call(base, "POST", "/api/robot/1/command", {"command": "stop"}, token, {"If-Match": '"old"'})[0] == 200


def test_the_jog_needs_arming_and_a_disabled_robot_only_stops(server):
    state, base = server
    token = sign_in(base)["token"]
    assert call(base, "POST", "/api/robot/2/command", {"command": "jog"}, token)[1]["code"] == "jog-not-armed"
    assert call(base, "POST", "/api/robot/2/command", {"command": "disable"}, token)[0] == 200
    status, refused = call(base, "POST", "/api/robot/2/command", {"command": "play"}, token)
    assert status == 423 and refused["code"] == "robot-disabled"
    assert call(base, "POST", "/api/robot/2/command", {"command": "stop"}, token)[0] == 200


def test_the_global_stop_stops_every_robot_and_says_so(server):
    state, base = server
    token = sign_in(base)["token"]
    status, result = call(base, "POST", "/api/stop-all", {}, token)
    assert status == 200 and result["stoppedCount"] == 2 and result["failedCount"] == 0
    assert all(r["stopped"] for r in result["robots"]) and all(r["stopped"] for r in state.robots.values())


def test_every_other_route_of_the_inventory_answers_with_its_full_body(server):
    _, base = server
    token = sign_in(base)["token"]
    status, answer = call(base, "GET", "/api/ecosystem/status", None, token)
    assert status == 200 and "projects" in answer
    assert call(base, "GET", "/api/not/a/route", None, token)[0] == 404

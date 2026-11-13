# =============================================================================
# HYDRA-UMC-SDK - Robot roster
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `RobotRoster` contract and the one way to read it from the settings of a server.

The adapters (MTConnect, OPC UA), the tools and the gateways each read `GET /api/settings` for the robots that the server has registered, and each wrote its own walk
through `controllers[].robots[]` with its own idea of what a missing field means. `roster_from_settings` is that walk, once: a robot without a usable id is skipped, a
missing `online` is false (the server has not said it is there), a missing or unknown playback state is `idle`, and `isFinished`, `isPaused` and `isPlaying` are read in
that order of precedence the way the server sets them (a finished run is not also playing). It never invents a robot: a settings answer without robots gives an empty roster.
"""

from __future__ import annotations

from typing import Any

from .contract_rules import check_fields, require_object, text, whole
from .validation import ContractValidationError

PLAYBACK_STATES: tuple[str, ...] = ("idle", "playing", "paused", "finished")
MAX_ROBOTS = 1000
MAX_CONTROLLER_ID_CHARS = 100


def _playback(state: Any) -> str:
    if not isinstance(state, dict):
        return "idle"
    if state.get("isFinished") is True:
        return "finished"
    if state.get("isPaused") is True:
        return "paused"
    if state.get("isPlaying") is True:
        return "playing"
    return "idle"


def roster_from_settings(settings: Any) -> dict[str, Any]:
    """The roster of the `controllers` of a settings answer. Never raises: what is not understood is skipped."""
    robots: list[dict[str, Any]] = []
    controllers = settings.get("controllers") if isinstance(settings, dict) else None
    for number, controller in enumerate(controllers if isinstance(controllers, list) else []):
        if not isinstance(controller, dict):
            continue
        raw_id = controller.get("id", controller.get("controllerId"))
        controller_id = raw_id if isinstance(raw_id, str) and 1 <= len(raw_id) <= MAX_CONTROLLER_ID_CHARS else f"controller-{number + 1}"
        for robot in controller.get("robots") if isinstance(controller.get("robots"), list) else []:
            if not isinstance(robot, dict) or type(robot.get("id")) is not int or robot["id"] < 0:
                continue
            if len(robots) >= MAX_ROBOTS:
                return {"schema_version": "1.0", "robots": robots}
            robots.append({
                "controller_id": controller_id,
                "robot_id": robot["id"],
                "online": robot.get("online") is True,
                "playback": _playback(robot.get("playbackState")),
            })
    return {"schema_version": "1.0", "robots": robots}


def validate_robot_roster(payload: dict[str, Any]) -> None:
    """The checks of the RobotRoster contract."""
    require_object(payload)
    check_fields(payload, ("schema_version", "robots"))
    robots = payload["robots"]
    if not isinstance(robots, list) or len(robots) > MAX_ROBOTS:
        raise ContractValidationError(f"robots must be a list of at most {MAX_ROBOTS}")
    for index, robot in enumerate(robots):
        where = f"robots[{index}]"
        require_object(robot, where)
        check_fields(robot, ("controller_id", "robot_id", "online", "playback"), label=where)
        text(robot, "controller_id", MAX_CONTROLLER_ID_CHARS)
        whole(robot, "robot_id", 0)
        if type(robot["online"]) is not bool:
            raise ContractValidationError(f"{where}.online must be true or false")
        if robot["playback"] not in PLAYBACK_STATES:
            raise ContractValidationError(f"{where}.playback must be one of {', '.join(PLAYBACK_STATES)}")

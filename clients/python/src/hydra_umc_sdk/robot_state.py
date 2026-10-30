# =============================================================================
# HYDRA-UMC-SDK - The state of one robot, as it is replicated between nodes
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `RobotState` contract: who a robot is, what it is doing, when that was true and where it is.

It is the typed value that nodes replicate (SWARM-SYNC keeps it under the key `robot_state/<robot_id>`), instead of a free string: a node that
receives a copy can check it and a consumer can read it without guessing. `estop` and `fault` are states a replica reports but never clears.
"""

from __future__ import annotations

import math
from typing import Any

from .pose import validate_pose
from .validation import ContractValidationError, _require_date_time

STATES = ("idle", "busy", "estop", "fault", "offline")
SOURCES = ("real", "simulated")


def validate_robot_state(payload: dict[str, Any]) -> None:
    """The checks of the RobotState contract, the pose included (the unit length of its quaternion too)."""
    if not isinstance(payload, dict):
        raise ContractValidationError("payload must be an object")
    for field in ("schema_version", "robot_id", "state", "updated_at_utc"):
        if field not in payload:
            raise ContractValidationError(f"missing required field: {field}")
    if payload["schema_version"] != "1.0":
        raise ContractValidationError("schema_version must be '1.0'")
    if not isinstance(payload["robot_id"], str) or not payload["robot_id"]:
        raise ContractValidationError("robot_id must be a non-empty string")
    if payload["state"] not in STATES:
        raise ContractValidationError(f"state must be one of {', '.join(STATES)}")
    if "source" in payload and payload["source"] not in SOURCES:
        raise ContractValidationError(f"source must be one of {', '.join(SOURCES)}")
    _require_date_time(payload, "updated_at_utc")
    if "mission_id" in payload and (not isinstance(payload["mission_id"], str) or not payload["mission_id"]):
        raise ContractValidationError("mission_id must be a non-empty string")
    if "battery_percent" in payload:
        battery = payload["battery_percent"]
        if isinstance(battery, bool) or not isinstance(battery, (int, float)) or not math.isfinite(battery) or not 0 <= battery <= 100:
            raise ContractValidationError("battery_percent must be a number from 0 to 100")
    if "pose" in payload:
        if not isinstance(payload["pose"], dict):
            raise ContractValidationError("pose must be a Pose object")
        try:
            validate_pose(payload["pose"])
        except ContractValidationError as error:
            raise ContractValidationError(f"pose: {error}") from error

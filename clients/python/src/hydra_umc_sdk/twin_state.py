# =============================================================================
# HYDRA-UMC-SDK - The state a digital twin exchanges
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `TwinState` contract: the joints and the named poses of one robot at one instant.

A twin and the robot (or the simulation) it follows exchange this and nothing looser: the joint states, the poses (each one a
`Pose` of the Pose contract), the instant, the frame and, above all, whether the state is of the REAL robot or of a SIMULATION.
A consumer that mixes the two up would act on a robot that is not there, so `source` is required and has two values only.
"""

from __future__ import annotations

import math
from typing import Any

from .pose import FRAMES, validate_pose
from .validation import ContractValidationError, _require_date_time

SOURCES = ("real", "simulated")


def _number(value: object, where: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ContractValidationError(f"{where} must be a finite number")


def validate_twin_state(payload: dict[str, Any]) -> None:
    """The checks of the TwinState contract, the poses included (the unit length of each quaternion too)."""
    if not isinstance(payload, dict):
        raise ContractValidationError("payload must be an object")
    for field in ("schema_version", "source", "frame", "timestamp_utc", "joint_states"):
        if field not in payload:
            raise ContractValidationError(f"missing required field: {field}")
    if payload["schema_version"] != "1.0":
        raise ContractValidationError("schema_version must be '1.0'")
    if payload["source"] not in SOURCES:
        raise ContractValidationError(f"source must be one of {', '.join(SOURCES)}")
    if payload["frame"] not in FRAMES:
        raise ContractValidationError(f"frame must be one of {', '.join(FRAMES)}")
    _require_date_time(payload, "timestamp_utc")
    if "robot_id" in payload and (not isinstance(payload["robot_id"], str) or not payload["robot_id"]):
        raise ContractValidationError("robot_id must be a non-empty string")
    if "sequence" in payload and (type(payload["sequence"]) is not int or payload["sequence"] < 0):
        raise ContractValidationError("sequence must be a non-negative integer")

    joints = payload["joint_states"]
    if not isinstance(joints, list):
        raise ContractValidationError("joint_states must be an array")
    names: set[str] = set()
    for index, joint in enumerate(joints):
        where = f"joint_states[{index}]"
        if not isinstance(joint, dict):
            raise ContractValidationError(f"{where} must be an object")
        name = joint.get("name")
        if not isinstance(name, str) or not name:
            raise ContractValidationError(f"{where}.name must be a non-empty string")
        if name in names:
            raise ContractValidationError(f"{where}.name repeats the joint {name!r}")
        names.add(name)
        if "position" not in joint:
            raise ContractValidationError(f"{where}.position is required")
        for field in ("position", "velocity", "effort"):
            if field in joint:
                _number(joint[field], f"{where}.{field}")

    poses = payload.get("poses", [])
    if not isinstance(poses, list):
        raise ContractValidationError("poses must be an array")
    for index, entry in enumerate(poses):
        where = f"poses[{index}]"
        if not isinstance(entry, dict):
            raise ContractValidationError(f"{where} must be an object")
        if not isinstance(entry.get("name"), str) or not entry["name"]:
            raise ContractValidationError(f"{where}.name must be a non-empty string")
        if not isinstance(entry.get("pose"), dict):
            raise ContractValidationError(f"{where}.pose must be a Pose object")
        try:
            validate_pose(entry["pose"])
        except ContractValidationError as error:
            raise ContractValidationError(f"{where}.pose: {error}") from error

# =============================================================================
# HYDRA-UMC-SDK - JointPoses
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `JointPoses` contract: the pose of every joint of a robot model, as the physics replica answers forward kinematics.

Each pose is a position in meters and a unit quaternion (w, x, y, z), all in one declared frame (`base`, the root link of the model). The poses go from
the root to the tip, a joint appears once, and the quaternions are unit quaternions within 1e-5. The schema is closed.
"""

from __future__ import annotations

import math
from typing import Any

from .contract_rules import check_fields, require_object
from .validation import ContractValidationError

MAX_POSES = 256
MAX_NAME_CHARS = 128
UNIT_TOLERANCE = 1e-5
FRAMES = ("base",)
_REQUIRED = ("schema_version", "frame", "poses")
_OPTIONAL = ("checked", "note")


def _number(value: Any, label: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ContractValidationError(f"{label} must be a finite number")
    return float(value)


def validate_joint_poses(payload: dict[str, Any]) -> None:
    """The checks of the JointPoses contract."""
    require_object(payload)
    check_fields(payload, _REQUIRED, _OPTIONAL)
    if payload["frame"] not in FRAMES:
        raise ContractValidationError(f"frame must be one of {', '.join(FRAMES)}")
    if "checked" in payload and not isinstance(payload["checked"], bool):
        raise ContractValidationError("checked must be true or false")
    if "note" in payload and (not isinstance(payload["note"], str) or len(payload["note"]) > 1000):
        raise ContractValidationError("note must be a text of at most 1000 characters")
    poses = payload["poses"]
    if not isinstance(poses, list) or not 1 <= len(poses) <= MAX_POSES:
        raise ContractValidationError(f"poses must be a list of 1 to {MAX_POSES}")
    seen: set[str] = set()
    for index, entry in enumerate(poses):
        label = f"poses[{index}]"
        pose = require_object(entry, label)
        check_fields(pose, ("joint", "position", "quaternion"), (), label)
        name = pose["joint"]
        if not isinstance(name, str) or not 1 <= len(name) <= MAX_NAME_CHARS:
            raise ContractValidationError(f"{label}.joint must be a text of 1 to {MAX_NAME_CHARS} characters")
        if name in seen:
            raise ContractValidationError(f"{label}.joint {name!r} appears twice")
        seen.add(name)
        position = require_object(pose["position"], f"{label}.position")
        check_fields(position, ("x", "y", "z"), (), f"{label}.position")
        for axis in ("x", "y", "z"):
            _number(position[axis], f"{label}.position.{axis}")
        quaternion = require_object(pose["quaternion"], f"{label}.quaternion")
        check_fields(quaternion, ("w", "x", "y", "z"), (), f"{label}.quaternion")
        norm = math.fsum(_number(quaternion[axis], f"{label}.quaternion.{axis}") ** 2 for axis in ("w", "x", "y", "z"))
        if abs(norm - 1.0) > UNIT_TOLERANCE:
            raise ContractValidationError(f"{label}.quaternion is not a unit quaternion (w*w + x*x + y*y + z*z = {norm:.9f})")

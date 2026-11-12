# =============================================================================
# HYDRA-UMC-SDK - Kinematics
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `Kinematics` contract: the joint ranges, the home pose and, where it is known, the chain of each robot model, in one document.

Limits and home are in degrees. A chain is written as a URDF writes its joints (the offset in meters from the parent, the rotation in radians, the
axis) and may carry the numbers it was built from. The schema is closed. `contracts/kinematics.json` is the canonical document.
"""

from __future__ import annotations

import math
from typing import Any

from .contract_rules import check_fields, require_object
from .validation import ContractValidationError

MAX_MODELS = 256
MAX_CHAIN_JOINTS = 9
_JOINT_NAMES = frozenset(f"j{n}" for n in range(1, 10))
_REQUIRED = ("schema_version", "models")
_OPTIONAL = ("note",)


def _number(value: Any, label: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ContractValidationError(f"{label} must be a finite number")
    return float(value)


def _vector3(value: Any, label: str) -> None:
    if not isinstance(value, list) or len(value) != 3:
        raise ContractValidationError(f"{label} must be a list of three numbers")
    for item in value:
        _number(item, label)


def _joint_map(value: Any, label: str, check) -> None:
    if not isinstance(value, dict) or not value:
        raise ContractValidationError(f"{label} must be a non-empty object")
    for name, item in value.items():
        if name not in _JOINT_NAMES:
            raise ContractValidationError(f"{label}: {name!r} is not a joint name (j1 to j9)")
        check(item, f"{label}.{name}")


def _limit(value: Any, label: str) -> None:
    if not isinstance(value, list) or len(value) != 2:
        raise ContractValidationError(f"{label} must be [lowest, highest]")
    low, high = _number(value[0], label), _number(value[1], label)
    if low > high:
        raise ContractValidationError(f"{label}: the lowest angle is above the highest")


def _chain(value: Any, label: str) -> None:
    chain = require_object(value, label)
    check_fields(chain, ("convention", "joints"), ("parameters",), label)
    if chain["convention"] != "urdf":
        raise ContractValidationError(f"{label}: convention must be 'urdf'")
    joints = chain["joints"]
    if not isinstance(joints, list) or not 1 <= len(joints) <= MAX_CHAIN_JOINTS:
        raise ContractValidationError(f"{label}: joints must be a list of 1 to {MAX_CHAIN_JOINTS}")
    for index, joint in enumerate(joints):
        row = require_object(joint, f"{label}.joints[{index}]")
        check_fields(row, ("pos", "rpy", "axis"), (), f"{label}.joints[{index}]")
        for field in ("pos", "rpy", "axis"):
            _vector3(row[field], f"{label}.joints[{index}].{field}")
    if "parameters" in chain:
        parameters = require_object(chain["parameters"], f"{label}.parameters")
        for name, item in parameters.items():
            _number(item, f"{label}.parameters.{name}")


def validate_kinematics(payload: dict[str, Any]) -> None:
    """The checks of the Kinematics contract."""
    require_object(payload)
    check_fields(payload, _REQUIRED, _OPTIONAL)
    if "note" in payload and not isinstance(payload["note"], str):
        raise ContractValidationError("note must be a text")
    models = require_object(payload["models"], "models")
    if not 1 <= len(models) <= MAX_MODELS:
        raise ContractValidationError(f"models must hold 1 to {MAX_MODELS} models")
    for name, entry in models.items():
        model = require_object(entry, f"model {name!r}")
        check_fields(model, ("limits", "home"), ("chain",), f"model {name!r}")
        _joint_map(model["limits"], f"model {name!r} limits", _limit)
        _joint_map(model["home"], f"model {name!r} home", lambda v, l: _number(v, l))
        if "chain" in model:
            _chain(model["chain"], f"model {name!r} chain")

# =============================================================================
# HYDRA-UMC-SDK - Visual servoing request and velocity command
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `VisualTargetRequest` and `VelocityCommand` contracts of visual servoing.

`VisualTargetRequest` is what asks the visual servoing service for one correction: where the tool is (`current`), where the image says it should be (`target`),
which frame the estimate came from, how sure the detector is, how old the estimate is and what the safety state was. Both poses are in meters and radians, with
roll, pitch and yaw as rotations about x, y and z applied in the order z, y, x (the convention of the service). `VelocityCommand` is the answer: the linear
velocity in meters per second and the angular velocity in radians per second, and the three facts a consumer needs to be safe: when it was issued
(`issued_at_ms`, milliseconds since the epoch), how long it is valid (`valid_for_ms`) and its `seq`; a consumer stops when it does not get a newer valid command
within `valid_for_ms`. Both contracts are closed, and both ends validate them with the same rules.
"""

from __future__ import annotations

from typing import Any

from .contract_rules import check_fields, identifier, one_of, real, require_object, text, whole
from .validation import ContractValidationError, _require_date_time

SAFETY_STATES: tuple[str, ...] = ("READY", "INHIBITED", "FAULT", "SAFE_STOP")
POSE_FIELDS: tuple[str, ...] = ("x", "y", "z", "roll", "pitch", "yaw")
MAX_VALID_FOR_MS = 60000

_REQUEST_REQUIRED = ("schema_version", "frame_id", "current", "target", "confidence", "safety_state")
_REQUEST_OPTIONAL = ("data_age_ms", "captured_at_utc", "calibration_version", "calibration_age_days")
_COMMAND_REQUIRED = ("schema_version", "vx", "vy", "vz", "wroll", "wpitch", "wyaw", "hold", "issued_at_ms", "valid_for_ms", "seq")
_COMMAND_OPTIONAL = ("frame_id",)


def _pose(payload: dict[str, Any], name: str) -> None:
    pose = payload[name]
    if not isinstance(pose, dict):
        raise ContractValidationError(f"{name} must be an object")
    check_fields(pose, POSE_FIELDS, (), label=name)
    for field in POSE_FIELDS:
        real(pose, field)


def validate_visual_target_request(payload: dict[str, Any]) -> None:
    """The checks of the VisualTargetRequest contract."""
    require_object(payload)
    check_fields(payload, _REQUEST_REQUIRED, _REQUEST_OPTIONAL)
    identifier(payload, "frame_id")
    _pose(payload, "current")
    _pose(payload, "target")
    real(payload, "confidence", 0, 1)
    one_of(payload, "safety_state", SAFETY_STATES)
    if "data_age_ms" not in payload and "captured_at_utc" not in payload:
        raise ContractValidationError("data_age_ms or captured_at_utc is required: a request must say how old the estimate is")
    if "data_age_ms" in payload:
        real(payload, "data_age_ms", 0)
    if "captured_at_utc" in payload:
        _require_date_time(payload, "captured_at_utc")
    if "calibration_version" in payload:
        text(payload, "calibration_version", 64)
    if "calibration_age_days" in payload:
        real(payload, "calibration_age_days", 0)


def validate_velocity_command(payload: dict[str, Any]) -> None:
    """The checks of the VelocityCommand contract."""
    require_object(payload)
    check_fields(payload, _COMMAND_REQUIRED, _COMMAND_OPTIONAL)
    for name in ("vx", "vy", "vz", "wroll", "wpitch", "wyaw"):
        real(payload, name)
    if type(payload["hold"]) is not bool:
        raise ContractValidationError("hold must be true or false")
    whole(payload, "issued_at_ms", 0)
    real(payload, "valid_for_ms", 0, MAX_VALID_FOR_MS, exclusive_minimum=True)
    whole(payload, "seq", 0)
    if payload.get("frame_id") is not None:
        identifier(payload, "frame_id")


def command_is_current(payload: dict[str, Any], now_ms: int) -> bool:
    """Whether a valid command can still be acted on at `now_ms` (milliseconds since the epoch): it was issued no later than now and its validity has not run out.

    A consumer that gets False must stop. A command issued in the future (a clock that is off) is not current either.
    """
    validate_velocity_command(payload)
    age_ms = now_ms - payload["issued_at_ms"]
    return 0 <= age_ms <= payload["valid_for_ms"]

# =============================================================================
# HYDRA-UMC-SDK - RobotState contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import pytest

from hydra_umc_sdk import ContractValidationError, validate, validate_robot_state


def _payload(**changes):
    payload = {
        "schema_version": "1.0",
        "robot_id": "arm-1",
        "state": "busy",
        "source": "real",
        "updated_at_utc": "2024-01-01T00:00:00Z",
        "mission_id": "m-1",
        "battery_percent": 80,
        "pose": {
            "schema_version": "1.0",
            "frame": "base",
            "position": {"x": 0.1, "y": 0.2, "z": 0.3},
            "orientation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
        },
    }
    payload.update(changes)
    return payload


def test_a_valid_state_is_accepted_with_or_without_the_optional_parts() -> None:
    validate("RobotState", _payload())
    minimal = {k: v for k, v in _payload().items() if k in {"schema_version", "robot_id", "state", "updated_at_utc"}}
    validate("RobotState", minimal)
    for state in ("idle", "busy", "estop", "fault", "offline"):
        validate_robot_state(_payload(state=state))


@pytest.mark.parametrize(
    "changes",
    [
        {"state": "sleeping"},
        {"state": None},
        {"robot_id": ""},
        {"robot_id": 7},
        {"source": "dreamed"},
        {"updated_at_utc": "later"},
        {"mission_id": ""},
        {"battery_percent": 101},
        {"battery_percent": -1},
        {"battery_percent": True},
        {"battery_percent": float("nan")},
        {"schema_version": "2.0"},
        {"pose": "here"},
        {"pose": {"schema_version": "1.0", "frame": "base", "position": {"x": 0, "y": 0, "z": 0}, "orientation": {"w": 2.0, "x": 0.0, "y": 0.0, "z": 0.0}}},
    ],
)
def test_a_wrong_state_is_refused(changes) -> None:
    with pytest.raises(ContractValidationError):
        validate("RobotState", _payload(**changes))


def test_each_required_field_is_required() -> None:
    for field in ("schema_version", "robot_id", "state", "updated_at_utc"):
        payload = _payload()
        del payload[field]
        with pytest.raises(ContractValidationError, match=field):
            validate("RobotState", payload)
    with pytest.raises(ContractValidationError):
        validate_robot_state([])  # type: ignore[arg-type]

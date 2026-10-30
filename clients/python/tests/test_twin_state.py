# =============================================================================
# HYDRA-UMC-SDK - TwinState contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import copy

import pytest

from hydra_umc_sdk import ContractValidationError, validate, validate_twin_state


def _payload(**changes):
    payload = {
        "schema_version": "1.0",
        "source": "real",
        "robot_id": "arm-1",
        "frame": "base",
        "timestamp_utc": "2024-01-01T00:00:00Z",
        "sequence": 7,
        "joint_states": [{"name": "shoulder", "position": 0.5, "velocity": 0.1, "effort": 2.0}, {"name": "elbow", "position": -1.0}],
        "poses": [
            {
                "name": "tcp",
                "pose": {
                    "schema_version": "1.0",
                    "frame": "base",
                    "position": {"x": 0.1, "y": 0.2, "z": 0.3},
                    "orientation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
                },
            }
        ],
    }
    payload.update(changes)
    return payload


def test_a_valid_state_is_accepted_and_the_optional_parts_may_be_missing() -> None:
    validate("TwinState", _payload())
    minimal = _payload()
    for key in ("robot_id", "sequence", "poses"):
        del minimal[key]
    validate("TwinState", minimal)
    validate("TwinState", _payload(joint_states=[], source="simulated"))


@pytest.mark.parametrize(
    "changes",
    [
        {"source": "imagined"},
        {"source": None},
        {"frame": "world"},
        {"schema_version": "2.0"},
        {"timestamp_utc": "yesterday"},
        {"robot_id": ""},
        {"sequence": -1},
        {"sequence": True},
        {"sequence": 1.5},
        {"joint_states": {"shoulder": 0.5}},
        {"joint_states": [{"position": 0.5}]},
        {"joint_states": [{"name": "a"}]},
        {"joint_states": [{"name": "a", "position": "0.5"}]},
        {"joint_states": [{"name": "a", "position": float("nan")}]},
        {"joint_states": [{"name": "a", "position": 1.0, "velocity": True}]},
        {"joint_states": [{"name": "a", "position": 1.0}, {"name": "a", "position": 2.0}]},
        {"poses": "tcp"},
        {"poses": [{"pose": {}}]},
        {"poses": [{"name": "tcp", "pose": "here"}]},
    ],
)
def test_a_wrong_state_is_refused(changes) -> None:
    with pytest.raises(ContractValidationError):
        validate("TwinState", _payload(**changes))


def test_each_required_field_is_required() -> None:
    for field in ("schema_version", "source", "frame", "timestamp_utc", "joint_states"):
        payload = _payload()
        del payload[field]
        with pytest.raises(ContractValidationError, match=field):
            validate("TwinState", payload)


def test_a_pose_must_be_a_real_pose_with_a_unit_quaternion() -> None:
    payload = _payload()
    payload["poses"][0]["pose"]["orientation"] = {"w": 1.0, "x": 1.0, "y": 0.0, "z": 0.0}
    with pytest.raises(ContractValidationError, match=r"poses\[0\]\.pose"):
        validate_twin_state(payload)
    payload = _payload()
    del payload["poses"][0]["pose"]["frame"]
    with pytest.raises(ContractValidationError, match="frame"):
        validate_twin_state(payload)


def test_a_non_object_is_refused_and_nothing_is_changed() -> None:
    with pytest.raises(ContractValidationError):
        validate_twin_state([])  # type: ignore[arg-type]
    payload = _payload()
    before = copy.deepcopy(payload)
    validate_twin_state(payload)
    assert payload == before

# =============================================================================
# HYDRA-UMC-SDK - TwinState contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import copy
import unittest

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


class TwinStateTests(unittest.TestCase):
    def test_a_valid_state_is_accepted_and_the_optional_parts_may_be_missing(self) -> None:
        validate("TwinState", _payload())
        minimal = _payload()
        for key in ("robot_id", "sequence", "poses"):
            del minimal[key]
        validate("TwinState", minimal)
        validate("TwinState", _payload(joint_states=[], source="simulated"))

    def test_a_wrong_state_is_refused(self) -> None:
        wrong = [
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
        ]
        for changes in wrong:
            with self.subTest(changes=changes):
                with self.assertRaises(ContractValidationError):
                    validate("TwinState", _payload(**changes))

    def test_each_required_field_is_required(self) -> None:
        for field in ("schema_version", "source", "frame", "timestamp_utc", "joint_states"):
            with self.subTest(field=field):
                payload = _payload()
                del payload[field]
                with self.assertRaisesRegex(ContractValidationError, field):
                    validate("TwinState", payload)

    def test_a_pose_must_be_a_real_pose_with_a_unit_quaternion(self) -> None:
        payload = _payload()
        payload["poses"][0]["pose"]["orientation"] = {"w": 1.0, "x": 1.0, "y": 0.0, "z": 0.0}
        with self.assertRaisesRegex(ContractValidationError, r"poses\[0\]\.pose"):
            validate_twin_state(payload)
        payload = _payload()
        del payload["poses"][0]["pose"]["frame"]
        with self.assertRaisesRegex(ContractValidationError, "frame"):
            validate_twin_state(payload)

    def test_a_non_object_is_refused_and_nothing_is_changed(self) -> None:
        with self.assertRaises(ContractValidationError):
            validate_twin_state([])  # type: ignore[arg-type]
        payload = _payload()
        before = copy.deepcopy(payload)
        validate_twin_state(payload)
        self.assertEqual(payload, before)


if __name__ == "__main__":
    unittest.main()

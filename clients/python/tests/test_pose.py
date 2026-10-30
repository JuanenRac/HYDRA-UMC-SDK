# =============================================================================
# HYDRA-UMC-SDK - Pose contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import math
import random
import unittest
import warnings

from hydra_umc_sdk import ContractValidationError, Pose, Quaternion, pose_from_dict, pose_to_legacy_euler, validate
from hydra_umc_sdk.pose import validate_pose


def _payload(**changes):
    payload = {
        "schema_version": "1.0",
        "frame": "base",
        "position": {"x": 0.1, "y": 0.2, "z": 0.3},
        "orientation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
    }
    payload.update(changes)
    return payload


class PoseContractTests(unittest.TestCase):
    def test_a_valid_pose_is_accepted_through_the_generic_entry_point(self) -> None:
        validate("Pose", _payload())
        pose = pose_from_dict(_payload())
        self.assertEqual(pose.position, (0.1, 0.2, 0.3))
        self.assertEqual(pose.frame, "base")
        self.assertEqual(pose.to_dict()["orientation"], {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0})

    def test_a_malformed_pose_is_refused(self) -> None:
        cases = [
            {"orientation": {"w": 1.0, "x": 1.0, "y": 0.0, "z": 0.0}},  # not a unit quaternion
            {"orientation": {"w": 1.0, "x": 0.0, "y": 0.0}},  # a component missing
            {"orientation": {"w": True, "x": 0.0, "y": 0.0, "z": 0.0}},
            {"orientation": {"w": float("nan"), "x": 0.0, "y": 0.0, "z": 0.0}},
            {"frame": "world"},
            {"position": {"x": 0.0, "y": 0.0}},
            {"position": {"x": "0", "y": 0.0, "z": 0.0}},
            {"schema_version": "2.0"},
        ]
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(ContractValidationError):
                validate_pose(_payload(**changes))

    def test_the_pose_without_orientation_is_refused(self) -> None:
        payload = _payload()
        del payload["orientation"]
        with self.assertRaises(ContractValidationError):
            validate("Pose", payload)

    def test_euler_next_to_the_quaternion_is_deprecated_and_must_agree(self) -> None:
        q = Quaternion.from_euler(0.3, -0.4, 1.2)
        consistent = _payload(orientation=q.to_dict(), euler={"roll": 0.3, "pitch": -0.4, "yaw": 1.2})
        with self.assertWarns(DeprecationWarning):
            pose_from_dict(consistent)
        contradicting = _payload(orientation=q.to_dict(), euler={"roll": 1.0, "pitch": 0.0, "yaw": 0.0})
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            with self.assertRaises(ContractValidationError):
                pose_from_dict(contradicting)

    def test_euler_round_trips_and_the_legacy_form_is_derived(self) -> None:
        random.seed(7)
        for _ in range(500):
            roll, pitch, yaw = random.uniform(-3, 3), random.uniform(-1.5, 1.5), random.uniform(-3, 3)
            q = Quaternion.from_euler(roll, pitch, yaw)
            self.assertAlmostEqual(q.norm, 1.0)
            self.assertLess(q.angle_to(Quaternion.from_euler(*q.to_euler())), 1e-6)
        legacy = pose_to_legacy_euler(Pose((0, 0, 0), Quaternion.from_euler(0.1, 0.2, 0.3)))
        for key, value in (("roll", 0.1), ("pitch", 0.2), ("yaw", 0.3)):
            self.assertAlmostEqual(legacy[key], value)

    def test_at_the_gimbal_lock_the_orientation_is_kept(self) -> None:
        for pitch in (math.pi / 2, -math.pi / 2):
            for roll, yaw in ((0.0, 0.4), (0.7, -1.1), (-2.0, 2.5)):
                q = Quaternion.from_euler(roll, pitch, yaw)
                self.assertLess(q.angle_to(Quaternion.from_euler(*q.to_euler())), 1e-6)

    def test_rotations_do_not_commute_but_compose_exactly(self) -> None:
        x90 = Quaternion.from_euler(math.pi / 2, 0, 0)
        y90 = Quaternion.from_euler(0, math.pi / 2, 0)
        self.assertGreater((x90 * y90).angle_to(y90 * x90), 1.0)  # different orientations
        self.assertLess((x90 * x90).angle_to(Quaternion.from_euler(math.pi, 0, 0)), 1e-9)
        self.assertLess((x90 * x90.conjugate()).angle_to(Quaternion.identity()), 1e-9)

    def test_the_rotation_vector_is_the_shortest_turn_and_round_trips(self) -> None:
        q = Quaternion.from_rotation_vector((0.0, 0.0, 0.5))
        for got, want in zip(q.to_rotation_vector(), (0.0, 0.0, 0.5)):
            self.assertAlmostEqual(got, want)
        flipped = Quaternion(-q.w, -q.x, -q.y, -q.z)  # q and -q are one orientation
        for got, want in zip(flipped.to_rotation_vector(), (0.0, 0.0, 0.5)):
            self.assertAlmostEqual(got, want)
        near_pi = Quaternion.from_rotation_vector((0.0, 0.0, math.pi - 0.01))
        self.assertAlmostEqual(near_pi.angle_to(Quaternion.identity()), math.pi - 0.01)
        with self.assertRaises(ContractValidationError):
            Quaternion(0, 0, 0, 0).normalized()


if __name__ == "__main__":
    unittest.main()

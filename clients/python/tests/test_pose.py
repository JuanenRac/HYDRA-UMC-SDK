# =============================================================================
# HYDRA-UMC-SDK - Pose contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

from __future__ import annotations

import math
import random
import warnings

import pytest

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


def test_a_valid_pose_is_accepted_through_the_generic_entry_point() -> None:
    validate("Pose", _payload())
    pose = pose_from_dict(_payload())
    assert pose.position == (0.1, 0.2, 0.3) and pose.frame == "base"
    assert pose.to_dict()["orientation"] == {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0}


@pytest.mark.parametrize(
    "changes",
    [
        {"orientation": {"w": 1.0, "x": 1.0, "y": 0.0, "z": 0.0}},  # not a unit quaternion
        {"orientation": {"w": 1.0, "x": 0.0, "y": 0.0}},  # a component missing
        {"orientation": {"w": True, "x": 0.0, "y": 0.0, "z": 0.0}},
        {"orientation": {"w": float("nan"), "x": 0.0, "y": 0.0, "z": 0.0}},
        {"frame": "world"},
        {"position": {"x": 0.0, "y": 0.0}},
        {"position": {"x": "0", "y": 0.0, "z": 0.0}},
        {"schema_version": "2.0"},
    ],
)
def test_a_malformed_pose_is_refused(changes) -> None:
    with pytest.raises(ContractValidationError):
        validate_pose(_payload(**changes))


def test_the_pose_without_orientation_is_refused() -> None:
    payload = _payload()
    del payload["orientation"]
    with pytest.raises(ContractValidationError):
        validate("Pose", payload)


def test_euler_alone_is_not_enough_and_next_to_the_quaternion_it_is_deprecated_and_must_agree() -> None:
    q = Quaternion.from_euler(0.3, -0.4, 1.2)
    consistent = _payload(orientation=q.to_dict(), euler={"roll": 0.3, "pitch": -0.4, "yaw": 1.2})
    with pytest.warns(DeprecationWarning):
        pose_from_dict(consistent)
    contradicting = _payload(orientation=q.to_dict(), euler={"roll": 1.0, "pitch": 0.0, "yaw": 0.0})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        with pytest.raises(ContractValidationError):
            pose_from_dict(contradicting)


def test_euler_round_trips_and_the_legacy_form_is_derived() -> None:
    random.seed(7)
    for _ in range(500):
        roll, pitch, yaw = random.uniform(-3, 3), random.uniform(-1.5, 1.5), random.uniform(-3, 3)
        q = Quaternion.from_euler(roll, pitch, yaw)
        assert q.norm == pytest.approx(1.0)
        assert q.angle_to(Quaternion.from_euler(*q.to_euler())) < 1e-6
    legacy = pose_to_legacy_euler(Pose((0, 0, 0), Quaternion.from_euler(0.1, 0.2, 0.3)))
    assert (legacy["roll"], legacy["pitch"], legacy["yaw"]) == pytest.approx((0.1, 0.2, 0.3))


def test_at_the_gimbal_lock_the_orientation_is_kept() -> None:
    for pitch in (math.pi / 2, -math.pi / 2):
        for roll, yaw in ((0.0, 0.4), (0.7, -1.1), (-2.0, 2.5)):
            q = Quaternion.from_euler(roll, pitch, yaw)
            assert q.angle_to(Quaternion.from_euler(*q.to_euler())) < 1e-6


def test_rotations_do_not_commute_but_compose_exactly() -> None:
    x90 = Quaternion.from_euler(math.pi / 2, 0, 0)
    y90 = Quaternion.from_euler(0, math.pi / 2, 0)
    assert (x90 * y90).angle_to(y90 * x90) > 1.0  # different orientations
    assert (x90 * x90).angle_to(Quaternion.from_euler(math.pi, 0, 0)) < 1e-9
    assert (x90 * x90.conjugate()).angle_to(Quaternion.identity()) < 1e-9


def test_the_rotation_vector_is_the_shortest_turn_and_round_trips() -> None:
    q = Quaternion.from_rotation_vector((0.0, 0.0, 0.5))
    assert q.to_rotation_vector() == pytest.approx((0.0, 0.0, 0.5))
    assert Quaternion(-q.w, -q.x, -q.y, -q.z).to_rotation_vector() == pytest.approx((0.0, 0.0, 0.5))  # q and -q are one orientation
    near_pi = Quaternion.from_rotation_vector((0.0, 0.0, math.pi - 0.01))
    assert near_pi.angle_to(Quaternion.identity()) == pytest.approx(math.pi - 0.01)
    with pytest.raises(ContractValidationError):
        Quaternion(0, 0, 0, 0).normalized()

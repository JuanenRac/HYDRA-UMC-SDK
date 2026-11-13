# =============================================================================
# HYDRA-UMC-SDK - edge-case tests: poses, operation results and signed commands
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Boundary and failure cases of pose.py, operation.py and signed_commands.py, with a fixed seed where random inputs are used."""
from __future__ import annotations

import math
import os
import random
import tempfile
import unittest
import warnings
from pathlib import Path

from hydra_umc_sdk.operation import OperationResult, concludes_success, parse_operation_result
from hydra_umc_sdk.pose import Quaternion, pose_from_dict, pose_to_legacy_euler
from hydra_umc_sdk.signed_commands import (
    CommandSigningError,
    CommandVerifier,
    SignedCommandSettings,
    load_key,
    sign_command,
    verify_command,
)
from hydra_umc_sdk.validation import ContractValidationError

KEY = b"k" * 40
TOPIC = "hydra/command/test"


def _pose(**over):
    payload = {
        "schema_version": "1.0",
        "frame": "base",
        "position": {"x": 0.0, "y": 0.0, "z": 0.0},
        "orientation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
    }
    payload.update(over)
    return payload


class QuaternionEdgeTests(unittest.TestCase):
    def test_a_vanishing_turn_has_a_tiny_rotation_vector(self):
        vector = Quaternion(1.0, 1e-14, 0.0, 0.0).to_rotation_vector()
        self.assertLess(math.sqrt(sum(c * c for c in vector)), 1e-12)

    def test_a_zero_rotation_vector_is_the_identity(self):
        q = Quaternion.from_rotation_vector((0.0, 0.0, 0.0))
        self.assertAlmostEqual(q.w, 1.0)
        self.assertAlmostEqual(q.norm, 1.0)

    def test_rotation_vector_round_trip_with_a_fixed_seed(self):
        rng = random.Random(4242)
        checked = 0
        for _ in range(200):
            vector = tuple(rng.uniform(-1.0, 1.0) for _ in range(3))
            back = Quaternion.from_rotation_vector(vector).to_rotation_vector()
            for a, b in zip(vector, back, strict=True):
                self.assertAlmostEqual(a, b, places=9)
            checked += 1
        self.assertEqual(checked, 200)

    def test_q_and_minus_q_are_one_orientation(self):
        q = Quaternion.from_euler(0.3, -0.2, 1.1)
        minus = Quaternion(-q.w, -q.x, -q.y, -q.z)
        self.assertAlmostEqual(q.angle_to(minus), 0.0, places=6)
        self.assertGreaterEqual(minus.canonical().w, 0.0)


class PoseRefusalTests(unittest.TestCase):
    def refused(self, payload):
        with self.assertRaises(ContractValidationError):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                pose_from_dict(payload)

    def test_not_an_object(self):
        for odd in (None, [], "pose", 7):
            self.refused(odd)

    def test_missing_fields_one_by_one(self):
        for name in ("schema_version", "frame", "position", "orientation"):
            payload = _pose()
            del payload[name]
            self.refused(payload)

    def test_wrong_version_and_frame(self):
        self.refused(_pose(schema_version="2.0"))
        self.refused(_pose(frame="moon"))

    def test_position_must_have_exactly_x_y_z_finite_numbers(self):
        self.refused(_pose(position={"x": 0, "y": 0}))
        self.refused(_pose(position={"x": 0, "y": 0, "z": 0, "w": 1}))
        for bad in (True, "1", None, float("nan"), float("inf")):
            self.refused(_pose(position={"x": bad, "y": 0, "z": 0}))

    def test_orientation_must_be_a_unit_quaternion(self):
        self.refused(_pose(orientation={"w": 2.0, "x": 0.0, "y": 0.0, "z": 0.0}))
        self.refused(_pose(orientation={"w": 1.0, "x": 0.0, "y": 0.0}))
        self.refused(_pose(orientation={"w": True, "x": 0.0, "y": 0.0, "z": 0.0}))

    def test_the_deprecated_euler_is_checked_when_present(self):
        self.refused(_pose(euler={"roll": 0.0, "pitch": 0.0}))
        self.refused(_pose(euler={"roll": "a", "pitch": 0.0, "yaw": 0.0}))
        self.refused(_pose(euler={"roll": float("nan"), "pitch": 0.0, "yaw": 0.0}))
        self.refused(_pose(euler={"roll": True, "pitch": 0.0, "yaw": 0.0}))
        self.refused(_pose(euler={"roll": 0.5, "pitch": 0.0, "yaw": 0.0}))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            pose = pose_from_dict(_pose(euler={"roll": 0.0, "pitch": 0.0, "yaw": 0.0}))
        self.assertEqual(pose.position, (0.0, 0.0, 0.0))

    def test_legacy_euler_of_a_pose(self):
        q = Quaternion.from_euler(0.1, 0.2, 0.3)
        pose = pose_from_dict(_pose(orientation=q.to_dict()))
        legacy = pose_to_legacy_euler(pose)
        self.assertAlmostEqual(legacy["roll"], 0.1, places=9)
        self.assertAlmostEqual(legacy["yaw"], 0.3, places=9)


class OperationResultEdgeTests(unittest.TestCase):
    def base(self, **over):
        payload = {"run_id": "run-1", "origin": "real", "observers_enabled": True, "outcome": "success",
                   "observed_at_utc": "2026-01-01T00:00:04Z"}
        payload.update(over)
        return payload

    def test_observers_enabled_must_be_a_real_boolean(self):
        for odd in ("false", "true", 1, 0, None):
            with self.assertRaises(ValueError):
                OperationResult(run_id="r", origin="real", observers_enabled=odd, outcome="success")

    def test_parse_refuses_what_is_not_an_object_or_is_incomplete(self):
        for odd in (None, [], "x"):
            with self.assertRaises(ContractValidationError):
                parse_operation_result(odd)
        for name in ("run_id", "origin", "observers_enabled", "outcome"):
            payload = self.base()
            del payload[name]
            with self.assertRaises(ContractValidationError):
                parse_operation_result(payload)

    def test_dates_must_be_text_valid_and_carry_a_zone(self):
        for bad in (12345, "yesterday", "2026-01-01T00:00:04"):
            with self.assertRaises(ContractValidationError):
                parse_operation_result(self.base(observed_at_utc=bad))
        self.assertIsNone(parse_operation_result(self.base(observed_at_utc="")).observed_at)

    def test_a_failure_needs_a_reason(self):
        with self.assertRaises(ContractValidationError):
            parse_operation_result(self.base(outcome="failure"))

    def test_the_gate_order_and_messages(self):
        ok = parse_operation_result(self.base())
        self.assertTrue(concludes_success(ok)[0])
        self.assertFalse(concludes_success(ok, expected_run_id="other")[0])
        silent = parse_operation_result(self.base(observers_enabled=False))
        self.assertFalse(concludes_success(silent)[0])
        unseen = parse_operation_result(self.base(observed_at_utc=None))
        self.assertFalse(concludes_success(unseen)[0])
        simulated = parse_operation_result(self.base(origin="simulated"))
        self.assertFalse(concludes_success(simulated)[0])
        accepted, reason = concludes_success(simulated, allow_simulated=True)
        self.assertTrue(accepted)
        self.assertIn("not the real machine", reason)
        failed = parse_operation_result(self.base(outcome="failure", outcome_reason="jammed"))
        self.assertEqual(concludes_success(failed), (False, "jammed"))


class SignedCommandEdgeTests(unittest.TestCase):
    def test_settings_refuse_nonsense(self):
        for bad in (-1, 1.5, True, "5"):
            with self.assertRaises(CommandSigningError):
                SignedCommandSettings(max_clock_skew_ms=bad)
        with self.assertRaises(CommandSigningError):
            SignedCommandSettings(max_expires_in_ms=0)
        with self.assertRaises(CommandSigningError):
            SignedCommandSettings(enabled=True)

    def test_signing_refuses_a_short_key_an_empty_topic_and_a_bad_expiry(self):
        with self.assertRaises(CommandSigningError):
            sign_command(TOPIC, {}, b"short")
        with self.assertRaises(CommandSigningError):
            sign_command("", {}, KEY)
        for bad in (0, -5, 1.5, True):
            with self.assertRaises(CommandSigningError):
                sign_command(TOPIC, {}, KEY, now_ms=1, expires_in_ms=bad)

    def test_verdicts_for_every_refusal(self):
        signed = sign_command(TOPIC, {"a": 1}, KEY, now_ms=1_000_000, expires_in_ms=5_000)
        self.assertTrue(verify_command(TOPIC, signed, KEY, now_ms=1_001_000).ok)
        self.assertFalse(verify_command(TOPIC, ["x"], KEY, now_ms=1).ok)
        self.assertFalse(verify_command(TOPIC, {"a": 1}, KEY, now_ms=1).ok)
        for name, value in (("issued_at_ms", -1), ("issued_at_ms", True), ("expires_in_ms", 0), ("signature", "ABC")):
            tampered = dict(signed)
            tampered[name] = value
            self.assertFalse(verify_command(TOPIC, tampered, KEY, now_ms=1_001_000).ok, (name, value))
        self.assertFalse(verify_command("other/topic", signed, KEY, now_ms=1_001_000).ok)
        self.assertFalse(verify_command(TOPIC, {**signed, "a": 2}, KEY, now_ms=1_001_000).ok)
        self.assertFalse(verify_command(TOPIC, signed, KEY, now_ms=1_006_000).ok)
        self.assertFalse(verify_command(TOPIC, signed, KEY, now_ms=1).ok)
        self.assertFalse(verify_command(TOPIC, signed, KEY, now_ms=1_001_000, max_expires_in_ms=1_000).ok)

    def test_a_body_that_cannot_be_written_is_refused_not_raised(self):
        signed = sign_command(TOPIC, {"a": 1}, KEY, now_ms=10, expires_in_ms=1000)
        signed["a"] = float("nan")
        self.assertFalse(verify_command(TOPIC, signed, KEY, now_ms=20).ok)

    def test_key_file_problems(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(CommandSigningError):
                load_key(str(Path(folder) / "none.key"))
            short = Path(folder) / "short.key"
            short.write_bytes(b"abc\n")
            if os.name == "posix":
                os.chmod(short, 0o600)
            with self.assertRaises(CommandSigningError):
                load_key(str(short))
            good = Path(folder) / "good.key"
            good.write_bytes(KEY + b"\n")
            if os.name == "posix":
                os.chmod(good, 0o600)
            self.assertEqual(load_key(str(good)), KEY)

    def test_the_verifier_short_key_is_refused_and_off_passes_everything(self):
        with self.assertRaises(CommandSigningError):
            CommandVerifier(SignedCommandSettings(enabled=True, key_file="x"), key=b"short")
        off = CommandVerifier(SignedCommandSettings())
        self.assertIsNone(off._key)


if __name__ == "__main__":
    unittest.main()

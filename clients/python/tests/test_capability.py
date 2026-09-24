# =============================================================================
# HYDRA-UMC-SDK - Capability tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import unittest
from datetime import datetime, timedelta, timezone

from hydra_umc_sdk.capability import (
    CapabilityError,
    CapabilityStatus,
    capability_check_age_seconds,
    is_capability_check_stale,
    is_capability_usable,
    parse_capability_status,
)
from hydra_umc_sdk.validation import ContractValidationError

NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _payload(**over):
    payload = {
        "schema_version": "1.0",
        "target": {"kind": "robot", "id": "controller-1:robot-3"},
        "kind": "move_to_pose",
        "declared": True,
        "last_checked_at_utc": "2026-01-01T11:59:00Z",
        "checked_configuration": "config-rev-7",
        "max_age_seconds": 3600,
        "last_check_outcome": "verified",
    }
    payload.update(over)
    return payload


class CapabilityStatusTests(unittest.TestCase):
    def test_rejects_non_positive_max_age(self):
        with self.assertRaises(CapabilityError):
            CapabilityStatus(target_kind="robot", target_id="r1", kind="move_to_pose", declared=True, max_age_seconds=0)
        with self.assertRaises(CapabilityError):
            CapabilityStatus(target_kind="robot", target_id="r1", kind="move_to_pose", declared=True, max_age_seconds=-1)

    def test_rejects_bool_masquerading_as_max_age(self):
        # Same real guard as calibration.py's own max_age_days parsing
        #: bool is a subclass of int in Python.
        with self.assertRaises(CapabilityError):
            CapabilityStatus(target_kind="robot", target_id="r1", kind="move_to_pose", declared=True, max_age_seconds=True)

    def test_rejects_unknown_last_check_outcome(self):
        with self.assertRaises(CapabilityError):
            CapabilityStatus(target_kind="robot", target_id="r1", kind="move_to_pose", declared=True, last_check_outcome="passed")


class CapabilityFreshnessTests(unittest.TestCase):
    def test_age_is_none_when_never_checked(self):
        status = CapabilityStatus(target_kind="robot", target_id="r1", kind="move_to_pose", declared=True)
        self.assertIsNone(capability_check_age_seconds(status, NOW))

    def test_never_checked_is_stale(self):
        status = CapabilityStatus(target_kind="robot", target_id="r1", kind="move_to_pose", declared=True)
        self.assertTrue(is_capability_check_stale(status, NOW))

    def test_no_max_age_declared_is_stale_even_with_a_fresh_check(self):
        status = CapabilityStatus(
            target_kind="robot", target_id="r1", kind="move_to_pose", declared=True,
            last_checked_at=NOW - timedelta(seconds=1),
        )
        self.assertTrue(is_capability_check_stale(status, NOW))

    def test_boundary_at_exactly_max_age_is_still_fresh(self):
        status = CapabilityStatus(
            target_kind="robot", target_id="r1", kind="move_to_pose", declared=True,
            last_checked_at=NOW - timedelta(seconds=30), max_age_seconds=30,
        )
        self.assertFalse(is_capability_check_stale(status, NOW))
        stale = CapabilityStatus(
            target_kind="robot", target_id="r1", kind="move_to_pose", declared=True,
            last_checked_at=NOW - timedelta(seconds=31), max_age_seconds=30,
        )
        self.assertTrue(is_capability_check_stale(stale, NOW))

    def test_future_timestamp_is_treated_as_stale_not_extra_fresh(self):
        status = CapabilityStatus(
            target_kind="robot", target_id="r1", kind="move_to_pose", declared=True,
            last_checked_at=NOW + timedelta(seconds=5), max_age_seconds=30,
        )
        self.assertTrue(is_capability_check_stale(status, NOW))


class IsCapabilityUsableTests(unittest.TestCase):
    def test_not_declared_is_never_usable_even_with_a_fresh_verified_check(self):
        status = CapabilityStatus(
            target_kind="robot", target_id="r1", kind="move_to_pose", declared=False,
            last_checked_at=NOW - timedelta(seconds=1), max_age_seconds=30, last_check_outcome="verified",
        )
        usable, reason = is_capability_usable(status, NOW)
        self.assertFalse(usable)
        self.assertIn("not declared", reason)

    def test_declared_but_never_checked_is_not_usable(self):
        status = CapabilityStatus(target_kind="robot", target_id="r1", kind="move_to_pose", declared=True)
        usable, _ = is_capability_usable(status, NOW)
        self.assertFalse(usable)

    def test_declared_but_stale_check_is_not_usable(self):
        status = CapabilityStatus(
            target_kind="robot", target_id="r1", kind="move_to_pose", declared=True,
            last_checked_at=NOW - timedelta(seconds=100), max_age_seconds=30, last_check_outcome="verified",
        )
        usable, _ = is_capability_usable(status, NOW)
        self.assertFalse(usable)

    def test_declared_with_a_failed_check_is_not_usable(self):
        status = CapabilityStatus(
            target_kind="robot", target_id="r1", kind="move_to_pose", declared=True,
            last_checked_at=NOW - timedelta(seconds=1), max_age_seconds=30,
            last_check_outcome="failed", last_check_reason="axis 3 stalled during test move",
        )
        usable, reason = is_capability_usable(status, NOW)
        self.assertFalse(usable)
        self.assertIn("axis 3 stalled", reason)

    def test_declared_with_unknown_outcome_is_not_usable(self):
        status = CapabilityStatus(
            target_kind="robot", target_id="r1", kind="move_to_pose", declared=True,
            last_checked_at=NOW - timedelta(seconds=1), max_age_seconds=30, last_check_outcome="unknown",
        )
        usable, _ = is_capability_usable(status, NOW)
        self.assertFalse(usable)

    def test_declared_and_recently_verified_is_usable(self):
        status = CapabilityStatus(
            target_kind="robot", target_id="r1", kind="move_to_pose", declared=True,
            last_checked_at=NOW - timedelta(seconds=1), max_age_seconds=30, last_check_outcome="verified",
        )
        usable, reason = is_capability_usable(status, NOW)
        self.assertTrue(usable)
        self.assertIn("move_to_pose", reason)


class ParseCapabilityStatusTests(unittest.TestCase):
    def test_parses_a_real_payload(self):
        status = parse_capability_status(_payload())
        self.assertEqual(status.target_kind, "robot")
        self.assertEqual(status.target_id, "controller-1:robot-3")
        self.assertEqual(status.kind, "move_to_pose")
        self.assertTrue(status.declared)
        self.assertEqual(status.checked_configuration, "config-rev-7")
        self.assertEqual(status.max_age_seconds, 3600)
        self.assertEqual(status.last_check_outcome, "verified")

    def test_never_checked_payload_omits_last_checked_at(self):
        payload = _payload(declared=True)
        del payload["last_checked_at_utc"]
        status = parse_capability_status(payload)
        self.assertIsNone(status.last_checked_at)

    def test_rejects_a_payload_the_contract_itself_would_reject(self):
        with self.assertRaises(ContractValidationError):
            parse_capability_status(_payload(declared="yes"))


if __name__ == "__main__":
    unittest.main()

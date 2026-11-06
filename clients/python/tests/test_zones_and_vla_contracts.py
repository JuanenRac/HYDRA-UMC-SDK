# =============================================================================
# HYDRA-UMC-SDK - SafetyZonesState and VlaApproval contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The validators, the fixtures and the schemas of the safety zones verdict and of the VLA approval say the same."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from hydra_umc_sdk import ContractValidationError, validate

FIXTURES = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1"


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class SafetyZonesStateTests(unittest.TestCase):
    def test_fixtures(self):
        validate("SafetyZonesState", fixture("safety-zones-state.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("SafetyZonesState", fixture("safety-zones-state.invalid.json"))

    def test_the_verdict_alone_is_enough(self):
        validate("SafetyZonesState", {"sdkSafetyState": fixture("safety-zones-state.valid.json")["sdkSafetyState"], "reason": None})

    def test_what_is_refused(self):
        base = fixture("safety-zones-state.valid.json")
        cases = {
            "unknown field": {"extra": 1},
            "reason as number": {"reason": 4},
            "short hash": {"configSha256": "abc"},
            "negative count": {"breachCount": -1},
            "boolean count": {"estopRequestCount": True},
            "armorInhibitOnly false": {"armorInhibitOnly": False},
            "too many breaches": {"breaches": [{"zone_id": "z", "level": "red", "object_id": "o"}] * 21},
            "breach with a position": {"breaches": [{"zone_id": "z", "level": "red", "object_id": "o", "x": 1}]},
            "unknown algorithm": {"sdkSafetyStateSignature": {"alg": "RSA", "key_id": "k", "counter": 1, "sig": "a" * 64}},
            "signature of 100 characters": {"sdkSafetyStateSignature": {"alg": "HMAC-SHA256", "key_id": "k", "counter": 1, "sig": "a" * 100}},
        }
        for label, change in cases.items():
            with self.subTest(label):
                with self.assertRaises(ContractValidationError):
                    validate("SafetyZonesState", copy.deepcopy(base) | change)

    def test_a_missing_required_field_is_named(self):
        for name in ("sdkSafetyState", "reason"):
            payload = fixture("safety-zones-state.valid.json")
            del payload[name]
            with self.assertRaisesRegex(ContractValidationError, name):
                validate("SafetyZonesState", payload)


class VlaApprovalTests(unittest.TestCase):
    def test_fixtures(self):
        validate("VlaApproval", fixture("vla-approval.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("VlaApproval", fixture("vla-approval.invalid.json"))

    def test_what_is_refused(self):
        base = fixture("vla-approval.valid.json")
        cases = {
            "not approved": {"approved": False},
            "unknown field": {"extra": 1},
            "operator empty": {"operator": ""},
            "robot too long": {"robot_id": "r" * 65},
            "time as text": {"approved_at_ms": "1"},
            "time zero": {"expires_at_ms": 0},
            "boolean time": {"approved_at_ms": True},
            "capital hex": {"signature": "A" * 64},
        }
        for label, change in cases.items():
            with self.subTest(label):
                with self.assertRaises(ContractValidationError):
                    validate("VlaApproval", copy.deepcopy(base) | change)

    def test_a_missing_required_field_is_named(self):
        for name in ("approved", "fingerprint", "robot_id", "operator", "approved_at_ms", "expires_at_ms", "signature"):
            payload = fixture("vla-approval.valid.json")
            del payload[name]
            with self.assertRaisesRegex(ContractValidationError, name):
                validate("VlaApproval", payload)


if __name__ == "__main__":
    unittest.main()

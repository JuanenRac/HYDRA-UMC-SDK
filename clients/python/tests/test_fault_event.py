# =============================================================================
# HYDRA-UMC-SDK - Fault event contract tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""`fault-event/1`: the validator, the fixtures and the schema say the same."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from hydra_umc_sdk import ContractValidationError, validate, validate_fault_event

FIXTURES = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1"


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class FaultEventTests(unittest.TestCase):
    def test_the_valid_fixture_passes_and_the_invalid_one_does_not(self):
        validate("FaultEvent", fixture("fault-event.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("FaultEvent", fixture("fault-event.invalid.json"))

    def test_only_the_four_required_fields_are_needed(self):
        validate_fault_event({"schema": "fault-event/1", "source": "s", "code": "c", "state": "cleared"})

    def test_a_missing_required_field_is_named(self):
        for name in ("schema", "source", "code", "state"):
            payload = fixture("fault-event.valid.json")
            del payload[name]
            with self.assertRaisesRegex(ContractValidationError, name):
                validate_fault_event(payload)

    def test_the_message_is_closed_and_has_no_schema_version(self):
        for extra in ({"schema_version": "1.0"}, {"robotId": "arm-1"}, {"unexpected": 1}):
            payload = fixture("fault-event.valid.json") | extra
            with self.assertRaises(ContractValidationError):
                validate_fault_event(payload)

    def test_robot_id_may_be_null_but_not_empty(self):
        payload = fixture("fault-event.valid.json")
        payload["robot_id"] = None
        validate_fault_event(payload)
        payload["robot_id"] = ""
        with self.assertRaises(ContractValidationError):
            validate_fault_event(payload)

    def test_bounds_of_the_texts(self):
        payload = fixture("fault-event.valid.json")
        for name, limit in (("source", 64), ("code", 64), ("robot_id", 64)):
            ok = copy.deepcopy(payload)
            ok[name] = "x" * limit
            validate_fault_event(ok)
            ok[name] = "x" * (limit + 1)
            with self.assertRaises(ContractValidationError):
                validate_fault_event(ok)
        payload["text"] = ""
        validate_fault_event(payload)
        payload["text"] = "x" * 240
        validate_fault_event(payload)
        payload["text"] = "x" * 241
        with self.assertRaises(ContractValidationError):
            validate_fault_event(payload)

    def test_the_value_types_are_never_converted(self):
        for name, value in (("source", 5), ("code", True), ("state", "RAISED"), ("severity", 3), ("text", None), ("schema", "fault-event/2")):
            payload = fixture("fault-event.valid.json")
            payload[name] = value
            with self.assertRaises(ContractValidationError):
                validate_fault_event(payload)


if __name__ == "__main__":
    unittest.main()

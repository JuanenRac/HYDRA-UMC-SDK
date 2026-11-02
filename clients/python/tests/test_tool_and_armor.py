# =============================================================================
# HYDRA-UMC-SDK - Tests of the tool contracts and of the alignment with A.R.M.O.R.
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from hydra_umc_sdk import (
    ContractValidationError,
    armor_alarm_to_safety_state,
    armor_state_to_event_envelope,
    armor_timestamp_ms_to_utc,
    descriptor_problems,
    state_problems,
    utc_to_armor_timestamp_ms,
    validate,
)

FIXTURES = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1"


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ToolContractTests(unittest.TestCase):
    def test_valid_fixtures_validate_and_invalid_ones_do_not(self):
        for contract, stem in (("ToolDescriptor", "tool-descriptor"), ("ToolState", "tool-state")):
            validate(contract, fixture(f"{stem}.valid.json"))
            with self.assertRaises(ContractValidationError):
                validate(contract, fixture(f"{stem}.invalid.json"))

    def test_closed_contracts_refuse_unknown_fields(self):
        for contract, stem in (("ToolDescriptor", "tool-descriptor"), ("ToolState", "tool-state")):
            payload = fixture(f"{stem}.valid.json")
            payload["password"] = "x"
            with self.assertRaises(ContractValidationError):
                validate(contract, payload)

    def test_descriptor_limits_must_be_ordered(self):
        descriptor = fixture("tool-descriptor.valid.json")
        self.assertEqual(descriptor_problems(descriptor), [])
        descriptor["limits"]["default"] = 500
        validate("ToolDescriptor", descriptor)  # the schema cannot state the order...
        self.assertEqual(descriptor_problems(descriptor), ["limits must satisfy min <= default <= max"])  # ...the rules do

    def test_a_fault_needs_its_reason_and_a_reason_needs_the_fault_state(self):
        state = fixture("tool-state.valid.json")
        self.assertEqual(state_problems(state), [])
        faulted = copy.deepcopy(state)
        faulted["thermal_fault"] = "MAXTEMP"
        self.assertEqual(state_problems(faulted), ["a critical error or a thermal fault needs the state fault"])
        faulted["state"] = "fault"
        self.assertEqual(state_problems(faulted), [])
        quiet = copy.deepcopy(state)
        quiet["state"] = "fault"
        self.assertEqual(state_problems(quiet), ["the state fault needs a critical error, a thermal fault or a CAN controller in bus-off"])
        quiet["can"] = {"state": "bus_off", "tec": 255}
        self.assertEqual(state_problems(quiet), [])
        quiet["can"]["tec"] = 12
        self.assertEqual(state_problems(quiet), ["a CAN controller in bus-off reports a transmit error counter of 255"])

    def test_a_state_is_read_against_its_descriptor(self):
        descriptor, state = fixture("tool-descriptor.valid.json"), fixture("tool-state.valid.json")
        self.assertEqual(state_problems(state, descriptor), [])
        other = copy.deepcopy(descriptor)
        other["tool_id"] = 9
        self.assertIn("the descriptor is the one of another tool", state_problems(state, other))
        high = copy.deepcopy(state)
        high["setpoint_c"] = 600
        self.assertIn("the setpoint is outside the limits of the tool", state_problems(high, descriptor))
        old = copy.deepcopy(state)
        old["firmware_version"] = "0.7.9"
        self.assertIn("the firmware of the head is older than the tool needs", state_problems(old, descriptor))
        new = copy.deepcopy(state)
        new["firmware_version"] = "0.8.0"
        self.assertEqual(state_problems(new, descriptor), [])

    def test_a_simulated_head_names_itself_and_is_still_a_state(self):
        state = fixture("tool-state.valid.json")
        state["source"] = "simulator:fake-urtc"
        validate("ToolState", state)

    def test_the_tool_table_of_urtc_validates_when_it_is_near(self):
        table = Path(__file__).resolve().parents[4] / "URTC-COMMON" / "spec" / "tools.json"
        if not table.exists():
            self.skipTest("URTC-COMMON is not next to this checkout")
        entries = json.loads(table.read_text(encoding="utf-8"))["tools"]
        self.assertGreater(len(entries), 20)
        for entry in entries:
            descriptor = {"schema_version": "1.0", "tool_id": entry["id"], "name": entry["name"], "title": entry["title"], "kind": entry["kind"]}
            for source, target in (("category", "category"), ("hero_metric", "hero_metric"), ("limits", "limits"), ("watchdog_ms", "watchdog_ms"), ("features", "features")):
                if source in entry:
                    descriptor[target] = entry[source]
            if entry.get("expansion_board"):
                descriptor["expansion_board"] = entry["expansion_board"]
            with self.subTest(tool=entry["name"]):
                self.assertEqual(descriptor_problems(descriptor), [])


class ArmorAlignmentTests(unittest.TestCase):
    ALARM = {"kind": "alarm", "node_id": "alarm-1", "timestamp_ms": 1_767_261_600_123, "phase": "alarm"}

    def test_time_converts_both_ways(self):
        self.assertEqual(armor_timestamp_ms_to_utc(0), "1970-01-01T00:00:00.000Z")
        self.assertEqual(armor_timestamp_ms_to_utc(1_767_261_600_123), "2026-01-01T10:00:00.123Z")
        self.assertEqual(utc_to_armor_timestamp_ms("2026-01-01T10:00:00.123Z"), 1_767_261_600_123)
        self.assertEqual(utc_to_armor_timestamp_ms("2026-01-01T11:00:00+01:00"), 1_767_261_600_000)
        for bad in (-1, 1.5, True, "1"):
            with self.assertRaises(ContractValidationError):
                armor_timestamp_ms_to_utc(bad)  # type: ignore[arg-type]
        for bad in ("2026-01-01T10:00:00", "1969-12-31T23:59:59Z", "no", 7):
            with self.assertRaises(ContractValidationError):
                utc_to_armor_timestamp_ms(bad)  # type: ignore[arg-type]

    def test_a_state_becomes_an_envelope_and_keeps_its_body(self):
        envelope = armor_state_to_event_envelope(self.ALARM, 7, topic="armor/alarm/alarm-1/state")
        validate("EventEnvelope", envelope)
        self.assertEqual(envelope["type"], "armor.alarm")
        self.assertEqual(envelope["source"], "armor:alarm-1")
        self.assertEqual(envelope["sequence"], 7)
        self.assertEqual(envelope["data"], self.ALARM)
        with self.assertRaises(ContractValidationError):
            armor_state_to_event_envelope(self.ALARM, 1, topic="armor/alarm/other-node/state")
        with self.assertRaises(ContractValidationError):
            armor_state_to_event_envelope({**self.ALARM, "node_id": "Bad Node"}, 1)
        with self.assertRaises(ContractValidationError):
            armor_state_to_event_envelope({**self.ALARM, "timestamp_ms": -5}, 1)

    def test_an_alarm_inhibits_and_never_stops_by_itself(self):
        state = armor_alarm_to_safety_state(self.ALARM)
        validate("SafetyState", state)
        self.assertEqual((state["state"], state["source"], state["armor_phase"]), ("INHIBITED", "armor:alarm-1", "alarm"))
        for phase in ("disarmed", "exit_delay", "armed", "entry_delay"):
            self.assertEqual(armor_alarm_to_safety_state({**self.ALARM, "phase": phase})["state"], "READY")
        from hydra_umc_sdk.armor_alignment import DEFAULT_ALARM_TO_SAFETY

        self.assertNotIn("SAFE_STOP", DEFAULT_ALARM_TO_SAFETY.values())

    def test_the_installation_may_choose_its_own_table_but_only_with_real_states(self):
        self.assertEqual(armor_alarm_to_safety_state(self.ALARM, {"alarm": "SAFE_STOP"})["state"], "SAFE_STOP")
        with self.assertRaises(ContractValidationError):
            armor_alarm_to_safety_state(self.ALARM, {"alarm": "PANIC"})
        with self.assertRaises(ContractValidationError):
            armor_alarm_to_safety_state({**self.ALARM, "phase": "unknown"})
        with self.assertRaises(ContractValidationError):
            armor_alarm_to_safety_state({**self.ALARM, "kind": "health"})


if __name__ == "__main__":
    unittest.main()

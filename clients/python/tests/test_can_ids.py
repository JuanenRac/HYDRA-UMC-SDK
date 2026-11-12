# =============================================================================
# HYDRA-UMC-SDK - Tests of the CanIds contract
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""contracts/can_ids.json: the canonical document, its schema, its fixtures, and the table of the firmware when it is next to this repository."""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

from hydra_umc_sdk.can_ids import identifier, validate_can_ids
from hydra_umc_sdk.validation import ContractValidationError, validate

try:
    import jsonschema
except ImportError:  # the optional package
    jsonschema = None

ROOT = Path(__file__).resolve().parents[3]
CANONICAL = ROOT / "contracts" / "can_ids.json"
SCHEMA = ROOT / "contracts" / "json-schema" / "v1" / "can-ids.schema.json"
FIXTURES = ROOT / "conformance" / "fixtures" / "v1"
FIRMWARE_TABLE = ROOT.parent / "HYDRA-UMC" / "tools" / "can_ids.py"
URTC_SPEC = ROOT.parent / "URTC-COMMON" / "spec" / "can_protocol.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class CanIdsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = load(CANONICAL)

    def refused(self, mutate) -> None:
        document = copy.deepcopy(self.document)
        mutate(document)
        with self.assertRaises(ContractValidationError):
            validate_can_ids(document)

    def test_the_canonical_document_passes(self) -> None:
        validate_can_ids(self.document)
        validate("CanIds", self.document)

    def test_the_fixtures_get_their_verdict(self) -> None:
        validate("CanIds", load(FIXTURES / "can-ids.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("CanIds", load(FIXTURES / "can-ids.invalid.json"))

    @unittest.skipIf(jsonschema is None, "the optional jsonschema package is not installed")
    def test_the_schema_and_the_validator_agree(self) -> None:
        validator = jsonschema.Draft202012Validator(load(SCHEMA))
        self.assertTrue(validator.is_valid(self.document))
        self.assertTrue(validator.is_valid(load(FIXTURES / "can-ids.valid.json")))
        self.assertFalse(validator.is_valid(load(FIXTURES / "can-ids.invalid.json")))

    def test_the_identifier_of_a_message_is_base_plus_slot_window_plus_offset(self) -> None:
        self.assertEqual(identifier(self.document, 0, 0x11), 0x611)
        self.assertEqual(identifier(self.document, 3, 0x01), 0x6C1)
        for slot in range(self.document["slots"]):
            for message in self.document["messages"]:
                self.assertLessEqual(identifier(self.document, slot, message["offset"]), 0x7FF)

    def test_the_emergency_stop_beats_every_slot_message(self) -> None:
        self.assertLess(self.document["estop_id"], self.document["slot_base"])

    def test_a_field_missing_or_unknown_is_refused(self) -> None:
        self.refused(lambda d: d.pop("estop_id"))
        self.refused(lambda d: d.pop("messages"))
        self.refused(lambda d: d.update(surprise=1))
        self.refused(lambda d: d["messages"][0].update(surprise=1))
        self.refused(lambda d: d["messages"][0].pop("emitter"))
        self.refused(lambda d: d.update(schema_version="2.0"))

    def test_numbers_are_whole_and_inside_the_bus(self) -> None:
        self.refused(lambda d: d.update(estop_id=0))
        self.refused(lambda d: d.update(estop_id=2048))
        self.refused(lambda d: d.update(estop_id=True))
        self.refused(lambda d: d.update(slot_base=1.5))
        self.refused(lambda d: d.update(slot_window=0))
        self.refused(lambda d: d.update(slots=0))
        self.refused(lambda d: d.update(slots=65))
        self.refused(lambda d: d.update(slot_base=2000))  # the last slot would go past 11 bits

    def test_the_stop_identifier_is_outside_the_slots(self) -> None:
        self.refused(lambda d: d.update(estop_id=d["slot_base"] + 5))

    def test_names_and_offsets_appear_once_and_fit_the_window(self) -> None:
        self.refused(lambda d: d["messages"][1].update(name=d["messages"][0]["name"]))
        self.refused(lambda d: d["messages"][1].update(offset=d["messages"][0]["offset"]))
        self.refused(lambda d: d["messages"][0].update(offset=d["slot_window"]))
        self.refused(lambda d: d["messages"][0].update(name="lower_case"))
        self.refused(lambda d: d["messages"][0].update(name="1_STARTS_WITH_DIGIT"))
        self.refused(lambda d: d["messages"][0].update(name=""))
        self.refused(lambda d: d["messages"][0].update(emitter="everybody"))
        self.refused(lambda d: d.update(messages=[]))
        self.refused(lambda d: d.update(note=5))

    def test_the_emergency_stop_frame_is_complete_and_checked(self) -> None:
        frame = self.document["estop_frame"]
        self.assertEqual(frame["bytes"][6:], ["kind_complement", "detail_complement"])
        self.refused(lambda d: d["estop_frame"].update(dlc=7))
        self.refused(lambda d: d["estop_frame"].update(bytes=list(reversed(d["estop_frame"]["bytes"]))))
        self.refused(lambda d: d["estop_frame"]["kinds"].update(ALIVE=1))
        self.refused(lambda d: d["estop_frame"]["kinds"].pop("ALIVE"))
        self.refused(lambda d: d["estop_frame"]["trip_reasons"].update(STOP_ALL=1))
        self.refused(lambda d: d["estop_frame"]["trip_reasons"].update(operator=9))
        self.refused(lambda d: d["estop_frame"]["sources"].update(KINEMATIC_BRAIN=1))
        self.refused(lambda d: d["estop_frame"]["sources"].update(HOST_BRIDGE=4))
        self.refused(lambda d: d["estop_frame"].update(surprise=1))

    def test_the_tool_head_identifiers_are_unique_and_the_stop_is_not_one_of_them(self) -> None:
        head = self.document["tool_head"]
        ids = [m["id"] for m in head["messages"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn(self.document["estop_id"], ids)
        self.assertEqual(min(ids), 0x095)
        self.refused(lambda d: d["tool_head"]["messages"][1].update(id=d["tool_head"]["messages"][0]["id"]))
        self.refused(lambda d: d["tool_head"]["messages"][1].update(name=d["tool_head"]["messages"][0]["name"]))
        self.refused(lambda d: d["tool_head"]["messages"][0].update(direction="sideways"))
        self.refused(lambda d: d["tool_head"]["messages"][0].update(id=2048))
        self.refused(lambda d: d["tool_head"].update(bus="stack_a"))
        self.refused(lambda d: d["tool_head"].update(bit_rate_bps=5))
        self.refused(lambda d: d["tool_head"].update(messages=[]))
        self.refused(lambda d: d["tool_head"].update(surprise=1))

    def test_the_optional_sections_may_be_left_out(self) -> None:
        document = copy.deepcopy(self.document)
        del document["estop_frame"], document["tool_head"]
        validate_can_ids(document)

    @unittest.skipUnless(URTC_SPEC.is_file(), "URTC-COMMON is not next to this repository")
    def test_the_tool_head_messages_are_those_of_the_urtc_spec(self) -> None:
        spec = json.loads(URTC_SPEC.read_text(encoding="utf-8"))
        theirs = {int(m["id"], 16): (m["name"], m["direction"]) for m in spec["messages"]}
        ours = {m["id"]: (m["name"], m["direction"]) for m in self.document["tool_head"]["messages"]}
        self.assertEqual(theirs, ours)
        self.assertEqual(next(c["value"] for c in spec["constants"] if c["name"] == "BITRATE"), self.document["tool_head"]["bit_rate_bps"])
        self.assertEqual(spec["protocol_version"], self.document["tool_head"]["protocol_version"])

    @unittest.skipUnless(FIRMWARE_TABLE.is_file(), "HYDRA-UMC is not next to this repository")
    def test_the_table_of_the_firmware_says_the_same(self) -> None:
        spec = importlib.util.spec_from_file_location("hydra_can_ids_firmware_table", FIRMWARE_TABLE)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        theirs = {m.name: (m.offset, m.emitter) for m in module.MESSAGES}
        ours = {m["name"]: (m["offset"], m["emitter"]) for m in self.document["messages"]}
        self.assertEqual(theirs, ours)
        self.assertEqual(module.ESTOP_CAN_ID, self.document["estop_id"])
        self.assertEqual(module.SLOT_WINDOW, self.document["slot_window"])


if __name__ == "__main__":
    unittest.main()

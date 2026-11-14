# =============================================================================
# HYDRA-UMC-SDK - Tests of the JetsonStatus contract (status of the Jetson for the display interface)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import copy
import json
import math
import random
import unittest
from pathlib import Path

from hydra_umc_sdk.jetson_status import (
    FLAG_PICTURE,
    ZONE_LEVELS,
    heartbeat_state,
    jetson_status_from_wire,
    validate_jetson_status,
    zone_level_code,
    zone_level_name,
)
from hydra_umc_sdk.validation import ContractValidationError, validate

FIXTURES = Path(__file__).resolve().parents[3] / "conformance" / "fixtures" / "v1"


def fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class JetsonStatusTests(unittest.TestCase):
    def test_the_fixtures(self):
        validate("JetsonStatus", fixture("jetson-status.valid.json"))
        with self.assertRaises(ContractValidationError):
            validate("JetsonStatus", fixture("jetson-status.invalid.json"))

    def test_each_rule_is_checked(self):
        base = fixture("jetson-status.valid.json")
        mutations = (
            lambda p: p.update(schema_version="2.0"),
            lambda p: p.update(extra=1),
            lambda p: p.pop("zone_level"),
            lambda p: p.update(zone_level="green"),
            lambda p: p.update(zone_level=3),
            lambda p: p.update(cpu_pct=-1),
            lambda p: p.update(cpu_pct=101),
            lambda p: p.update(cpu_pct=True),
            lambda p: p.update(cpu_pct=12.5),
            lambda p: p.update(temperature_c=math.nan),
            lambda p: p.update(temperature_c=math.inf),
            lambda p: p.update(temperature_c=-100.5),
            lambda p: p.update(temperature_c=200.5),
            lambda p: p.update(temperature_c="hot"),
            lambda p: p.update(camera_picture=1),
            lambda p: p.update(camera_picture="yes"),
            lambda p: p.update(uptime_s=-1),
            lambda p: p.update(uptime_s=4294967296),
            lambda p: p.update(uptime_s=1.5),
        )
        for mutate in mutations:
            payload = copy.deepcopy(base)
            mutate(payload)
            with self.assertRaises(ContractValidationError):
                validate_jetson_status(payload)

    def test_a_payload_that_is_not_an_object_is_refused(self):
        for bad in (None, [], "status", 3):
            with self.assertRaises(ContractValidationError):
                validate_jetson_status(bad)

    def test_the_limits_themselves_are_valid(self):
        base = fixture("jetson-status.valid.json")
        for field, value in (("cpu_pct", 0), ("cpu_pct", 100), ("temperature_c", -100), ("temperature_c", 200), ("uptime_s", 0), ("uptime_s", 4294967295)):
            payload = dict(base, **{field: value})
            validate_jetson_status(payload)


class WireTests(unittest.TestCase):
    def test_every_code_has_its_name_and_back(self):
        for code, name in enumerate(ZONE_LEVELS):
            self.assertEqual(zone_level_name(code), name)
            self.assertEqual(zone_level_code(name), code)

    def test_what_cannot_be_placed_reads_as_unknown_never_as_ready(self):
        for code in (-1, 6, 255, 1000, True, 2.0, None, "0"):  # True is 1 for the wire, but a code is a whole number and a boolean is not
            self.assertEqual(zone_level_name(code), "unknown", code)
        self.assertEqual(zone_level_code("green"), 5)
        self.assertEqual(zone_level_code(""), 5)

    def test_a_frame_becomes_a_valid_status(self):
        status = jetson_status_from_wire(2, 23, 524, FLAG_PICTURE, 3600)
        self.assertEqual(status, {"schema_version": "1.0", "zone_level": "danger", "cpu_pct": 23, "temperature_c": 52.4, "camera_picture": True, "uptime_s": 3600})
        validate("JetsonStatus", status)

    def test_a_load_out_of_range_is_held_and_an_unknown_code_is_unknown(self):
        status = jetson_status_from_wire(9, 250, -35, 0, 0)
        self.assertEqual((status["zone_level"], status["cpu_pct"], status["temperature_c"], status["camera_picture"]), ("unknown", 100, -3.5, False))
        self.assertEqual(jetson_status_from_wire(0, -5, 0, 0xFE, 1)["cpu_pct"], 0)

    def test_only_the_picture_bit_of_the_flags_counts(self):
        self.assertFalse(jetson_status_from_wire(0, 0, 0, 0xFE, 0)["camera_picture"])
        self.assertTrue(jetson_status_from_wire(0, 0, 0, 0xFF, 0)["camera_picture"])

    def test_any_frame_the_wire_can_carry_gives_a_valid_status(self):
        rng = random.Random(7)
        for _ in range(500):
            status = jetson_status_from_wire(rng.randrange(256), rng.randrange(256), rng.randrange(-1000, 2000), rng.randrange(256), rng.randrange(2**32))
            validate_jetson_status(status)

    def test_a_temperature_the_contract_cannot_hold_is_refused(self):
        with self.assertRaises(ContractValidationError):
            jetson_status_from_wire(0, 0, 3000, 0, 0)  # 300 degrees: a broken sensor is not shown as a reading


class HeartbeatTests(unittest.TestCase):
    def test_a_recent_status_is_alive_and_the_limit_itself_still_counts(self):
        self.assertEqual(heartbeat_state(0, 100000, 1500, 90000), "alive")
        self.assertEqual(heartbeat_state(1500, 100000, 1500, 90000), "alive")
        self.assertEqual(heartbeat_state(1501, 100000, 1500, 90000), "lost")

    def test_before_the_first_status_the_boot_grace_applies(self):
        self.assertEqual(heartbeat_state(None, 0, 1500, 90000), "starting")
        self.assertEqual(heartbeat_state(None, 89999, 1500, 90000), "starting")
        self.assertEqual(heartbeat_state(None, 90000, 1500, 90000), "lost")

    def test_the_grace_does_not_excuse_a_status_that_stopped(self):
        self.assertEqual(heartbeat_state(5000, 10, 1500, 90000), "lost")

    def test_a_clock_that_went_back_is_lost(self):
        self.assertEqual(heartbeat_state(-1, 5000, 1500, 90000), "lost")
        self.assertEqual(heartbeat_state(None, -1, 1500, 90000), "lost")

    def test_the_answer_is_always_one_of_the_states(self):
        from hydra_umc_sdk.jetson_status import HEARTBEAT_STATES

        rng = random.Random(11)
        for _ in range(300):
            since = rng.choice([None, rng.randrange(-5, 200000)])
            self.assertIn(heartbeat_state(since, rng.randrange(-5, 200000), rng.randrange(0, 5000), rng.randrange(0, 100000)), HEARTBEAT_STATES)


if __name__ == "__main__":
    unittest.main()

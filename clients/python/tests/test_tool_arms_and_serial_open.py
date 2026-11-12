# =============================================================================
# HYDRA-UMC-SDK - Tests of the tool arms contract edges and of opening a serial port
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Every refusal of the ToolArms checks, one field at a time, and the opening of a real serial port with the library replaced.

The opening must declare the control lines off before the port is opened (an open line resets a GRBL board and loses the job), must say so when pyserial is
missing, and resolves a USB identifier to the path it has right now or fails instead of guessing.
"""

from __future__ import annotations

import copy
import sys
import tempfile
import types
import unittest
from unittest import mock

from hydra_umc_sdk.serial_link import open_serial_port, open_serial_port_by_id, resolve_serial_device_path
from hydra_umc_sdk.tool_arms import MAX_ARMS, MAX_TOOL_ID, validate_tool_arms
from hydra_umc_sdk.validation import ContractValidationError


def arm(**over):
    base = {"robot": "arm-1", "toolId": 3, "armed": True, "by": "urtc", "seq": 7, "ageSeconds": 1.5, "stale": False}
    base.update(over)
    return base


def payload(**over):
    base = {"schema_version": "1.0", "ttlSeconds": 30, "arms": [arm()], "armedCount": 1, "staleCount": 0}
    base.update(over)
    return base


class ToolArmsEdgeTests(unittest.TestCase):
    def refuses(self, document, pattern):
        with self.assertRaisesRegex(ContractValidationError, pattern):
            validate_tool_arms(document)

    def test_a_good_document_and_the_empty_one_pass(self):
        validate_tool_arms(payload())
        validate_tool_arms(payload(arms=[], armedCount=0, staleCount=0))

    def test_what_is_not_an_object_is_refused(self):
        for bad in (None, [], "text", 5):
            with self.subTest(bad), self.assertRaises(ContractValidationError):
                validate_tool_arms(bad)  # type: ignore[arg-type]

    def test_a_missing_field_an_unknown_field_and_another_schema_version_are_refused(self):
        for name in ("schema_version", "ttlSeconds", "arms", "armedCount", "staleCount"):
            document = payload()
            del document[name]
            with self.subTest(name):
                self.refuses(document, "missing required field")
        self.refuses(payload(extra=1), "unsupported field")
        self.refuses(payload(schema_version="2.0"), "schema_version")

    def test_the_time_to_live_is_a_positive_finite_number(self):
        for bad in (0, -1, float("inf"), float("nan"), True, "30", None):
            with self.subTest(bad):
                self.refuses(payload(ttlSeconds=bad), "ttlSeconds")
        validate_tool_arms(payload(ttlSeconds=0.001))

    def test_arms_is_a_list_of_at_most_the_limit(self):
        self.refuses(payload(arms={}), "arms must be a list")
        self.refuses(payload(arms="none"), "arms must be a list")
        many = [arm(toolId=i % (MAX_TOOL_ID + 1)) for i in range(MAX_ARMS)]
        validate_tool_arms(payload(arms=many, armedCount=MAX_ARMS))
        self.refuses(payload(arms=many + [arm()], armedCount=0), "at most")

    def test_an_entry_that_is_not_an_object_or_has_a_wrong_field_set_is_refused(self):
        self.refuses(payload(arms=["x"]), "arm must be an object")
        for name in ("robot", "toolId", "armed", "by", "seq", "ageSeconds", "stale"):
            entry = arm()
            del entry[name]
            with self.subTest(name):
                self.refuses(payload(arms=[entry]), "arm: missing required field")
        self.refuses(payload(arms=[arm(color="red")]), "arm: unsupported field")

    def test_the_robot_id_is_a_short_id_of_the_allowed_characters(self):
        for bad in ("", " ", "-lead", ".lead", "has space", "a/b", "x" * 65, 5, None):
            with self.subTest(repr(bad)):
                self.refuses(payload(arms=[arm(robot=bad)]), "robot must be a robot id")
        for good in ("a", "A1", "arm-1", "cell_2".replace("_", "."), "r:1", "x" * 64):
            validate_tool_arms(payload(arms=[arm(robot=good)]))

    def test_the_tool_id_is_a_whole_number_in_range(self):
        for bad in (-1, MAX_TOOL_ID + 1, 1.5, True, "3", None):
            with self.subTest(repr(bad)):
                self.refuses(payload(arms=[arm(toolId=bad)]), "toolId")
        for good in (0, MAX_TOOL_ID):
            validate_tool_arms(payload(arms=[arm(toolId=good)]))

    def test_armed_and_stale_are_real_booleans(self):
        for name in ("armed", "stale"):
            for bad in (1, 0, "true", None, "yes"):
                with self.subTest(f"{name}={bad!r}"):
                    self.refuses(payload(arms=[arm(**{name: bad})]), f"{name} must be true or false")

    def test_who_reported_is_a_text_of_at_most_64_characters(self):
        for bad in (5, None, ["x"], "y" * 65):
            with self.subTest(repr(bad)):
                self.refuses(payload(arms=[arm(by=bad)]), "by must be a text")
        validate_tool_arms(payload(arms=[arm(by="")]))
        validate_tool_arms(payload(arms=[arm(by="y" * 64)]))

    def test_the_sequence_starts_at_one_and_the_age_at_zero(self):
        for bad in (0, -3, 1.0, True, "1"):
            with self.subTest(repr(bad)):
                self.refuses(payload(arms=[arm(seq=bad)]), "seq")
        for bad in (-0.001, float("nan"), float("inf"), True, "1"):
            with self.subTest(repr(bad)):
                self.refuses(payload(arms=[arm(ageSeconds=bad)]), "ageSeconds")
        validate_tool_arms(payload(arms=[arm(ageSeconds=0)]))

    def test_the_counts_are_whole_numbers_from_zero(self):
        for name in ("armedCount", "staleCount"):
            for bad in (-1, 1.5, True, "1", None):
                with self.subTest(f"{name}={bad!r}"):
                    self.refuses(payload(**{name: bad}), name)

    def test_the_document_is_not_changed_by_checking_it(self):
        document = payload()
        before = copy.deepcopy(document)
        validate_tool_arms(document)
        self.assertEqual(document, before)


class FakeSerialModule(types.ModuleType):
    """A pyserial stand-in that records, in order, what is set on the port before it is opened."""

    def __init__(self):
        super().__init__("serial")
        outer = self
        self.events = []

        class Serial:
            def __init__(self):
                object.__setattr__(self, "_values", {})

            def __setattr__(self, name, value):
                outer.events.append(("set", name, value))
                self._values[name] = value

            def open(self):
                outer.events.append(("open",))

        self.Serial = Serial


class OpenSerialPortTests(unittest.TestCase):
    def test_the_control_lines_are_declared_off_before_the_port_is_opened(self):
        fake = FakeSerialModule()
        with mock.patch.dict(sys.modules, {"serial": fake}):
            connection = open_serial_port("COM7", baud=250000, timeout_seconds=0.25)
        events = fake.events
        self.assertEqual(events[-1], ("open",), "open is the last thing that happens")
        before = {name: value for kind, *rest in events[:-1] for name, value in [tuple(rest)]}
        self.assertEqual(before, {"port": "COM7", "baudrate": 250000, "timeout": 0.25, "dsrdtr": False, "rtscts": False, "dtr": False, "rts": False})
        self.assertIs(type(connection).__name__, "Serial")

    def test_the_defaults_are_115200_baud_and_a_one_second_timeout(self):
        fake = FakeSerialModule()
        with mock.patch.dict(sys.modules, {"serial": fake}):
            open_serial_port("/dev/ttyUSB0")
        values = {event[1]: event[2] for event in fake.events if event[0] == "set"}
        self.assertEqual((values["baudrate"], values["timeout"]), (115200, 1.0))

    def test_without_pyserial_the_error_says_what_to_install(self):
        with mock.patch.dict(sys.modules, {"serial": None}):
            with self.assertRaisesRegex(RuntimeError, "pyserial is not installed"):
                open_serial_port("COM7")

    def test_a_port_that_cannot_be_opened_is_the_error_of_the_library(self):
        fake = FakeSerialModule()
        original = fake.Serial.open

        def failing(self):
            original(self)
            raise OSError("busy")
        fake.Serial.open = failing
        with mock.patch.dict(sys.modules, {"serial": fake}):
            with self.assertRaisesRegex(OSError, "busy"):
                open_serial_port("COM7")


class Port:
    def __init__(self, device, serial_number=None, hwid=""):
        self.device, self.serial_number, self.hwid = device, serial_number, hwid


class ResolveDeviceTests(unittest.TestCase):
    def test_an_existing_path_is_returned_as_it_is_without_listing_ports(self):
        with tempfile.NamedTemporaryFile() as handle:
            def refuse():
                raise AssertionError("ports were listed")
            self.assertEqual(resolve_serial_device_path(handle.name, list_ports=refuse), handle.name)

    def test_a_serial_number_or_a_part_of_the_hardware_id_names_the_port(self):
        ports = [Port("COM3", "AAA", "USB VID:PID=1111:2222 SER=AAA"), Port("COM9", "BBB", "USB VID:PID=3333:4444 SER=BBB LOCATION=1-2")]
        self.assertEqual(resolve_serial_device_path("BBB", list_ports=lambda: ports), "COM9")
        self.assertEqual(resolve_serial_device_path("VID:PID=1111", list_ports=lambda: ports), "COM3")
        self.assertEqual(resolve_serial_device_path("LOCATION=1-2", list_ports=lambda: ports), "COM9")

    def test_the_first_match_wins_when_two_ports_match(self):
        ports = [Port("COM3", None, "SER=X1"), Port("COM4", "X1", "")]
        self.assertEqual(resolve_serial_device_path("X1", list_ports=lambda: ports), "COM3")

    def test_a_port_without_a_hardware_id_or_serial_number_is_skipped_not_a_crash(self):
        ports = [Port("COM1", None, None), Port("COM2", None, ""), Port("COM5", "KEY", "")]
        self.assertEqual(resolve_serial_device_path("KEY", list_ports=lambda: ports), "COM5")

    def test_nothing_that_matches_is_an_error_that_names_the_id_never_a_guess(self):
        for ports in ([], [Port("COM1", "AAA", "SER=AAA")]):
            with self.subTest(len(ports)), self.assertRaisesRegex(RuntimeError, "no currently-connected serial device matches id 'ZZZ'"):
                resolve_serial_device_path("ZZZ", list_ports=lambda ports=ports: ports)

    def test_without_pyserial_a_device_that_is_not_a_path_cannot_be_resolved(self):
        with mock.patch.dict(sys.modules, {"serial": None, "serial.tools": None, "serial.tools.list_ports": None}):
            with self.assertRaisesRegex(RuntimeError, "pyserial is not installed"):
                resolve_serial_device_path("no-such-path-or-id")

    def test_the_real_port_lister_is_used_when_none_is_given(self):
        listing = types.ModuleType("serial.tools.list_ports")
        listing.comports = lambda: [Port("COM11", "SERIALX", "")]  # type: ignore[attr-defined]
        tools = types.ModuleType("serial.tools")
        tools.list_ports = listing  # type: ignore[attr-defined]
        package = types.ModuleType("serial")
        package.tools = tools  # type: ignore[attr-defined]
        with mock.patch.dict(sys.modules, {"serial": package, "serial.tools": tools, "serial.tools.list_ports": listing}):
            self.assertEqual(resolve_serial_device_path("SERIALX"), "COM11")

    def test_opening_by_id_resolves_first_and_then_opens_that_path_with_the_given_settings(self):
        fake = FakeSerialModule()
        ports = [Port("COM8", "KEY", "")]
        with mock.patch.dict(sys.modules, {"serial": fake}):
            open_serial_port_by_id("KEY", baud=9600, timeout_seconds=2.0, list_ports=lambda: ports)
        values = {event[1]: event[2] for event in fake.events if event[0] == "set"}
        self.assertEqual((values["port"], values["baudrate"], values["timeout"]), ("COM8", 9600, 2.0))

    def test_opening_by_an_unknown_id_opens_nothing(self):
        fake = FakeSerialModule()
        with mock.patch.dict(sys.modules, {"serial": fake}):
            with self.assertRaises(RuntimeError):
                open_serial_port_by_id("GHOST", list_ports=lambda: [])
        self.assertEqual(fake.events, [])


if __name__ == "__main__":
    unittest.main()

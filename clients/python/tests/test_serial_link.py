# =============================================================================
# HYDRA-UMC-SDK - Shared GRBL serial link tests
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
import os
import unittest

from hydra_umc_sdk.serial_link import (
    CYCLE_START_RESUME,
    FEED_HOLD,
    SOFT_RESET,
    STATUS_QUERY,
    ReconnectingSerialConnection,
    call_bool,
    open_serial_port,
    parse_status_report,
    read_status_line,
    resolve_serial_device_path,
    send_realtime,
)


class FakeSerial:
    """A deterministic stand-in for a pyserial connection: a script of lines, the way a controller talks."""

    def __init__(self, lines=(b"<Idle|MPos:0,0,0>\n",)):
        self.lines = list(lines)
        self.written = []
        self.closed = False
        self.raise_on_write = None
        self.write_return_value = None
        self.report_byte_count = True
        self.discarded = 0

    def write(self, data):
        if self.raise_on_write:
            raise self.raise_on_write
        self.written.append(data)
        if not self.report_byte_count:
            return None
        return self.write_return_value if self.write_return_value is not None else len(data)

    def readline(self):
        return self.lines.pop(0) if self.lines else b""

    def reset_input_buffer(self):
        self.discarded += 1

    @property
    def in_waiting(self):
        return sum(len(line) for line in self.lines)

    def close(self):
        self.closed = True


class FakePortInfo:
    def __init__(self, device, serial_number=None, hwid=""):
        self.device, self.serial_number, self.hwid = device, serial_number, hwid


class StatusLineTests(unittest.TestCase):
    def test_the_query_byte_is_the_grbl_status_request(self):
        self.assertEqual(STATUS_QUERY, b"?")
        self.assertEqual(FEED_HOLD, b"!")
        self.assertEqual(CYCLE_START_RESUME, b"~")
        self.assertEqual(SOFT_RESET, b"\x18")

    def test_sends_the_query_and_returns_the_report(self):
        connection = FakeSerial([b"<Run|MPos:1,2,3|FS:500,0>\r\n"])
        self.assertEqual(read_status_line(connection), "<Run|MPos:1,2,3|FS:500,0>")
        self.assertEqual(connection.written, [b"?"])
        self.assertEqual(connection.discarded, 1)

    def test_skips_the_banner_ok_and_messages_until_the_report(self):
        connection = FakeSerial([b"Grbl 1.1h ['$' for help]\r\n", b"ok\r\n", b"[MSG:Caution]\r\n", b"<Idle|MPos:0,0,0>\r\n"])
        self.assertEqual(read_status_line(connection), "<Idle|MPos:0,0,0>")

    def test_no_report_is_an_empty_string(self):
        self.assertEqual(read_status_line(FakeSerial([b"ok\r\n"])), "")
        self.assertEqual(read_status_line(FakeSerial([])), "")

    def test_the_newest_of_several_waiting_reports_wins(self):
        connection = FakeSerial([b"<Run|MPos:0,0,0>\r\n", b"<Idle|MPos:9,9,9>\r\n"])
        self.assertEqual(read_status_line(connection), "<Idle|MPos:9,9,9>")

    def test_a_link_failure_propagates_so_the_caller_can_fail_closed(self):
        connection = FakeSerial()
        connection.raise_on_write = OSError("unplugged")
        with self.assertRaises(OSError):
            read_status_line(connection)


class SendRealtimeTests(unittest.TestCase):
    def test_a_full_write_is_executed(self):
        connection = FakeSerial()
        result = send_realtime(connection, FEED_HOLD, "feed hold sent")
        self.assertTrue(result.allowed and result.executed)
        self.assertEqual(result.reason, "feed hold sent")
        self.assertEqual(connection.written, [b"!"])

    def test_a_failing_link_is_not_executed(self):
        connection = FakeSerial()
        connection.raise_on_write = OSError("gone")
        result = send_realtime(connection, FEED_HOLD, "x")
        self.assertTrue(result.allowed)
        self.assertFalse(result.executed)
        self.assertIn("serial write failed", result.reason)

    def test_a_short_or_zero_write_is_not_executed(self):
        for count in (0, 2):
            with self.subTest(count=count):
                connection = FakeSerial()
                connection.write_return_value = count
                self.assertFalse(send_realtime(connection, b"!", "x").executed)

    def test_a_count_that_is_not_a_real_int_is_never_trusted(self):
        for value in (None, True, "1", 1.0):
            with self.subTest(value=value):
                connection = FakeSerial()
                connection.write = lambda data, value=value: value  # type: ignore[method-assign]
                self.assertFalse(send_realtime(connection, b"!", "x").executed)

    def test_a_count_larger_than_the_command_is_not_trusted(self):
        connection = FakeSerial()
        connection.write_return_value = 5
        self.assertFalse(send_realtime(connection, b"!", "x").executed)


class CallBoolTests(unittest.TestCase):
    def test_only_a_real_bool_is_trusted(self):
        self.assertTrue(call_bool(lambda: True, False))
        self.assertFalse(call_bool(lambda: 1, False))
        self.assertTrue(call_bool(lambda: "yes", True))

    def test_a_getter_that_raises_takes_the_safe_default(self):
        def boom():
            raise RuntimeError("sensor")

        self.assertTrue(call_bool(boom, True))
        self.assertFalse(call_bool(boom, False))


class OpenSerialPortTests(unittest.TestCase):
    def test_missing_pyserial_is_a_clear_runtime_error(self):
        try:
            import serial  # noqa: F401

            self.skipTest("pyserial is installed in this environment")
        except ImportError:
            pass
        with self.assertRaises(RuntimeError) as context:
            open_serial_port("COM3")
        self.assertIn("pyserial is not installed", str(context.exception))


class ResolveSerialDevicePathTests(unittest.TestCase):
    def test_an_existing_path_is_returned_as_is(self):
        this_file = os.path.abspath(__file__)
        self.assertEqual(resolve_serial_device_path(this_file), this_file)

    def test_a_serial_number_resolves_to_the_current_path(self):
        ports = [FakePortInfo("/dev/ttyUSB0", serial_number="AB123"), FakePortInfo("/dev/ttyUSB1", serial_number="ZZ999")]
        self.assertEqual(resolve_serial_device_path("AB123", list_ports=lambda: ports), "/dev/ttyUSB0")

    def test_a_replug_that_changes_the_port_name_still_resolves(self):
        self.assertEqual(resolve_serial_device_path("AB123", list_ports=lambda: [FakePortInfo("COM3", "AB123")]), "COM3")
        self.assertEqual(resolve_serial_device_path("AB123", list_ports=lambda: [FakePortInfo("COM5", "AB123")]), "COM5")

    def test_a_hwid_substring_resolves(self):
        ports = [FakePortInfo("COM4", None, "USB VID:PID=1A86:7523 SER=AB123")]
        self.assertEqual(resolve_serial_device_path("VID:PID=1A86:7523", list_ports=lambda: ports), "COM4")

    def test_a_device_that_is_not_connected_is_a_clear_error(self):
        with self.assertRaises(RuntimeError) as context:
            resolve_serial_device_path("not-plugged-in", list_ports=lambda: [])
        self.assertIn("not-plugged-in", str(context.exception))


class ReconnectingSerialConnectionTests(unittest.TestCase):
    def test_opens_lazily(self):
        opened = []

        def connect():
            opened.append(FakeSerial())
            return opened[-1]

        link = ReconnectingSerialConnection(connect)
        self.assertEqual(opened, [])
        link.write(b"?")
        self.assertEqual(len(opened), 1)

    def test_a_write_failure_reconnects_once_and_retries(self):
        first = FakeSerial()
        first.raise_on_write = OSError("device disconnected")
        second = FakeSerial()
        connections = [first, second]
        link = ReconnectingSerialConnection(lambda: connections.pop(0))
        self.assertEqual(link.write(b"?"), 1)
        self.assertTrue(first.closed)
        self.assertEqual(second.written, [b"?"])

    def test_a_read_failure_reconnects_once_and_retries(self):
        class Flaky(FakeSerial):
            def __init__(self, fail):
                super().__init__([b"<Idle|MPos:0,0,0>\n"])
                self.fail = fail

            def readline(self):
                if self.fail:
                    raise OSError("device disconnected")
                return super().readline()

        connections = [Flaky(True), Flaky(False)]
        link = ReconnectingSerialConnection(lambda: connections.pop(0))
        self.assertEqual(link.readline(), b"<Idle|MPos:0,0,0>\n")

    def test_a_failed_reconnect_is_an_oserror(self):
        first = FakeSerial()
        first.raise_on_write = OSError("device disconnected")
        calls = {"n": 0}

        def connect():
            calls["n"] += 1
            if calls["n"] == 1:
                return first
            raise RuntimeError("no such device")

        link = ReconnectingSerialConnection(connect)
        with self.assertRaises(OSError):
            link.write(b"?")

    def test_a_status_query_survives_a_replug(self):
        first = FakeSerial()
        first.raise_on_write = OSError("unplugged")
        second = FakeSerial([b"<Idle|MPos:0,0,0>\n"])
        connections = [first, second]
        link = ReconnectingSerialConnection(lambda: connections.pop(0))
        self.assertEqual(read_status_line(link), "<Idle|MPos:0,0,0>")
        self.assertTrue(first.closed)

    def test_close_closes_the_connection_and_a_later_use_reopens(self):
        made = []

        def connect():
            made.append(FakeSerial())
            return made[-1]

        link = ReconnectingSerialConnection(connect)
        link.write(b"?")
        link.close()
        self.assertTrue(made[0].closed)
        link.write(b"?")
        self.assertEqual(len(made), 2)



class ParseStatusReportTests(unittest.TestCase):
    def test_reads_every_field_of_a_full_report(self):
        report = parse_status_report("<Run|MPos:1.000,2.000,-3.500|FS:500,12000|WCO:10,20,0|Ov:100,50,110|Pn:XD>")
        self.assertEqual(report.state, "Run")
        self.assertEqual(report.machine_position, (1.0, 2.0, -3.5))
        self.assertEqual(report.work_offset, (10.0, 20.0, 0.0))
        self.assertEqual(report.feed_rate, 500.0)
        self.assertEqual(report.spindle_speed, 12000.0)
        self.assertEqual(report.overrides, (100.0, 50.0, 110.0))
        self.assertEqual(report.pins, "XD")

    def test_a_work_position_report(self):
        report = parse_status_report("<Idle|WPos:0.000,0.000,0.000|F:250>")
        self.assertEqual(report.work_position, (0.0, 0.0, 0.0))
        self.assertEqual(report.feed_rate, 250.0)
        self.assertIsNone(report.spindle_speed)

    def test_the_substate_stays_in_the_state_token(self):
        self.assertEqual(parse_status_report("<Hold:0|MPos:0,0,0>").state, "Hold:0")

    def test_a_missing_field_is_none_never_zero(self):
        report = parse_status_report("<Idle|MPos:0,0,0>")
        self.assertIsNone(report.feed_rate)
        self.assertIsNone(report.spindle_speed)
        self.assertIsNone(report.overrides)

    def test_values_that_are_not_finite_numbers_are_dropped(self):
        for text in ("<Idle|FS:nan,0>", "<Idle|FS:inf,5>", "<Idle|FS:abc,def>", "<Idle|FS:1>", "<Idle|MPos:1,x,3>", "<Idle|Ov:1,2>"):
            with self.subTest(text=text):
                report = parse_status_report(text)
                self.assertEqual(report.state, "Idle")
                self.assertIsNone(report.feed_rate)
                self.assertIsNone(report.machine_position)
                self.assertIsNone(report.overrides)

    def test_what_is_not_a_report_is_empty(self):
        for value in ("ok", "", "<Idle", "Idle>", None, 5, b"<Idle>"):
            with self.subTest(value=value):
                self.assertEqual(parse_status_report(value).state, "")


if __name__ == "__main__":
    unittest.main()

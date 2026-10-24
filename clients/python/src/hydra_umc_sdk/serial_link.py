# =============================================================================
# HYDRA-UMC-SDK - Shared GRBL serial link
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""What every bridge that talks to a GRBL controller over a serial port needs.

The CNC bridge and the laser bridge both read a GRBL controller and both may send
GRBL's own real-time bytes. They share this module instead of keeping a copy each:

- ``SerialLike``: the three calls the logic needs, so every safety rule is testable with an in-memory fake;
- ``open_serial_port`` / ``open_serial_port_by_id`` / ``resolve_serial_device_path``: the one place that imports
  ``pyserial`` (lazily), opening the port without resetting an Arduino-based board, and finding a device by a stable id;
- ``ReconnectingSerialConnection``: reopens the same device after a cable replug;
- ``read_status_line``: sends ``?`` and returns the answer to *that* query, not an old line from the stream;
- ``send_realtime``: writes one real-time byte and reports whether it was really written;
- ``parse_status_report``: reads a status report into its fields (state, positions, feed and spindle/laser speed, overrides).

It never streams a G-code program. A GRBL controller has ONE serial port: whoever holds it open keeps every other sender out.
"""

from __future__ import annotations

import math
import os
import threading
import time
from dataclasses import dataclass
from typing import Callable, Protocol

# Real GRBL v1.1 real-time command bytes: each is handled at once, out of band from the line-buffered G-code channel.
STATUS_QUERY = b"?"
FEED_HOLD = b"!"
CYCLE_START_RESUME = b"~"
SOFT_RESET = b"\x18"  # Ctrl-X

# GRBL talks without being asked: the banner after every reset (opening the port resets an Arduino), "ok"/"error:N",
# "[MSG:...]", "ALARM:n", and the late answer to an earlier "?". The answer to OUR "?" is the first line that looks like a
# status report, within this many lines or this long.
MAX_LINES_PER_QUERY = 16
QUERY_DEADLINE_SECONDS = 2.0


class SerialLike(Protocol):
    """The minimal real serial interface the logic depends on."""

    def write(self, data: bytes) -> object: ...
    def readline(self) -> bytes: ...
    def close(self) -> object: ...


def call_bool(getter: Callable[[], object], safe_default: bool) -> bool:
    """Read a safety signal and fail closed: only a real ``bool`` is trusted, and a getter that raises is a missing reading."""
    try:
        value = getter()
    except Exception:  # noqa: BLE001 - any failure to read a signal fails closed, deliberately broad
        return safe_default
    return value if isinstance(value, bool) else safe_default


def open_serial_port(port: str, baud: int = 115200, timeout_seconds: float = 1.0) -> SerialLike:
    """Open a real serial port. The only place this module imports pyserial.

    The port is created closed, the control lines are declared off and only then is it opened: opening it with DTR
    asserted resets an Arduino-based GRBL board and a running job is lost. Raises ``RuntimeError`` with a clear message
    when pyserial is not installed.
    """

    try:
        import serial  # type: ignore[import-untyped]
    except ImportError as error:
        raise RuntimeError(
            "pyserial is not installed - install it to talk to a real GRBL controller "
            "(the parsing and gating logic works and is tested without it)"
        ) from error
    connection = serial.Serial()
    connection.port = port
    connection.baudrate = baud
    connection.timeout = timeout_seconds
    connection.dsrdtr = False
    connection.rtscts = False
    connection.dtr = False
    connection.rts = False
    connection.open()
    return connection


def resolve_serial_device_path(device_id: str, *, list_ports: Callable[[], list] | None = None) -> str:
    """Resolve a stable USB device identifier to whatever path or port name it has right now.

    Two shapes are accepted: an existing path (a Linux ``/dev/serial/by-id/...`` link, stable per physical device) is
    returned as is; anything else is the device's serial number or a substring of its ``hwid`` and is matched against
    ``list_ports()`` (what a Windows ``COM*`` reconnect needs). ``list_ports`` defaults to
    ``serial.tools.list_ports.comports`` and is injectable. Raises ``RuntimeError`` (never a guess) when nothing matches:
    a device that is not plugged in right now is a condition a reconnect loop retries.
    """

    if os.path.exists(device_id):
        return device_id

    if list_ports is None:
        try:
            from serial.tools.list_ports import comports as list_ports  # type: ignore[import-untyped]
        except ImportError as error:
            raise RuntimeError(
                "pyserial is not installed - install it to resolve a USB device by id "
                "(the parsing and gating logic works and is tested without it)"
            ) from error

    for port in list_ports():
        hwid = getattr(port, "hwid", "") or ""
        serial_number = getattr(port, "serial_number", None)
        if serial_number == device_id or device_id in hwid:
            return port.device

    raise RuntimeError(f"no currently-connected serial device matches id {device_id!r}")


def open_serial_port_by_id(
    device_id: str,
    baud: int = 115200,
    timeout_seconds: float = 1.0,
    *,
    list_ports: Callable[[], list] | None = None,
) -> SerialLike:
    """Open the serial port of a device identified by a stable USB id rather than an OS-assigned port name."""

    port = resolve_serial_device_path(device_id, list_ports=list_ports)
    return open_serial_port(port, baud=baud, timeout_seconds=timeout_seconds)


class ReconnectingSerialConnection:
    """A ``SerialLike`` that reopens the same physical device after a real I/O failure.

    ``connect`` opens one connection (in production ``lambda: open_serial_port_by_id(device_id, ...)``). A write or read
    that raises ``OSError`` closes the dead connection, reconnects once and retries the operation once. When the reconnect
    itself fails the failure comes out as an ``OSError`` wrapping the cause, so the callers, which fail closed on it,
    never see an exception type they do not expect from a port.

    Several threads may share one connection (a status query on one, a feed hold on another): the lock only guards
    swapping the connection, never the blocking I/O, so a stop never waits for a read to time out.
    """

    def __init__(self, connect: Callable[[], SerialLike]) -> None:
        self._connect = connect
        self._connection: SerialLike | None = None
        self._lock = threading.Lock()

    def _open(self) -> SerialLike:
        try:
            return self._connect()
        except OSError:
            raise
        except Exception as error:  # noqa: BLE001 - "no such device" and the like are a port that is not there
            raise OSError(f"could not open the serial device: {error}") from error

    def _ensure_connected(self) -> SerialLike:
        with self._lock:
            if self._connection is None:
                self._connection = self._open()
            return self._connection

    def _reconnect(self, failed: SerialLike) -> SerialLike:
        with self._lock:
            if self._connection is not None and self._connection is not failed:
                return self._connection  # another thread has already reopened it
            if self._connection is not None:
                try:
                    self._connection.close()
                except Exception:  # noqa: BLE001 - closing an already-dead connection must never mask the real error
                    pass
                self._connection = None
            self._connection = self._open()
            return self._connection

    def write(self, data: bytes) -> object:
        connection = self._ensure_connected()
        try:
            return connection.write(data)
        except OSError:
            connection = self._reconnect(connection)
            return connection.write(data)

    def readline(self) -> bytes:
        connection = self._ensure_connected()
        try:
            return connection.readline()
        except OSError:
            connection = self._reconnect(connection)
            return connection.readline()

    def reset_input_buffer(self) -> None:
        """Throw away what the controller has sent that nobody asked for (when the underlying port can)."""
        connection = self._ensure_connected()
        discard = getattr(connection, "reset_input_buffer", None)
        if discard is not None:
            discard()

    @property
    def in_waiting(self) -> int:
        """Bytes already received and not read yet (0 when the underlying port cannot tell)."""
        with self._lock:
            connection = self._connection
        return int(getattr(connection, "in_waiting", 0) or 0)

    def close(self) -> object:
        with self._lock:
            connection, self._connection = self._connection, None
        return connection.close() if connection is not None else None


def is_status_report(line: str) -> bool:
    """A GRBL status report is the one line shaped ``<...>``."""
    return line.startswith("<") and line.endswith(">")


def read_status_line(connection: SerialLike) -> str:
    """Ask GRBL for its status and return the report that answers *this* query.

    What ``readline()`` hands back is not necessarily the answer to the ``?`` just sent: the banner, ``ok``, ``error:N``,
    ``[MSG:...]``, ``ALARM:n`` and the late answer to an earlier ``?`` all come on the same stream, and taking the next line
    would leave every later query one reply behind. So: discard what is already waiting, send ``?`` and read until a line
    that is a status report turns up, keeping the newest when several are waiting. Returns ``""`` when none arrived (an
    empty read is the port's own timeout). A failure of the link propagates: the caller decides how to fail closed.
    """

    discard = getattr(connection, "reset_input_buffer", None)
    if discard is not None:
        discard()
    connection.write(STATUS_QUERY)
    deadline = time.monotonic() + QUERY_DEADLINE_SECONDS
    latest = ""
    for _ in range(MAX_LINES_PER_QUERY):
        raw = connection.readline()
        if not raw:
            break  # the port timed out: nothing more is coming
        line = raw.decode("ascii", errors="replace").strip()
        if is_status_report(line):
            latest = line
            # a second report already waiting means the first was an old one: the newest is the truth
            if int(getattr(connection, "in_waiting", 0) or 0) <= 0:
                break
        if time.monotonic() >= deadline:
            break
    return latest


@dataclass(frozen=True)
class RealtimeCommandResult:
    """A real command outcome with its reason, not a bare bool that loses why."""

    allowed: bool
    executed: bool
    reason: str


def send_realtime(connection: SerialLike, command: bytes, ok_reason: str) -> RealtimeCommandResult:
    """Write one real-time byte and say whether it really went out.

    A failing link is a command that did not happen, not a crash. A real ``write()`` returns the int number of bytes
    written and, for a fully sent command, it equals ``len(command)``: a short count, ``None``, a bool or any other type is
    reported as not executed instead of a confirmed write. "Bytes sent" is not "the action completed", and is never
    claimed to be.
    """

    try:
        written = connection.write(command)
    except Exception as error:  # noqa: BLE001
        return RealtimeCommandResult(True, False, f"serial write failed: {error}")
    if not isinstance(written, int) or isinstance(written, bool):
        return RealtimeCommandResult(True, False, f"serial write did not report a real byte count sent (got {written!r})")
    if written != len(command):
        return RealtimeCommandResult(True, False, f"serial write incomplete: {written}/{len(command)} bytes sent")
    return RealtimeCommandResult(True, True, ok_reason)


@dataclass(frozen=True)
class GrblReport:
    """The fields of one GRBL v1.1 status report ``<State|MPos:..|FS:f,s|...>``.

    Every field that the report did not carry, or carried in a form that is not a finite number, is ``None``: a missing
    reading is never a zero. ``feed_rate`` and ``spindle_speed`` come from ``FS:f,s`` (or ``F:f`` when the variable spindle
    is off); the spindle speed is the laser power on a laser build.
    """

    state: str
    machine_position: tuple[float, ...] | None = None
    work_position: tuple[float, ...] | None = None
    work_offset: tuple[float, ...] | None = None
    feed_rate: float | None = None
    spindle_speed: float | None = None
    overrides: tuple[float, float, float] | None = None  # feed %, rapid %, spindle %
    pins: str | None = None


def _numbers(text: str, count_min: int = 1, count_max: int = 6) -> tuple[float, ...] | None:
    try:
        values = tuple(float(part) for part in text.split(","))
    except ValueError:
        return None
    if not (count_min <= len(values) <= count_max) or not all(math.isfinite(value) for value in values):
        return None
    return values


def parse_status_report(line: object) -> GrblReport:
    """Read a status report; anything that is not one is an empty report (``state == ""``), never an exception."""

    if not isinstance(line, str) or not is_status_report(line.strip()):
        return GrblReport("")
    fields = line.strip()[1:-1].split("|")
    state = fields[0]
    report: dict[str, object] = {}
    for field_text in fields[1:]:
        name, _, value = field_text.partition(":")
        if name == "MPos":
            report["machine_position"] = _numbers(value)
        elif name == "WPos":
            report["work_position"] = _numbers(value)
        elif name == "WCO":
            report["work_offset"] = _numbers(value)
        elif name == "FS":
            pair = _numbers(value, 2, 2)
            if pair is not None:
                report["feed_rate"], report["spindle_speed"] = pair
        elif name == "F":
            single = _numbers(value, 1, 1)
            if single is not None:
                report["feed_rate"] = single[0]
        elif name == "Ov":
            triple = _numbers(value, 3, 3)
            if triple is not None:
                report["overrides"] = triple
        elif name == "Pn":
            report["pins"] = value
    return GrblReport(state, **report)  # type: ignore[arg-type]

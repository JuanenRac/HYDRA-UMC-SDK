# =============================================================================
# HYDRA-UMC-SDK - Data contract of the status of the Jetson
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `JetsonStatus` contract: what the Jetson tells the display interface of the H757 on every status poll.

On the SPI link the H757 is the master and asks; the Jetson answers with one status frame (verdict of the safety zones service, load and temperature, a flag for a
waiting camera picture and its uptime). This module gives that answer a name that every client reads the same way: `zone_level` is one of `ZONE_LEVELS` (on the
wire the position in the list, 0 to 5), the temperature is in degrees and the picture flag is a boolean. A code the panel cannot place reads as `unknown`, never as
`ready`. The arrival of the status is the heartbeat; `heartbeat_state` says what a master does with the time since the last one, with the limits it takes from its
configuration file (nothing is fixed here).

The schema holds the shape; the clients also check that the numbers are finite and whole where the wire has whole numbers.
"""

from __future__ import annotations

from typing import Any

from .contract_rules import check_fields, one_of, real, require_object, whole
from .validation import ContractValidationError

ZONE_LEVELS: tuple[str, ...] = ("ready", "warning", "danger", "inhibited", "fault", "unknown")
ZONE_UNKNOWN = len(ZONE_LEVELS) - 1
FLAG_PICTURE = 0x01
HEARTBEAT_STATES: tuple[str, ...] = ("alive", "starting", "lost")
_REQUIRED = ("schema_version", "zone_level", "cpu_pct", "temperature_c", "camera_picture", "uptime_s")


def validate_jetson_status(payload: dict[str, Any]) -> None:
    """The checks of the JetsonStatus contract."""
    require_object(payload)
    check_fields(payload, _REQUIRED)
    one_of(payload, "zone_level", ZONE_LEVELS)
    whole(payload, "cpu_pct", 0, 100)
    real(payload, "temperature_c", -100, 200)
    if type(payload["camera_picture"]) is not bool:
        raise ContractValidationError("camera_picture must be true or false")
    whole(payload, "uptime_s", 0, 4294967295)


def zone_level_name(code: int) -> str:
    """The name of a zone level code of the wire; a code outside 0 to 5 (or not a whole number) is `unknown`."""
    if type(code) is int and 0 <= code < len(ZONE_LEVELS):
        return ZONE_LEVELS[code]
    return ZONE_LEVELS[ZONE_UNKNOWN]


def zone_level_code(name: str) -> int:
    """The code of the wire for a zone level name; a name that is not in `ZONE_LEVELS` is the code of `unknown`."""
    return ZONE_LEVELS.index(name) if name in ZONE_LEVELS else ZONE_UNKNOWN


def jetson_status_from_wire(zone_code: int, cpu_pct: int, temperature_x10: int, flags: int, uptime_s: int) -> dict[str, Any]:
    """The contract object for the fields of one status frame (temperature in tenths of a degree). The load is held between 0 and 100 and an unknown zone code
    reads as `unknown`; the result always passes `validate_jetson_status` for the values a frame can carry."""
    status = {
        "schema_version": "1.0",
        "zone_level": zone_level_name(zone_code),
        "cpu_pct": max(0, min(100, int(cpu_pct))),
        "temperature_c": int(temperature_x10) / 10,
        "camera_picture": bool(int(flags) & FLAG_PICTURE),
        "uptime_s": int(uptime_s),
    }
    validate_jetson_status(status)
    return status


def heartbeat_state(since_last_ms: int | None, now_ms: int, timeout_ms: int, boot_grace_ms: int) -> str:
    """What the master makes of the silence of the Jetson: `alive` when the last status is no older than `timeout_ms`, `starting` while none has come and the
    master itself is still inside `boot_grace_ms` of its start, otherwise `lost`. `since_last_ms` is None when no status has been heard yet. Both limits come from
    the configuration of the master; a negative age is a clock that went back and counts as lost."""
    if since_last_ms is not None:
        return "alive" if 0 <= since_last_ms <= timeout_ms else "lost"
    return "starting" if 0 <= now_ms < boot_grace_ms else "lost"

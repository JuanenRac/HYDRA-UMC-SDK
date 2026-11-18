# =============================================================================
# HYDRA-UMC-SDK - Zone occupancy (the message that says which zones are occupied)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The occupancy message of the safety zones, as a consumer reads it.

    {"occupied": ["press-1"], "observed_at": <wall-clock milliseconds>, "known": true}

`occupied` lists the zones with something in them. `observed_at` is when the emitter looked. `known` is optional and means "the emitter could see the zones":
`false` says that it could not (a sensor out, a camera blind), so the empty `occupied` list is NOT "free" but "not known". A message without `known` is read as before
(`known` true), so an emitter that does not send it changes nothing. The schema is closed: any other field makes the message unreadable.

A stamp in the future (more than `max_future_ms` ahead of the clock of the reader) is refused: an emitter with a wrong clock must not look fresh for ever.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

DEFAULT_MAX_FUTURE_MS = 2000
MAX_ZONES = 256
MAX_ZONE_ID_CHARS = 128
MAX_BYTES = 65536
_FIELDS = frozenset({"occupied", "observed_at", "known"})


class OccupancyError(ValueError):
    """The message is not a usable occupancy report (unreadable, wrong types, too large or stamped in the future)."""


@dataclass(frozen=True)
class Occupancy:
    """`known` False means the emitter could not see: `occupied` is then empty and says nothing about free zones."""

    occupied: frozenset[str]
    observed_at_ms: int
    known: bool = True


def parse_occupancy(payload: bytes | str | dict, *, now_ms: int, max_future_ms: int = DEFAULT_MAX_FUTURE_MS) -> Occupancy:
    """The occupancy a message stands for, or `OccupancyError`. `now_ms` is the wall clock of the reader in milliseconds."""
    if isinstance(payload, (bytes, str)):
        if len(payload) > MAX_BYTES:
            raise OccupancyError("the message is too large")
        try:
            payload = json.loads(payload)
        except ValueError as error:
            raise OccupancyError("the message is not JSON") from error
    if not isinstance(payload, dict):
        raise OccupancyError("the message must be an object")
    extra = set(payload) - _FIELDS
    if extra:
        raise OccupancyError("the message has fields that are not part of the contract")
    stamp = payload.get("observed_at")
    if isinstance(stamp, bool) or not isinstance(stamp, (int, float)) or not math.isfinite(stamp) or stamp < 0:
        raise OccupancyError("observed_at must be a number of milliseconds")
    stamp = int(stamp)
    if stamp > now_ms + max_future_ms:
        raise OccupancyError("observed_at is in the future")
    known = payload.get("known", True)
    if not isinstance(known, bool):
        raise OccupancyError("known must be true or false")
    zones = payload.get("occupied", [])
    if not isinstance(zones, list) or len(zones) > MAX_ZONES:
        raise OccupancyError(f"occupied must be a list of at most {MAX_ZONES} zones")
    for zone in zones:
        if not isinstance(zone, str) or not zone or len(zone) > MAX_ZONE_ID_CHARS:
            raise OccupancyError(f"a zone is a text of 1 to {MAX_ZONE_ID_CHARS} characters")
    if not known:
        return Occupancy(frozenset(), stamp, False)
    return Occupancy(frozenset(zones), stamp, True)

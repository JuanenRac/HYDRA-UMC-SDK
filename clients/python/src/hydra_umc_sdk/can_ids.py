# =============================================================================
# HYDRA-UMC-SDK - CanIds
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `CanIds` contract: the CAN identifiers of the stack bus of HYDRA-UMC, in one document.

The identifier of a message is `slot_base + slot * slot_window + offset`. The checks that a schema cannot say: every identifier fits in 11 bits, an offset is inside
the window, a name and an offset appear once, the slot windows do not run into the emergency stop identifier, and the whole range of the slots fits the bus.
`contracts/can_ids.json` is the canonical document.
"""

from __future__ import annotations

from typing import Any

from .contract_rules import check_fields, require_object
from .validation import ContractValidationError

MAX_IDENTIFIER = 0x7FF
MAX_MESSAGES = 256
EMITTERS = ("kinematic-brain", "controller-board", "bootloader", "host")
_REQUIRED = ("schema_version", "estop_id", "slot_base", "slot_window", "slots", "messages")
_OPTIONAL = ("note", "estop_frame", "tool_head")
ESTOP_BYTES = ["kind", "detail", "source", "epoch", "sequence_low", "sequence_high", "kind_complement", "detail_complement"]
ESTOP_KINDS = ("TRIP", "RELEASE", "ALIVE")
ESTOP_SOURCES = ("KINEMATIC_BRAIN", "SLOT_BOARD_FIRST", "SLOT_BOARD_LAST", "HOST_BRIDGE")
DIRECTIONS = ("host_to_board", "board_to_host", "both")


def _named_numbers(value, label: str, low: int, high: int, *, count: tuple[int, int]) -> dict:
    section = require_object(value, label)
    if not count[0] <= len(section) <= count[1]:
        raise ContractValidationError(f"{label} must hold {count[0]} to {count[1]} entries")
    for name, number in section.items():
        if not isinstance(name, str) or not name or len(name) > 64 or not name.replace("_", "").isalnum() or name != name.upper():
            raise ContractValidationError(f"{label}: {name!r} is not a name in capital letters")
        _integer(number, f"{label}.{name}", low, high)
    return section


def _validate_estop_frame(value) -> None:
    frame = require_object(value, "estop_frame")
    check_fields(frame, ("dlc", "bytes", "kinds", "trip_reasons", "sources"), (), "estop_frame")
    if frame["dlc"] != 8 or type(frame["dlc"]) is not int:
        raise ContractValidationError("estop_frame.dlc must be 8")
    if frame["bytes"] != ESTOP_BYTES:
        raise ContractValidationError("estop_frame.bytes must be the 8 fields of the frame, in order")
    kinds = _named_numbers(frame["kinds"], "estop_frame.kinds", 1, 255, count=(3, 3))
    if set(kinds) != set(ESTOP_KINDS):
        raise ContractValidationError(f"estop_frame.kinds must be {', '.join(ESTOP_KINDS)}")
    if len(set(kinds.values())) != 3:
        raise ContractValidationError("estop_frame.kinds: two kinds share a value")
    reasons = _named_numbers(frame["trip_reasons"], "estop_frame.trip_reasons", 1, 255, count=(1, 32))
    if len(set(reasons.values())) != len(reasons):
        raise ContractValidationError("estop_frame.trip_reasons: two reasons share a value")
    sources = _named_numbers(frame["sources"], "estop_frame.sources", 0, 255, count=(4, 4))
    if set(sources) != set(ESTOP_SOURCES):
        raise ContractValidationError(f"estop_frame.sources must be {', '.join(ESTOP_SOURCES)}")
    if sources["KINEMATIC_BRAIN"] != 0 or not 0 < sources["SLOT_BOARD_FIRST"] <= sources["SLOT_BOARD_LAST"] < sources["HOST_BRIDGE"]:
        raise ContractValidationError("estop_frame.sources: the brain is 0, the slot boards are a range above it, the bridge is above the range")


def _validate_tool_head(value) -> None:
    head = require_object(value, "tool_head")
    check_fields(head, ("source", "protocol_version", "bit_rate_bps", "bus", "messages"), (), "tool_head")
    if not isinstance(head["source"], str) or not 1 <= len(head["source"]) <= 200:
        raise ContractValidationError("tool_head.source must be a text of 1 to 200 characters")
    _integer(head["protocol_version"], "tool_head.protocol_version", 1, 65535)
    _integer(head["bit_rate_bps"], "tool_head.bit_rate_bps", 10000, 1000000)
    if head["bus"] != "tool_head_downlink":
        raise ContractValidationError("tool_head.bus must be tool_head_downlink")
    messages = head["messages"]
    if not isinstance(messages, list) or not 1 <= len(messages) <= 512:
        raise ContractValidationError("tool_head.messages must be a list of 1 to 512")
    ids: set[int] = set()
    names: set[str] = set()
    for index, entry in enumerate(messages):
        label = f"tool_head.messages[{index}]"
        message = require_object(entry, label)
        check_fields(message, ("id", "name", "direction"), (), label)
        identifier_value = _integer(message["id"], f"{label}.id", 0, MAX_IDENTIFIER)
        if identifier_value in ids:
            raise ContractValidationError(f"{label}.id {identifier_value} is used by another message")
        ids.add(identifier_value)
        name = message["name"]
        if not isinstance(name, str) or not name or len(name) > 64 or not name.isascii() or not name.replace("_", "").isalnum() or not name[0].isalpha() or name != name.upper():
            raise ContractValidationError(f"{label}.name must be capital letters, digits and underscores, starting with a letter (at most 64)")
        if name in names:
            raise ContractValidationError(f"{label}.name {name!r} appears twice")
        names.add(name)
        if message["direction"] not in DIRECTIONS:
            raise ContractValidationError(f"{label}.direction must be one of {', '.join(DIRECTIONS)}")


def _integer(value: Any, label: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ContractValidationError(f"{label} must be a whole number from {low} to {high}")
    return value


def identifier(document: dict[str, Any], slot: int, offset: int) -> int:
    """The identifier of the message at `offset` of `slot`."""
    return document["slot_base"] + slot * document["slot_window"] + offset


def validate_can_ids(payload: dict[str, Any]) -> None:
    """The checks of the CanIds contract."""
    require_object(payload)
    check_fields(payload, _REQUIRED, _OPTIONAL)
    if "note" in payload and (not isinstance(payload["note"], str) or len(payload["note"]) > 2000):
        raise ContractValidationError("note must be a text of at most 2000 characters")
    estop = _integer(payload["estop_id"], "estop_id", 1, MAX_IDENTIFIER)
    base = _integer(payload["slot_base"], "slot_base", 0, MAX_IDENTIFIER)
    window = _integer(payload["slot_window"], "slot_window", 1, MAX_IDENTIFIER + 1)
    slots = _integer(payload["slots"], "slots", 1, 64)
    last = base + slots * window - 1
    if last > MAX_IDENTIFIER:
        raise ContractValidationError(f"the slots reach the identifier {last}, past the 11 bits of a standard identifier")
    if base <= estop <= last:
        raise ContractValidationError("the emergency stop identifier is inside the slot windows")
    messages = payload["messages"]
    if not isinstance(messages, list) or not 1 <= len(messages) <= MAX_MESSAGES:
        raise ContractValidationError(f"messages must be a list of 1 to {MAX_MESSAGES}")
    names: set[str] = set()
    offsets: set[int] = set()
    for index, entry in enumerate(messages):
        label = f"messages[{index}]"
        message = require_object(entry, label)
        check_fields(message, ("name", "offset", "emitter"), (), label)
        name = message["name"]
        if not isinstance(name, str) or not name or len(name) > 64 or not name.isascii() or not name.replace("_", "").isalnum() or not name[0].isalpha() or name != name.upper():
            raise ContractValidationError(f"{label}.name must be capital letters, digits and underscores, starting with a letter (at most 64)")
        if name in names:
            raise ContractValidationError(f"{label}.name {name!r} appears twice")
        names.add(name)
        offset = _integer(message["offset"], f"{label}.offset", 0, MAX_IDENTIFIER)
        if offset >= window:
            raise ContractValidationError(f"{label}.offset {offset} is outside the window of {window} identifiers")
        if offset in offsets:
            raise ContractValidationError(f"{label}.offset {offset} is used by another message")
        offsets.add(offset)
        if message["emitter"] not in EMITTERS:
            raise ContractValidationError(f"{label}.emitter must be one of {', '.join(EMITTERS)}")
    if "estop_frame" in payload:
        _validate_estop_frame(payload["estop_frame"])
    if "tool_head" in payload:
        _validate_tool_head(payload["tool_head"])

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
_OPTIONAL = ("note",)


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

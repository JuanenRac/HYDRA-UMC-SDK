# =============================================================================
# HYDRA-UMC-SDK - Fault event
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `FaultEvent` contract (`fault-event/1`): a fault that is raised or cleared, published by a service on the broker under `hydra/faults/`.

The server reads these messages, keeps the active faults and the history and offers them to the feeds. Until this contract existed the only definition of the
shape was the parser of the server. The field that names the contract is `schema` (it carries its own version), not `schema_version`; the schema is closed.
A reader is more forgiving than this validator (it takes an unknown severity as `error` and cuts long texts): the validator is what an emitter checks its
own message against before it publishes.
"""

from __future__ import annotations

from typing import Any

from .contract_rules import check_fields, one_of, require_object, text
from .validation import ContractValidationError

SCHEMA = "fault-event/1"
STATES: tuple[str, ...] = ("raised", "cleared")
SEVERITIES: tuple[str, ...] = ("info", "warning", "error", "critical")
MAX_NAME = 64
MAX_TEXT = 240

_REQUIRED = ("schema", "source", "code", "state")
_OPTIONAL = ("severity", "robot_id", "text")


def validate_fault_event(payload: dict[str, Any]) -> None:
    """The checks of the FaultEvent contract."""
    require_object(payload)
    check_fields(payload, _REQUIRED, _OPTIONAL)
    if payload["schema"] != SCHEMA:
        raise ContractValidationError(f"schema must be '{SCHEMA}'")
    text(payload, "source", MAX_NAME)
    text(payload, "code", MAX_NAME)
    one_of(payload, "state", STATES)
    if "severity" in payload:
        one_of(payload, "severity", SEVERITIES)
    if "robot_id" in payload and payload["robot_id"] is not None:
        text(payload, "robot_id", MAX_NAME)
    if "text" in payload:
        value = payload["text"]
        if not isinstance(value, str) or len(value) > MAX_TEXT:
            raise ContractValidationError(f"text must be a text of at most {MAX_TEXT} characters")

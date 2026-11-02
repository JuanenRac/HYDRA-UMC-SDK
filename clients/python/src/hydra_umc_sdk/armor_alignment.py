# =============================================================================
# HYDRA-UMC-SDK - Alignment with the contracts of A.R.M.O.R. (ARMOR-COMMON)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Reading the messages of A.R.M.O.R. in the words of the HYDRA-UMC contracts.

The two ecosystems keep their own libraries of contracts and neither imports the other. They differ in three conventions, listed in `docs/ARMOR_ALIGNMENT.md`:

* time: A.R.M.O.R. says `timestamp_ms` (integer milliseconds since the Unix epoch); HYDRA-UMC says `timestamp_utc` (an RFC 3339 date-time);
* identity: A.R.M.O.R. says `kind` and `node_id` in the body (and repeats `node_id` in the topic); HYDRA-UMC says `type` and `source`, with `schema_version` and an `event_id`;
* shape: A.R.M.O.R. closes every message and carries no version in the body; HYDRA-UMC carries `schema_version: "1.0"`.

This module converts, it does not decide anything about safety. `armor_state_to_event_envelope` wraps any A.R.M.O.R. state message in an `EventEnvelope`.
`armor_alarm_to_safety_state` is the one place where a meaning is chosen, so the table is a parameter: by default an alarm that is sounding **inhibits** (`INHIBITED`) and
nothing ever becomes `SAFE_STOP` by itself, because stopping machines for a burglar alarm is a decision of the installation, not of a library.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Mapping

from .contract_rules import require_object, whole
from .validation import ContractValidationError, validate

_NODE_ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}")
_KIND = re.compile(r"[a-z][a-z0-9_]{0,31}")

#: What an alarm phase of A.R.M.O.R. means for the machines, unless the installation chooses another table. `SAFE_STOP` is never in the default.
DEFAULT_ALARM_TO_SAFETY: dict[str, str] = {
    "disarmed": "READY",
    "exit_delay": "READY",
    "armed": "READY",
    "entry_delay": "READY",
    "alarm": "INHIBITED",
}
SAFETY_STATES = ("READY", "INHIBITED", "FAULT", "SAFE_STOP")


def armor_timestamp_ms_to_utc(timestamp_ms: int) -> str:
    """`timestamp_ms` of A.R.M.O.R. -> RFC 3339 date-time in UTC, with milliseconds."""
    if type(timestamp_ms) is not int or timestamp_ms < 0:
        raise ContractValidationError("timestamp_ms must be an integer >= 0")
    moment = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{timestamp_ms % 1000:03d}Z"


def utc_to_armor_timestamp_ms(timestamp_utc: str) -> int:
    """RFC 3339 date-time -> `timestamp_ms` of A.R.M.O.R. (a time before the epoch is refused)."""
    if not isinstance(timestamp_utc, str):
        raise ContractValidationError("timestamp_utc must be a text")
    try:
        moment = datetime.fromisoformat(timestamp_utc.upper().replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractValidationError("timestamp_utc must be an RFC 3339 date-time") from error
    if moment.tzinfo is None:
        raise ContractValidationError("timestamp_utc must carry a time zone")
    milliseconds = round(moment.timestamp() * 1000)
    if milliseconds < 0:
        raise ContractValidationError("timestamp_utc is before the Unix epoch")
    return milliseconds


def _armor_header(message: Mapping[str, Any]) -> tuple[str, str, int]:
    require_object(message, "message")
    kind, node_id = message.get("kind"), message.get("node_id")
    if not (isinstance(kind, str) and _KIND.fullmatch(kind)):
        raise ContractValidationError("kind must be a lower-case word")
    if not (isinstance(node_id, str) and _NODE_ID.fullmatch(node_id)):
        raise ContractValidationError("node_id must be lower-case letters, digits, dashes or underscores")
    whole(dict(message), "timestamp_ms", 0)
    return kind, node_id, message["timestamp_ms"]


def armor_state_to_event_envelope(message: Mapping[str, Any], sequence: int, *, topic: str | None = None) -> dict[str, Any]:
    """Wraps a state message of A.R.M.O.R. (`kind`, `node_id`, `timestamp_ms`, ...) in an `EventEnvelope` of HYDRA-UMC.

    `sequence` is the order the caller saw it in (the envelope requires one). When the topic is given its `node_id` must be the one of the body, as ARMOR-COMMON demands;
    a mismatch is refused. The message goes untouched in `data`, so nothing is lost and nothing is interpreted.
    """
    kind, node_id, timestamp_ms = _armor_header(message)
    if topic is not None and node_id not in topic.split("/"):
        raise ContractValidationError("the node_id of the message is not in its topic")
    envelope = {
        "schema_version": "1.0",
        "event_id": f"armor:{node_id}:{kind}:{timestamp_ms}",
        "type": f"armor.{kind}",
        "source": f"armor:{node_id}",
        "timestamp_utc": armor_timestamp_ms_to_utc(timestamp_ms),
        "sequence": sequence,
        "data": dict(message),
    }
    validate("EventEnvelope", envelope)
    return envelope


def armor_alarm_to_safety_state(message: Mapping[str, Any], mapping: Mapping[str, str] | None = None) -> dict[str, Any]:
    """The `SafetyState` that an alarm message of A.R.M.O.R. (`kind: alarm`, with a `phase`) stands for, by the table `mapping` (default: `DEFAULT_ALARM_TO_SAFETY`)."""
    kind, node_id, timestamp_ms = _armor_header(message)
    if kind != "alarm":
        raise ContractValidationError("only a message of kind alarm has a phase")
    table = dict(DEFAULT_ALARM_TO_SAFETY if mapping is None else mapping)
    for phase, state in table.items():
        if state not in SAFETY_STATES:
            raise ContractValidationError(f"the table maps {phase} to {state}, which is not a safety state")
    phase = message.get("phase")
    if not isinstance(phase, str) or phase not in table:
        raise ContractValidationError("phase is not one the table knows")
    state = {
        "schema_version": "1.0",
        "state": table[phase],
        "source": f"armor:{node_id}",
        "timestamp_utc": armor_timestamp_ms_to_utc(timestamp_ms),
        "armor_phase": phase,
    }
    validate("SafetyState", state)
    return state

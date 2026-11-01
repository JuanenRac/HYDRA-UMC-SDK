# =============================================================================
# HYDRA-UMC-SDK - Lifecycle of a robot command
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The `CommandLifecycleEvent` contract: what happened to one command after the server accepted it.

A client that sends a command to a robot used to learn only that the server had taken it. This contract is the event a server publishes on the WebSocket the
clients already hold, one per step: `ACCEPTED` (the server owns the command), `RUNNING` (the controller has it), `COMPLETED` (the controller reported it done),
`FAILED` and `CANCELLED` (both say why). The events of one command share its `operation_id`, the identifier of the `Operation` that carries it, and grow by `sequence`.

`command_state_from_operation` derives the state from an `Operation` so a service that already keeps one does not keep a second state machine: `sent` is
`RUNNING`, a command is `COMPLETED` only when its `Operation` ended with a result that `concludes_success` (a queue that says done is not enough), and a refusal
is `FAILED`. `validate_state_transition` says which step may follow which.
"""

from __future__ import annotations

from typing import Any

from .contract_rules import check_fields, identifier, one_of, require_object, text, whole
from .operation import OperationResult, concludes_success, parse_operation_result
from .validation import ContractValidationError, _require_date_time

COMMAND_STATES: tuple[str, ...] = ("ACCEPTED", "RUNNING", "COMPLETED", "FAILED", "CANCELLED")
TERMINAL_COMMAND_STATES = frozenset({"COMPLETED", "FAILED", "CANCELLED"})
# A step that ends badly or by choice must say why; a command that ran normally needs no reason.
STATES_THAT_NEED_A_REASON = frozenset({"FAILED", "CANCELLED"})

_REQUIRED = ("schema_version", "operation_id", "robot_id", "command", "state", "at_utc", "sequence")
_OPTIONAL = ("reason",)

_ALLOWED: dict[str, frozenset[str]] = {
    "ACCEPTED": frozenset({"RUNNING", "FAILED", "CANCELLED"}),
    "RUNNING": frozenset({"COMPLETED", "FAILED", "CANCELLED"}),
    "COMPLETED": frozenset(),
    "FAILED": frozenset(),
    "CANCELLED": frozenset(),
}

_OPERATION_STATE = {
    "received": "ACCEPTED",
    "authorized": "ACCEPTED",
    "queued": "ACCEPTED",
    "sent": "RUNNING",
    "confirmed": "RUNNING",
    "rejected": "FAILED",
}


def validate_command_lifecycle_event(payload: dict[str, Any]) -> None:
    """The checks of the CommandLifecycleEvent contract."""
    require_object(payload)
    check_fields(payload, _REQUIRED, _OPTIONAL)
    for name in ("operation_id", "robot_id", "command"):
        identifier(payload, name)
    one_of(payload, "state", COMMAND_STATES)
    _require_date_time(payload, "at_utc")
    whole(payload, "sequence", 1)
    if "reason" in payload:
        text(payload, "reason", 200)
    elif payload["state"] in STATES_THAT_NEED_A_REASON:
        raise ContractValidationError(f"reason is required when state is {payload['state']}")


def is_terminal_state(state: str) -> bool:
    """True once no later step may follow."""
    return state in TERMINAL_COMMAND_STATES


def validate_state_transition(previous: str, following: str) -> bool:
    """Whether `following` may come right after `previous`; False (never raises) for an unknown state or an illegal step."""
    if previous not in _ALLOWED or following not in COMMAND_STATES:
        return False
    return following in _ALLOWED[previous]


def command_state_from_operation(status: str, result: dict[str, Any] | OperationResult | None = None, *, allow_simulated: bool = False) -> tuple[str, str | None]:
    """The lifecycle state and, when the state needs one, the reason, for an `Operation` in `status` with its optional `result`.

    `terminated` is `COMPLETED` only when the result is real evidence of success (see `concludes_success`); a result that failed, that nobody observed or that
    comes from a simulation (unless `allow_simulated`) is `FAILED` with the reason the gate gave. A `terminated` operation without a result is `FAILED` as well:
    the bookkeeping finished, nothing proves the command did.
    """
    if status == "terminated":
        if result is None:
            return "FAILED", "the operation ended without evidence that the command was carried out"
        try:
            record = result if isinstance(result, OperationResult) else parse_operation_result(result)
        except ContractValidationError as exc:
            return "FAILED", f"the result of the operation is not usable: {exc}"
        concluded, why = concludes_success(record, allow_simulated=allow_simulated)
        return ("COMPLETED", None) if concluded else ("FAILED", why)
    if status == "rejected":
        return "FAILED", "the operation was rejected"
    if status in _OPERATION_STATE:
        return _OPERATION_STATE[status], None
    raise ContractValidationError(f"unknown operation status: {status!r}")

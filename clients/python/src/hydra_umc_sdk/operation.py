# =============================================================================
# HYDRA-UMC-SDK - Operation lifecycle (P03: shared, strict, versioned contracts)
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""The Operation contract's real lifecycle state machine.

Every goal or job that crosses one of this ecosystem's own service
boundaries (SERVER, ORCHESTRATOR, DEV-SERVER, OPS-AGENT, ...) passes
through several genuinely distinct, observable states on its way to
actually happening - received, authorized, queued, sent, confirmed by
the target, and only then terminated. Collapsing all of that into a
single "executed" bucket (what most of this ecosystem's services did
before this contract existed) throws away exactly the information a
caller needs to answer "did this really happen, or did I just get an
ACK from a queue": this module is the one shared, enforced place that
distinguishes them, so no consumer has to invent its own guess at what
"in progress" honestly means.

Distinct from `bridge_contract.py`'s own `BridgeJob`/`JobPhase`: that one
is a narrow, domain-specific PREPARE/LOAD/PROCESS/UNLOAD/COMPLETE/ABORT
safety gate for external machine bridges specifically, not a general
cross-service lifecycle - the two are not redundant, and a bridge job
reaching SERVER/ORCHESTRATOR can be wrapped in an Operation without
either contract needing to change.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .validation import validate

OPERATION_STATUSES: tuple[str, ...] = (
    "received",
    "authorized",
    "queued",
    "sent",
    "confirmed",
    "terminated",
    "rejected",
)

# "terminado" in P03's own words - once here, no later message can walk an
# Operation back to any other status. `rejected` counts as terminal too:
# a refused operation is exactly as finished as a completed one, just
# with a different outcome.
TERMINAL_STATUSES = frozenset({"terminated", "rejected"})

# The real, intended forward path is received -> authorized -> queued ->
# sent -> confirmed -> terminated. `rejected` is reachable from every
# non-terminal status (an operation can be turned down at authorization,
# dropped from the queue, fail to send, or be refused by the target after
# sending) but never reachable FROM a terminal status - and nothing is
# ever reachable from `terminated`/`rejected` themselves.
_ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "received": frozenset({"authorized", "rejected"}),
    "authorized": frozenset({"queued", "rejected"}),
    "queued": frozenset({"sent", "rejected"}),
    "sent": frozenset({"confirmed", "rejected"}),
    "confirmed": frozenset({"terminated", "rejected"}),
    "terminated": frozenset(),
    "rejected": frozenset(),
}


def is_terminal(status: str) -> bool:
    """True for the 2 statuses P03 means by "terminado" - no further
    transition is ever legal from either one."""
    return status in TERMINAL_STATUSES


def validate_status_transition(previous: str, next_status: str) -> bool:
    """Whether moving an Operation from `previous` to `next_status` is a
    legal step in the shared lifecycle above - the concrete, enforced
    form of P03's "distinguir recibido, autorizado, encolado, enviado,
    confirmado por destino y terminado: no presentar todos como
    ejecutado". Returns False (never raises) for an unrecognised status
    on either side, exactly like for an illegal transition - the caller
    decides what an invalid transition means for its own flow (reject
    the update, log it, alert); this only answers whether one is legal.
    """
    if previous not in _ALLOWED_TRANSITIONS or next_status not in OPERATION_STATUSES:
        return False
    return next_status in _ALLOWED_TRANSITIONS[previous]


@dataclass(frozen=True)
class OperationRecord:
    """A thin, validated read of one real Operation payload's fields a
    caller actually branches on. Not a replacement for the JSON Schema
    (still the normative source of truth, enforced by `validate()` in
    `from_payload` below) - just a typed, attribute-access convenience
    over the dict every wire payload already is.
    """

    operation_id: str
    correlation_id: str
    kind: str
    status: str
    target_kind: str
    target_id: str

    @property
    def is_terminal(self) -> bool:
        return is_terminal(self.status)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "OperationRecord":
        """Validates `payload` against the real Operation contract first
        (raises ContractValidationError on anything non-conformant, same
        as calling `validate("Operation", payload)` directly would) and
        only then builds the record - never silently accepts a payload
        this contract itself would reject.
        """
        validate("Operation", payload)
        target = payload["target"]
        return cls(
            operation_id=payload["operation_id"],
            correlation_id=payload["correlation_id"],
            kind=payload["kind"],
            status=payload["status"],
            target_kind=target["kind"],
            target_id=target["id"],
        )

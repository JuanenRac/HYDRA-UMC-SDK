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

("Contrato de evidencia de ejecucion, distinto de la capacidad
declarada"): an Operation reaching a terminal status is not, by itself,
proof anything really happened - `status: "terminated"` only means the
lifecycle's own bookkeeping finished, which a queue can report even
with observation entirely disabled. `OperationResult`/
`concludes_success()` below are the one real gate that decides whether
a result is trustworthy evidence of success: a result from a different
run (a stale/replayed message), one produced with observers disabled,
or one never actually observed, must never be silently read as success.
See `capability.py`'s own module docstring for the companion half of
- whether a target even declares (and recently verified) support
for a `kind` at all, a separate question from whether one particular
Operation of that kind actually succeeded.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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


OPERATION_RESULT_ORIGINS: tuple[str, ...] = ("real", "simulated")
OPERATION_RESULT_OUTCOMES: tuple[str, ...] = ("success", "failure", "unknown")


@dataclass(frozen=True)
class OperationResult:
    """this project's own "resultado compartido": run_id/origin/observers_enabled
    are the evidence `concludes_success()` needs to refuse a stale,
    simulated-when-real-was-expected, or unobserved outcome - never
    trust `outcome == "success"` alone."""

    run_id: str
    origin: str
    observers_enabled: bool
    outcome: str
    revision: str | None = None
    accepted_at: datetime | None = None
    executed_at: datetime | None = None
    observed_at: datetime | None = None
    outcome_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.run_id:
            raise ValueError("run_id must be a non-empty string")
        if self.origin not in OPERATION_RESULT_ORIGINS:
            raise ValueError(f"origin must be one of {OPERATION_RESULT_ORIGINS}, got {self.origin!r}")
        if self.outcome not in OPERATION_RESULT_OUTCOMES:
            raise ValueError(f"outcome must be one of {OPERATION_RESULT_OUTCOMES}, got {self.outcome!r}")
        if self.outcome != "success" and not self.outcome_reason:
            raise ValueError("outcome_reason is required when outcome is not 'success'")


def parse_operation_result(payload: dict[str, Any]) -> OperationResult:
    """Parses a bare `result` object - the same shape `Operation.result`
    carries - independent of the enclosing Operation, so a result can be
    stored/audited/compared on its own. Does not itself validate against
    the full Operation contract (there is no standalone Operation.result
    JSON Schema entry); construction's own `__post_init__` above is the
    real invariant check for this shape."""

    def _parse_dt(key: str) -> datetime | None:
        raw = payload.get(key)
        return datetime.fromisoformat(raw.replace("Z", "+00:00")) if raw else None

    return OperationResult(
        run_id=payload["run_id"],
        origin=payload["origin"],
        observers_enabled=payload["observers_enabled"],
        outcome=payload["outcome"],
        revision=payload.get("revision"),
        accepted_at=_parse_dt("accepted_at_utc"),
        executed_at=_parse_dt("executed_at_utc"),
        observed_at=_parse_dt("observed_at_utc"),
        outcome_reason=payload.get("outcome_reason"),
    )


def concludes_success(result: OperationResult, *, expected_run_id: str | None = None) -> tuple[bool, str]:
    """The real gate exists for: whether `result` is trustworthy
    enough evidence to conclude the Operation it belongs to actually
    succeeded. Checked in this fixed order, each able to short-circuit
    the rest:

    1. `expected_run_id` (when the caller supplies one - e.g. "the run_id
       I started this Operation under") must match `result.run_id` - a
       result from another session/process instance must never be
       silently accepted as evidence for this one.
    2. `observers_enabled` must be true - a result produced while
       observation itself was turned off cannot confirm anything really
       happened, regardless of what `outcome` claims.
    3. `observed_at` must be set - `outcome == "success"` alone (backed
       only by `accepted_at`/`executed_at`) is exactly the "queue says
       done" illusion exists to close; only a real observation
       counts.
    4. Only then is `outcome` itself checked.

    Returns (True, reason) only when every one of those holds AND
    `outcome == "success"`.
    """
    if expected_run_id is not None and result.run_id != expected_run_id:
        return False, (
            f"result belongs to run {result.run_id!r}, not the expected {expected_run_id!r} - "
            "a stale or replayed result must not be trusted"
        )
    if not result.observers_enabled:
        return False, "observers were disabled for this run - cannot confirm the outcome really happened"
    if result.observed_at is None:
        return False, "never actually observed - requested/accepted/executed alone do not confirm the outcome"
    if result.outcome != "success":
        return False, result.outcome_reason or f"outcome is {result.outcome}"
    return True, f"confirmed by a real, active observer (run {result.run_id})"

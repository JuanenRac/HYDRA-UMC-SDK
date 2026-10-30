# =============================================================================
# HYDRA-UMC-SDK - External machine bridge safety contract
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""Typed, dependency-free v0 contract shared by external machine bridges.

It is deliberately a policy/data boundary, not a motor-control API. ROS 2,
OpenPnP, printer, CNC and laser bridges may request a coordinated cell job,
but only HYDRA-UMC's authorised server/MCU path can approve physical motion.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


MAX_PARAMETERS = 32
MAX_PARAMETER_KEY_CHARS = 64
MAX_PARAMETER_VALUE_CHARS = 1024
MAX_IDENTIFIER_CHARS = 128


class BridgeError(ValueError):
    """Raised for an invalid bridge request before any transport is used."""


class MachineState(str, Enum):
    OFFLINE = "OFFLINE"
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    HOLDING = "HOLDING"
    # Stopped and not going on until an operator resets it (MTConnect STOPPED): unlike HOLDING it cannot be resumed.
    STOPPED = "STOPPED"
    FAULT = "FAULT"
    SAFE_STOP = "SAFE_STOP"


class CellState(str, Enum):
    READY = "READY"
    INHIBITED = "INHIBITED"
    FAULT = "FAULT"
    SAFE_STOP = "SAFE_STOP"


class JobPhase(str, Enum):
    PREPARE = "PREPARE"
    LOAD = "LOAD"
    PROCESS = "PROCESS"
    UNLOAD = "UNLOAD"
    COMPLETE = "COMPLETE"
    ABORT = "ABORT"


@dataclass(frozen=True)
class BridgeJob:
    """A correlated request for a safe, high-level cell phase."""

    job_id: str
    idempotency_key: str
    source: str
    phase: JobPhase
    machine_state: MachineState
    parameters: Mapping[str, str]

    def __post_init__(self) -> None:
        if not all(isinstance(value, str) and value.strip() for value in (self.job_id, self.idempotency_key, self.source)):
            raise BridgeError("job_id, idempotency_key and source must be non-empty strings")
        # `phase`/`machine_state` are typed as `JobPhase`/
        # `MachineState` in the dataclass annotation, but Python never
        # enforces that at runtime - constructing `BridgeJob` directly
        # (not through `job_from_dict`, which does validate this) with
        # an unrecognised string for either field used to construct
        # successfully, and `evaluate_job` could then return
        # `allowed=True` for a phase it never actually recognised (its
        # own `job.phase is JobPhase.ABORT` check is simply `False` for
        # any value that isn't literally that one real enum member,
        # falling through to the same "allowed" path a real, known phase
        # would take). Every construction path - the public constructor
        # AND `job_from_dict` - must reject an unknown value identically.
        if not isinstance(self.phase, JobPhase):
            raise BridgeError(f"phase must be a real JobPhase member, got {self.phase!r}")
        if not isinstance(self.machine_state, MachineState):
            raise BridgeError(f"machine_state must be a real MachineState member, got {self.machine_state!r}")
        # (P2):
        # `parameters` is typed as `Mapping[str, str]` in the dataclass
        # annotation, but - same class of gap as above - Python
        # never enforces that at runtime. `job_from_dict()` already
        # guards this before ever constructing a `BridgeJob` (see its own
        # `isinstance(parameters, Mapping)` check), but the direct
        # public-constructor path had no equivalent: passing a list
        # (e.g. `parameters=[]`) used to blow up on the `.items()` call
        # below with a bare `AttributeError`, not the intended
        # `BridgeError` every other invalid-shape input here raises.
        # Every construction path must fail the same clean way.
        if not isinstance(self.parameters, Mapping):
            raise BridgeError(f"parameters must be a mapping (dict-like) object, got {type(self.parameters).__name__}")
        if any(not isinstance(key, str) or not isinstance(value, str) for key, value in self.parameters.items()):
            raise BridgeError("parameters must map strings to strings")
        # A job comes from a message anybody on the broker may publish: its size is bounded so that it cannot be used to exhaust a bridge.
        if len(self.parameters) > MAX_PARAMETERS:
            raise BridgeError(f"a job carries at most {MAX_PARAMETERS} parameters")
        if any(len(key) > MAX_PARAMETER_KEY_CHARS or len(value) > MAX_PARAMETER_VALUE_CHARS for key, value in self.parameters.items()):
            raise BridgeError(f"a parameter name has at most {MAX_PARAMETER_KEY_CHARS} characters and a value {MAX_PARAMETER_VALUE_CHARS}")
        if any(len(value) > MAX_IDENTIFIER_CHARS for value in (self.job_id, self.idempotency_key, self.source)):
            raise BridgeError(f"job_id, idempotency_key and source have at most {MAX_IDENTIFIER_CHARS} characters")


@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    reason: str


def evaluate_job(
    job: BridgeJob,
    cell_state: CellState,
    observed_machine_state: MachineState | None = None,
    *,
    allow_unobserved: bool = False,
) -> GateDecision:
    """Apply the minimum common safety rule before a bridge forwards a job.

    Abort is always allowed so that an external integration can request a
    controlled stop. Any productive phase needs a READY cell and an IDLE
    external machine; the lower MCU safety authority remains independent.

    `observed_machine_state` is the state of the external machine as the BRIDGE
    sees it (read from the machine just now), and it is what the gate uses
    when it is given. `job.machine_state` is only what the requester CLAIMS:
    it arrives in a message anybody on the broker may publish, so a gate that
    trusted it would let "machine_state": "IDLE" through while the machine runs.
    Without an observation the job is REFUSED (the gate fails closed): a bridge that
    cannot read its machine yet has no state to trust, and the claim of the requester
    is not one. `allow_unobserved=True` is the explicit, temporary opt-in of such a
    bridge to use the claim again; every bridge that can observe must pass what it saw.
    """

    if job.phase is JobPhase.ABORT:
        return GateDecision(True, "abort requests are always forwarded to the authorised safety path")
    if cell_state is not CellState.READY:
        return GateDecision(False, f"cell is {cell_state.value}, not READY")
    if observed_machine_state is not None and not isinstance(observed_machine_state, MachineState):
        raise BridgeError(f"observed_machine_state must be a real MachineState member, got {observed_machine_state!r}")
    if observed_machine_state is None and not allow_unobserved:
        return GateDecision(False, "the bridge did not read the state of its machine: the job is refused (read it and pass it as observed_machine_state)")
    machine_state = observed_machine_state if observed_machine_state is not None else job.machine_state
    if machine_state is not MachineState.IDLE:
        return GateDecision(False, f"external machine is {machine_state.value}, not IDLE")
    return GateDecision(True, "cell and external machine are ready")


# Real, shared JSON shape for BridgeJob/GateDecision - added so every bridge
# that now also reaches HYDRA-UMC-MQTT-BROKER (CNC/LASER/OPENPNP/PRINTER3D/
# ROS2) parses/serializes the exact same wire format instead of each one
# reinventing its own ad-hoc JSON mapping for the identical dataclass. Pure
# stdlib (dict/json-compatible types only) - this module stays
# dependency-free either way.
def job_to_dict(job: BridgeJob) -> dict[str, object]:
    """The real wire shape a bridge publishes/consumes for a `BridgeJob`."""

    return {
        "job_id": job.job_id,
        "idempotency_key": job.idempotency_key,
        "source": job.source,
        "phase": job.phase.value,
        "machine_state": job.machine_state.value,
        "parameters": dict(job.parameters),
    }


def job_from_dict(payload: Mapping[str, object]) -> BridgeJob:
    """The inverse of `job_to_dict()` - fails closed with `BridgeError` (never
    a bare `KeyError`/`ValueError`/`AttributeError`) on any malformed input,
    since this is the real parse boundary for a job arriving from an
    untrusted external transport (an MQTT PUBLISH payload, in practice)."""

    if not isinstance(payload, Mapping):
        raise BridgeError("job payload must be a JSON object")
    try:
        job_id = payload["job_id"]
        idempotency_key = payload["idempotency_key"]
        source = payload["source"]
        phase_raw = payload["phase"]
        machine_state_raw = payload["machine_state"]
        parameters = payload.get("parameters", {})
    except KeyError as error:
        raise BridgeError(f"job payload is missing required field {error}") from error
    if not isinstance(parameters, Mapping):
        raise BridgeError("job payload 'parameters' must be a JSON object")
    try:
        phase = JobPhase(phase_raw)
    except ValueError as error:
        raise BridgeError(f"job payload has an unrecognised phase: {phase_raw!r}") from error
    try:
        machine_state = MachineState(machine_state_raw)
    except ValueError as error:
        raise BridgeError(f"job payload has an unrecognised machine_state: {machine_state_raw!r}") from error
    # BridgeJob.__post_init__() still runs its own real validation (non-empty
    # job_id/idempotency_key/source, string-only parameters) - not duplicated
    # here, just given already-typed inputs to check.
    if not isinstance(job_id, str) or not isinstance(idempotency_key, str) or not isinstance(source, str):
        raise BridgeError("job payload's job_id, idempotency_key and source must be strings")
    return BridgeJob(job_id, idempotency_key, source, phase, machine_state, dict(parameters))


def decision_to_dict(decision: GateDecision) -> dict[str, object]:
    """The real wire shape a bridge publishes for a `GateDecision`."""

    return {"allowed": decision.allowed, "reason": decision.reason}

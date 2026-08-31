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


class BridgeError(ValueError):
    """Raised for an invalid bridge request before any transport is used."""


class MachineState(str, Enum):
    OFFLINE = "OFFLINE"
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    HOLDING = "HOLDING"
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
        if any(not isinstance(key, str) or not isinstance(value, str) for key, value in self.parameters.items()):
            raise BridgeError("parameters must map strings to strings")


@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    reason: str


def evaluate_job(job: BridgeJob, cell_state: CellState) -> GateDecision:
    """Apply the minimum common safety rule before a bridge forwards a job.

    Abort is always allowed so that an external integration can request a
    controlled stop. Any productive phase needs a READY cell and an IDLE
    external machine; the lower MCU safety authority remains independent.
    """

    if job.phase is JobPhase.ABORT:
        return GateDecision(True, "abort requests are always forwarded to the authorised safety path")
    if cell_state is not CellState.READY:
        return GateDecision(False, f"cell is {cell_state.value}, not READY")
    if job.machine_state is not MachineState.IDLE:
        return GateDecision(False, f"external machine is {job.machine_state.value}, not IDLE")
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

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

# =============================================================================
# HYDRA-UMC-SDK - Public contract package
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================

"""HYDRA-UMC public contracts and lightweight validation helpers."""

from .bridge_contract import (
    BridgeError,
    BridgeJob,
    CellState,
    GateDecision,
    JobPhase,
    MachineState,
    evaluate_job,
)

__all__ = [
    "BridgeError",
    "BridgeJob",
    "CellState",
    "GateDecision",
    "JobPhase",
    "MachineState",
    "evaluate_job",
]

__version__ = "0.0.9"

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
from .operation import (
    OPERATION_STATUSES,
    OperationRecord,
    TERMINAL_STATUSES,
    is_terminal,
    validate_status_transition,
)
from .lifecycle import (
    BoundedLog,
    ProcessLifecycleState,
    StructuredLogEntry,
    trace_first_failure,
)
from .promotion_journal import PromotionJournal, PromotionPhase, PromotionRecord, recover
from .scenario import ScenarioComparison, compare_runs
from .validation import ContractValidationError, validate

__all__ = [
    "BridgeError",
    "BridgeJob",
    "CellState",
    "GateDecision",
    "JobPhase",
    "MachineState",
    "evaluate_job",
    "OPERATION_STATUSES",
    "OperationRecord",
    "TERMINAL_STATUSES",
    "is_terminal",
    "validate_status_transition",
    "BoundedLog",
    "ProcessLifecycleState",
    "StructuredLogEntry",
    "trace_first_failure",
    "PromotionJournal",
    "PromotionPhase",
    "PromotionRecord",
    "recover",
    "ScenarioComparison",
    "compare_runs",
    "ContractValidationError",
    "validate",
]

__version__ = "0.1.8"

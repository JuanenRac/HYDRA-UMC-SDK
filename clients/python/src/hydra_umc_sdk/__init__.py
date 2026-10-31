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
    decision_to_dict,
    evaluate_job,
    job_from_dict,
    job_to_dict,
)
from .job_intake import IdempotencyStore, Intake, JobIntake
from .capability import (
    CapabilityError,
    CapabilityStatus,
    capability_check_age_seconds,
    is_capability_check_stale,
    is_capability_usable,
    parse_capability_status,
)
from .operation import (
    OPERATION_STATUSES,
    OperationRecord,
    OperationResult,
    TERMINAL_STATUSES,
    concludes_success,
    is_terminal,
    parse_operation_result,
    validate_status_transition,
)
from .lifecycle import (
    BoundedLog,
    ProcessLifecycleState,
    StructuredLogEntry,
    trace_first_failure,
)
from .mqtt_connection import MqttConnectionSettings, apply_connection_settings, settings_from_env
from .promotion_journal import PromotionJournal, PromotionPhase, PromotionRecord, check_service_health, recover
from .pose import FRAMES as POSE_FRAMES, Pose, Quaternion, pose_from_dict, pose_to_legacy_euler, validate_pose
from .scenario import ScenarioComparison, compare_runs
from .model_weights import ANY_WEIGHT_SUFFIXES, COMPILED_MODEL_SUFFIXES, contains_model_artifact
from .production_event import production_event_fields, validate_production_event
from .connection import ACTIONS as CONNECTION_ACTIONS, CLIENT_KINDS, validate_connection_client, validate_connection_event
from .robot_state import STATES as ROBOT_STATES, validate_robot_state
from .twin_state import SOURCES as TWIN_STATE_SOURCES, validate_twin_state
from .server_api import (
    ApiError,
    AuditEntry,
    AuditView,
    CommandResult,
    RevisionMismatchError,
    RobotView,
    TableApplied,
    TableMoveError,
    ClaimConflictError,
    ClaimEntry,
    ClaimResult,
    ControllerIdRequiredError,
    InvalidControllerIdError,
    JogArmResult,
    JogNotArmedError,
    Reservation,
    SafetyLimitsView,
    ServerClient,
    ServerRequestError,
    parse_api_error,
)
from .validation import ContractValidationError, validate

__all__ = [
    "POSE_FRAMES",
    "TWIN_STATE_SOURCES",
    "ROBOT_STATES",
    "CONNECTION_ACTIONS",
    "CLIENT_KINDS",
    "validate_connection_client",
    "validate_production_event",
    "production_event_fields",
    "contains_model_artifact",
    "ANY_WEIGHT_SUFFIXES",
    "COMPILED_MODEL_SUFFIXES",
    "validate_connection_event",
    "validate_robot_state",
    "validate_twin_state",
    "Pose",
    "Quaternion",
    "pose_from_dict",
    "pose_to_legacy_euler",
    "validate_pose",
    "BridgeError",
    "BridgeJob",
    "CellState",
    "GateDecision",
    "JobPhase",
    "MachineState",
    "decision_to_dict",
    "evaluate_job",
    "job_from_dict",
    "job_to_dict",
    "MqttConnectionSettings",
    "apply_connection_settings",
    "settings_from_env",
    "IdempotencyStore",
    "Intake",
    "JobIntake",
    "CapabilityError",
    "CapabilityStatus",
    "capability_check_age_seconds",
    "is_capability_check_stale",
    "is_capability_usable",
    "parse_capability_status",
    "OPERATION_STATUSES",
    "OperationRecord",
    "OperationResult",
    "TERMINAL_STATUSES",
    "concludes_success",
    "is_terminal",
    "parse_operation_result",
    "validate_status_transition",
    "BoundedLog",
    "ProcessLifecycleState",
    "StructuredLogEntry",
    "trace_first_failure",
    "PromotionJournal",
    "PromotionPhase",
    "PromotionRecord",
    "check_service_health",
    "recover",
    "ScenarioComparison",
    "compare_runs",
    "ApiError",
    "AuditEntry",
    "AuditView",
    "CommandResult",
    "RevisionMismatchError",
    "RobotView",
    "TableApplied",
    "TableMoveError",
    "ClaimConflictError",
    "ClaimEntry",
    "ClaimResult",
    "ControllerIdRequiredError",
    "InvalidControllerIdError",
    "JogArmResult",
    "JogNotArmedError",
    "Reservation",
    "SafetyLimitsView",
    "ServerClient",
    "ServerRequestError",
    "parse_api_error",
    "ContractValidationError",
    "validate",
]

__version__ = "0.4.2"

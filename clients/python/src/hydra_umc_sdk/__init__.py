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
from .command_lifecycle import COMMAND_STATES, command_state_from_operation, is_terminal_state, validate_command_lifecycle_event, validate_state_transition
from .mcu_errors import MCU_ERROR_CODES, RECOVERY_ACTIONS, McuErrorCode, default_mcu_error_action, describe_mcu_error, is_known_mcu_error
from .servoing import command_is_current, validate_velocity_command, validate_visual_target_request
from .vision_pipeline import BOX_UNITS, PIXEL_FORMATS, box_to_pixels, validate_detection_frame, validate_frame_meta
from .signed_commands import CommandSigningError, CommandVerdict, CommandVerifier, SignedCommandSettings, sign_command, verify_command
from .signed_commands import load_key as load_command_key, settings_from_environment as signed_command_settings_from_environment
from .bridge_health import BridgeHealth, health_enabled_from_environment, health_report, health_topic, read_health
from .job_intake import JobMessage, read_job_message
from .maintenance import incident_may_be_stored, validate_maintenance_incident
from .evidence_bundle import bundle_checksum, bundle_matches_checksum, seal_bundle, validate_evidence_bundle
from .fault_event import validate_fault_event
from .safety_zones_state import validate_safety_zones_state
from .vla_approval import validate_vla_approval
from .maintenance_agent import validate_canary_deploy_result, validate_change_proposal, validate_node_snapshot
from .armor_alignment import DEFAULT_ALARM_TO_SAFETY, armor_alarm_to_safety_state, armor_state_to_event_envelope, armor_timestamp_ms_to_utc, utc_to_armor_timestamp_ms
from .tool import CAN_STATES, THERMAL_FAULTS, TOOL_KINDS, TOOL_STATES, descriptor_problems, state_problems, validate_tool_descriptor, validate_tool_state
from .ecosystem import (
    CERTIFICATE_STATES,
    LIVENESS_SOURCES,
    LIVENESS_STATES,
    SERVICE_REASONS,
    SERVICE_STATES,
    WARNING_CODES,
    validate_ecosystem_health,
    validate_robot_liveness,
)
from .robot_roster import PLAYBACK_STATES, roster_from_settings, validate_robot_roster
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
    "CERTIFICATE_STATES",
    "LIVENESS_SOURCES",
    "LIVENESS_STATES",
    "SERVICE_REASONS",
    "SERVICE_STATES",
    "WARNING_CODES",
    "validate_ecosystem_health",
    "PLAYBACK_STATES",
    "roster_from_settings",
    "validate_robot_roster",
    "validate_robot_liveness",
    "validate_connection_client",
    "validate_production_event",
    "COMMAND_STATES",
    "MCU_ERROR_CODES",
    "RECOVERY_ACTIONS",
    "McuErrorCode",
    "default_mcu_error_action",
    "describe_mcu_error",
    "is_known_mcu_error",
    "command_state_from_operation",
    "is_terminal_state",
    "validate_command_lifecycle_event",
    "validate_state_transition",
    "command_is_current",
    "validate_velocity_command",
    "validate_visual_target_request",
    "BOX_UNITS",
    "PIXEL_FORMATS",
    "box_to_pixels",
    "validate_detection_frame",
    "validate_frame_meta",
    "incident_may_be_stored",
    "CommandSigningError",
    "CommandVerdict",
    "CommandVerifier",
    "SignedCommandSettings",
    "sign_command",
    "verify_command",
    "load_command_key",
    "signed_command_settings_from_environment",
    "BridgeHealth",
    "health_enabled_from_environment",
    "health_report",
    "health_topic",
    "read_health",
    "JobMessage",
    "read_job_message",
    "validate_maintenance_incident",
    "validate_fault_event",
    "validate_safety_zones_state",
    "validate_vla_approval",
    "validate_evidence_bundle",
    "bundle_checksum",
    "bundle_matches_checksum",
    "seal_bundle",
    "validate_node_snapshot",
    "validate_change_proposal",
    "validate_canary_deploy_result",
    "DEFAULT_ALARM_TO_SAFETY",
    "armor_alarm_to_safety_state",
    "armor_state_to_event_envelope",
    "armor_timestamp_ms_to_utc",
    "utc_to_armor_timestamp_ms",
    "CAN_STATES",
    "THERMAL_FAULTS",
    "TOOL_KINDS",
    "TOOL_STATES",
    "descriptor_problems",
    "state_problems",
    "validate_tool_descriptor",
    "validate_tool_state",
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

__version__ = "0.6.2"

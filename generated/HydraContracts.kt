// Generated from the HYDRA-UMC JSON Schemas by tools/generate_types.py. Do not edit.
package hydra.umc.contracts

data class Capability(
    val schema_version: String,
    val target: CapabilityTarget,
    val kind: String,
    val declared: Boolean,
    val last_checked_at_utc: String? = null,
    val checked_configuration: String? = null,
    val max_age_seconds: Double? = null,
    val last_check_outcome: String? = null,
    val last_check_reason: String? = null
)

data class CapabilityTarget(
    val kind: String,
    val id: String
)

data class CommandLifecycleEvent(
    val schema_version: String,
    val operation_id: String,
    val robot_id: String,
    val command: String,
    val state: String,
    val at_utc: String,
    val sequence: Long,
    val reason: String? = null
)

data class ConnectionClient(
    val schema_version: String,
    val id: String,
    val kind: String,
    val user: String? = null,
    val app_version: String? = null,
    val origin: String? = null,
    val two_factor: Boolean? = null,
    val first_seen_utc: String,
    val last_seen_utc: String,
    val last_failure_utc: String? = null,
    val active_sessions: Long,
    val logins_ok: Long,
    val logins_failed: Long,
    val ip: String? = null,
    val agent: String? = null
)

data class ConnectionEvent(
    val schema_version: String,
    val id: Long,
    val at_utc: String,
    val action: String,
    val client_kind: String,
    val client_id: String,
    val user: String? = null,
    val origin: String? = null,
    val two_factor: Boolean? = null,
    val app_version: String? = null,
    val ip: String? = null,
    val agent: String? = null
)

data class DetectionFrame(
    val schema_version: String,
    val frame_id: String,
    val capture_ts_utc: String,
    val box_unit: String,
    val detections: List<DetectionFrameDetections>,
    val session_id: String? = null,
    val model: DetectionFrameModel? = null
)

data class DetectionFrameDetections(
    val class_id: Long,
    val label: String,
    val score: Double,
    val box: DetectionFrameDetectionsBox
)

data class DetectionFrameDetectionsBox(
    val x_min: Double,
    val y_min: Double,
    val x_max: Double,
    val y_max: Double
)

data class DetectionFrameModel(
    val model_name: String,
    val model_version: String,
    val model_sha256: String,
    val hailo_arch: String,
    val pipeline_version: String
)

data class DeviceDescriptor(
    val schema_version: String,
    val node_id: String,
    val profile: String,
    val hostname: String,
    val machine: String,
    val operating_system: String,
    val kernel: String,
    val interfaces: List<String>
)

data class EcosystemHealth(
    val schema_version: String,
    val generated_at_utc: String,
    val available: Boolean,
    val summary: EcosystemHealthSummary,
    val services: List<EcosystemHealthServices>,
    val certificate: Any? = null,
    val warnings: List<EcosystemHealthWarnings>
)

data class EcosystemHealthSummary(
    val total: Long,
    val ok: Long,
    val degraded: Long,
    val down: Long,
    val unknown: Long,
    val drift: Long
)

data class EcosystemHealthServices(
    val name: String,
    val family: Any? = null,
    val role: Any? = null,
    val state: String,
    val reason: String,
    val version_expected: Any? = null,
    val version_reported: Any? = null,
    val drift: Boolean,
    val last_seen_utc: Any? = null,
    val latency_ms: Any? = null,
    val port: Any? = null,
    val health_path: Any? = null,
    val systemd_unit: Any? = null,
    val active_state: Any? = null
)

data class EcosystemHealthWarnings(
    val code: String,
    val service: String? = null
)

data class EventEnvelope(
    val schema_version: String,
    val event_id: String,
    val type: String,
    val source: String,
    val timestamp_utc: String,
    val sequence: Long,
    val correlation_id: String? = null
)

data class FrameMeta(
    val schema_version: String,
    val frame_id: String,
    val capture_ts_utc: String,
    val width: Long,
    val height: Long,
    val pixel_format: String,
    val session_id: String? = null,
    val source_id: String? = null,
    val stride: Long? = null,
    val sequence: Long? = null
)

data class HealthReport(
    val schema_version: String,
    val state: String,
    val timestamp_utc: String,
    val checks: Map<String, Any?>
)

data class MaintenanceIncident(
    val schema_version: String? = null,
    val incidentId: String,
    val sourceNode: String,
    val detectedAt: String,
    val severity: String,
    val component: String,
    val symptom: String,
    val evidenceRefs: List<String>,
    val redactionLevel: String,
    val requestedBy: String? = null,
    val correlationId: String
)

data class Operation(
    val schema_version: String,
    val operation_id: String,
    val correlation_id: String,
    val kind: String,
    val target: OperationTarget,
    val status: String,
    val status_reason: String? = null,
    val requested_at_utc: String,
    val updated_at_utc: String,
    val params: Map<String, Any?>,
    val error: OperationError? = null,
    val result: OperationResult? = null
)

data class OperationTarget(
    val kind: String,
    val id: String
)

data class OperationError(
    val code: String,
    val message: String
)

data class OperationResult(
    val run_id: String,
    val revision: String? = null,
    val origin: String,
    val observers_enabled: Boolean,
    val accepted_at_utc: String? = null,
    val executed_at_utc: String? = null,
    val observed_at_utc: String? = null,
    val outcome: String,
    val outcome_reason: String? = null
)

data class Pose(
    val schema_version: String,
    val frame: String,
    val position: PosePosition,
    val orientation: PoseOrientation,
    val euler: PoseEuler? = null
)

data class PosePosition(
    val x: Double,
    val y: Double,
    val z: Double
)

data class PoseOrientation(
    val w: Double,
    val x: Double,
    val y: Double,
    val z: Double
)

data class PoseEuler(
    val roll: Double,
    val pitch: Double,
    val yaw: Double
)

data class ProductionEvent(
    val schema_version: String,
    val source_id: String,
    val at_utc: String,
    val good: Boolean,
    val cycle_time_s: Double,
    val job_id: String? = null,
    val reject_reason: String? = null
)

data class ProjectManifest(
    val schema_version: String,
    val ecosystem: String,
    val name: String,
    val version: String,
    val role: String,
    val stack: String,
    val technologies: List<String>,
    val deployment_target: String,
    val maturity: String,
    val evidence: String? = null,
    val hardware_bound: Boolean? = null,
    val depends_on: List<String>? = null,
    val deployment_target_note: String? = null,
    val service: ProjectManifestService? = null,
    val family: String,
    val parent: String? = null,
    val native_version: ProjectManifestNativeVersion,
    val build: String,
    val notes: String
)

data class ProjectManifestService(
    val port: Long? = null,
    val health_path: String? = null,
    val systemd_unit: String? = null
)

data class ProjectManifestNativeVersion(
    val file: String,
    val pattern: Any? = null
)

data class RobotLiveness(
    val schema_version: String,
    val stale_after_s: Long,
    val robots: List<RobotLivenessRobots>
)

data class RobotLivenessRobots(
    val controller_id: String,
    val robot_id: Long,
    val state: String,
    val last_update_utc: String? = null,
    val age_s: Long? = null,
    val source: String? = null
)

data class RobotState(
    val schema_version: String,
    val robot_id: String,
    val state: String,
    val source: String? = null,
    val updated_at_utc: String,
    val mission_id: String? = null,
    val battery_percent: Double? = null,
    val pose: RobotStatePose? = null
)

data class RobotStatePose(
    val schema_version: String,
    val frame: String,
    val position: RobotStatePosePosition,
    val orientation: RobotStatePoseOrientation
)

data class RobotStatePosePosition(
    val x: Double,
    val y: Double,
    val z: Double
)

data class RobotStatePoseOrientation(
    val w: Double,
    val x: Double,
    val y: Double,
    val z: Double
)

data class SafetyState(
    val schema_version: String,
    val state: String,
    val source: String,
    val timestamp_utc: String
)

data class ScenarioOutcome(
    val schema_version: String,
    val scenario_id: String,
    val run_id: String,
    val base_fingerprint: String,
    val phase: String,
    val repro_case: String,
    val observed: ScenarioOutcomeObserved,
    val timestamp_utc: String
)

data class ScenarioOutcomeObserved(
    val outcome: String,
    val exit_code: Long? = null,
    val evidence: String? = null
)

data class ServerDiscovery(
    val schema_version: String,
    val product: String,
    val remoteApiVersion: Long,
    val appVersion: String,
    val hostname: String,
    val controllerCount: Long,
    val robotCount: Long,
    val uptimeSeconds: Long
)

data class ToolDescriptor(
    val schema_version: String,
    val tool_id: Long,
    val name: String,
    val title: String,
    val kind: String,
    val category: String? = null,
    val hero_metric: ToolDescriptorHeroMetric? = null,
    val limits: ToolDescriptorLimits? = null,
    val watchdog_ms: Long? = null,
    val features: List<String>? = null,
    val expansion_board: String? = null,
    val min_firmware_version: String? = null
)

data class ToolDescriptorHeroMetric(
    val label: String,
    val unit: String
)

data class ToolDescriptorLimits(
    val default: Double,
    val min: Double,
    val max: Double
)

data class ToolState(
    val schema_version: String,
    val tool_id: Long,
    val state: String,
    val source: String,
    val timestamp_utc: String,
    val firmware_version: String? = null,
    val can: ToolStateCan? = null,
    val temperature_c: Double? = null,
    val setpoint_c: Double? = null,
    val mcu_temp_c: Double? = null,
    val vdda_mv: Long? = null,
    val critical_error: Boolean? = null,
    val thermal_fault: String? = null
)

data class ToolStateCan(
    val state: String,
    val tec: Long? = null,
    val rec: Long? = null,
    val bus_off_count: Long? = null
)

data class TwinState(
    val schema_version: String,
    val source: String,
    val robot_id: String? = null,
    val frame: String,
    val timestamp_utc: String,
    val sequence: Long? = null,
    val joint_states: List<TwinStateJointStates>,
    val poses: List<TwinStatePoses>? = null
)

data class TwinStateJointStates(
    val name: String,
    val position: Double,
    val velocity: Double? = null,
    val effort: Double? = null
)

data class TwinStatePoses(
    val name: String,
    val pose: TwinStatePosesPose
)

data class TwinStatePosesPose(
    val schema_version: String,
    val frame: String,
    val position: TwinStatePosesPosePosition,
    val orientation: TwinStatePosesPoseOrientation
)

data class TwinStatePosesPosePosition(
    val x: Double,
    val y: Double,
    val z: Double
)

data class TwinStatePosesPoseOrientation(
    val w: Double,
    val x: Double,
    val y: Double,
    val z: Double
)

data class UpdateManifest(
    val schema_version: String,
    val project: String,
    val version: String,
    val artifact_url: String,
    val sha256: String
)

data class VelocityCommand(
    val schema_version: String,
    val vx: Double,
    val vy: Double,
    val vz: Double,
    val wroll: Double,
    val wpitch: Double,
    val wyaw: Double,
    val hold: Boolean,
    val issued_at_ms: Long,
    val valid_for_ms: Double,
    val seq: Long,
    val frame_id: String? = null
)

data class VisualTargetRequest(
    val schema_version: String,
    val frame_id: String,
    val current: VisualTargetRequestCurrent,
    val target: VisualTargetRequestTarget,
    val confidence: Double,
    val safety_state: String,
    val data_age_ms: Double? = null,
    val captured_at_utc: String? = null,
    val calibration_version: String? = null,
    val calibration_age_days: Double? = null
)

data class VisualTargetRequestCurrent(
    val x: Double,
    val y: Double,
    val z: Double,
    val roll: Double,
    val pitch: Double,
    val yaw: Double
)

data class VisualTargetRequestTarget(
    val x: Double,
    val y: Double,
    val z: Double,
    val roll: Double,
    val pitch: Double,
    val yaw: Double
)

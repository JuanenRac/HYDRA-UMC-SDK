// Generated from the HYDRA-UMC JSON Schemas by tools/generate_types.py. Do not edit.

export interface CanIds {
  schema_version: "1.0";
  note?: string;
  estop_id: number;
  slot_base: number;
  slot_window: number;
  slots: number;
  messages: CanIdsMessages[];
  estop_frame?: CanIdsEstopFrame;
  tool_head?: CanIdsToolHead;
  [extra: string]: unknown;
}

export interface CanIdsMessages {
  name: string;
  offset: number;
  emitter: "kinematic-brain" | "controller-board" | "bootloader" | "host";
  [extra: string]: unknown;
}

export interface CanIdsEstopFrame {
  dlc: 8;
  bytes: ["kind", "detail", "source", "epoch", "sequence_low", "sequence_high", "kind_complement", "detail_complement"];
  kinds: Record<string, number>;
  trip_reasons: Record<string, number>;
  sources: Record<string, number>;
  [extra: string]: unknown;
}

export interface CanIdsToolHead {
  source: string;
  protocol_version: number;
  bit_rate_bps: number;
  bus: "tool_head_downlink";
  messages: CanIdsToolHeadMessages[];
  [extra: string]: unknown;
}

export interface CanIdsToolHeadMessages {
  id: number;
  name: string;
  direction: "host_to_board" | "board_to_host" | "both";
  [extra: string]: unknown;
}

export interface CanaryDeployResult {
  schema_version?: "1.0";
  deployId: string;
  proposalId: string;
  projectName: string;
  startedAt: string;
  finishedAt: string;
  promoted: boolean;
  stageReached: "staged" | "diff_applied" | "build_verified" | "diff_committed" | "promoted" | "rolled_back";
  buildOutput: string;
  detail: string;
  backupPath?: string | null;
  patchPath?: string | null;
  [extra: string]: unknown;
}

export interface Capability {
  schema_version: "1.0";
  target: CapabilityTarget;
  kind: string;
  declared: boolean;
  last_checked_at_utc?: string;
  checked_configuration?: string;
  max_age_seconds?: number;
  last_check_outcome?: "verified" | "failed" | "unknown";
  last_check_reason?: string;
  [extra: string]: unknown;
}

export interface CapabilityTarget {
  kind: string;
  id: string;
  [extra: string]: unknown;
}

export interface ChangeProposal {
  schema_version?: "1.0";
  proposalId: string;
  incidentId: string;
  correlationId: string;
  createdAt: string;
  projectName: string;
  description: string;
  diff: string;
  rationale: string;
  status: "pending" | "approved" | "rejected";
  decidedBy?: string | null;
  decidedAt?: string | null;
  decisionReason?: string | null;
  approvedContentDigest?: string | null;
  allowProtectedPaths?: boolean;
  approvalExpiresAt?: string | null;
  approvedBaseCommit?: string | null;
  approvalSignature?: string | null;
  generatedBy?: string | null;
  [extra: string]: unknown;
}

export interface CommandLifecycleEvent {
  schema_version: "1.0";
  operation_id: string;
  robot_id: string;
  command: string;
  state: "ACCEPTED" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED";
  at_utc: string;
  sequence: number;
  reason?: string;
  [extra: string]: unknown;
}

export interface ConnectionClient {
  schema_version: "1.0";
  id: string;
  kind: "studio" | "suite" | "android" | "ios" | "dsi" | "watch" | "voice" | "other";
  user?: string;
  app_version?: string;
  origin?: "local" | "remote";
  two_factor?: boolean;
  first_seen_utc: string;
  last_seen_utc: string;
  last_failure_utc?: string;
  active_sessions: number;
  logins_ok: number;
  logins_failed: number;
  ip?: string;
  agent?: string;
  [extra: string]: unknown;
}

export interface ConnectionEvent {
  schema_version: "1.0";
  id: number;
  at_utc: string;
  action: "first_seen" | "login" | "login_failed" | "second_factor_failed" | "logout" | "session_ended" | "session_expired";
  client_kind: "studio" | "suite" | "android" | "ios" | "dsi" | "watch" | "voice" | "other";
  client_id: string;
  user?: string;
  origin?: "local" | "remote";
  two_factor?: boolean;
  app_version?: string;
  ip?: string;
  agent?: string;
  [extra: string]: unknown;
}

export interface DetectionFrame {
  schema_version: "1.0";
  frame_id: string;
  capture_ts_utc: string;
  box_unit: "pixel" | "normalized";
  detections: DetectionFrameDetections[];
  session_id?: string;
  model?: DetectionFrameModel;
  [extra: string]: unknown;
}

export interface DetectionFrameDetections {
  class_id: number;
  label: string;
  score: number;
  box: DetectionFrameDetectionsBox;
  [extra: string]: unknown;
}

export interface DetectionFrameDetectionsBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  [extra: string]: unknown;
}

export interface DetectionFrameModel {
  model_name: string;
  model_version: string;
  model_sha256: string;
  hailo_arch: string;
  pipeline_version: string;
  [extra: string]: unknown;
}

export interface DeviceDescriptor {
  schema_version: "1.0";
  node_id: string;
  profile: string;
  hostname: string;
  machine: string;
  operating_system: string;
  kernel: string;
  interfaces: string[];
  [extra: string]: unknown;
}

export interface EcosystemHealth {
  schema_version: "1.0";
  generated_at_utc: string;
  available: boolean;
  summary: EcosystemHealthSummary;
  services: EcosystemHealthServices[];
  certificate: unknown;
  warnings: EcosystemHealthWarnings[];
  [extra: string]: unknown;
}

export interface EcosystemHealthSummary {
  total: number;
  ok: number;
  degraded: number;
  down: number;
  unknown: number;
  drift: number;
  [extra: string]: unknown;
}

export interface EcosystemHealthServices {
  name: string;
  family: unknown;
  role: unknown;
  state: "ok" | "degraded" | "down" | "unknown";
  reason: "health_ok" | "health_degraded" | "health_failed" | "http_error" | "unreachable" | "unreachable_unit_active" | "reachable_unit_not_active" | "unit_active" | "unit_starting" | "unit_failed" | "unit_inactive" | "no_signal" | "probe_error";
  version_expected: unknown;
  version_reported: unknown;
  drift: boolean;
  last_seen_utc: unknown;
  latency_ms: unknown;
  port?: unknown;
  health_path?: unknown;
  systemd_unit?: unknown;
  active_state?: unknown;
  [extra: string]: unknown;
}

export interface EcosystemHealthWarnings {
  code: "certificate_expiring" | "certificate_expired" | "certificate_unreadable" | "version_drift" | "service_down" | "service_degraded";
  service?: string;
  [extra: string]: unknown;
}

export interface EventEnvelope {
  schema_version: "1.0";
  event_id: string;
  type: string;
  source: string;
  timestamp_utc: string;
  sequence: number;
  correlation_id?: string;
  [extra: string]: unknown;
}

export interface EvidenceBundle {
  componentVersions: Record<string, unknown>;
  relevantManifests: string[];
  redactedLogExcerpts: string[];
  reproductionSteps: string[];
  failedTests: string[];
  impact: string;
  actionsAttempted: string[];
  checksum: string;
  date: string;
  localValidationResult: string;
  [extra: string]: unknown;
}

export interface FaultEvent {
  schema: "fault-event/1";
  source: string;
  code: string;
  state: "raised" | "cleared";
  severity?: "info" | "warning" | "error" | "critical";
  robot_id?: string | null;
  text?: string;
  [extra: string]: unknown;
}

export interface FrameMeta {
  schema_version: "1.0";
  frame_id: string;
  capture_ts_utc: string;
  width: number;
  height: number;
  pixel_format: "RGB" | "BGR" | "RGBA" | "BGRA" | "GRAY" | "YUYV" | "NV12" | "JPEG";
  session_id?: string;
  source_id?: string;
  stride?: number;
  sequence?: number;
  [extra: string]: unknown;
}

export interface HealthReport {
  schema_version: "1.0";
  state: "READY" | "DEGRADED" | "INHIBITED" | "FAULT" | "SAFE_STOP";
  timestamp_utc: string;
  checks: Record<string, unknown>;
  [extra: string]: unknown;
}

export interface JointPoses {
  schema_version: "1.0";
  frame: "base";
  checked?: boolean;
  note?: string;
  poses: JointPosesPoses[];
  [extra: string]: unknown;
}

export interface JointPosesPoses {
  joint: string;
  position: JointPosesPosesPosition;
  quaternion: JointPosesPosesQuaternion;
  [extra: string]: unknown;
}

export interface JointPosesPosesPosition {
  x: number;
  y: number;
  z: number;
  [extra: string]: unknown;
}

export interface JointPosesPosesQuaternion {
  w: number;
  x: number;
  y: number;
  z: number;
  [extra: string]: unknown;
}

export interface Kinematics {
  schema_version: "1.0";
  note?: string;
  models: Record<string, unknown>;
  [extra: string]: unknown;
}

export interface MaintenanceIncident {
  schema_version?: "1.0";
  incidentId: string;
  sourceNode: string;
  detectedAt: string;
  severity: "info" | "warning" | "critical";
  component: string;
  symptom: string;
  evidenceRefs: string[];
  redactionLevel: "sanitized" | "raw";
  requestedBy: string | null;
  correlationId: string;
  [extra: string]: unknown;
}

export interface NodeSnapshot {
  schema_version?: "1.0";
  sourceNode: string;
  collectedAt: string;
  correlationId: string;
  projects: NodeSnapshotProjects[];
  manifestIssues: NodeSnapshotManifestIssues[];
  systemdAvailable: boolean | null;
  systemdUnavailableReason: string | null;
  serviceHealth: NodeSnapshotServiceHealth[];
  httpHealth: NodeSnapshotHttpHealth[];
  incidents: NodeSnapshotIncidents[];
  hostHealth?: NodeSnapshotHostHealth;
  [extra: string]: unknown;
}

export interface NodeSnapshotProjects {
  name: string;
  version: string;
  maturity: string;
  manifestPath: string;
  [extra: string]: unknown;
}

export interface NodeSnapshotManifestIssues {
  path: string;
  reason: string;
  [extra: string]: unknown;
}

export interface NodeSnapshotServiceHealth {
  unitName: string;
  active: boolean;
  detail: string;
  [extra: string]: unknown;
}

export interface NodeSnapshotHttpHealth {
  url: string;
  reachable: boolean;
  statusCode: number | null;
  detail: string;
  [extra: string]: unknown;
}

export interface NodeSnapshotIncidents {
  schema_version?: "1.0";
  incidentId: string;
  sourceNode: string;
  detectedAt: string;
  severity: "info" | "warning" | "critical";
  component: string;
  symptom: string;
  evidenceRefs: string[];
  redactionLevel: "sanitized" | "raw";
  requestedBy: string | null;
  correlationId: string;
  [extra: string]: unknown;
}

export interface NodeSnapshotHostHealth {
  disks: NodeSnapshotHostHealthDisks[];
  thermal: NodeSnapshotHostHealthThermal;
  backups: NodeSnapshotHostHealthBackups | null;
  [extra: string]: unknown;
}

export interface NodeSnapshotHostHealthDisks {
  path: string;
  freeBytes: number | null;
  totalBytes: number | null;
  freePercent: number | null;
  error: string | null;
  [extra: string]: unknown;
}

export interface NodeSnapshotHostHealthThermal {
  celsius: number | null;
  throttledRaw: number | null;
  throttledNow: string[];
  throttledPast: string[];
  vcgencmdAvailable: boolean;
  [extra: string]: unknown;
}

export interface NodeSnapshotHostHealthBackups {
  directory: string;
  count: number | null;
  newestAgeDays: number | null;
  error: string | null;
  [extra: string]: unknown;
}

export interface Operation {
  schema_version: "1.0";
  operation_id: string;
  correlation_id: string;
  kind: string;
  target: OperationTarget;
  status: "received" | "authorized" | "queued" | "sent" | "confirmed" | "terminated" | "rejected";
  status_reason?: string;
  requested_at_utc: string;
  updated_at_utc: string;
  params: Record<string, unknown>;
  error?: OperationError;
  result?: OperationResult;
  [extra: string]: unknown;
}

export interface OperationTarget {
  kind: string;
  id: string;
  [extra: string]: unknown;
}

export interface OperationError {
  code: string;
  message: string;
  [extra: string]: unknown;
}

export interface OperationResult {
  run_id: string;
  revision?: string;
  origin: "real" | "simulated";
  observers_enabled: boolean;
  accepted_at_utc?: string;
  executed_at_utc?: string;
  observed_at_utc?: string;
  outcome: "success" | "failure" | "unknown";
  outcome_reason?: string;
  [extra: string]: unknown;
}

export interface Pose {
  schema_version: "1.0";
  frame: "base" | "tool";
  position: PosePosition;
  orientation: PoseOrientation;
  euler?: PoseEuler;
  [extra: string]: unknown;
}

export interface PosePosition {
  x: number;
  y: number;
  z: number;
  [extra: string]: unknown;
}

export interface PoseOrientation {
  w: number;
  x: number;
  y: number;
  z: number;
  [extra: string]: unknown;
}

export interface PoseEuler {
  roll: number;
  pitch: number;
  yaw: number;
  [extra: string]: unknown;
}

export interface ProductionEvent {
  schema_version: "1.0";
  source_id: string;
  at_utc: string;
  good: boolean;
  cycle_time_s: number;
  job_id?: string;
  reject_reason?: string;
  [extra: string]: unknown;
}

export interface ProjectManifest {
  schema_version: "1.0";
  ecosystem: "HYDRA-UMC" | "URTC";
  name: string;
  version: string;
  role: "api" | "ui" | "cli" | "firmware" | "library" | "service" | "tool";
  stack: string;
  technologies: string[];
  deployment_target: "cm5" | "user-pc" | "mobile" | "wearable" | "dev-server" | "mcu";
  maturity: "scaffolding" | "functional" | "established" | "production";
  evidence?: "none" | "host-test" | "simulator" | "bench" | "field";
  hardware_bound?: boolean;
  depends_on?: string[];
  deployment_target_note?: string;
  service?: ProjectManifestService;
  family: string;
  parent: string | null;
  native_version: ProjectManifestNativeVersion;
  build: string;
  notes: string;
  [extra: string]: unknown;
}

export interface ProjectManifestService {
  port?: number;
  health_path?: string;
  systemd_unit?: string;
  grpc_port?: number;
  grpc_service?: string;
  [extra: string]: unknown;
}

export interface ProjectManifestNativeVersion {
  file: string;
  pattern: unknown;
  [extra: string]: unknown;
}

export interface RobotLiveness {
  schema_version: "1.0";
  stale_after_s: number;
  robots: RobotLivenessRobots[];
  [extra: string]: unknown;
}

export interface RobotLivenessRobots {
  controller_id: string;
  robot_id: number;
  state: "live" | "stale" | "unknown";
  last_update_utc?: string;
  age_s?: number;
  source?: "state" | "heartbeat";
  [extra: string]: unknown;
}

export interface RobotState {
  schema_version: "1.0";
  robot_id: string;
  state: "idle" | "busy" | "estop" | "fault" | "offline";
  source?: "real" | "simulated";
  updated_at_utc: string;
  mission_id?: string;
  battery_percent?: number;
  pose?: RobotStatePose;
  [extra: string]: unknown;
}

export interface RobotStatePose {
  schema_version: "1.0";
  frame: "base" | "tool";
  position: RobotStatePosePosition;
  orientation: RobotStatePoseOrientation;
  [extra: string]: unknown;
}

export interface RobotStatePosePosition {
  x: number;
  y: number;
  z: number;
  [extra: string]: unknown;
}

export interface RobotStatePoseOrientation {
  w: number;
  x: number;
  y: number;
  z: number;
  [extra: string]: unknown;
}

export interface SafetyState {
  schema_version: "1.0";
  state: "READY" | "INHIBITED" | "FAULT" | "SAFE_STOP";
  source: string;
  timestamp_utc: string;
  [extra: string]: unknown;
}

export interface SafetyZonesState {
  sdkSafetyState: SafetyZonesStateSdkSafetyState;
  sdkSafetyStateSignature?: SafetyZonesStateSdkSafetyStateSignature;
  reason: string | null;
  armorInhibitOnly?: true;
  configSha256?: string;
  separation?: Record<string, unknown>;
  breaches?: SafetyZonesStateBreaches[];
  breachCount?: number;
  estopRequestCount?: number;
  [extra: string]: unknown;
}

export interface SafetyZonesStateSdkSafetyState {
  schema_version: "1.0";
  state: "READY" | "INHIBITED" | "FAULT" | "SAFE_STOP";
  source: string;
  timestamp_utc: string;
  [extra: string]: unknown;
}

export interface SafetyZonesStateSdkSafetyStateSignature {
  alg: "HMAC-SHA256" | "Ed25519";
  key_id: string;
  counter: number;
  sig: string;
  [extra: string]: unknown;
}

export interface SafetyZonesStateBreaches {
  zone_id: string;
  level: string;
  object_id: string;
  [extra: string]: unknown;
}

export interface ScenarioOutcome {
  schema_version: "1.0";
  scenario_id: string;
  run_id: string;
  base_fingerprint: string;
  phase: "before" | "after";
  repro_case: string;
  observed: ScenarioOutcomeObserved;
  timestamp_utc: string;
  fingerprint_kind?: "manifest" | "live-service";
  [extra: string]: unknown;
}

export interface ScenarioOutcomeObserved {
  outcome: "reproduced" | "not-reproduced" | "error";
  exit_code?: number;
  evidence?: string;
  [extra: string]: unknown;
}

export interface ServerDiscovery {
  schema_version: "1.0";
  product: string;
  remoteApiVersion: number;
  appVersion: string;
  hostname: string;
  controllerCount: number;
  robotCount: number;
  uptimeSeconds: number;
  [extra: string]: unknown;
}

export interface ToolArms {
  schema_version: "1.0";
  ttlSeconds: number;
  arms: ToolArmsArms[];
  armedCount: number;
  staleCount: number;
  [extra: string]: unknown;
}

export interface ToolArmsArms {
  robot: string;
  toolId: number;
  armed: boolean;
  by: string;
  seq: number;
  ageSeconds: number;
  stale: boolean;
  [extra: string]: unknown;
}

export interface ToolDescriptor {
  schema_version: "1.0";
  tool_id: number;
  name: string;
  title: string;
  kind: "motion" | "actuator" | "telemetry" | "external";
  category?: string;
  hero_metric?: ToolDescriptorHeroMetric;
  limits?: ToolDescriptorLimits;
  watchdog_ms?: number;
  features?: string[];
  expansion_board?: string;
  min_firmware_version?: string;
  [extra: string]: unknown;
}

export interface ToolDescriptorHeroMetric {
  label: string;
  unit: string;
  [extra: string]: unknown;
}

export interface ToolDescriptorLimits {
  default: number;
  min: number;
  max: number;
  [extra: string]: unknown;
}

export interface ToolState {
  schema_version: "1.0";
  tool_id: number;
  state: "active" | "idle" | "fault" | "unknown";
  source: string;
  timestamp_utc: string;
  firmware_version?: string;
  can?: ToolStateCan;
  temperature_c?: number;
  setpoint_c?: number;
  mcu_temp_c?: number;
  vdda_mv?: number;
  critical_error?: boolean;
  thermal_fault?: "NONE" | "MAXTEMP" | "HEATING_NO_RISE" | "DROPPED_AT_TARGET";
  [extra: string]: unknown;
}

export interface ToolStateCan {
  state: "ok" | "error_passive" | "bus_off" | "unknown";
  tec?: number;
  rec?: number;
  bus_off_count?: number;
  [extra: string]: unknown;
}

export interface TwinState {
  schema_version: "1.0";
  source: "real" | "simulated";
  robot_id?: string;
  frame: "base" | "tool";
  timestamp_utc: string;
  sequence?: number;
  joint_states: TwinStateJointStates[];
  poses?: TwinStatePoses[];
  [extra: string]: unknown;
}

export interface TwinStateJointStates {
  name: string;
  position: number;
  velocity?: number;
  effort?: number;
  [extra: string]: unknown;
}

export interface TwinStatePoses {
  name: string;
  pose: TwinStatePosesPose;
  [extra: string]: unknown;
}

export interface TwinStatePosesPose {
  schema_version: "1.0";
  frame: "base" | "tool";
  position: TwinStatePosesPosePosition;
  orientation: TwinStatePosesPoseOrientation;
  [extra: string]: unknown;
}

export interface TwinStatePosesPosePosition {
  x: number;
  y: number;
  z: number;
  [extra: string]: unknown;
}

export interface TwinStatePosesPoseOrientation {
  w: number;
  x: number;
  y: number;
  z: number;
  [extra: string]: unknown;
}

export interface UpdateManifest {
  schema_version: "1.0";
  project: string;
  version: string;
  artifact_url: string;
  sha256: string;
  signature?: string;
  signature_alg?: "ed25519";
  key_id?: string;
  min_bootloader?: string;
  target?: string;
  [extra: string]: unknown;
}

export interface VelocityCommand {
  schema_version: "1.0";
  vx: number;
  vy: number;
  vz: number;
  wroll: number;
  wpitch: number;
  wyaw: number;
  hold: boolean;
  issued_at_ms: number;
  valid_for_ms: number;
  seq: number;
  frame_id?: string | null;
  [extra: string]: unknown;
}

export interface VisualTargetRequest {
  schema_version: "1.0";
  frame_id: string;
  current: VisualTargetRequestCurrent;
  target: VisualTargetRequestTarget;
  confidence: number;
  safety_state: "READY" | "INHIBITED" | "FAULT" | "SAFE_STOP";
  data_age_ms?: number;
  captured_at_utc?: string;
  calibration_version?: string;
  calibration_age_days?: number;
  [extra: string]: unknown;
}

export interface VisualTargetRequestCurrent {
  x: number;
  y: number;
  z: number;
  roll: number;
  pitch: number;
  yaw: number;
  [extra: string]: unknown;
}

export interface VisualTargetRequestTarget {
  x: number;
  y: number;
  z: number;
  roll: number;
  pitch: number;
  yaw: number;
  [extra: string]: unknown;
}

export interface VlaApproval {
  approved: true;
  fingerprint: string;
  robot_id: string;
  operator: string;
  approved_at_ms: number;
  expires_at_ms: number;
  signature: string;
  [extra: string]: unknown;
}

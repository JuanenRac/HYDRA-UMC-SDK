// Generated from the server contract by tools/generate_clients.py. Do not edit.

/* eslint-disable */

export interface BluetoothScan {
  success: boolean;
  devices: Record<string, unknown>[];
}

export interface BridgeCommandAccepted {
  accepted: boolean;
  /** The answer the bridge published on the result topic, as it published it; null when none arrived in time. */
  result: unknown;
}

export interface BridgeList {
  /** Whether the gateway is connected to the broker now. */
  connected: boolean;
  bridges: BridgeState[];
}

export interface BridgeState {
  name: string;
  /** True while the bridge is online (or its health report is not a FAULT), false when offline, null when it published neither. */
  available: unknown;
  /** The last retained state of the bridge exactly as it published it (null when it published none). */
  state: unknown;
  /** The last retained HealthReport of the bridge (null when it publishes none). */
  health: unknown;
  updatedAt: unknown;
}

export interface CameraCapture {
  success: boolean;
  cameraId: number;
  filename: string;
  capturedAt?: string;
  sizeBytes?: number;
  startedAt?: string;
  stoppedAt?: string;
}

export interface CameraMediaList {
  items: ({ cameraId: number; kind: "snapshots" | "recordings"; filename: string; sizeBytes: number; capturedAt: string; recording: boolean; durationMs?: number; frameCount?: number })[];
}

export interface CameraProcessStatus {
  [other: string]: { status: string; lastError: unknown; port: number };
}

export interface CanotaFlash {
  success: boolean;
  finalPhase: string;
}

export interface Clients {
  clients: Record<string, unknown>[];
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
  /** Administrators only, and only when connections.recordAddress is on. */
  ip?: string;
  /** Administrators only, and only when connections.recordAddress is on. */
  agent?: string;
}

export interface ConnectionClientList {
  clients: ConnectionClient[];
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
  /** Administrators only, and only when connections.recordAddress is on. */
  ip?: string;
  /** Administrators only, and only when connections.recordAddress is on. */
  agent?: string;
}

export interface ConnectionEventList {
  events: ConnectionEvent[];
}

export interface DeviceTokenIssued {
  /** The id of the token (22 URL-safe characters); the token itself is never kept. */
  id: string;
  /** What the administrator called the device. */
  name: string;
  /** The account the device signs in as. */
  username: string;
  createdAt: string;
  expiresAt: string;
  revokedAt: unknown;
  lastUsedAt: unknown;
  state: "active" | "expired" | "revoked";
  /** Signed token of one device; the device presents it on POST /api/device/login. */
  token: string;
}

export interface DeviceTokenList {
  items: DeviceTokenView[];
}

export interface DeviceTokenRevoked {
  revoked: boolean;
  sessionsEnded: number;
}

export interface DeviceTokenView {
  /** The id of the token (22 URL-safe characters); the token itself is never kept. */
  id: string;
  /** What the administrator called the device. */
  name: string;
  /** The account the device signs in as. */
  username: string;
  createdAt: string;
  expiresAt: string;
  revokedAt: unknown;
  lastUsedAt: unknown;
  state: "active" | "expired" | "revoked";
}

export interface EcosystemHealth {
  schema_version: string;
  generated_at_utc: string;
  /** False when the sibling checkouts could not be scanned (no services then). */
  available: boolean;
  summary: { total: number; ok: number; degraded: number; down: number; unknown: number; drift: number };
  services: ({ name: string; family: string | null; role: string | null; state: string; reason: string; version_expected: string | null; version_reported: string | null; drift: boolean; last_seen_utc: string | null; latency_ms: number | null; port?: number | null; health_path?: string | null; systemd_unit?: string | null; active_state?: string | null })[];
  /** The TLS certificate of this server; null when it runs without TLS. state is ok, expiring (fewer days left than warn_days), expired or unreadable. */
  certificate: { state?: string; not_after_utc?: string | null; days_left?: number | null; warn_days?: number } | null;
  warnings: { code: string; service?: string }[];
}

export interface EcosystemStatus {
  available: boolean;
  scannedAt: string;
  projects: { name: string; role?: unknown; stack?: unknown; maturity?: unknown; family?: unknown; version?: unknown; deploymentTarget?: unknown; servicePort?: unknown; serviceHealthPath?: unknown; serviceHost?: unknown; systemdUnit?: unknown; pid?: unknown; activeState?: unknown; subState?: unknown; live?: unknown }[];
}

export interface Error {
  error: string;
}

export interface FleetUpdateReport {
  schema: "hydra-fleet-update/1";
  id: string;
  mode: "plan" | "run";
  state: "planned" | "running" | "done" | "failed" | "blocked" | "interrupted";
  startedAt: string;
  updatedAt: string;
  error: string;
  stoppedAt: string;
  requireSignedTags: boolean;
  disk: { rootFreeMb: unknown; workspaceFreeMb: unknown };
  services: FleetUpdateRow[];
}

export interface FleetUpdateRow {
  name: string;
  kind: "repo" | "svc" | "frontend";
  repo: string;
  installed: unknown;
  latest: unknown;
  action: "update" | "current" | "skip" | "review";
  reason: string;
  state: "waiting" | "running" | "done" | "failed" | "rolled_back" | "interrupted" | "skipped" | "blocked";
  step: "" | "disk" | "fetching" | "backup" | "building" | "installing" | "verifying" | "done";
  substep?: string;
  substeps?: number;
  detail: string;
  error: string;
  order: number;
  elapsedS?: number;
  freeMb?: unknown;
  needMb?: unknown;
  unitRestored?: unknown;
  log: { at: string; text: string }[];
}

export interface FleetUpdateStatus {
  applyEnabled: boolean;
  busy: boolean;
  report: unknown;
}

export interface GlobalStopReleased {
  success: boolean;
  /** Whether the retained READY went out on the MQTT bridge (false when announcing is not configured or the broker is not connected). */
  announced: boolean;
}

export interface HealthReport {
  schema_version: string;
  state: string;
  timestamp_utc: string;
  checks: Record<string, unknown>;
  service?: string;
}

export interface HydraInfo {
  schema_version: string;
  product: string;
  remoteApiVersion: number;
  appVersion: string;
  hostname: string;
  controllerCount: number;
  robotCount: number;
  uptimeSeconds: number;
  /** The addresses of this server on the local network. Present only while an administrator allowed it (discovery.advertiseAddress); a client must not rely on it. */
  addresses?: string[];
}

export interface InfoTicket {
  /** Signed ticket for the read-only information routes; it goes in the address as ?ticket=. */
  ticket: string;
  expiresInSeconds: number;
}

export interface JwksDocument {
  keys: { kty: "OKP"; crv: "Ed25519"; x: string; kid: string; use: "sig"; alg: "EdDSA" }[];
}

export interface JwtKeyRotated {
  success: boolean;
  /** The key id of the new active key. */
  kid: string;
  algorithm: "HS256" | "EdDSA";
  keys: { kid: string; createdAt: number; retiredAt: unknown; active: boolean; acceptedUntil: unknown }[];
  jwksPath: string;
}

export interface JwtKeys {
  algorithm: "HS256" | "EdDSA";
  keys: { kid: string; createdAt: number; retiredAt: unknown; active: boolean; acceptedUntil: unknown }[];
  jwksPath: string;
}

export interface LiveActivityRegistered {
  registered: boolean;
}

export interface LiveActivityRemoved {
  removed: boolean;
}

export interface LogLines {
  lines: string[];
}

export interface LoginResult {
  success: boolean;
  token: string;
  refreshToken: string;
  role: string;
}

export interface MaintenanceOutcome {
  ok: boolean;
  action: "status" | "install" | "rollback" | "prune";
  exitCode: number;
  timedOut: boolean;
  result: unknown;
  message: string;
}

export interface ModelList {
  models: Record<string, unknown>[];
}

export interface ModelSubmitted {
  success: boolean;
  slug: string;
}

export interface NodeHealth {
  /** False when the brain did not answer (its build has the health query off, or the link is down): then only slot and source carry anything. */
  online: boolean;
  slot: number;
  /** True when the brain has heard a health frame of the slot, false when it never has, null when it did not answer. */
  heard: unknown;
  /** How long ago the brain heard it, in steps of 100 ms. */
  ageMs?: number;
  sequence?: number;
  flags?: number;
  flagNames?: string[];
  txErrors?: number;
  rxErrors?: number;
  stalls?: number;
  /** Seconds since the board started, in steps of 16 (4080 means 4080 or more). */
  uptimeS?: number;
  source: "brain-health";
}

export interface OperatorPresence {
  state: "unknown" | "present" | "lost" | "left" | "recovering";
  lastSequence: unknown;
  secondsSinceBeat: unknown;
  action: "slow" | "pause" | "notify" | "stop";
  timeoutSeconds: number;
  degradedRobots: number[];
}

export interface OperatorPresenceAck {
  accepted: boolean;
  duplicate: boolean;
  stale: boolean;
  state: "present" | "lost" | "left" | "recovering";
  sequence: number;
  action: "slow" | "pause" | "notify" | "stop";
  timeoutSeconds: number;
}

export interface Passthrough {
}

export interface PtzResult {
  ok: boolean;
}

export interface PushDeviceRegistered {
  registered: boolean;
}

export interface PushDeviceRemoved {
  removed: boolean;
}

export interface PushStatus {
  enabled: boolean;
  configured: boolean;
  problem: "missing" | "key-in-repo" | "key-unreadable" | "invalid" | null;
  devices: number;
  sandbox: boolean;
  events: { jobFinished: boolean; globalStop: boolean };
  /** The Live Activity on the lock screen: whether it is sent (off by default), the most it may show (status, progress or full; status by default) and how many activities are registered. */
  liveActivity?: { enabled: boolean; level: "status" | "progress" | "full"; activities: number };
}

export interface Reachable {
  reachable: boolean;
}

export interface Reservation {
  success: boolean;
  reservation?: unknown;
  reservationHistory: Record<string, unknown>[];
}

export interface RobotLiveness {
  schema_version: string;
  stale_after_s: number;
  robots: { controller_id: string; robot_id: number; state: string; last_update_utc?: string; age_s?: number; source?: string }[];
}

export interface RulConfig {
  /** True only when the relay is open to operators (rul.enabled, or HYDRA_UMC_RUL=1). */
  enabled: boolean;
  /** Largest number of points the relay accepts in one request. */
  maxPoints: number;
  /** How long the relay waits for the detector, in milliseconds. */
  timeoutMs: number;
}

export interface SelfUpdateItem {
  id: "server" | "studio" | "os-agent";
  repo: string;
  installed: unknown;
  previous: unknown;
  latest: unknown;
  state: "current" | "behind" | "ahead" | "unknown";
  /** Whether the newest release carries the package, its hash and its signature. */
  signedPackage: boolean;
}

export interface SelfUpdateJob {
  id: string;
  action: "apply" | "rollback";
  component: "server" | "studio" | "os-agent";
  state: "checking" | "downloading" | "verifying" | "applying" | "restarting" | "done" | "failed";
  fromVersion: unknown;
  targetVersion: unknown;
  startedAt: string;
  updatedAt: string;
  error: "no_release" | "already_current" | "no_signed_package" | "download_failed" | "package_too_large" | "signature_invalid" | "no_earlier_release" | "start_failed" | "rolled_back" | "deploy_failed" | "timeout" | "interrupted" | null;
  detail: string;
  packageName?: string;
  log: ({ at: string; step: "checking" | "downloading" | "verifying" | "applying" | "restarting" | "done" | "failed"; text: string })[];
  by: string;
}

export interface SelfUpdateStatus {
  checkedAt: unknown;
  owner: string;
  rateLimited: boolean;
  items: SelfUpdateItem[];
  applyEnabled: boolean;
  job: unknown;
}

export interface ServerConfig {
  port: number;
  pendingPort: unknown;
}

export interface ServerConfigSaved {
  success: boolean;
  appliesOnRestart: boolean;
}

export interface ServiceIdentityStatus {
  enabled: boolean;
  source: "env" | "config" | "default";
  /** True when the switch comes from the environment (HYDRA_UMC_SERVICE_IDENTITY) and cannot be changed here. */
  locked: boolean;
  /** Whether JWT_SECRET can sign: unset, an example value or too short is unusable. */
  key: "usable" | "unusable";
  state: "presenting" | "idle_no_key" | "off";
  services: ({ name: string; support: "accepts" | "own_verifier" | "not_yet" })[];
  /** The safe order of the steps, as codes the screens translate. */
  order: ("server_first" | "then_one_by_one" | "enable_in_root" | "restart_unit" | "check_status")[];
}

export interface Settings {
  controllers?: Record<string, unknown>[];
}

export interface StopAllResult {
  success: boolean;
  stoppedCount: number;
  failedCount: number;
  persisted: boolean;
  /** Present only when announcing a global stop is configured (safety.publishGlobalStop): whether the retained SAFE_STOP went out on the MQTT bridge. */
  announced?: boolean;
  robots: { robotId: number; controllerId: string; name: string; stopped: boolean; valvesOff: number; pumpsOff: number; reservedBy?: string; error?: string }[];
}

export interface Success {
  success: boolean;
}

export interface SupervisorSnapshot {
}

export interface SystemMetrics {
  cpu_load: number;
  memory_usage: number;
  temp: unknown;
  temp_is_real: boolean;
  rp1_temp: unknown;
  uptime: number;
  network: Record<string, unknown>;
}

export interface ToolArmResetResult {
  success: boolean;
  robot: string;
  toolId: number;
}

export interface ToolArmsReport {
  schema_version: string;
  ttlSeconds: number;
  arms: { robot: string; toolId: number; armed: boolean; by?: string; seq: number; ageSeconds: number; stale: boolean }[];
  armedCount: number;
  staleCount: number;
}

export interface TotpConfirmed {
  success: boolean;
  recoveryCodes: string[];
}

export interface TotpEnrolment {
  success: boolean;
  secret: string;
  uri: string;
}

export interface TotpStatus {
  enabled: boolean;
  recoveryLeft: number;
}

export interface UpdateItem {
  name: string;
  family: unknown;
  installed: unknown;
  /** The newest published release, or null when it could not be looked up. */
  latest: unknown;
  state: "current" | "behind" | "ahead" | "unknown";
}

export interface UpdateReport {
  checkedAt: unknown;
  owner: string;
  /** True when GitHub refused for quota during the look; the programs it did not reach have no newest version. */
  rateLimited: boolean;
  items: UpdateItem[];
}

export interface UsbDevices {
  devices: Record<string, unknown>[];
}

export interface UserList {
  users: Record<string, unknown>[];
}

export interface VoiceReply {
  type: unknown;
  requestId: string;
  text: string;
  level: string;
  speak: boolean;
  requiresConfirmation: boolean;
  visualState?: string;
  intent?: Record<string, unknown>;
  interpretation?: Record<string, unknown>;
  messageCode?: string;
  messageParams?: Record<string, unknown>;
  textLanguage?: string;
  confirmationToken?: string;
  confirmationValiditySeconds?: number;
}

export interface WatchStatus {
  type: unknown;
  headline: string;
  detail: string;
  level: "NOMINAL" | "WARNING" | "CRITICAL";
  speak: boolean;
}

export interface HydraRequest {
  readonly method: string;
  readonly path: string;
  readonly query: Readonly<Record<string, string>>;
  readonly body: unknown;
  readonly access: string;
}

/** Carries one request to the server and returns the decoded JSON of the answer (undefined when there is none). */
export type HydraTransport = (request: HydraRequest) => Promise<unknown>;

export function fillPath(template: string, values: Readonly<Record<string, string | number>> | undefined): string {
  return template.replace(/\{([^}]+)\}/g, (_whole, name: string) => {
    const value = values?.[name];
    if (value === undefined || value === "") throw new Error(`missing path parameter ${name}`);
    return encodeURIComponent(String(value));
  });
}

export function queryOf(values: Readonly<Record<string, unknown>> | undefined): Record<string, string> {
  const found: Record<string, string> = {};
  for (const [name, value] of Object.entries(values ?? {})) {
    if (value !== undefined && value !== null) found[name] = String(value);
  }
  return found;
}

export class HydraServerClient {
  constructor(private readonly transport: HydraTransport) {}

  /** GET /.well-known/jwks.json (access: public) */
  getWellKnownJwksJson(): Promise<JwksDocument> {
    return this.transport({ method: "GET", path: "/.well-known/jwks.json", query: {}, body: undefined, access: "public" }) as Promise<JwksDocument>;
  }

  /** GET /api/adapters (access: user) */
  getAdapters(): Promise<Passthrough> {
    return this.transport({ method: "GET", path: "/api/adapters", query: {}, body: undefined, access: "user" }) as Promise<Passthrough>;
  }

  /** GET /api/adapters/{adapterId} (access: user) */
  getAdaptersByAdapterId(args: { path: { adapterId: string } }): Promise<void> {
    return this.transport({ method: "GET", path: fillPath("/api/adapters/{adapterId}", args?.path), query: {}, body: undefined, access: "user" }) as Promise<void>;
  }

  /** GET /api/admin/clients (access: admin) */
  getAdminClients(): Promise<Clients> {
    return this.transport({ method: "GET", path: "/api/admin/clients", query: {}, body: undefined, access: "admin" }) as Promise<Clients>;
  }

  /** GET /api/admin/device-tokens (access: admin) */
  getAdminDeviceTokens(): Promise<DeviceTokenList> {
    return this.transport({ method: "GET", path: "/api/admin/device-tokens", query: {}, body: undefined, access: "admin" }) as Promise<DeviceTokenList>;
  }

  /** POST /api/admin/device-tokens (access: admin) */
  postAdminDeviceTokens(args: { body: { name: string; username: string; ttlDays?: number; confirm: boolean } }): Promise<DeviceTokenIssued> {
    return this.transport({ method: "POST", path: "/api/admin/device-tokens", query: {}, body: args?.body, access: "admin" }) as Promise<DeviceTokenIssued>;
  }

  /** DELETE /api/admin/device-tokens/{id} (access: admin) */
  deleteAdminDeviceTokensById(args: { path: { id: string } }): Promise<DeviceTokenRevoked> {
    return this.transport({ method: "DELETE", path: fillPath("/api/admin/device-tokens/{id}", args?.path), query: {}, body: undefined, access: "admin" }) as Promise<DeviceTokenRevoked>;
  }

  /** GET /api/admin/fleet-update (access: admin) */
  getAdminFleetUpdate(): Promise<FleetUpdateStatus> {
    return this.transport({ method: "GET", path: "/api/admin/fleet-update", query: {}, body: undefined, access: "admin" }) as Promise<FleetUpdateStatus>;
  }

  /** POST /api/admin/fleet-update/apply (access: admin) */
  postAdminFleetUpdateApply(args: { body: { services?: string[]; confirm: true } }): Promise<FleetUpdateStatus> {
    return this.transport({ method: "POST", path: "/api/admin/fleet-update/apply", query: {}, body: args?.body, access: "admin" }) as Promise<FleetUpdateStatus>;
  }

  /** POST /api/admin/fleet-update/plan (access: admin) */
  postAdminFleetUpdatePlan(): Promise<FleetUpdateStatus> {
    return this.transport({ method: "POST", path: "/api/admin/fleet-update/plan", query: {}, body: undefined, access: "admin" }) as Promise<FleetUpdateStatus>;
  }

  /** POST /api/admin/fleet-update/resume (access: admin) */
  postAdminFleetUpdateResume(args: { body: { service: string; confirm: true } }): Promise<FleetUpdateStatus> {
    return this.transport({ method: "POST", path: "/api/admin/fleet-update/resume", query: {}, body: args?.body, access: "admin" }) as Promise<FleetUpdateStatus>;
  }

  /** GET /api/admin/jwt-keys (access: admin) */
  getAdminJwtKeys(): Promise<JwtKeys> {
    return this.transport({ method: "GET", path: "/api/admin/jwt-keys", query: {}, body: undefined, access: "admin" }) as Promise<JwtKeys>;
  }

  /** POST /api/admin/jwt-keys/rotate (access: admin) */
  postAdminJwtKeysRotate(): Promise<JwtKeyRotated> {
    return this.transport({ method: "POST", path: "/api/admin/jwt-keys/rotate", query: {}, body: undefined, access: "admin" }) as Promise<JwtKeyRotated>;
  }

  /** GET /api/admin/logs (access: admin) */
  getAdminLogs(args?: { query?: { lines?: string } }): Promise<LogLines> {
    return this.transport({ method: "GET", path: "/api/admin/logs", query: queryOf(args?.query), body: undefined, access: "admin" }) as Promise<LogLines>;
  }

  /** POST /api/admin/maintenance/install (access: admin) */
  postAdminMaintenanceInstall(args: { body: { package: string; allowDowngrade?: boolean; confirm: boolean } }): Promise<MaintenanceOutcome> {
    return this.transport({ method: "POST", path: "/api/admin/maintenance/install", query: {}, body: args?.body, access: "admin" }) as Promise<MaintenanceOutcome>;
  }

  /** POST /api/admin/maintenance/prune (access: admin) */
  postAdminMaintenancePrune(args: { body: { component: string; keep?: number; confirm: boolean } }): Promise<MaintenanceOutcome> {
    return this.transport({ method: "POST", path: "/api/admin/maintenance/prune", query: {}, body: args?.body, access: "admin" }) as Promise<MaintenanceOutcome>;
  }

  /** POST /api/admin/maintenance/rollback (access: admin) */
  postAdminMaintenanceRollback(args: { body: { component: string; confirm: boolean } }): Promise<MaintenanceOutcome> {
    return this.transport({ method: "POST", path: "/api/admin/maintenance/rollback", query: {}, body: args?.body, access: "admin" }) as Promise<MaintenanceOutcome>;
  }

  /** GET /api/admin/maintenance/status (access: admin) */
  getAdminMaintenanceStatus(args?: { query?: { component?: string } }): Promise<MaintenanceOutcome> {
    return this.transport({ method: "GET", path: "/api/admin/maintenance/status", query: queryOf(args?.query), body: undefined, access: "admin" }) as Promise<MaintenanceOutcome>;
  }

  /** GET /api/admin/push (access: admin) */
  getAdminPush(): Promise<PushStatus> {
    return this.transport({ method: "GET", path: "/api/admin/push", query: {}, body: undefined, access: "admin" }) as Promise<PushStatus>;
  }

  /** POST /api/admin/restart (access: admin) */
  postAdminRestart(): Promise<Success> {
    return this.transport({ method: "POST", path: "/api/admin/restart", query: {}, body: undefined, access: "admin" }) as Promise<Success>;
  }

  /** GET /api/admin/robot-ids (access: admin) */
  getAdminRobotIds(): Promise<{ ok: boolean; ambiguousCount: number; ambiguous: { robotId: number; controllers: string[] }[] }> {
    return this.transport({ method: "GET", path: "/api/admin/robot-ids", query: {}, body: undefined, access: "admin" }) as Promise<{ ok: boolean; ambiguousCount: number; ambiguous: { robotId: number; controllers: string[] }[] }>;
  }

  /** PUT /api/admin/safety-limits (access: admin) */
  putAdminSafetyLimits(): Promise<void> {
    return this.transport({ method: "PUT", path: "/api/admin/safety-limits", query: {}, body: undefined, access: "admin" }) as Promise<void>;
  }

  /** GET /api/admin/self-update (access: admin) */
  getAdminSelfUpdate(args?: { query?: { refresh?: string } }): Promise<SelfUpdateStatus> {
    return this.transport({ method: "GET", path: "/api/admin/self-update", query: queryOf(args?.query), body: undefined, access: "admin" }) as Promise<SelfUpdateStatus>;
  }

  /** POST /api/admin/self-update/apply (access: admin) */
  postAdminSelfUpdateApply(args: { body: { component: "server" | "studio" | "os-agent"; confirm: true } }): Promise<SelfUpdateJob> {
    return this.transport({ method: "POST", path: "/api/admin/self-update/apply", query: {}, body: args?.body, access: "admin" }) as Promise<SelfUpdateJob>;
  }

  /** GET /api/admin/self-update/jobs/{id} (access: admin) */
  getAdminSelfUpdateJobsById(args: { path: { id: string } }): Promise<SelfUpdateJob> {
    return this.transport({ method: "GET", path: fillPath("/api/admin/self-update/jobs/{id}", args?.path), query: {}, body: undefined, access: "admin" }) as Promise<SelfUpdateJob>;
  }

  /** POST /api/admin/self-update/rollback (access: admin) */
  postAdminSelfUpdateRollback(args: { body: { component: "server" | "studio" | "os-agent"; confirm: true } }): Promise<SelfUpdateJob> {
    return this.transport({ method: "POST", path: "/api/admin/self-update/rollback", query: {}, body: args?.body, access: "admin" }) as Promise<SelfUpdateJob>;
  }

  /** GET /api/admin/server-config (access: admin) */
  getAdminServerConfig(): Promise<ServerConfig> {
    return this.transport({ method: "GET", path: "/api/admin/server-config", query: {}, body: undefined, access: "admin" }) as Promise<ServerConfig>;
  }

  /** PUT /api/admin/server-config (access: admin) */
  putAdminServerConfig(args: { body: { port: number } }): Promise<ServerConfigSaved> {
    return this.transport({ method: "PUT", path: "/api/admin/server-config", query: {}, body: args?.body, access: "admin" }) as Promise<ServerConfigSaved>;
  }

  /** GET /api/admin/service-identity (access: admin) */
  getAdminServiceIdentity(): Promise<ServiceIdentityStatus> {
    return this.transport({ method: "GET", path: "/api/admin/service-identity", query: {}, body: undefined, access: "admin" }) as Promise<ServiceIdentityStatus>;
  }

  /** GET /api/admin/updates (access: admin) */
  getAdminUpdates(args?: { query?: { refresh?: string } }): Promise<UpdateReport> {
    return this.transport({ method: "GET", path: "/api/admin/updates", query: queryOf(args?.query), body: undefined, access: "admin" }) as Promise<UpdateReport>;
  }

  /** GET /api/anomaly/verdicts (access: user) */
  getAnomalyVerdicts(args?: { query?: { verdict?: string; verify?: string } }): Promise<void> {
    return this.transport({ method: "GET", path: "/api/anomaly/verdicts", query: queryOf(args?.query), body: undefined, access: "user" }) as Promise<void>;
  }

  /** GET /api/audit (access: admin) */
  getAudit(args?: { query?: { afterSeq?: string; format?: string; limit?: string; robotId?: string; type?: string; verify?: string } }): Promise<void> {
    return this.transport({ method: "GET", path: "/api/audit", query: queryOf(args?.query), body: undefined, access: "admin" }) as Promise<void>;
  }

  /** GET /api/bridges (access: user) */
  getBridges(): Promise<BridgeList> {
    return this.transport({ method: "GET", path: "/api/bridges", query: {}, body: undefined, access: "user" }) as Promise<BridgeList>;
  }

  /** POST /api/bridges/{name}/cmd/{verb} (access: user) */
  postBridgesByNameCmdByVerb(args: { path: { name: string; verb: string }; body?: Record<string, unknown> }): Promise<BridgeCommandAccepted> {
    return this.transport({ method: "POST", path: fillPath("/api/bridges/{name}/cmd/{verb}", args?.path), query: {}, body: args?.body, access: "user" }) as Promise<BridgeCommandAccepted>;
  }

  /** GET /api/bridges/{name}/state (access: user) */
  getBridgesByNameState(args: { path: { name: string } }): Promise<BridgeState> {
    return this.transport({ method: "GET", path: fillPath("/api/bridges/{name}/state", args?.path), query: {}, body: undefined, access: "user" }) as Promise<BridgeState>;
  }

  /** POST /api/camera/discover-rtsp-path (access: admin) */
  postCameraDiscoverRtspPath(args: { body: { host: string; port?: number; username?: string; password?: string } }): Promise<void> {
    return this.transport({ method: "POST", path: "/api/camera/discover-rtsp-path", query: {}, body: args?.body, access: "admin" }) as Promise<void>;
  }

  /** GET /api/camera/discover-usb-devices (access: user) */
  getCameraDiscoverUsbDevices(): Promise<UsbDevices> {
    return this.transport({ method: "GET", path: "/api/camera/discover-usb-devices", query: {}, body: undefined, access: "user" }) as Promise<UsbDevices>;
  }

  /** GET /api/camera/media (access: user) */
  getCameraMedia(): Promise<CameraMediaList> {
    return this.transport({ method: "GET", path: "/api/camera/media", query: {}, body: undefined, access: "user" }) as Promise<CameraMediaList>;
  }

  /** GET /api/camera/media/{cameraId}/{kind}/{filename} (access: public) */
  getCameraMediaByCameraIdByKindByFilename(args: { path: { cameraId: number; kind: string; filename: string } }): Promise<void> {
    return this.transport({ method: "GET", path: fillPath("/api/camera/media/{cameraId}/{kind}/{filename}", args?.path), query: {}, body: undefined, access: "public" }) as Promise<void>;
  }

  /** DELETE /api/camera/media/{cameraId}/{kind}/{filename} (access: user) */
  deleteCameraMediaByCameraIdByKindByFilename(args: { path: { cameraId: number; kind: string; filename: string } }): Promise<CameraCapture> {
    return this.transport({ method: "DELETE", path: fillPath("/api/camera/media/{cameraId}/{kind}/{filename}", args?.path), query: {}, body: undefined, access: "user" }) as Promise<CameraCapture>;
  }

  /** POST /api/camera/ticket (access: user) */
  postCameraTicket(): Promise<void> {
    return this.transport({ method: "POST", path: "/api/camera/ticket", query: {}, body: undefined, access: "user" }) as Promise<void>;
  }

  /** POST /api/camera/{id}/ptz (access: admin) */
  postCameraByIdPtz(args: { path: { id: number }; body: { host: string; port?: number; username?: string; password?: string; channel?: number; pan?: number; tilt?: number; zoom?: number } }): Promise<PtzResult> {
    return this.transport({ method: "POST", path: fillPath("/api/camera/{id}/ptz", args?.path), query: {}, body: args?.body, access: "admin" }) as Promise<PtzResult>;
  }

  /** POST /api/camera/{id}/recording/start (access: user) */
  postCameraByIdRecordingStart(args: { path: { id: number } }): Promise<CameraCapture> {
    return this.transport({ method: "POST", path: fillPath("/api/camera/{id}/recording/start", args?.path), query: {}, body: undefined, access: "user" }) as Promise<CameraCapture>;
  }

  /** POST /api/camera/{id}/recording/stop (access: user) */
  postCameraByIdRecordingStop(args: { path: { id: number } }): Promise<CameraCapture> {
    return this.transport({ method: "POST", path: fillPath("/api/camera/{id}/recording/stop", args?.path), query: {}, body: undefined, access: "user" }) as Promise<CameraCapture>;
  }

  /** POST /api/camera/{id}/snapshot (access: user) */
  postCameraByIdSnapshot(args: { path: { id: number } }): Promise<CameraCapture> {
    return this.transport({ method: "POST", path: fillPath("/api/camera/{id}/snapshot", args?.path), query: {}, body: undefined, access: "user" }) as Promise<CameraCapture>;
  }

  /** GET /api/camera/{id}/stream (access: public) */
  getCameraByIdStream(args: { path: { id: number } }): Promise<void> {
    return this.transport({ method: "GET", path: fillPath("/api/camera/{id}/stream", args?.path), query: {}, body: undefined, access: "public" }) as Promise<void>;
  }

  /** GET /api/cameras/status (access: user) */
  getCamerasStatus(): Promise<CameraProcessStatus> {
    return this.transport({ method: "GET", path: "/api/cameras/status", query: {}, body: undefined, access: "user" }) as Promise<CameraProcessStatus>;
  }

  /** GET /api/claims (access: user) */
  getClaims(): Promise<void> {
    return this.transport({ method: "GET", path: "/api/claims", query: {}, body: undefined, access: "user" }) as Promise<void>;
  }

  /** List the clients the server has seen (access: user) */
  getConnectionsClients(args?: { query?: { kind?: "studio" | "suite" | "android" | "ios" | "dsi" | "watch" | "voice" | "other"; user?: string; active?: "1" | "true" } }): Promise<ConnectionClientList> {
    return this.transport({ method: "GET", path: "/api/connections/clients", query: queryOf(args?.query), body: undefined, access: "user" }) as Promise<ConnectionClientList>;
  }

  /** List the history of the sign-ins of the clients (access: user) */
  getConnectionsEvents(args?: { query?: { kind?: "studio" | "suite" | "android" | "ios" | "dsi" | "watch" | "voice" | "other"; action?: "first_seen" | "login" | "login_failed" | "second_factor_failed" | "logout" | "session_ended" | "session_expired"; user?: string; before?: string; limit?: string } }): Promise<ConnectionEventList> {
    return this.transport({ method: "GET", path: "/api/connections/events", query: queryOf(args?.query), body: undefined, access: "user" }) as Promise<ConnectionEventList>;
  }

  /** GET /api/connector-hub/gate/audit (access: user) */
  getConnectorHubGateAudit(): Promise<Passthrough> {
    return this.transport({ method: "GET", path: "/api/connector-hub/gate/audit", query: {}, body: undefined, access: "user" }) as Promise<Passthrough>;
  }

  /** POST /api/connector-hub/gate/evaluate (access: user) */
  postConnectorHubGateEvaluate(): Promise<Passthrough> {
    return this.transport({ method: "POST", path: "/api/connector-hub/gate/evaluate", query: {}, body: undefined, access: "user" }) as Promise<Passthrough>;
  }

  /** GET /api/connector-hub/gate/settings (access: user) */
  getConnectorHubGateSettings(): Promise<void> {
    return this.transport({ method: "GET", path: "/api/connector-hub/gate/settings", query: {}, body: undefined, access: "user" }) as Promise<void>;
  }

  /** POST /api/connector-hub/gate/settings (access: admin) */
  postConnectorHubGateSettings(): Promise<void> {
    return this.transport({ method: "POST", path: "/api/connector-hub/gate/settings", query: {}, body: undefined, access: "admin" }) as Promise<void>;
  }

  /** GET /api/dev-server/status (access: user) */
  getDevServerStatus(args?: { query?: { verify?: string } }): Promise<void> {
    return this.transport({ method: "GET", path: "/api/dev-server/status", query: queryOf(args?.query), body: undefined, access: "user" }) as Promise<void>;
  }

  /** GET /api/developer-node/status (access: user) */
  getDeveloperNodeStatus(args?: { query?: { verify?: string } }): Promise<void> {
    return this.transport({ method: "GET", path: "/api/developer-node/status", query: queryOf(args?.query), body: undefined, access: "user" }) as Promise<void>;
  }

  /** POST /api/device/login (access: public) */
  postDeviceLogin(args: { body: { token: string } }): Promise<LoginResult> {
    return this.transport({ method: "POST", path: "/api/device/login", query: {}, body: args?.body, access: "public" }) as Promise<LoginResult>;
  }

  /** GET /api/droid-estop/settings (access: user) */
  getDroidEstopSettings(): Promise<void> {
    return this.transport({ method: "GET", path: "/api/droid-estop/settings", query: {}, body: undefined, access: "user" }) as Promise<void>;
  }

  /** POST /api/droid-estop/settings (access: admin) */
  postDroidEstopSettings(): Promise<void> {
    return this.transport({ method: "POST", path: "/api/droid-estop/settings", query: {}, body: undefined, access: "admin" }) as Promise<void>;
  }

  /** GET /api/ecosystem/health (access: user) */
  getEcosystemHealth(): Promise<EcosystemHealth> {
    return this.transport({ method: "GET", path: "/api/ecosystem/health", query: {}, body: undefined, access: "user" }) as Promise<EcosystemHealth>;
  }

  /** GET /api/ecosystem/node-health (access: user) */
  getEcosystemNodeHealth(args?: { query?: { slot?: string } }): Promise<NodeHealth> {
    return this.transport({ method: "GET", path: "/api/ecosystem/node-health", query: queryOf(args?.query), body: undefined, access: "user" }) as Promise<NodeHealth>;
  }

  /** POST /api/ecosystem/service/{unit}/{action} (access: admin) */
  postEcosystemServiceByUnitByAction(args: { path: { unit: string; action: string } }): Promise<Success> {
    return this.transport({ method: "POST", path: fillPath("/api/ecosystem/service/{unit}/{action}", args?.path), query: {}, body: undefined, access: "admin" }) as Promise<Success>;
  }

  /** GET /api/ecosystem/status (access: public) */
  getEcosystemStatus(): Promise<EcosystemStatus> {
    return this.transport({ method: "GET", path: "/api/ecosystem/status", query: {}, body: undefined, access: "public" }) as Promise<EcosystemStatus>;
  }

  /** GET /api/faults (access: user) */
  getFaults(args?: { query?: { active?: string; limit?: string; verify?: string } }): Promise<void> {
    return this.transport({ method: "GET", path: "/api/faults", query: queryOf(args?.query), body: undefined, access: "user" }) as Promise<void>;
  }

  /** POST /api/hardware/canota/flash (access: admin) */
  postHardwareCanotaFlash(): Promise<CanotaFlash> {
    return this.transport({ method: "POST", path: "/api/hardware/canota/flash", query: {}, body: undefined, access: "admin" }) as Promise<CanotaFlash>;
  }

  /** GET /api/hardware/canota/version (access: user) */
  getHardwareCanotaVersion(args?: { query?: { relay?: string; slot?: string; tier?: string } }): Promise<Passthrough> {
    return this.transport({ method: "GET", path: "/api/hardware/canota/version", query: queryOf(args?.query), body: undefined, access: "user" }) as Promise<Passthrough>;
  }

  /** POST /api/hardware/fram/erase (access: admin) */
  postHardwareFramErase(): Promise<Passthrough> {
    return this.transport({ method: "POST", path: "/api/hardware/fram/erase", query: {}, body: undefined, access: "admin" }) as Promise<Passthrough>;
  }

  /** POST /api/hardware/fram/selftest (access: admin) */
  postHardwareFramSelftest(): Promise<Passthrough> {
    return this.transport({ method: "POST", path: "/api/hardware/fram/selftest", query: {}, body: undefined, access: "admin" }) as Promise<Passthrough>;
  }

  /** GET /api/hil-bridge/settings (access: user) */
  getHilBridgeSettings(): Promise<void> {
    return this.transport({ method: "GET", path: "/api/hil-bridge/settings", query: {}, body: undefined, access: "user" }) as Promise<void>;
  }

  /** POST /api/hil-bridge/settings (access: admin) */
  postHilBridgeSettings(): Promise<void> {
    return this.transport({ method: "POST", path: "/api/hil-bridge/settings", query: {}, body: undefined, access: "admin" }) as Promise<void>;
  }

  /** GET /api/hydra-info (access: public) */
  getHydraInfo(): Promise<HydraInfo> {
    return this.transport({ method: "GET", path: "/api/hydra-info", query: {}, body: undefined, access: "public" }) as Promise<HydraInfo>;
  }

  /** POST /api/info/ticket (access: user) */
  postInfoTicket(args?: { body?: { ttlSeconds?: unknown } }): Promise<InfoTicket> {
    return this.transport({ method: "POST", path: "/api/info/ticket", query: {}, body: args?.body, access: "user" }) as Promise<InfoTicket>;
  }

  /** POST /api/ingest/dev-server/status (access: public) */
  postIngestDevServerStatus(): Promise<void> {
    return this.transport({ method: "POST", path: "/api/ingest/dev-server/status", query: {}, body: undefined, access: "public" }) as Promise<void>;
  }

  /** POST /api/ingest/developer-node/status (access: public) */
  postIngestDeveloperNodeStatus(): Promise<void> {
    return this.transport({ method: "POST", path: "/api/ingest/developer-node/status", query: {}, body: undefined, access: "public" }) as Promise<void>;
  }

  /** POST /api/ingest/scenario-outcome (access: user) */
  postIngestScenarioOutcome(): Promise<void> {
    return this.transport({ method: "POST", path: "/api/ingest/scenario-outcome", query: {}, body: undefined, access: "user" }) as Promise<void>;
  }

  /** GET /api/ingest/scenario-outcomes (access: user) */
  getIngestScenarioOutcomes(args?: { query?: { fingerprint_kind?: string; limit?: string; scenario_id?: string; verify?: string } }): Promise<void> {
    return this.transport({ method: "GET", path: "/api/ingest/scenario-outcomes", query: queryOf(args?.query), body: undefined, access: "user" }) as Promise<void>;
  }

  /** POST /api/integrations/test-connection (access: user) */
  postIntegrationsTestConnection(args: { body: { host: string; port: number } }): Promise<Reachable> {
    return this.transport({ method: "POST", path: "/api/integrations/test-connection", query: {}, body: args?.body, access: "user" }) as Promise<Reachable>;
  }

  /** POST /api/login (access: public) */
  postLogin(args: { body: { username: string; password: string; totp?: string } }): Promise<LoginResult> {
    return this.transport({ method: "POST", path: "/api/login", query: {}, body: args?.body, access: "public" }) as Promise<LoginResult>;
  }

  /** POST /api/logout (access: public) */
  postLogout(args?: { body?: { refreshToken?: string } }): Promise<Success> {
    return this.transport({ method: "POST", path: "/api/logout", query: {}, body: args?.body, access: "public" }) as Promise<Success>;
  }

  /** GET /api/models (access: public) */
  getModels(): Promise<ModelList> {
    return this.transport({ method: "GET", path: "/api/models", query: {}, body: undefined, access: "public" }) as Promise<ModelList>;
  }

  /** POST /api/models/submit (access: admin) */
  postModelsSubmit(args?: { body?: { category?: unknown; meshFiles?: unknown; name?: unknown; overwrite?: unknown; urdfFilename?: unknown; urdfXml?: unknown } }): Promise<ModelSubmitted> {
    return this.transport({ method: "POST", path: "/api/models/submit", query: {}, body: args?.body, access: "admin" }) as Promise<ModelSubmitted>;
  }

  /** GET /api/models/{category}/{slug}/download (access: public) */
  getModelsByCategoryBySlugDownload(args: { path: { category: string; slug: string } }): Promise<void> {
    return this.transport({ method: "GET", path: fillPath("/api/models/{category}/{slug}/download", args?.path), query: {}, body: undefined, access: "public" }) as Promise<void>;
  }

  /** POST /api/operator/confirmations (access: user) */
  postOperatorConfirmations(args: { body: { action: string; job_id: string; confirm: true; ttl_seconds?: number } }): Promise<{ token: string; action: string; job_id: string; expires_at: number; ttl_seconds: number; single_use: true }> {
    return this.transport({ method: "POST", path: "/api/operator/confirmations", query: {}, body: args?.body, access: "user" }) as Promise<{ token: string; action: string; job_id: string; expires_at: number; ttl_seconds: number; single_use: true }>;
  }

  /** GET /api/operator/presence (access: user) */
  getOperatorPresence(): Promise<OperatorPresence> {
    return this.transport({ method: "GET", path: "/api/operator/presence", query: {}, body: undefined, access: "user" }) as Promise<OperatorPresence>;
  }

  /** POST /api/operator/presence (access: user) */
  postOperatorPresence(args: { body: { type?: "presence_heartbeat"; protocolVersion?: number; sequence: number; intervalSeconds: number; state: "PRESENT" | "LEFT" } }): Promise<OperatorPresenceAck> {
    return this.transport({ method: "POST", path: "/api/operator/presence", query: {}, body: args?.body, access: "user" }) as Promise<OperatorPresenceAck>;
  }

  /** GET /api/ops-agent/proposals (access: admin) */
  getOpsAgentProposals(): Promise<void> {
    return this.transport({ method: "GET", path: "/api/ops-agent/proposals", query: {}, body: undefined, access: "admin" }) as Promise<void>;
  }

  /** POST /api/ops-agent/proposals/decide (access: admin) */
  postOpsAgentProposalsDecide(): Promise<void> {
    return this.transport({ method: "POST", path: "/api/ops-agent/proposals/decide", query: {}, body: undefined, access: "admin" }) as Promise<void>;
  }

  /** POST /api/push/devices (access: user) */
  postPushDevices(args: { body: { token: string; platform: "ios"; locale?: "en" | "es" | "de" | "fr" | "it" | "ja" | "zh" | "pt" } }): Promise<PushDeviceRegistered> {
    return this.transport({ method: "POST", path: "/api/push/devices", query: {}, body: args?.body, access: "user" }) as Promise<PushDeviceRegistered>;
  }

  /** DELETE /api/push/devices/{token} (access: user) */
  deletePushDevicesByToken(args: { path: { token: string } }): Promise<PushDeviceRemoved> {
    return this.transport({ method: "DELETE", path: fillPath("/api/push/devices/{token}", args?.path), query: {}, body: undefined, access: "user" }) as Promise<PushDeviceRemoved>;
  }

  /** POST /api/push/live-activities (access: user) */
  postPushLiveActivities(args: { body: { activityToken: string; robotId: string } }): Promise<LiveActivityRegistered> {
    return this.transport({ method: "POST", path: "/api/push/live-activities", query: {}, body: args?.body, access: "user" }) as Promise<LiveActivityRegistered>;
  }

  /** DELETE /api/push/live-activities/{token} (access: user) */
  deletePushLiveActivitiesByToken(args: { path: { token: string } }): Promise<LiveActivityRemoved> {
    return this.transport({ method: "DELETE", path: fillPath("/api/push/live-activities/{token}", args?.path), query: {}, body: undefined, access: "user" }) as Promise<LiveActivityRemoved>;
  }

  /** POST /api/refresh (access: public) */
  postRefresh(args: { body: { refreshToken: string } }): Promise<LoginResult> {
    return this.transport({ method: "POST", path: "/api/refresh", query: {}, body: args?.body, access: "public" }) as Promise<LoginResult>;
  }

  /** GET /api/robot/{id} (access: user) */
  getRobotById(args: { path: { id: number } }): Promise<void> {
    return this.transport({ method: "GET", path: fillPath("/api/robot/{id}", args?.path), query: {}, body: undefined, access: "user" }) as Promise<void>;
  }

  /** POST /api/robot/{id}/claim (access: user) */
  postRobotByIdClaim(args: { path: { id: number }; body?: { ttlMs?: number; force?: boolean; reason?: string } }): Promise<Reservation> {
    return this.transport({ method: "POST", path: fillPath("/api/robot/{id}/claim", args?.path), query: {}, body: args?.body, access: "user" }) as Promise<Reservation>;
  }

  /** POST /api/robot/{id}/command (access: user) */
  postRobotByIdCommand(args: { path: { id: number }; body: { command: string; params?: Record<string, unknown>; seq?: number } }): Promise<void> {
    return this.transport({ method: "POST", path: fillPath("/api/robot/{id}/command", args?.path), query: {}, body: args?.body, access: "user" }) as Promise<void>;
  }

  /** POST /api/robot/{id}/heartbeat (access: user) */
  postRobotByIdHeartbeat(args: { path: { id: number } }): Promise<Success> {
    return this.transport({ method: "POST", path: fillPath("/api/robot/{id}/heartbeat", args?.path), query: {}, body: undefined, access: "user" }) as Promise<Success>;
  }

  /** POST /api/robot/{id}/jog-arm (access: user) */
  postRobotByIdJogArm(args: { path: { id: number }; body?: { armed?: unknown; controllerId?: unknown; ttlMs?: unknown } }): Promise<void> {
    return this.transport({ method: "POST", path: fillPath("/api/robot/{id}/jog-arm", args?.path), query: {}, body: args?.body, access: "user" }) as Promise<void>;
  }

  /** POST /api/robot/{id}/release (access: user) */
  postRobotByIdRelease(args: { path: { id: number }; body?: { reason?: string } }): Promise<Reservation> {
    return this.transport({ method: "POST", path: fillPath("/api/robot/{id}/release", args?.path), query: {}, body: args?.body, access: "user" }) as Promise<Reservation>;
  }

  /** GET /api/robots/liveness (access: user) */
  getRobotsLiveness(): Promise<RobotLiveness> {
    return this.transport({ method: "GET", path: "/api/robots/liveness", query: {}, body: undefined, access: "user" }) as Promise<RobotLiveness>;
  }

  /** GET /api/ros2-bridge/settings (access: user) */
  getRos2BridgeSettings(): Promise<{ requireSros2: boolean; active: boolean; restartNeeded: boolean; canChange: boolean; environmentReady: boolean }> {
    return this.transport({ method: "GET", path: "/api/ros2-bridge/settings", query: {}, body: undefined, access: "user" }) as Promise<{ requireSros2: boolean; active: boolean; restartNeeded: boolean; canChange: boolean; environmentReady: boolean }>;
  }

  /** POST /api/ros2-bridge/settings (access: admin) */
  postRos2BridgeSettings(): Promise<void> {
    return this.transport({ method: "POST", path: "/api/ros2-bridge/settings", query: {}, body: undefined, access: "admin" }) as Promise<void>;
  }

  /** GET /api/rul/config (access: user) */
  getRulConfig(): Promise<RulConfig> {
    return this.transport({ method: "GET", path: "/api/rul/config", query: {}, body: undefined, access: "user" }) as Promise<RulConfig>;
  }

  /** GET /api/safety-limits (access: user) */
  getSafetyLimits(args?: { query?: { robotId?: string } }): Promise<void> {
    return this.transport({ method: "GET", path: "/api/safety-limits", query: queryOf(args?.query), body: undefined, access: "user" }) as Promise<void>;
  }

  /** GET /api/semantic-planner/settings (access: user) */
  getSemanticPlannerSettings(): Promise<void> {
    return this.transport({ method: "GET", path: "/api/semantic-planner/settings", query: {}, body: undefined, access: "user" }) as Promise<void>;
  }

  /** POST /api/semantic-planner/settings (access: admin) */
  postSemanticPlannerSettings(): Promise<void> {
    return this.transport({ method: "POST", path: "/api/semantic-planner/settings", query: {}, body: undefined, access: "admin" }) as Promise<void>;
  }

  /** GET /api/settings (access: user) */
  getSettings(): Promise<Settings> {
    return this.transport({ method: "GET", path: "/api/settings", query: {}, body: undefined, access: "user" }) as Promise<Settings>;
  }

  /** PUT /api/settings (access: admin) */
  putSettings(): Promise<Success> {
    return this.transport({ method: "PUT", path: "/api/settings", query: {}, body: undefined, access: "admin" }) as Promise<Success>;
  }

  /** POST /api/settings (access: admin) */
  postSettings(): Promise<Success> {
    return this.transport({ method: "POST", path: "/api/settings", query: {}, body: undefined, access: "admin" }) as Promise<Success>;
  }

  /** POST /api/stop-all (access: user) */
  postStopAll(): Promise<StopAllResult> {
    return this.transport({ method: "POST", path: "/api/stop-all", query: {}, body: undefined, access: "user" }) as Promise<StopAllResult>;
  }

  /** POST /api/stop-all/release (access: admin) */
  postStopAllRelease(): Promise<GlobalStopReleased> {
    return this.transport({ method: "POST", path: "/api/stop-all/release", query: {}, body: undefined, access: "admin" }) as Promise<GlobalStopReleased>;
  }

  /** POST /api/system/bluetooth/pair (access: admin) */
  postSystemBluetoothPair(args: { body: { mac: string } }): Promise<void> {
    return this.transport({ method: "POST", path: "/api/system/bluetooth/pair", query: {}, body: args?.body, access: "admin" }) as Promise<void>;
  }

  /** POST /api/system/bluetooth/power (access: admin) */
  postSystemBluetoothPower(args: { body: { on: boolean } }): Promise<Success> {
    return this.transport({ method: "POST", path: "/api/system/bluetooth/power", query: {}, body: args?.body, access: "admin" }) as Promise<Success>;
  }

  /** POST /api/system/bluetooth/remove (access: admin) */
  postSystemBluetoothRemove(args: { body: { mac: string } }): Promise<Success> {
    return this.transport({ method: "POST", path: "/api/system/bluetooth/remove", query: {}, body: args?.body, access: "admin" }) as Promise<Success>;
  }

  /** POST /api/system/bluetooth/scan (access: admin) */
  postSystemBluetoothScan(): Promise<BluetoothScan> {
    return this.transport({ method: "POST", path: "/api/system/bluetooth/scan", query: {}, body: undefined, access: "admin" }) as Promise<BluetoothScan>;
  }

  /** GET /api/system/bluetooth/status (access: admin) */
  getSystemBluetoothStatus(): Promise<void> {
    return this.transport({ method: "GET", path: "/api/system/bluetooth/status", query: {}, body: undefined, access: "admin" }) as Promise<void>;
  }

  /** GET /api/system/metrics (access: public) */
  getSystemMetrics(): Promise<SystemMetrics> {
    return this.transport({ method: "GET", path: "/api/system/metrics", query: {}, body: undefined, access: "public" }) as Promise<SystemMetrics>;
  }

  /** POST /api/system/reboot (access: public) */
  postSystemReboot(): Promise<Success> {
    return this.transport({ method: "POST", path: "/api/system/reboot", query: {}, body: undefined, access: "public" }) as Promise<Success>;
  }

  /** POST /api/system/shutdown (access: public) */
  postSystemShutdown(): Promise<Success> {
    return this.transport({ method: "POST", path: "/api/system/shutdown", query: {}, body: undefined, access: "public" }) as Promise<Success>;
  }

  /** GET /api/system/supervisor (access: public) */
  getSystemSupervisor(): Promise<SupervisorSnapshot> {
    return this.transport({ method: "GET", path: "/api/system/supervisor", query: {}, body: undefined, access: "public" }) as Promise<SupervisorSnapshot>;
  }

  /** GET /api/telemetry/aggregate (access: user) */
  getTelemetryAggregate(): Promise<Passthrough> {
    return this.transport({ method: "GET", path: "/api/telemetry/aggregate", query: {}, body: undefined, access: "user" }) as Promise<Passthrough>;
  }

  /** GET /api/telemetry/downsample-plan (access: admin) */
  getTelemetryDownsamplePlan(): Promise<Passthrough> {
    return this.transport({ method: "GET", path: "/api/telemetry/downsample-plan", query: {}, body: undefined, access: "admin" }) as Promise<Passthrough>;
  }

  /** PUT /api/telemetry/downsample-plan (access: admin) */
  putTelemetryDownsamplePlan(args?: { query?: { preview?: string } }): Promise<Passthrough> {
    return this.transport({ method: "PUT", path: "/api/telemetry/downsample-plan", query: queryOf(args?.query), body: undefined, access: "admin" }) as Promise<Passthrough>;
  }

  /** GET /api/telemetry/query (access: user) */
  getTelemetryQuery(): Promise<Passthrough> {
    return this.transport({ method: "GET", path: "/api/telemetry/query", query: {}, body: undefined, access: "user" }) as Promise<Passthrough>;
  }

  /** GET /api/tool-arms (access: user) */
  getToolArms(): Promise<ToolArmsReport> {
    return this.transport({ method: "GET", path: "/api/tool-arms", query: {}, body: undefined, access: "user" }) as Promise<ToolArmsReport>;
  }

  /** POST /api/tool-arms/reset (access: admin) */
  postToolArmsReset(args: { body: { robot: string; toolId: number; confirm: string } }): Promise<ToolArmResetResult> {
    return this.transport({ method: "POST", path: "/api/tool-arms/reset", query: {}, body: args?.body, access: "admin" }) as Promise<ToolArmResetResult>;
  }

  /** POST /api/totp/begin (access: user) */
  postTotpBegin(args: { body: { password: string } }): Promise<TotpEnrolment> {
    return this.transport({ method: "POST", path: "/api/totp/begin", query: {}, body: args?.body, access: "user" }) as Promise<TotpEnrolment>;
  }

  /** POST /api/totp/confirm (access: user) */
  postTotpConfirm(args: { body: { code: string } }): Promise<TotpConfirmed> {
    return this.transport({ method: "POST", path: "/api/totp/confirm", query: {}, body: args?.body, access: "user" }) as Promise<TotpConfirmed>;
  }

  /** POST /api/totp/disable (access: user) */
  postTotpDisable(args: { body: { password: string; code: string } }): Promise<Success> {
    return this.transport({ method: "POST", path: "/api/totp/disable", query: {}, body: args?.body, access: "user" }) as Promise<Success>;
  }

  /** GET /api/totp/status (access: user) */
  getTotpStatus(): Promise<TotpStatus> {
    return this.transport({ method: "GET", path: "/api/totp/status", query: {}, body: undefined, access: "user" }) as Promise<TotpStatus>;
  }

  /** POST /api/trajectory/proposals/verify (access: user) */
  postTrajectoryProposalsVerify(): Promise<void> {
    return this.transport({ method: "POST", path: "/api/trajectory/proposals/verify", query: {}, body: undefined, access: "user" }) as Promise<void>;
  }

  /** POST /api/upload-work (access: user) */
  postUploadWork(args: { body: { folderPath: string; fileName: string; content: string } }): Promise<Success> {
    return this.transport({ method: "POST", path: "/api/upload-work", query: {}, body: args?.body, access: "user" }) as Promise<Success>;
  }

  /** GET /api/users (access: admin) */
  getUsers(): Promise<UserList> {
    return this.transport({ method: "GET", path: "/api/users", query: {}, body: undefined, access: "admin" }) as Promise<UserList>;
  }

  /** POST /api/users (access: admin) */
  postUsers(args: { body: { username: string; password: string; role: string } }): Promise<Success> {
    return this.transport({ method: "POST", path: "/api/users", query: {}, body: args?.body, access: "admin" }) as Promise<Success>;
  }

  /** PUT /api/users/{username} (access: admin) */
  putUsersByUsername(args: { path: { username: string }; body?: { newUsername?: string; password?: string; role?: string } }): Promise<Success> {
    return this.transport({ method: "PUT", path: fillPath("/api/users/{username}", args?.path), query: {}, body: args?.body, access: "admin" }) as Promise<Success>;
  }

  /** DELETE /api/users/{username} (access: admin) */
  deleteUsersByUsername(args: { path: { username: string } }): Promise<Success> {
    return this.transport({ method: "DELETE", path: fillPath("/api/users/{username}", args?.path), query: {}, body: undefined, access: "admin" }) as Promise<Success>;
  }

  /** DELETE /api/users/{username}/totp (access: admin) */
  deleteUsersByUsernameTotp(args: { path: { username: string } }): Promise<Success> {
    return this.transport({ method: "DELETE", path: fillPath("/api/users/{username}/totp", args?.path), query: {}, body: undefined, access: "admin" }) as Promise<Success>;
  }

  /** GET /api/voice/chain (access: admin) */
  getVoiceChain(args?: { query?: { limit?: string; verify?: string } }): Promise<void> {
    return this.transport({ method: "GET", path: "/api/voice/chain", query: queryOf(args?.query), body: undefined, access: "admin" }) as Promise<void>;
  }

  /** POST /api/voice/confirm (access: user) */
  postVoiceConfirm(args?: { body?: { confirmationToken?: unknown } }): Promise<void> {
    return this.transport({ method: "POST", path: "/api/voice/confirm", query: {}, body: args?.body, access: "user" }) as Promise<void>;
  }

  /** POST /api/voice/turn (access: user) */
  postVoiceTurn(args?: { body?: { locale?: unknown; requestId?: unknown; subject?: unknown } }): Promise<void> {
    return this.transport({ method: "POST", path: "/api/voice/turn", query: {}, body: args?.body, access: "user" }) as Promise<void>;
  }

  /** GET /api/watch/system-status (access: user) */
  getWatchSystemStatus(): Promise<void> {
    return this.transport({ method: "GET", path: "/api/watch/system-status", query: {}, body: undefined, access: "user" }) as Promise<void>;
  }

  /** GET /health (access: public) */
  getHealth(): Promise<HealthReport> {
    return this.transport({ method: "GET", path: "/health", query: {}, body: undefined, access: "public" }) as Promise<HealthReport>;
  }

  /** GET /metrics (access: public) */
  getMetrics(): Promise<void> {
    return this.transport({ method: "GET", path: "/metrics", query: {}, body: undefined, access: "public" }) as Promise<void>;
  }

}

export const HYDRA_CLIENT_OPERATIONS: readonly string[] = [
  "getWellKnownJwksJson",
  "getAdapters",
  "getAdaptersByAdapterId",
  "getAdminClients",
  "getAdminDeviceTokens",
  "postAdminDeviceTokens",
  "deleteAdminDeviceTokensById",
  "getAdminFleetUpdate",
  "postAdminFleetUpdateApply",
  "postAdminFleetUpdatePlan",
  "postAdminFleetUpdateResume",
  "getAdminJwtKeys",
  "postAdminJwtKeysRotate",
  "getAdminLogs",
  "postAdminMaintenanceInstall",
  "postAdminMaintenancePrune",
  "postAdminMaintenanceRollback",
  "getAdminMaintenanceStatus",
  "getAdminPush",
  "postAdminRestart",
  "getAdminRobotIds",
  "putAdminSafetyLimits",
  "getAdminSelfUpdate",
  "postAdminSelfUpdateApply",
  "getAdminSelfUpdateJobsById",
  "postAdminSelfUpdateRollback",
  "getAdminServerConfig",
  "putAdminServerConfig",
  "getAdminServiceIdentity",
  "getAdminUpdates",
  "getAnomalyVerdicts",
  "getAudit",
  "getBridges",
  "postBridgesByNameCmdByVerb",
  "getBridgesByNameState",
  "postCameraDiscoverRtspPath",
  "getCameraDiscoverUsbDevices",
  "getCameraMedia",
  "getCameraMediaByCameraIdByKindByFilename",
  "deleteCameraMediaByCameraIdByKindByFilename",
  "postCameraTicket",
  "postCameraByIdPtz",
  "postCameraByIdRecordingStart",
  "postCameraByIdRecordingStop",
  "postCameraByIdSnapshot",
  "getCameraByIdStream",
  "getCamerasStatus",
  "getClaims",
  "getConnectionsClients",
  "getConnectionsEvents",
  "getConnectorHubGateAudit",
  "postConnectorHubGateEvaluate",
  "getConnectorHubGateSettings",
  "postConnectorHubGateSettings",
  "getDevServerStatus",
  "getDeveloperNodeStatus",
  "postDeviceLogin",
  "getDroidEstopSettings",
  "postDroidEstopSettings",
  "getEcosystemHealth",
  "getEcosystemNodeHealth",
  "postEcosystemServiceByUnitByAction",
  "getEcosystemStatus",
  "getFaults",
  "postHardwareCanotaFlash",
  "getHardwareCanotaVersion",
  "postHardwareFramErase",
  "postHardwareFramSelftest",
  "getHilBridgeSettings",
  "postHilBridgeSettings",
  "getHydraInfo",
  "postInfoTicket",
  "postIngestDevServerStatus",
  "postIngestDeveloperNodeStatus",
  "postIngestScenarioOutcome",
  "getIngestScenarioOutcomes",
  "postIntegrationsTestConnection",
  "postLogin",
  "postLogout",
  "getModels",
  "postModelsSubmit",
  "getModelsByCategoryBySlugDownload",
  "postOperatorConfirmations",
  "getOperatorPresence",
  "postOperatorPresence",
  "getOpsAgentProposals",
  "postOpsAgentProposalsDecide",
  "postPushDevices",
  "deletePushDevicesByToken",
  "postPushLiveActivities",
  "deletePushLiveActivitiesByToken",
  "postRefresh",
  "getRobotById",
  "postRobotByIdClaim",
  "postRobotByIdCommand",
  "postRobotByIdHeartbeat",
  "postRobotByIdJogArm",
  "postRobotByIdRelease",
  "getRobotsLiveness",
  "getRos2BridgeSettings",
  "postRos2BridgeSettings",
  "getRulConfig",
  "getSafetyLimits",
  "getSemanticPlannerSettings",
  "postSemanticPlannerSettings",
  "getSettings",
  "putSettings",
  "postSettings",
  "postStopAll",
  "postStopAllRelease",
  "postSystemBluetoothPair",
  "postSystemBluetoothPower",
  "postSystemBluetoothRemove",
  "postSystemBluetoothScan",
  "getSystemBluetoothStatus",
  "getSystemMetrics",
  "postSystemReboot",
  "postSystemShutdown",
  "getSystemSupervisor",
  "getTelemetryAggregate",
  "getTelemetryDownsamplePlan",
  "putTelemetryDownsamplePlan",
  "getTelemetryQuery",
  "getToolArms",
  "postToolArmsReset",
  "postTotpBegin",
  "postTotpConfirm",
  "postTotpDisable",
  "getTotpStatus",
  "postTrajectoryProposalsVerify",
  "postUploadWork",
  "getUsers",
  "postUsers",
  "putUsersByUsername",
  "deleteUsersByUsername",
  "deleteUsersByUsernameTotp",
  "getVoiceChain",
  "postVoiceConfirm",
  "postVoiceTurn",
  "getWatchSystemStatus",
  "getHealth",
  "getMetrics",
];

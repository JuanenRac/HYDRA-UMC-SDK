// =============================================================================
// HYDRA-UMC-SDK - Client of the claim, jog arming and safety-limit routes
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

// Typed access to the routes of HYDRA-UMC-SERVER that decide who controls a
// robot and how far a jog may go: claim, release, jog-arm, GET /api/claims,
// GET /api/safety-limits and PUT /api/admin/safety-limits, plus the optional
// controllerId of command. The second block of the contract is here too: GET
// /api/robot/:id with its revision, If-Match on command/claim/release (and the
// 412 it can answer), the atomic table command, GET /api/audit and the claims
// message of the WebSocket. Request builders and response parsers never touch
// the network; HydraServerClient carries them over an injectable transport
// (fetch by default). Everything is additive: a request without a controller
// id is the v1 request, unknown response fields are ignored and an unknown
// error code stays a plain ApiError. The server decides; nothing here checks
// a limit, a claim or an arming on its own.

export const CONTROLLER_ID_HEADER = "X-Controller-Id";
const CONTROLLER_ID = /^[A-Za-z0-9._:-]{1,64}$/;

export const CODE_OTHER_ACCOUNT = "other-account";
export const CODE_OTHER_CONTROLLER = "other-controller";
export const CODE_CONTROLLER_ID_REQUIRED = "controller-id-required";
export const CODE_INVALID_CONTROLLER_ID = "invalid-controller-id";
export const CODE_JOG_NOT_ARMED = "jog-not-armed";
export const CODE_REVISION_MISMATCH = "revision-mismatch";
export const CODE_TABLE_INVALID = "table-invalid";
export const CODE_TABLE_OUT_OF_LIMIT = "table-out-of-limit";
export const CODE_TABLE_MISSING = "table-missing";
export const TABLE_MODES = ["absolute", "relative"] as const;
export type TableMode = (typeof TABLE_MODES)[number];
export const KNOWN_ERROR_CODES = [
  CODE_OTHER_ACCOUNT,
  CODE_OTHER_CONTROLLER,
  CODE_CONTROLLER_ID_REQUIRED,
  CODE_INVALID_CONTROLLER_ID,
  CODE_JOG_NOT_ARMED,
  CODE_REVISION_MISMATCH,
  CODE_TABLE_INVALID,
  CODE_TABLE_OUT_OF_LIMIT,
  CODE_TABLE_MISSING,
] as const;
export type KnownErrorCode = (typeof KNOWN_ERROR_CODES)[number];

// ---- Values ---------------------------------------------------------------

export interface Reservation {
  ownerId: unknown;
  ownerUsername: string;
  claimedAt: number;
  expiresAt: number;
  controllerId: string | null;
}

export interface ClaimResult {
  reservation: Reservation | null;
  history: Array<Record<string, unknown>>;
  /** The new revision of the robot, when the server sent one. */
  revision: string | null;
}

export interface JogArmResult {
  armed: boolean;
  expiresAt: number | null;
  ttlMs: number | null;
}

export interface ClaimEntry {
  robotId: number;
  robotName: string | null;
  cellId: unknown;
  ownerId: unknown;
  ownerUsername: string;
  controllerId: string | null;
  claimedAt: number;
  expiresAt: number;
  jogArmedUntil: number | null;
}

/** GET /api/robot/:id: the robot, its revision (the ETag) and its cell. */
export interface RobotView {
  robot: Record<string, unknown>;
  revision: string;
  cellId: unknown;
}

export interface TableApplied {
  robotId: number;
  x: number;
  y: number;
  rz: number | null;
}

export interface CommandResult {
  success: boolean;
  affectedCount: number | null;
  revision: string | null;
  applied: TableApplied | null;
  warnings: Array<Record<string, unknown>>;
}

export interface AuditEntry {
  seq: number;
  ts: string;
  type: string;
  outcome: string;
  prev: string;
  hash: string;
  username: string | null;
  controllerId: string | null;
  ip: string | null;
  robotId: number | null;
  detail: Record<string, unknown>;
}

export interface AuditView {
  enabled: boolean;
  lockedOff: boolean;
  entries: AuditEntry[];
  verification: Record<string, unknown> | null;
}

export interface RobotSafety {
  id: number;
  model: string | null;
  jog: Record<string, unknown>;
  temperature: Record<string, unknown>;
  jogArmedUntil: number | null;
}

export interface SafetyLimitsView {
  limits: Record<string, unknown>;
  defaults: Record<string, unknown>;
  hardLimits: Record<string, unknown>;
  robot: RobotSafety | null;
}

export interface ServerRequest {
  method: "GET" | "POST" | "PUT";
  path: string;
  body: Record<string, unknown> | null;
  /** Extra headers of the request (If-Match); empty when there are none. */
  headers: Record<string, string>;
}

// ---- Errors ---------------------------------------------------------------

/** A request the client refuses to build; nothing was sent. */
export class ServerRequestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ServerRequestError";
  }
}

/** An error answer: HTTP status, readable text, the stable code when sent, and the whole body. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
    readonly code: string | null = null,
    readonly body: unknown = null,
  ) {
    super(`${status} ${code ? `${code}: ` : ""}${message}`);
    this.name = "ApiError";
  }
}

/** Claimed by someone else: code is other-account or other-controller (null on a server that predates the codes). */
export class ClaimConflictError extends ApiError {
  constructor(status: number, message: string, code: string | null, body: unknown, readonly reservation: Reservation | null) {
    super(status, message, code, body);
    this.name = "ClaimConflictError";
  }
}

/** The claim has a controller (409) or the server demands one to claim (400): send a controllerId. */
export class ControllerIdRequiredError extends ClaimConflictError {
  constructor(status: number, message: string, code: string | null, body: unknown, reservation: Reservation | null) {
    super(status, message, code, body, reservation);
    this.name = "ControllerIdRequiredError";
  }
}

export class InvalidControllerIdError extends ApiError {
  constructor(status: number, message: string, code: string | null, body: unknown) {
    super(status, message, code, body);
    this.name = "InvalidControllerIdError";
  }
}

/** A jog was refused because the robot is not armed (403): arm it first. */
export class JogNotArmedError extends ApiError {
  constructor(status: number, message: string, code: string | null, body: unknown) {
    super(status, message, code, body);
    this.name = "JogNotArmedError";
  }
}

/** If-Match failed (412): the robot changed since it was read; `revision` is the current one. */
export class RevisionMismatchError extends ApiError {
  constructor(status: number, message: string, code: string | null, body: unknown, readonly revision: string | null) {
    super(status, message, code, body);
    this.name = "RevisionMismatchError";
  }
}

/** A table move was refused as a whole and nothing changed (400): table-invalid, table-out-of-limit or table-missing. */
export class TableMoveError extends ApiError {
  constructor(status: number, message: string, code: string | null, body: unknown) {
    super(status, message, code, body);
    this.name = "TableMoveError";
  }
}

// ---- Request builders -----------------------------------------------------

export function isValidControllerId(value: unknown): value is string {
  return typeof value === "string" && CONTROLLER_ID.test(value);
}

function robotId(value: unknown): number {
  if (typeof value !== "number" || !Number.isInteger(value)) throw new ServerRequestError("robotId must be an integer");
  return value;
}

function controller(value: string | undefined): string | undefined {
  if (value === undefined) return undefined;
  if (!isValidControllerId(value)) throw new ServerRequestError("controllerId must be 1 to 64 characters: letters, digits, . _ : -");
  return value;
}

function finite(value: unknown, name: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) throw new ServerRequestError(`${name} must be a number`);
  return value;
}

/** The If-Match header for a revision (quoted or not) or for "*"; none when there is no revision. */
function ifMatchHeaders(value: string | undefined): Record<string, string> {
  if (value === undefined) return {};
  if (typeof value !== "string" || value.trim() === "" || /[\r\n]/.test(value)) throw new ServerRequestError("ifMatch must be a revision string");
  const text = value.trim();
  return { "If-Match": text === "*" || text.startsWith('"') || text.startsWith("W/") ? text : `"${text}"` };
}

export interface ClaimOptions {
  ttlMs?: number;
  force?: boolean;
  reason?: string;
  controllerId?: string;
  ifMatch?: string;
}

export function claimRequest(id: number, options: ClaimOptions = {}): ServerRequest {
  const body: Record<string, unknown> = {};
  if (options.ttlMs !== undefined) body.ttlMs = finite(options.ttlMs, "ttlMs");
  if (options.force !== undefined) body.force = Boolean(options.force);
  if (options.reason !== undefined) body.reason = String(options.reason);
  const controllerId = controller(options.controllerId);
  if (controllerId !== undefined) body.controllerId = controllerId;
  return { method: "POST", path: `/api/robot/${robotId(id)}/claim`, body, headers: ifMatchHeaders(options.ifMatch) };
}

export interface ReleaseOptions {
  reason?: string;
  controllerId?: string;
  ifMatch?: string;
}

export function releaseRequest(id: number, options: ReleaseOptions = {}): ServerRequest {
  const body: Record<string, unknown> = {};
  if (options.reason !== undefined) body.reason = String(options.reason);
  const controllerId = controller(options.controllerId);
  if (controllerId !== undefined) body.controllerId = controllerId;
  return { method: "POST", path: `/api/robot/${robotId(id)}/release`, body, headers: ifMatchHeaders(options.ifMatch) };
}

export interface JogArmOptions {
  ttlMs?: number;
  controllerId?: string;
}

export function jogArmRequest(id: number, armed: boolean, options: JogArmOptions = {}): ServerRequest {
  if (typeof armed !== "boolean") throw new ServerRequestError("armed must be true or false");
  const body: Record<string, unknown> = { armed };
  if (options.ttlMs !== undefined) body.ttlMs = finite(options.ttlMs, "ttlMs");
  const controllerId = controller(options.controllerId);
  if (controllerId !== undefined) body.controllerId = controllerId;
  return { method: "POST", path: `/api/robot/${robotId(id)}/jog-arm`, body, headers: {} };
}

export function listClaimsRequest(): ServerRequest {
  return { method: "GET", path: "/api/claims", body: null, headers: {} };
}

export function safetyLimitsRequest(id?: number): ServerRequest {
  return { method: "GET", path: id === undefined ? "/api/safety-limits" : `/api/safety-limits?robotId=${robotId(id)}`, body: null, headers: {} };
}

export function updateSafetyLimitsRequest(patch: Record<string, unknown>): ServerRequest {
  if (typeof patch !== "object" || patch === null || Array.isArray(patch)) throw new ServerRequestError("patch must be an object");
  return { method: "PUT", path: "/api/admin/safety-limits", body: { ...patch }, headers: {} };
}

export interface CommandOptions {
  params?: Record<string, unknown>;
  controllerId?: string;
  ifMatch?: string;
}

export function commandRequest(id: number, command: string, options: CommandOptions = {}): ServerRequest {
  if (typeof command !== "string" || command === "") throw new ServerRequestError("command must be a non-empty string");
  const body: Record<string, unknown> = { command };
  if (options.params !== undefined) body.params = { ...options.params };
  const controllerId = controller(options.controllerId);
  if (controllerId !== undefined) body.controllerId = controllerId;
  return { method: "POST", path: `/api/robot/${robotId(id)}/command`, body, headers: ifMatchHeaders(options.ifMatch) };
}

export interface TableOptions {
  rz?: number;
  mode?: TableMode;
  controllerId?: string;
  ifMatch?: string;
}

/** One move of the XY table in one request; the server checks it as a whole and applies all of it or none. */
export function tableCommandRequest(id: number, x: number, y: number, options: TableOptions = {}): ServerRequest {
  const mode = options.mode ?? "absolute";
  if (!(TABLE_MODES as readonly string[]).includes(mode)) throw new ServerRequestError('mode must be "absolute" or "relative"');
  const params: Record<string, unknown> = { x: finite(x, "x"), y: finite(y, "y"), mode };
  if (options.rz !== undefined) params.rz = finite(options.rz, "rz");
  return commandRequest(id, "table", { params, controllerId: options.controllerId, ifMatch: options.ifMatch });
}

export function getRobotRequest(id: number): ServerRequest {
  return { method: "GET", path: `/api/robot/${robotId(id)}`, body: null, headers: {} };
}

export interface AuditQuery {
  limit?: number;
  afterSeq?: number;
  type?: string;
  robotId?: number;
  verify?: boolean;
}

/** GET /api/audit (administrators): the newest entries of the audit record, oldest first. */
export function auditRequest(query: AuditQuery = {}): ServerRequest {
  const parts: string[] = [];
  if (query.limit !== undefined) parts.push(`limit=${Math.trunc(finite(query.limit, "limit"))}`);
  if (query.afterSeq !== undefined) parts.push(`afterSeq=${Math.trunc(finite(query.afterSeq, "afterSeq"))}`);
  if (query.type !== undefined) {
    if (!/^[A-Za-z0-9._-]{1,40}$/.test(query.type)) throw new ServerRequestError("type must be a short plain name");
    parts.push(`type=${query.type}`);
  }
  if (query.robotId !== undefined) parts.push(`robotId=${robotId(query.robotId)}`);
  if (query.verify) parts.push("verify=1");
  return { method: "GET", path: "/api/audit" + (parts.length ? `?${parts.join("&")}` : ""), body: null, headers: {} };
}

// ---- Response parsers -----------------------------------------------------

function asObject(value: unknown, what: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) throw new ServerRequestError(`${what} must be a JSON object`);
  return value as Record<string, unknown>;
}

function orNull<T>(value: T | undefined | null): T | null {
  return value === undefined ? null : value;
}

export function parseReservation(value: unknown): Reservation | null {
  if (value === null || value === undefined) return null;
  const data = asObject(value, "reservation");
  return {
    ownerId: data.ownerId,
    ownerUsername: String(data.ownerUsername ?? ""),
    claimedAt: Number(data.claimedAt ?? 0),
    expiresAt: Number(data.expiresAt ?? 0),
    controllerId: typeof data.controllerId === "string" ? data.controllerId : null,
  };
}

/** The answer of claim and of release (the reservation is null after a release). */
export function parseClaimResult(body: unknown): ClaimResult {
  const data = asObject(body, "claim answer");
  const history = Array.isArray(data.reservationHistory) ? data.reservationHistory : [];
  return {
    reservation: parseReservation(data.reservation),
    history: history.filter((entry): entry is Record<string, unknown> => typeof entry === "object" && entry !== null && !Array.isArray(entry)),
    revision: typeof data.revision === "string" ? data.revision : null,
  };
}

export function parseJogArmResult(body: unknown): JogArmResult {
  const data = asObject(body, "jog-arm answer");
  if (typeof data.armed !== "boolean") throw new ServerRequestError("jog-arm answer has no boolean 'armed'");
  return {
    armed: data.armed,
    expiresAt: typeof data.expiresAt === "number" ? data.expiresAt : null,
    ttlMs: typeof data.ttlMs === "number" ? data.ttlMs : null,
  };
}

export function parseClaims(body: unknown): ClaimEntry[] {
  const data = asObject(body, "claims answer");
  if (!Array.isArray(data.claims)) throw new ServerRequestError("claims answer has no 'claims' list");
  return data.claims.map((raw) => {
    const item = asObject(raw, "claim");
    return {
      robotId: Number(item.robotId),
      robotName: typeof item.robotName === "string" ? item.robotName : null,
      cellId: item.cellId,
      ownerId: item.ownerId,
      ownerUsername: String(item.ownerUsername ?? ""),
      controllerId: typeof item.controllerId === "string" ? item.controllerId : null,
      claimedAt: Number(item.claimedAt ?? 0),
      expiresAt: Number(item.expiresAt ?? 0),
      jogArmedUntil: typeof item.jogArmedUntil === "number" ? item.jogArmedUntil : null,
    };
  });
}

/** The `claims` message of the WebSocket (clients that opened /ws with ?remoteApiVersion=2): the list of GET /api/claims. Null for any other message. */
export function parseClaimsEvent(message: unknown): ClaimEntry[] | null {
  if (typeof message !== "object" || message === null || Array.isArray(message) || (message as Record<string, unknown>).type !== "claims") return null;
  return parseClaims(message);
}

export function parseRobot(body: unknown): RobotView {
  const data = asObject(body, "robot answer");
  if (typeof data.revision !== "string" || data.revision === "") throw new ServerRequestError("robot answer has no 'revision'");
  return { robot: asObject(data.robot, "robot"), revision: data.revision, cellId: data.cellId };
}

/** The answer of command: `revision` is the robot's new one, `applied` is set after a table move. */
export function parseCommandResult(body: unknown): CommandResult {
  const data = asObject(body, "command answer");
  let applied: TableApplied | null = null;
  if (typeof data.applied === "object" && data.applied !== null && !Array.isArray(data.applied)) {
    const item = data.applied as Record<string, unknown>;
    applied = { robotId: Number(item.robotId), x: Number(item.x), y: Number(item.y), rz: typeof item.rz === "number" ? item.rz : null };
  }
  const warnings = Array.isArray(data.warnings) ? data.warnings : [];
  return {
    success: data.success === true,
    affectedCount: typeof data.affectedCount === "number" ? data.affectedCount : null,
    revision: typeof data.revision === "string" ? data.revision : null,
    applied,
    warnings: warnings.filter((w): w is Record<string, unknown> => typeof w === "object" && w !== null && !Array.isArray(w)),
  };
}

export function parseAudit(body: unknown): AuditView {
  const data = asObject(body, "audit answer");
  const entries = (Array.isArray(data.entries) ? data.entries : []).map((raw) => {
    const item = asObject(raw, "audit entry");
    return {
      seq: Number(item.seq),
      ts: String(item.ts ?? ""),
      type: String(item.type ?? ""),
      outcome: String(item.outcome ?? ""),
      prev: String(item.prev ?? ""),
      hash: String(item.hash ?? ""),
      username: typeof item.username === "string" ? item.username : null,
      controllerId: typeof item.controllerId === "string" ? item.controllerId : null,
      ip: typeof item.ip === "string" ? item.ip : null,
      robotId: typeof item.robotId === "number" ? item.robotId : null,
      detail: typeof item.detail === "object" && item.detail !== null && !Array.isArray(item.detail) ? (item.detail as Record<string, unknown>) : {},
    };
  });
  const verification = typeof data.verification === "object" && data.verification !== null && !Array.isArray(data.verification) ? (data.verification as Record<string, unknown>) : null;
  return { enabled: data.enabled === true, lockedOff: data.lockedOff === true, entries, verification };
}

/** The answer of GET and PUT of the safety limits; the sections stay as the server sent them. */
export function parseSafetyLimits(body: unknown): SafetyLimitsView {
  const data = asObject(body, "safety-limits answer");
  let robot: RobotSafety | null = null;
  if (data.robot !== undefined && data.robot !== null) {
    const item = asObject(data.robot, "robot");
    robot = {
      id: Number(item.id),
      model: typeof item.model === "string" ? item.model : null,
      jog: asObject(item.jog ?? {}, "robot.jog"),
      temperature: asObject(item.temperature ?? {}, "robot.temperature"),
      jogArmedUntil: typeof item.jogArmedUntil === "number" ? item.jogArmedUntil : null,
    };
  }
  return {
    limits: asObject(data.limits ?? {}, "limits"),
    defaults: asObject(data.defaults ?? {}, "defaults"),
    hardLimits: asObject(data.hardLimits ?? {}, "hardLimits"),
    robot,
  };
}

/** Turns an error answer into the most specific typed error. body is the decoded JSON, or null when it was not JSON. */
export function parseApiError(status: number, body: unknown): ApiError {
  const data = typeof body === "object" && body !== null && !Array.isArray(body) ? (body as Record<string, unknown>) : {};
  const message = typeof data.error === "string" ? data.error : `HTTP ${status}`;
  const code = typeof data.code === "string" ? data.code : null;
  const reservation = typeof data.reservation === "object" && data.reservation !== null ? parseReservation(data.reservation) : null;
  if (code === CODE_CONTROLLER_ID_REQUIRED) return new ControllerIdRequiredError(status, message, code, body, reservation);
  if (code === CODE_OTHER_ACCOUNT || code === CODE_OTHER_CONTROLLER) return new ClaimConflictError(status, message, code, body, reservation);
  if (code === CODE_INVALID_CONTROLLER_ID) return new InvalidControllerIdError(status, message, code, body);
  if (code === CODE_JOG_NOT_ARMED) return new JogNotArmedError(status, message, code, body);
  if (code === CODE_REVISION_MISMATCH || status === 412) {
    return new RevisionMismatchError(status, message, code, body, typeof data.revision === "string" ? data.revision : null);
  }
  if (code === CODE_TABLE_INVALID || code === CODE_TABLE_OUT_OF_LIMIT || code === CODE_TABLE_MISSING) return new TableMoveError(status, message, code, body);
  if (status === 409 && reservation !== null) return new ClaimConflictError(status, message, code, body, reservation);
  return new ApiError(status, message, code, body);
}

// ---- Client ---------------------------------------------------------------

/** Sends one request and returns the status and the raw text of the answer. Never throws for an HTTP error status. */
export type Transport = (method: string, url: string, headers: Record<string, string>, body: string | null) => Promise<{ status: number; text: string }>;

export function fetchTransport(): Transport {
  return async (method, url, headers, body) => {
    const send = (globalThis as unknown as { fetch: (url: string, init: object) => Promise<{ status: number; text(): Promise<string> }> }).fetch;
    const response = await send(url, { method, headers, body });
    return { status: response.status, text: await response.text() };
  };
}

export interface ServerClientOptions {
  token?: string;
  /** The identity this client picked for its session; sent with every request that accepts one. */
  controllerId?: string;
  transport?: Transport;
}

export class HydraServerClient {
  private readonly baseUrl: string;
  private readonly token: string | undefined;
  private readonly defaultController: string | undefined;
  private readonly transport: Transport;

  constructor(baseUrl: string, options: ServerClientOptions = {}) {
    this.baseUrl = baseUrl.replace(/\/+$/, "");
    this.token = options.token;
    this.defaultController = controller(options.controllerId);
    this.transport = options.transport ?? fetchTransport();
  }

  private async send(request: ServerRequest): Promise<unknown> {
    const headers: Record<string, string> = { Accept: "application/json", ...request.headers };
    if (this.token) headers.Authorization = `Bearer ${this.token}`;
    let body: string | null = null;
    if (request.body !== null) {
      headers["Content-Type"] = "application/json";
      body = JSON.stringify(request.body);
    }
    const answer = await this.transport(request.method, this.baseUrl + request.path, headers, body);
    let decoded: unknown = null;
    try {
      decoded = answer.text ? JSON.parse(answer.text) : null;
    } catch {
      decoded = null;
    }
    if (answer.status >= 400) throw parseApiError(answer.status, decoded);
    return decoded;
  }

  private controllerFor(own: string | undefined): string | undefined {
    return own ?? this.defaultController;
  }

  async claim(id: number, options: ClaimOptions = {}): Promise<ClaimResult> {
    return parseClaimResult(await this.send(claimRequest(id, { ...options, controllerId: this.controllerFor(options.controllerId) })));
  }

  async release(id: number, options: ReleaseOptions = {}): Promise<ClaimResult> {
    return parseClaimResult(await this.send(releaseRequest(id, { ...options, controllerId: this.controllerFor(options.controllerId) })));
  }

  async jogArm(id: number, armed: boolean, options: JogArmOptions = {}): Promise<JogArmResult> {
    return parseJogArmResult(await this.send(jogArmRequest(id, armed, { ...options, controllerId: this.controllerFor(options.controllerId) })));
  }

  async listClaims(): Promise<ClaimEntry[]> {
    return parseClaims(await this.send(listClaimsRequest()));
  }

  async safetyLimits(id?: number): Promise<SafetyLimitsView> {
    return parseSafetyLimits(await this.send(safetyLimitsRequest(id)));
  }

  async updateSafetyLimits(patch: Record<string, unknown>): Promise<SafetyLimitsView> {
    return parseSafetyLimits(await this.send(updateSafetyLimitsRequest(patch)));
  }

  /** Sends a robot command and returns the decoded answer unchanged. */
  async command(id: number, command: string, options: CommandOptions = {}): Promise<unknown> {
    return this.send(commandRequest(id, command, { ...options, controllerId: this.controllerFor(options.controllerId) }));
  }

  /** Like command, but parsed: the new revision of the robot, the warnings, the applied table position. */
  async commandResult(id: number, command: string, options: CommandOptions = {}): Promise<CommandResult> {
    return parseCommandResult(await this.command(id, command, options));
  }

  async moveTable(id: number, x: number, y: number, options: TableOptions = {}): Promise<CommandResult> {
    return parseCommandResult(await this.send(tableCommandRequest(id, x, y, { ...options, controllerId: this.controllerFor(options.controllerId) })));
  }

  /** One robot with its revision, to send back as ifMatch. */
  async robot(id: number): Promise<RobotView> {
    return parseRobot(await this.send(getRobotRequest(id)));
  }

  async audit(query: AuditQuery = {}): Promise<AuditView> {
    return parseAudit(await this.send(auditRequest(query)));
  }
}

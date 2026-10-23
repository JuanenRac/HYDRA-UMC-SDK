// =============================================================================
// HYDRA-UMC-SDK - Rust client of the claim, jog arming and safety-limit routes
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

//! Typed access to the routes of HYDRA-UMC-SERVER that decide who controls a
//! robot and how far a jog may go: `claim`, `release`, `jog-arm`,
//! `GET /api/claims`, `GET /api/safety-limits` and
//! `PUT /api/admin/safety-limits`, plus the optional `controllerId` of
//! `command`.
//!
//! This module builds requests and reads answers; it opens no connection, so
//! any HTTP stack (reqwest, ureq, hyper, ...) can carry them. Everything is
//! additive: a request without a controller id is the v1 request, unknown
//! response fields are ignored and an unknown error code stays a plain
//! [`ApiError::Other`]. The server decides; nothing here checks a limit, a
//! claim or an arming on its own.

use serde::{Deserialize, Serialize};
use serde_json::{Map, Value, json};
use std::fmt;

/// The header that names the controller of a request.
pub const CONTROLLER_ID_HEADER: &str = "X-Controller-Id";

pub const CODE_OTHER_ACCOUNT: &str = "other-account";
pub const CODE_OTHER_CONTROLLER: &str = "other-controller";
pub const CODE_CONTROLLER_ID_REQUIRED: &str = "controller-id-required";
pub const CODE_INVALID_CONTROLLER_ID: &str = "invalid-controller-id";
pub const CODE_JOG_NOT_ARMED: &str = "jog-not-armed";

/// 1 to 64 characters of letters, digits and `. _ : -`.
pub fn is_valid_controller_id(value: &str) -> bool {
    (1..=64).contains(&value.len())
        && value
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || matches!(b, b'.' | b'_' | b':' | b'-'))
}

/// A request the client refuses to build; nothing was sent.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ServerRequestError(pub String);

impl fmt::Display for ServerRequestError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

impl std::error::Error for ServerRequestError {}

/// A claim on a robot.
#[derive(Debug, Clone, PartialEq, Deserialize, Serialize)]
pub struct Reservation {
    #[serde(rename = "ownerId", default)]
    pub owner_id: Value,
    #[serde(rename = "ownerUsername", default)]
    pub owner_username: String,
    #[serde(rename = "claimedAt", default)]
    pub claimed_at: f64,
    #[serde(rename = "expiresAt", default)]
    pub expires_at: f64,
    #[serde(rename = "controllerId", default)]
    pub controller_id: Option<String>,
}

/// The answer of `claim` and `release` (no reservation after a release).
#[derive(Debug, Clone, PartialEq, Deserialize)]
pub struct ClaimResult {
    #[serde(default)]
    pub reservation: Option<Reservation>,
    #[serde(rename = "reservationHistory", default)]
    pub history: Vec<Value>,
}

/// The answer of `jog-arm`.
#[derive(Debug, Clone, PartialEq, Deserialize)]
pub struct JogArmResult {
    pub armed: bool,
    #[serde(rename = "expiresAt", default)]
    pub expires_at: Option<f64>,
    #[serde(rename = "ttlMs", default)]
    pub ttl_ms: Option<f64>,
}

/// One line of `GET /api/claims`. `cell_id` is the cell of the settings tree,
/// not a client; `controller_id` is `None` for a claim made without one.
#[derive(Debug, Clone, PartialEq, Deserialize)]
pub struct ClaimEntry {
    #[serde(rename = "robotId")]
    pub robot_id: i64,
    #[serde(rename = "robotName", default)]
    pub robot_name: Option<String>,
    #[serde(rename = "cellId", default)]
    pub cell_id: Value,
    #[serde(rename = "ownerId", default)]
    pub owner_id: Value,
    #[serde(rename = "ownerUsername", default)]
    pub owner_username: String,
    #[serde(rename = "controllerId", default)]
    pub controller_id: Option<String>,
    #[serde(rename = "claimedAt", default)]
    pub claimed_at: f64,
    #[serde(rename = "expiresAt", default)]
    pub expires_at: f64,
}

/// The part of the safety limits that applies to one robot.
#[derive(Debug, Clone, PartialEq, Deserialize)]
pub struct RobotSafety {
    pub id: i64,
    #[serde(default)]
    pub model: Option<String>,
    #[serde(default)]
    pub jog: Value,
    #[serde(default)]
    pub temperature: Value,
    #[serde(rename = "jogArmedUntil", default)]
    pub jog_armed_until: Option<f64>,
}

/// The answer of `GET` and `PUT` of the safety limits; the sections stay as
/// the server sent them because the server owns their shape.
#[derive(Debug, Clone, PartialEq, Deserialize)]
pub struct SafetyLimitsView {
    #[serde(default)]
    pub limits: Value,
    #[serde(default)]
    pub defaults: Value,
    #[serde(rename = "hardLimits", default)]
    pub hard_limits: Value,
    #[serde(default)]
    pub robot: Option<RobotSafety>,
}

/// A request ready to send. `body` is `None` for a request without one.
#[derive(Debug, Clone, PartialEq)]
pub struct ServerRequest {
    pub method: &'static str,
    pub path: String,
    pub body: Option<Value>,
}

fn controller(value: Option<&str>) -> Result<Option<&str>, ServerRequestError> {
    match value {
        Some(id) if !is_valid_controller_id(id) => Err(ServerRequestError(
            "controllerId must be 1 to 64 characters: letters, digits, . _ : -".into(),
        )),
        other => Ok(other),
    }
}

/// A finite number as JSON: a whole number is written without a fraction (`60000`, not `60000.0`).
fn finite(value: f64, name: &str) -> Result<Value, ServerRequestError> {
    if value.is_finite() {
        if value.fract() == 0.0 && value.abs() < 1e15 {
            Ok(json!(value as i64))
        } else {
            Ok(json!(value))
        }
    } else {
        Err(ServerRequestError(format!("{name} must be a number")))
    }
}

/// The optional fields of `claim`.
#[derive(Debug, Clone, Default)]
pub struct ClaimOptions<'a> {
    pub ttl_ms: Option<f64>,
    pub force: Option<bool>,
    pub reason: Option<&'a str>,
    pub controller_id: Option<&'a str>,
}

/// Builds `POST /api/robot/{id}/claim`.
pub fn claim_request(
    robot_id: i64,
    options: &ClaimOptions,
) -> Result<ServerRequest, ServerRequestError> {
    let mut body = Map::new();
    if let Some(ttl) = options.ttl_ms {
        body.insert("ttlMs".into(), finite(ttl, "ttlMs")?);
    }
    if let Some(force) = options.force {
        body.insert("force".into(), json!(force));
    }
    if let Some(reason) = options.reason {
        body.insert("reason".into(), json!(reason));
    }
    if let Some(id) = controller(options.controller_id)? {
        body.insert("controllerId".into(), json!(id));
    }
    Ok(ServerRequest {
        method: "POST",
        path: format!("/api/robot/{robot_id}/claim"),
        body: Some(Value::Object(body)),
    })
}

/// Builds `POST /api/robot/{id}/release`.
pub fn release_request(
    robot_id: i64,
    reason: Option<&str>,
    controller_id: Option<&str>,
) -> Result<ServerRequest, ServerRequestError> {
    let mut body = Map::new();
    if let Some(reason) = reason {
        body.insert("reason".into(), json!(reason));
    }
    if let Some(id) = controller(controller_id)? {
        body.insert("controllerId".into(), json!(id));
    }
    Ok(ServerRequest {
        method: "POST",
        path: format!("/api/robot/{robot_id}/release"),
        body: Some(Value::Object(body)),
    })
}

/// Builds `POST /api/robot/{id}/jog-arm`.
pub fn jog_arm_request(
    robot_id: i64,
    armed: bool,
    ttl_ms: Option<f64>,
    controller_id: Option<&str>,
) -> Result<ServerRequest, ServerRequestError> {
    let mut body = Map::new();
    body.insert("armed".into(), json!(armed));
    if let Some(ttl) = ttl_ms {
        body.insert("ttlMs".into(), finite(ttl, "ttlMs")?);
    }
    if let Some(id) = controller(controller_id)? {
        body.insert("controllerId".into(), json!(id));
    }
    Ok(ServerRequest {
        method: "POST",
        path: format!("/api/robot/{robot_id}/jog-arm"),
        body: Some(Value::Object(body)),
    })
}

/// Builds `GET /api/claims`.
pub fn list_claims_request() -> ServerRequest {
    ServerRequest {
        method: "GET",
        path: "/api/claims".into(),
        body: None,
    }
}

/// Builds `GET /api/safety-limits`, with `?robotId=` when a robot is given.
pub fn safety_limits_request(robot_id: Option<i64>) -> ServerRequest {
    let path = match robot_id {
        Some(id) => format!("/api/safety-limits?robotId={id}"),
        None => "/api/safety-limits".into(),
    };
    ServerRequest {
        method: "GET",
        path,
        body: None,
    }
}

/// Builds `PUT /api/admin/safety-limits`; `patch` must be a JSON object.
pub fn update_safety_limits_request(patch: &Value) -> Result<ServerRequest, ServerRequestError> {
    if !patch.is_object() {
        return Err(ServerRequestError("patch must be an object".into()));
    }
    Ok(ServerRequest {
        method: "PUT",
        path: "/api/admin/safety-limits".into(),
        body: Some(patch.clone()),
    })
}

/// Builds `POST /api/robot/{id}/command` with the optional controller id.
pub fn command_request(
    robot_id: i64,
    command: &str,
    params: Option<&Value>,
    controller_id: Option<&str>,
) -> Result<ServerRequest, ServerRequestError> {
    if command.is_empty() {
        return Err(ServerRequestError(
            "command must be a non-empty string".into(),
        ));
    }
    let mut body = Map::new();
    body.insert("command".into(), json!(command));
    if let Some(params) = params {
        body.insert("params".into(), params.clone());
    }
    if let Some(id) = controller(controller_id)? {
        body.insert("controllerId".into(), json!(id));
    }
    Ok(ServerRequest {
        method: "POST",
        path: format!("/api/robot/{robot_id}/command"),
        body: Some(Value::Object(body)),
    })
}

fn decode<T: for<'de> Deserialize<'de>>(body: &Value, what: &str) -> Result<T, ServerRequestError> {
    if !body.is_object() {
        return Err(ServerRequestError(format!("{what} must be a JSON object")));
    }
    serde_json::from_value(body.clone())
        .map_err(|error| ServerRequestError(format!("{what}: {error}")))
}

/// Reads the answer of `claim` and `release`.
pub fn parse_claim_result(body: &Value) -> Result<ClaimResult, ServerRequestError> {
    decode(body, "claim answer")
}

/// Reads the answer of `jog-arm`; it must carry a boolean `armed`.
pub fn parse_jog_arm_result(body: &Value) -> Result<JogArmResult, ServerRequestError> {
    decode(body, "jog-arm answer")
}

/// Reads `GET /api/claims`.
pub fn parse_claims(body: &Value) -> Result<Vec<ClaimEntry>, ServerRequestError> {
    let claims = body
        .get("claims")
        .filter(|value| value.is_array())
        .ok_or_else(|| ServerRequestError("claims answer has no 'claims' list".into()))?;
    serde_json::from_value(claims.clone())
        .map_err(|error| ServerRequestError(format!("claim: {error}")))
}

/// Reads `GET` and `PUT` of the safety limits.
pub fn parse_safety_limits(body: &Value) -> Result<SafetyLimitsView, ServerRequestError> {
    decode(body, "safety-limits answer")
}

/// An error answer of the server, told apart by its stable `code`.
#[derive(Debug, Clone, PartialEq)]
pub enum ApiError {
    /// Claimed by someone else: `code` is `other-account` or `other-controller`
    /// (`None` on a server that predates the codes).
    ClaimConflict {
        status: u16,
        message: String,
        code: Option<String>,
        reservation: Option<Reservation>,
    },
    /// The claim has a controller (409) or the server demands one to claim
    /// (400): send a `controllerId`.
    ControllerIdRequired {
        status: u16,
        message: String,
        reservation: Option<Reservation>,
    },
    /// The server refused the shape of the `controllerId` (400).
    InvalidControllerId { status: u16, message: String },
    /// A jog was refused because the robot is not armed (403).
    JogNotArmed { status: u16, message: String },
    /// Any other error; an unknown `code` is kept.
    Other {
        status: u16,
        message: String,
        code: Option<String>,
    },
}

impl ApiError {
    pub fn status(&self) -> u16 {
        match self {
            ApiError::ClaimConflict { status, .. }
            | ApiError::ControllerIdRequired { status, .. }
            | ApiError::InvalidControllerId { status, .. }
            | ApiError::JogNotArmed { status, .. }
            | ApiError::Other { status, .. } => *status,
        }
    }

    pub fn code(&self) -> Option<&str> {
        match self {
            ApiError::ClaimConflict { code, .. } | ApiError::Other { code, .. } => code.as_deref(),
            ApiError::ControllerIdRequired { .. } => Some(CODE_CONTROLLER_ID_REQUIRED),
            ApiError::InvalidControllerId { .. } => Some(CODE_INVALID_CONTROLLER_ID),
            ApiError::JogNotArmed { .. } => Some(CODE_JOG_NOT_ARMED),
        }
    }

    pub fn message(&self) -> &str {
        match self {
            ApiError::ClaimConflict { message, .. }
            | ApiError::ControllerIdRequired { message, .. }
            | ApiError::InvalidControllerId { message, .. }
            | ApiError::JogNotArmed { message, .. }
            | ApiError::Other { message, .. } => message,
        }
    }

    /// The claim that blocks the caller, when the answer carried one.
    pub fn reservation(&self) -> Option<&Reservation> {
        match self {
            ApiError::ClaimConflict { reservation, .. }
            | ApiError::ControllerIdRequired { reservation, .. } => reservation.as_ref(),
            _ => None,
        }
    }
}

impl fmt::Display for ApiError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self.code() {
            Some(code) => write!(f, "{} {}: {}", self.status(), code, self.message()),
            None => write!(f, "{} {}", self.status(), self.message()),
        }
    }
}

impl std::error::Error for ApiError {}

/// Turns an error answer into the most specific typed error. `body` is the
/// decoded JSON, or `None` when the answer was not JSON.
pub fn parse_api_error(status: u16, body: Option<&Value>) -> ApiError {
    let message = body
        .and_then(|b| b.get("error"))
        .and_then(Value::as_str)
        .map(str::to_owned)
        .unwrap_or_else(|| format!("HTTP {status}"));
    let code = body
        .and_then(|b| b.get("code"))
        .and_then(Value::as_str)
        .map(str::to_owned);
    let reservation = body
        .and_then(|b| b.get("reservation"))
        .filter(|value| value.is_object())
        .and_then(|value| serde_json::from_value::<Reservation>(value.clone()).ok());
    match code.as_deref() {
        Some(CODE_CONTROLLER_ID_REQUIRED) => ApiError::ControllerIdRequired {
            status,
            message,
            reservation,
        },
        Some(CODE_OTHER_ACCOUNT) | Some(CODE_OTHER_CONTROLLER) => ApiError::ClaimConflict {
            status,
            message,
            code,
            reservation,
        },
        Some(CODE_INVALID_CONTROLLER_ID) => ApiError::InvalidControllerId { status, message },
        Some(CODE_JOG_NOT_ARMED) => ApiError::JogNotArmed { status, message },
        _ if status == 409 && reservation.is_some() => ApiError::ClaimConflict {
            status,
            message,
            code,
            reservation,
        },
        _ => ApiError::Other {
            status,
            message,
            code,
        },
    }
}

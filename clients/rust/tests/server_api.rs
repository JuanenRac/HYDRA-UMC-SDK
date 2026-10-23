// =============================================================================
// HYDRA-UMC-SDK - Rust tests: claim, jog arming and safety-limit client
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

use std::fs;
use std::path::PathBuf;

use serde_json::Value;

use hydra_umc_sdk::server_api::*;

fn cases() -> Value {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("..")
        .join("conformance")
        .join("server-routes")
        .join("cases.json");
    serde_json::from_str(&fs::read_to_string(path).expect("the server route cases exist"))
        .expect("valid JSON")
}

fn text<'a>(args: &'a Value, key: &str) -> Option<&'a str> {
    args.get(key).and_then(Value::as_str)
}

fn build(call: &str, args: &Value) -> Result<ServerRequest, ServerRequestError> {
    let robot = args.get("robotId").and_then(Value::as_i64).unwrap_or(0);
    let controller = text(args, "controllerId");
    match call {
        "claim" => claim_request(
            robot,
            &ClaimOptions {
                ttl_ms: args.get("ttlMs").and_then(Value::as_f64),
                force: args.get("force").and_then(Value::as_bool),
                reason: text(args, "reason"),
                controller_id: controller,
                ..Default::default()
            },
        ),
        "release" => release_request(robot, text(args, "reason"), controller),
        "jogArm" => jog_arm_request(
            robot,
            args["armed"].as_bool().unwrap(),
            args.get("ttlMs").and_then(Value::as_f64),
            controller,
        ),
        "listClaims" => Ok(list_claims_request()),
        "getSafetyLimits" => Ok(safety_limits_request(
            args.get("robotId").and_then(Value::as_i64),
        )),
        "updateSafetyLimits" => update_safety_limits_request(&args["patch"]),
        "command" => command_request(
            robot,
            text(args, "command").unwrap_or(""),
            args.get("params"),
            controller,
        ),
        other => panic!("unknown call {other}"),
    }
}

#[test]
fn every_request_case_builds_the_expected_request() {
    for case in cases()["requests"].as_array().unwrap() {
        let name = case["name"].as_str().unwrap();
        let request = build(case["call"].as_str().unwrap(), &case["args"])
            .unwrap_or_else(|e| panic!("{name}: {e}"));
        let expect = &case["expect"];
        assert_eq!(request.method, expect["method"].as_str().unwrap(), "{name}");
        assert_eq!(request.path, expect["path"].as_str().unwrap(), "{name}");
        match &expect["body"] {
            Value::Null => assert!(request.body.is_none(), "{name}"),
            body => assert_eq!(request.body.as_ref(), Some(body), "{name}"),
        }
    }
}

#[test]
fn invalid_requests_are_refused_before_sending() {
    for case in cases()["invalidRequests"].as_array().unwrap() {
        let name = case["name"].as_str().unwrap();
        assert!(
            build(case["call"].as_str().unwrap(), &case["args"]).is_err(),
            "{name}"
        );
    }
}

#[test]
fn every_error_case_gets_its_typed_error() {
    for case in cases()["errors"].as_array().unwrap() {
        let name = case["name"].as_str().unwrap();
        let status = case["status"].as_u64().unwrap() as u16;
        let body = if case["body"].is_null() {
            None
        } else {
            Some(&case["body"])
        };
        let error = parse_api_error(status, body);
        let expect = &case["expect"];
        let kind = match &error {
            ApiError::ClaimConflict { .. } => "claim-conflict",
            ApiError::ControllerIdRequired { .. } => "controller-id-required",
            ApiError::InvalidControllerId { .. } => "invalid-controller-id",
            ApiError::JogNotArmed { .. } => "jog-not-armed",
            ApiError::RevisionMismatch { .. } => "revision-mismatch",
            ApiError::TableMove { .. } => "table-move",
            ApiError::Other { .. } => "api-error",
        };
        assert_eq!(kind, expect["kind"].as_str().unwrap(), "{name}");
        assert_eq!(error.status(), status, "{name}");
        assert_eq!(error.code(), expect["code"].as_str(), "{name}");
        assert_eq!(
            error.reservation().is_some(),
            expect["hasReservation"].as_bool().unwrap(),
            "{name}"
        );
    }
}

#[test]
fn reservation_details_survive() {
    let all = cases();
    let case = all["errors"]
        .as_array()
        .unwrap()
        .iter()
        .find(|c| c["name"] == "other-controller")
        .unwrap();
    let error = parse_api_error(409, Some(&case["body"]));
    let reservation = error.reservation().unwrap();
    assert_eq!(reservation.controller_id.as_deref(), Some("tab-1"));
    assert_eq!(reservation.owner_username, "alice");
}

#[test]
fn responses_are_read_and_unknown_fields_ignored() {
    let all = cases();
    let responses = &all["responses"];

    let claim = parse_claim_result(&responses["claim"]).unwrap();
    assert_eq!(
        claim.reservation.unwrap().controller_id.as_deref(),
        Some("tab-1")
    );
    assert_eq!(claim.history[0]["action"], "claimed");
    assert!(
        parse_claim_result(&serde_json::json!({"success": true, "reservation": null}))
            .unwrap()
            .reservation
            .is_none()
    );

    let on = parse_jog_arm_result(&responses["jogArmOn"]).unwrap();
    assert!(on.armed);
    assert_eq!(on.ttl_ms, Some(30000.0));
    let off = parse_jog_arm_result(&responses["jogArmOff"]).unwrap();
    assert!(!off.armed && off.expires_at.is_none());
    assert!(parse_jog_arm_result(&serde_json::json!({"success": true})).is_err());
    let mut extra = responses["jogArmOn"].clone();
    extra["futureField"] = serde_json::json!(1);
    assert!(parse_jog_arm_result(&extra).unwrap().armed);

    let claims = parse_claims(&responses["claims"]).unwrap();
    assert_eq!(
        claims.iter().map(|c| c.robot_id).collect::<Vec<_>>(),
        vec![1, 2]
    );
    assert_eq!(claims[0].controller_id.as_deref(), Some("tab-1"));
    assert!(claims[1].controller_id.is_none() && claims[1].robot_name.is_none());

    let view = parse_safety_limits(&responses["safetyLimits"]).unwrap();
    let robot = view.robot.unwrap();
    assert_eq!(robot.jog_armed_until, Some(31000.0));
    assert_eq!(robot.model.as_deref(), Some("Parol6 (6-DOF)"));
    assert_eq!(view.hard_limits["armTtlMs"]["max"], 600000);
}

#[test]
fn controller_id_pattern() {
    for (value, valid) in [
        ("tab-1", true),
        ("a.b_c:d-e", true),
        (&"a".repeat(64), true),
        (&"a".repeat(65), false),
        ("a b", false),
        ("", false),
        ("a/b", false),
    ] {
        assert_eq!(is_valid_controller_id(value), valid, "{value}");
    }
}

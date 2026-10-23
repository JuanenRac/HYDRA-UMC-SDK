// =============================================================================
// HYDRA-UMC-SDK - Rust tests: blocks 2 to 5 of the second server contract
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
        .join("cases_v2.json");
    serde_json::from_str(&fs::read_to_string(path).expect("the v2 server route cases exist"))
        .expect("valid JSON")
}

fn text<'a>(args: &'a Value, key: &str) -> Option<&'a str> {
    args.get(key).and_then(Value::as_str)
}

fn build(call: &str, args: &Value) -> Result<ServerRequest, ServerRequestError> {
    let robot = match args.get("robotId") {
        None => 0,
        Some(value) => value
            .as_i64()
            .ok_or_else(|| ServerRequestError("robot_id must be an integer".into()))?,
    };
    let controller = text(args, "controllerId");
    let if_match = text(args, "ifMatch");
    match call {
        "getRobot" => Ok(get_robot_request(robot)),
        "claim" => claim_request(
            robot,
            &ClaimOptions {
                controller_id: controller,
                if_match,
                ..Default::default()
            },
        ),
        "release" => release_request_if_match(robot, None, controller, if_match),
        "command" => command_request_if_match(
            robot,
            text(args, "command").unwrap_or(""),
            args.get("params"),
            controller,
            if_match,
        ),
        "table" => {
            let x = args["x"]
                .as_f64()
                .ok_or_else(|| ServerRequestError("x must be a number".into()))?;
            let y = args["y"]
                .as_f64()
                .ok_or_else(|| ServerRequestError("y must be a number".into()))?;
            table_command_request(
                robot,
                x,
                y,
                &TableOptions {
                    rz: args.get("rz").and_then(Value::as_f64),
                    mode: text(args, "mode"),
                    controller_id: controller,
                    if_match,
                },
            )
        }
        "audit" => audit_request(&AuditQuery {
            limit: args.get("limit").and_then(Value::as_i64),
            after_seq: args.get("afterSeq").and_then(Value::as_i64),
            kind: text(args, "type"),
            robot_id: args.get("robotId").and_then(Value::as_i64),
            verify: args.get("verify").and_then(Value::as_bool).unwrap_or(false),
        }),
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
        let want: Vec<(String, String)> = expect["headers"]
            .as_object()
            .unwrap()
            .iter()
            .map(|(k, v)| (k.clone(), v.as_str().unwrap().to_string()))
            .collect();
        assert_eq!(request.headers, want, "{name}");
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
        let error = parse_api_error(status, Some(&case["body"]));
        let expect = &case["expect"];
        let kind = match &error {
            ApiError::RevisionMismatch { revision, .. } => {
                assert_eq!(revision.as_deref(), expect["revision"].as_str(), "{name}");
                "revision-mismatch"
            }
            ApiError::TableMove { .. } => "table-move",
            other => panic!("{name}: unexpected {other:?}"),
        };
        assert_eq!(kind, expect["kind"].as_str().unwrap(), "{name}");
        assert_eq!(error.status(), status, "{name}");
        assert_eq!(error.code(), expect["code"].as_str(), "{name}");
    }
}

#[test]
fn responses_are_read() {
    let all = cases();
    let responses = &all["responses"];

    let robot = parse_robot(&responses["robot"]).unwrap();
    assert_eq!(robot.revision, "0123456789abcdef");
    assert_eq!(robot.robot["name"], "B");
    assert_eq!(robot.cell_id, "c1");
    assert!(parse_robot(&serde_json::json!({"robot": {}})).is_err());

    let plain = parse_command_result(&responses["commandPlain"]).unwrap();
    assert!(plain.success && plain.applied.is_none());
    assert_eq!(plain.revision.as_deref(), Some("fedcba9876543210"));
    let table = parse_command_result(&responses["commandTable"]).unwrap();
    let applied = table.applied.unwrap();
    assert_eq!((applied.x, applied.y, applied.rz), (40.0, 65.0, Some(15.0)));

    let claim = parse_claim_result(&responses["claimWithRevision"]).unwrap();
    assert_eq!(claim.revision.as_deref(), Some("0123456789abcdef"));
    assert!(
        parse_claim_result(&serde_json::json!({"success": true, "reservation": null}))
            .unwrap()
            .revision
            .is_none()
    );

    let audit = parse_audit(&responses["audit"]).unwrap();
    assert!(audit.enabled && !audit.locked_off);
    assert_eq!(
        audit.entries.iter().map(|e| e.seq).collect::<Vec<_>>(),
        vec![1, 2]
    );
    assert_eq!(audit.entries[0].controller_id.as_deref(), Some("tab-1"));
    assert_eq!(audit.entries[0].detail["action"], "claimed");
    assert!(audit.entries[1].username.is_none());
    assert_eq!(audit.verification.unwrap()["entries"], 2);

    let claims = parse_claims_event(&responses["claimsEvent"])
        .unwrap()
        .unwrap();
    assert_eq!(
        claims.iter().map(|c| c.robot_id).collect::<Vec<_>>(),
        vec![1, 2]
    );
    assert_eq!(claims[0].jog_armed_until, Some(31000.0));
    assert!(claims[1].jog_armed_until.is_none());
    assert!(
        parse_claims_event(&responses["otherMessage"])
            .unwrap()
            .is_none()
    );
    assert!(
        parse_claims_event(&serde_json::json!("not a message"))
            .unwrap()
            .is_none()
    );
}

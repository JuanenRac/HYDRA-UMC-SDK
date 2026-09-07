// =============================================================================
// HYDRA-UMC-SDK - Rust reference client tests: real schema validation
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

use std::fs;
use std::path::{Path, PathBuf};

use serde_json::{Value, json};

use hydra_umc_sdk::{known_contracts, validate, validate_json, verify_contract_manifest};

/// Locates `conformance/fixtures/v1` relative to this monorepo checkout -
/// the same fixtures `clients/python/tests`, `clients/go/validation_test.go`
/// and `clients/typescript/tests/validation.test.mts` all validate against.
fn fixtures_dir() -> Option<PathBuf> {
    let dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("..")
        .join("..")
        .join("conformance")
        .join("fixtures")
        .join("v1");
    dir.is_dir().then_some(dir)
}

fn read_fixture(dir: &Path, name: &str) -> String {
    fs::read_to_string(dir.join(name))
        .unwrap_or_else(|error| panic!("cannot read fixture {name}: {error}"))
}

/// The same fixture-naming convention `tools/verify_contract_matrix.py`
/// enforces: `<kebab-case-contract>.valid.json` / `.invalid.json`.
const CONTRACT_FIXTURE_STEM: &[(&str, &str)] = &[
    ("DeviceDescriptor", "device-descriptor"),
    ("EventEnvelope", "event-envelope"),
    ("HealthReport", "health-report"),
    ("ProjectManifest", "project-manifest"),
    ("SafetyState", "safety-state"),
    ("ServerDiscovery", "server-discovery"),
    ("UpdateManifest", "update-manifest"),
];

#[test]
fn accepts_every_valid_fixture() {
    let Some(dir) = fixtures_dir() else {
        eprintln!(
            "conformance fixtures not found; skipping (expected inside a HYDRA-UMC-SDK checkout)"
        );
        return;
    };
    for (contract, stem) in CONTRACT_FIXTURE_STEM {
        let data = read_fixture(&dir, &format!("{stem}.valid.json"));
        assert!(
            validate_json(contract, &data).is_ok(),
            "expected {contract} valid fixture to pass"
        );
    }
}

#[test]
fn rejects_every_invalid_fixture() {
    let Some(dir) = fixtures_dir() else {
        eprintln!(
            "conformance fixtures not found; skipping (expected inside a HYDRA-UMC-SDK checkout)"
        );
        return;
    };
    for (contract, stem) in CONTRACT_FIXTURE_STEM {
        let data = read_fixture(&dir, &format!("{stem}.invalid.json"));
        assert!(
            validate_json(contract, &data).is_err(),
            "expected {contract} invalid fixture to be rejected"
        );
    }
}

#[test]
fn unknown_contract_is_rejected() {
    let error = validate("NotARealContract", &json!({})).unwrap_err();
    assert_eq!(error.contract, "NotARealContract");
}

#[test]
fn known_contracts_lists_all_seven() {
    let names = known_contracts();
    assert_eq!(names.len(), 7, "expected 7 known contracts, got {names:?}");
}

#[test]
fn rejects_boolean_for_integer_sequence() {
    // bool must never satisfy an "integer" schema - mirrors
    // clients/python/tests/test_validation.py's
    // test_rejects_boolean_event_sequence, clients/go's
    // TestValidateRejectsBooleanForIntegerSequence, and clients/typescript's
    // equivalent test.
    let payload: Value = json!({
        "schema_version": "1.0",
        "event_id": "e",
        "type": "x",
        "source": "os",
        "timestamp_utc": "2026-08-26T12:00:00Z",
        "sequence": true,
    });
    assert!(validate("EventEnvelope", &payload).is_err());
}

#[test]
fn rejects_invalid_date_time() {
    let payload: Value = json!({
        "schema_version": "1.0",
        "state": "READY",
        "timestamp_utc": "2026-02-30T12:00:00Z", // no such calendar day
        "checks": {},
    });
    assert!(validate("HealthReport", &payload).is_err());
}

#[test]
fn accepts_a_minimal_health_report() {
    let payload: Value = json!({
        "schema_version": "1.0",
        "state": "READY",
        "timestamp_utc": "2026-01-01T00:00:00Z",
        "checks": {"storage": {"state": "PASS"}},
    });
    assert!(validate("HealthReport", &payload).is_ok());
}

#[test]
fn rejects_unknown_property_on_project_manifest() {
    // project-manifest.schema.json is the one contract with
    // additionalProperties: false - an unknown field is a real violation,
    // not an allowed extension.
    let Some(dir) = fixtures_dir() else {
        eprintln!(
            "conformance fixtures not found; skipping (expected inside a HYDRA-UMC-SDK checkout)"
        );
        return;
    };
    let data = read_fixture(&dir, "project-manifest.valid.json");
    let mut payload: Value = serde_json::from_str(&data).expect("fixture must be valid JSON");
    payload
        .as_object_mut()
        .expect("fixture must be a JSON object")
        .insert("unexpected_field".to_string(), json!("nope"));
    assert!(validate("ProjectManifest", &payload).is_err());
}

#[test]
fn verify_contract_manifest_passes() {
    verify_contract_manifest()
        .expect("every embedded schema must match manifest.json's own sha256 digest");
}

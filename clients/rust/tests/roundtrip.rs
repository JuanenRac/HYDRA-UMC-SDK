// =============================================================================
// HYDRA-UMC-SDK - Cross-language contract round-trip tests (Rust side)
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

use std::fs;
use std::path::{Path, PathBuf};

use serde::Serialize;
use serde::de::DeserializeOwned;
use serde_json::Value;

use hydra_umc_sdk::{
    Capability, DeviceDescriptor, EventEnvelope, HealthReport, Operation, ProjectManifest,
    SafetyState, ScenarioOutcome, ServerDiscovery, UpdateManifest,
};

/// Same fixtures every other language's own round-trip test uses - see
/// `clients/python/tests/test_contract_roundtrip.py` and
/// `clients/go/roundtrip_test.go`.
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

/// Decodes `raw` into `T`, re-encodes it, and asserts the re-encoded JSON
/// is structurally equivalent (compared as a generic `serde_json::Value`,
/// so key order never counts as a mismatch) to the original fixture. `T`
/// here is this client's own actual current representation for that
/// contract - a hand-written struct for each of the 10 contracts
/// (`DeviceDescriptor`, `HealthReport`, `SafetyState`, `UpdateManifest`,
/// `EventEnvelope`, `ServerDiscovery`, `ProjectManifest`, `Capability`,
/// `Operation`, `ScenarioOutcome` - each with a
/// `#[serde(flatten)] extra` field for any `additionalProperties: true`
/// schema, so even fields this struct doesn't explicitly name still
/// round-trip instead of being silently dropped).
fn assert_roundtrips_structurally<T: DeserializeOwned + Serialize>(contract: &str, raw: &str) {
    let original: Value = serde_json::from_str(raw)
        .unwrap_or_else(|error| panic!("{contract}: fixture is not valid JSON: {error}"));

    let decoded: T = serde_json::from_str(raw).unwrap_or_else(|error| {
        panic!("{contract}: failed to decode into the native type: {error}")
    });

    let reencoded = serde_json::to_string(&decoded)
        .unwrap_or_else(|error| panic!("{contract}: failed to re-encode: {error}"));

    let roundtripped: Value = serde_json::from_str(&reencoded)
        .unwrap_or_else(|error| panic!("{contract}: re-encoded output is not valid JSON: {error}"));

    assert_eq!(
        original, roundtripped,
        "{contract}: round trip did not structurally match the original fixture"
    );
}

macro_rules! roundtrip_test {
    ($name:ident, $contract:literal, $fixture:literal, $ty:ty) => {
        #[test]
        fn $name() {
            let Some(dir) = fixtures_dir() else {
                eprintln!("conformance fixtures not found - skipping (expected inside a HYDRA-UMC-SDK checkout)");
                return;
            };
            let raw = read_fixture(&dir, $fixture);
            assert_roundtrips_structurally::<$ty>($contract, &raw);
        }
    };
}

roundtrip_test!(
    device_descriptor_roundtrips,
    "DeviceDescriptor",
    "device-descriptor.valid.json",
    DeviceDescriptor
);
roundtrip_test!(
    health_report_roundtrips,
    "HealthReport",
    "health-report.valid.json",
    HealthReport
);
roundtrip_test!(
    safety_state_roundtrips,
    "SafetyState",
    "safety-state.valid.json",
    SafetyState
);
roundtrip_test!(
    update_manifest_roundtrips,
    "UpdateManifest",
    "update-manifest.valid.json",
    UpdateManifest
);
roundtrip_test!(
    event_envelope_roundtrips,
    "EventEnvelope",
    "event-envelope.valid.json",
    EventEnvelope
);
roundtrip_test!(
    server_discovery_roundtrips,
    "ServerDiscovery",
    "server-discovery.valid.json",
    ServerDiscovery
);
roundtrip_test!(
    project_manifest_roundtrips,
    "ProjectManifest",
    "project-manifest.valid.json",
    ProjectManifest
);

roundtrip_test!(
    capability_roundtrips,
    "Capability",
    "capability.valid.json",
    Capability
);
roundtrip_test!(
    operation_roundtrips,
    "Operation",
    "operation.valid.json",
    Operation
);
roundtrip_test!(
    scenario_outcome_roundtrips,
    "ScenarioOutcome",
    "scenario-outcome.valid.json",
    ScenarioOutcome
);

#[test]
fn unknown_fields_survive_in_the_three_newer_contracts() {
    let op = r#"{"schema_version":"1.0","operation_id":"o","correlation_id":"c","kind":"k","target":{"kind":"robot","id":"r","x":1},"status":"queued","requested_at_utc":"2024-01-01T00:00:00Z","updated_at_utc":"2024-01-01T00:00:00Z","params":{},"future":{"a":1}}"#;
    assert_roundtrips_structurally::<Operation>("Operation+extra", op);
    let cap = r#"{"schema_version":"1.0","target":{"kind":"robot","id":"r"},"kind":"k","declared":false,"future":[1,2]}"#;
    assert_roundtrips_structurally::<Capability>("Capability+extra", cap);
    let sc = r#"{"schema_version":"1.0","scenario_id":"s","run_id":"r","base_fingerprint":"f","phase":"before","repro_case":"c","observed":{"outcome":"reproduced","more":true},"timestamp_utc":"2024-01-01T00:00:00Z","future":1}"#;
    assert_roundtrips_structurally::<ScenarioOutcome>("ScenarioOutcome+extra", sc);
}

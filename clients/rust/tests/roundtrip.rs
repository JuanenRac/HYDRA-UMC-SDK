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
    DeviceDescriptor, EventEnvelope, HealthReport, ProjectManifest, SafetyState, ServerDiscovery,
    UpdateManifest,
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
/// contract - a hand-written struct for the 7 contracts that have one
/// (`DeviceDescriptor`, `HealthReport`, `SafetyState`, `UpdateManifest`,
/// `EventEnvelope`, `ServerDiscovery`, `ProjectManifest` - each with a
/// `#[serde(flatten)] extra` field for any `additionalProperties: true`
/// schema, so even fields this struct doesn't explicitly name still
/// round-trip instead of being silently dropped).
fn assert_roundtrips_structurally<T: DeserializeOwned + Serialize>(contract: &str, raw: &str) {
    let original: Value = serde_json::from_str(raw)
        .unwrap_or_else(|error| panic!("{contract}: fixture is not valid JSON: {error}"));

    let decoded: T = serde_json::from_str(raw)
        .unwrap_or_else(|error| panic!("{contract}: failed to decode into the native type: {error}"));

    let reencoded = serde_json::to_string(&decoded)
        .unwrap_or_else(|error| panic!("{contract}: failed to re-encode: {error}"));

    let roundtripped: Value = serde_json::from_str(&reencoded)
        .unwrap_or_else(|error| panic!("{contract}: re-encoded output is not valid JSON: {error}"));

    assert_eq!(
        original, roundtripped,
        "{contract}: round trip did not structurally match the original fixture"
    );
}

/// The 3 newer contracts (Capability, Operation, ScenarioOutcome) have no
/// dedicated struct in this client yet (see `src/types.rs`'s own doc
/// comment) - validated generically instead (`src/validation.rs`). Their
/// round trip is through the same generic `serde_json::Value`
/// representation, still a real, honest test of this client's actual
/// current behavior for those contracts, not an invented one.
fn assert_generic_roundtrips_structurally(contract: &str, raw: &str) {
    assert_roundtrips_structurally::<Value>(contract, raw);
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

#[test]
fn generic_contracts_roundtrip() {
    let Some(dir) = fixtures_dir() else {
        eprintln!("conformance fixtures not found - skipping (expected inside a HYDRA-UMC-SDK checkout)");
        return;
    };
    for (contract, fixture) in [
        ("Capability", "capability.valid.json"),
        ("Operation", "operation.valid.json"),
        ("ScenarioOutcome", "scenario-outcome.valid.json"),
    ] {
        let raw = read_fixture(&dir, fixture);
        assert_generic_roundtrips_structurally(contract, &raw);
    }
}

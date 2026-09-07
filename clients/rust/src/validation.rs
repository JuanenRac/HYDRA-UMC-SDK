// =============================================================================
// HYDRA-UMC-SDK - Rust reference client: real JSON Schema runtime validation
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

//! Real JSON Schema Draft 2020-12 runtime validation for the HYDRA-UMC-SDK
//! v1 contracts, backed by the [`jsonschema`] crate compiling this crate's
//! own vendored copy of each real `*.schema.json` (embedded at compile
//! time via `include_str!`, so a built binary needs no access to the
//! monorepo's `contracts/` directory at runtime - the same guarantee
//! `clients/go/validation.go`'s `//go:embed` and
//! `clients/typescript/src/validation.ts`'s vendored `schemas/` give their
//! own languages). `tests/schema_drift.rs` proves these embedded copies
//! stay byte-identical to `contracts/json-schema/v1/`.

use std::collections::HashMap;
use std::sync::OnceLock;

use serde_json::Value;
use sha2::{Digest, Sha256};

use crate::types::ContractManifest;

/// Raised on the first schema violation the underlying validator reports,
/// or on an unknown contract name. A real `std::error::Error` impl,
/// matching the Python client's `ContractValidationError` (a `ValueError`
/// subclass) and Go/TypeScript's own error types in spirit.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ContractValidationError {
    pub contract: String,
    pub message: String,
}

impl std::fmt::Display for ContractValidationError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}: {}", self.contract, self.message)
    }
}

impl std::error::Error for ContractValidationError {}

/// Contract name -> vendored schema file name - the same 7 names
/// documented in `docs/PYTHON_CLIENT.md`'s REQUIRED table for the Python
/// reference client, and the same mapping
/// `clients/go/validation.go`'s `contractFiles` and
/// `clients/typescript/src/validation.ts`'s `CONTRACT_FILES` use.
const CONTRACT_FILES: &[(&str, &str)] = &[
    ("DeviceDescriptor", "device-descriptor.schema.json"),
    ("EventEnvelope", "event-envelope.schema.json"),
    ("HealthReport", "health-report.schema.json"),
    ("ProjectManifest", "project-manifest.schema.json"),
    ("SafetyState", "safety-state.schema.json"),
    ("ServerDiscovery", "server-discovery.schema.json"),
    ("UpdateManifest", "update-manifest.schema.json"),
];

/// Vendored schema file name -> raw JSON text, embedded at compile time.
/// `include_str!` is this crate's equivalent of Go's `//go:embed`: the
/// resulting binary carries these bytes and needs no filesystem access to
/// `contracts/json-schema/v1/` at runtime.
const SCHEMA_FILES: &[(&str, &str)] = &[
    (
        "device-descriptor.schema.json",
        include_str!("../schemas/device-descriptor.schema.json"),
    ),
    (
        "event-envelope.schema.json",
        include_str!("../schemas/event-envelope.schema.json"),
    ),
    (
        "health-report.schema.json",
        include_str!("../schemas/health-report.schema.json"),
    ),
    (
        "project-manifest.schema.json",
        include_str!("../schemas/project-manifest.schema.json"),
    ),
    (
        "safety-state.schema.json",
        include_str!("../schemas/safety-state.schema.json"),
    ),
    (
        "server-discovery.schema.json",
        include_str!("../schemas/server-discovery.schema.json"),
    ),
    (
        "update-manifest.schema.json",
        include_str!("../schemas/update-manifest.schema.json"),
    ),
];

/// This crate's embedded copy of `manifest.json` - the generated
/// integrity manifest listing every published v1 schema file and its
/// sha256 digest (see `contracts/generate_manifest.py`).
const MANIFEST_JSON: &str = include_str!("../schemas/manifest.json");

fn schema_text_for_file(file: &str) -> Option<&'static str> {
    SCHEMA_FILES
        .iter()
        .find(|(name, _)| *name == file)
        .map(|(_, text)| *text)
}

fn compiled_schemas() -> &'static HashMap<&'static str, jsonschema::Validator> {
    static SCHEMAS: OnceLock<HashMap<&'static str, jsonschema::Validator>> = OnceLock::new();
    SCHEMAS.get_or_init(|| {
        CONTRACT_FILES
            .iter()
            .map(|(contract, file)| {
                let raw = schema_text_for_file(file)
                    .unwrap_or_else(|| panic!("no embedded schema text for {contract} ({file})"));
                let schema: Value = serde_json::from_str(raw).unwrap_or_else(|error| {
                    panic!("embedded schema for {contract} is not valid JSON: {error}")
                });
                // should_validate_formats(true) makes `format: "date-time"`
                // (used by every timestamp_utc field) a real, enforced
                // check - format validation is draft-dependent and NOT
                // enabled by default in this crate, matching Go's
                // `AssertFormat = true` and TypeScript's `ajv-formats`.
                let validator = jsonschema::draft202012::options()
                    .should_validate_formats(true)
                    .build(&schema)
                    .unwrap_or_else(|error| {
                        panic!("embedded schema for {contract} does not compile: {error}")
                    });
                (*contract, validator)
            })
            .collect()
    })
}

/// Validate `payload` against the real, published v1 JSON Schema for
/// `contract`. Returns `Ok(())` for a valid payload, or the first schema
/// violation the underlying validator reports (or an unknown contract
/// name) as `Err(ContractValidationError)`. This enforces the real
/// Draft 2020-12 schema directly (compiled from this crate's vendored
/// copy), not a hand-reimplemented subset.
pub fn validate(contract: &str, payload: &Value) -> Result<(), ContractValidationError> {
    let schemas = compiled_schemas();
    let validator = schemas
        .get(contract)
        .ok_or_else(|| ContractValidationError {
            contract: contract.to_string(),
            message: "unknown contract".to_string(),
        })?;
    validator
        .validate(payload)
        .map_err(|error| ContractValidationError {
            contract: contract.to_string(),
            message: error.to_string(),
        })
}

/// `validate()` for a raw JSON document instead of an already-decoded
/// [`Value`].
pub fn validate_json(contract: &str, data: &str) -> Result<(), ContractValidationError> {
    let payload: Value = serde_json::from_str(data).map_err(|error| ContractValidationError {
        contract: contract.to_string(),
        message: format!("invalid JSON: {error}"),
    })?;
    validate(contract, &payload)
}

/// The contract names `validate()`/`validate_json()` accept, sorted.
pub fn known_contracts() -> Vec<&'static str> {
    let mut names: Vec<&'static str> = CONTRACT_FILES
        .iter()
        .map(|(contract, _)| *contract)
        .collect();
    names.sort_unstable();
    names
}

/// Decodes this crate's embedded `manifest.json`. It is data, not itself a
/// JSON Schema, so it has no `validate()` entry point of its own;
/// [`verify_contract_manifest`] checks it directly instead.
pub fn load_contract_manifest() -> Result<ContractManifest, ContractValidationError> {
    // The real, canonical contracts/json-schema/v1/manifest.json (unlike
    // the *.schema.json files) is saved with a leading UTF-8 byte order
    // mark (U+FEFF). serde_json does not skip it, so it is stripped
    // explicitly here rather than "fixed" by re-encoding the normative
    // file this crate only vendors a copy of - the same handling Go's
    // utf8BOM trim and TypeScript's stripBom() give their own languages.
    let text = MANIFEST_JSON
        .strip_prefix('\u{FEFF}')
        .unwrap_or(MANIFEST_JSON);
    serde_json::from_str(text).map_err(|error| ContractValidationError {
        contract: "ContractManifest".to_string(),
        message: format!("cannot decode embedded manifest.json: {error}"),
    })
}

/// Recomputes the sha256 digest of every schema file this crate embeds
/// and compares it against `manifest.json`'s own claim for that file,
/// returning an error naming the first file whose embedded bytes do not
/// match - a real integrity check, not just a structural one, mirroring
/// Go's `VerifyContractManifest()` and TypeScript's
/// `verifyContractManifest()`.
pub fn verify_contract_manifest() -> Result<(), ContractValidationError> {
    let manifest = load_contract_manifest()?;
    for entry in &manifest.contracts {
        let raw = schema_text_for_file(&entry.file).ok_or_else(|| ContractValidationError {
            contract: "ContractManifest".to_string(),
            message: format!("manifest.json names {} but it is not embedded", entry.file),
        })?;
        let mut hasher = Sha256::new();
        hasher.update(raw.as_bytes());
        let actual = hasher
            .finalize()
            .iter()
            .map(|byte| format!("{byte:02x}"))
            .collect::<String>();
        if actual != entry.sha256 {
            return Err(ContractValidationError {
                contract: "ContractManifest".to_string(),
                message: format!(
                    "{}: manifest.json sha256 {} does not match embedded file's actual sha256 {actual}",
                    entry.file, entry.sha256
                ),
            });
        }
    }
    Ok(())
}

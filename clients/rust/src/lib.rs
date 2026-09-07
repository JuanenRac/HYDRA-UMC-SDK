// =============================================================================
// HYDRA-UMC-SDK - Rust reference client: public entry point
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

//! Rust reference client for the HYDRA-UMC-SDK v1 contracts documented in
//! [`docs/CONTRACTS.md`](https://github.com/JuanenRac/HYDRA-UMC-SDK/blob/main/docs/CONTRACTS.md):
//! hand-written types ([`types`]) plus real JSON Schema Draft 2020-12
//! runtime validation ([`validation`]), mirroring the scope of the Go and
//! TypeScript reference clients (`clients/go`, `clients/typescript`) for a
//! third language. The published JSON Schema files under
//! `contracts/json-schema/v1/` remain the normative source.

pub mod types;
pub mod validation;

pub use types::{
    ContractManifest, ContractManifestEntry, DeviceDescriptor, EventEnvelope, HealthReport,
    HealthState, NativeVersion, NativeVersionPattern, NativeVersionPatternComponents,
    ProjectManifest, ProjectManifestDeploymentTarget, ProjectManifestMaturity, ProjectManifestRole,
    SCHEMA_VERSION, SafetyState, SafetyStateValue, ServerDiscovery, UpdateManifest,
};
pub use validation::{
    ContractValidationError, known_contracts, load_contract_manifest, validate, validate_json,
    verify_contract_manifest,
};

// =============================================================================
// HYDRA-UMC-SDK - Rust reference client: anti-drift check for vendored schemas
// Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
// GPL-3.0-or-later - see LICENSE
// =============================================================================

//! Proves `clients/rust/schemas/*.json` (this crate's `include_str!`-
//! embedded copies, see `src/validation.rs`) stay byte-identical to the
//! normative `contracts/json-schema/v1/*.json` this monorepo publishes -
//! the same guarantee `clients/go`'s `TestVendoredSchemasMatchCanonical`
//! and `clients/typescript`'s `schema-drift.test.mts` give their own
//! languages.

use std::collections::BTreeSet;
use std::fs;
use std::path::PathBuf;

fn manifest_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

#[test]
fn vendored_schemas_match_canonical() {
    let canonical_dir = manifest_dir()
        .join("..")
        .join("..")
        .join("contracts")
        .join("json-schema")
        .join("v1");
    if !canonical_dir.is_dir() {
        // Not inside a HYDRA-UMC-SDK checkout (e.g. a standalone crate
        // install) - validate()/validate_json() never depend on this
        // directory, only on the embedded schemas/, so skip rather than
        // fail.
        eprintln!("canonical contracts/json-schema/v1 not found at {canonical_dir:?}; skipping");
        return;
    }
    let vendored_dir = manifest_dir().join("schemas");

    let canonical_names: BTreeSet<String> = fs::read_dir(&canonical_dir)
        .expect("cannot read canonical schema directory")
        .filter_map(|entry| entry.ok())
        .map(|entry| entry.file_name().to_string_lossy().into_owned())
        .filter(|name| name.ends_with(".json"))
        .collect();
    let vendored_names: BTreeSet<String> = fs::read_dir(&vendored_dir)
        .expect("cannot read vendored schema directory")
        .filter_map(|entry| entry.ok())
        .map(|entry| entry.file_name().to_string_lossy().into_owned())
        .filter(|name| name.ends_with(".json"))
        .collect();

    assert_eq!(
        canonical_names, vendored_names,
        "clients/rust/schemas/ must vendor exactly the files published under contracts/json-schema/v1/"
    );

    for name in &canonical_names {
        let canonical_bytes =
            fs::read(canonical_dir.join(name)).expect("cannot read canonical file");
        let vendored_bytes = fs::read(vendored_dir.join(name)).expect("cannot read vendored file");
        assert_eq!(
            canonical_bytes, vendored_bytes,
            "clients/rust/schemas/{name} has drifted from contracts/json-schema/v1/{name}"
        );
    }
}

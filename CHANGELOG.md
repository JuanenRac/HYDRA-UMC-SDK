# Changelog

## [0.0.8] - Go, TypeScript and Rust reference clients

### Added

- **`clients/go`** - real, tested Go reference client: hand-written struct
  types field-for-field from the v1 schemas (`types.go`), a custom
  `MarshalJSON`/`UnmarshalJSON` pair for `native_version.pattern`'s real
  `oneOf` shape (`native_version_pattern.go`, since `encoding/json` has no
  native union-type support), and real Draft 2020-12 validation
  (`validation.go`) via `github.com/santhosh-tekuri/jsonschema/v5`
  compiling this client's own `//go:embed`-vendored schema copies -
  enforcing the full published schema, not a reimplemented subset.
- **`clients/typescript`** - real, tested TypeScript reference client:
  hand-written interfaces (`src/types.ts`) and real Draft 2020-12
  validation (`src/validation.ts`) via Ajv (`ajv` + `ajv-formats`)
  compiling this package's own vendored `schemas/`.
- **`clients/rust`** - real, tested Rust reference client: hand-written
  structs (`src/types.rs`, including a real `#[serde(untagged)]` enum for
  `native_version.pattern`'s `oneOf`) and real Draft 2020-12 validation
  (`src/validation.rs`) via the `jsonschema` crate compiling this crate's
  own `include_str!`-embedded schema copies, with `should_validate_formats(true)`
  set explicitly since format validation is draft-dependent and not on by
  default in that crate.
- Every one of the three new clients has its own anti-drift test proving
  its vendored `schemas/*.json` stays byte-identical to
  `contracts/json-schema/v1/`, and its own full pass over
  `conformance/fixtures/v1/*.valid.json`/`*.invalid.json` - the same
  fixtures the Python reference client's own tests already use.

### Fixed

- **`.github/workflows/ci.yml`** - the Node/TypeScript, Rust and Go
  validation steps only ever looked for `package.json`/`Cargo.toml`/`go.mod`
  at the repository root (`hashFiles('package.json')` etc. are not
  recursive), so none of them ever actually ran for this repository's own
  `clients/go`, `clients/rust` and `clients/typescript` - a real, silent
  CI gap now closed by also matching `clients/**/package.json` etc. and by
  `cd`-ing into the discovered client directory before running
  `npm`/`cargo`/`go`, mirroring the existing Go step's own module-discovery
  pattern.
- **`contracts/json-schema/v1/manifest.json`** - the recorded sha256 for
  `update-manifest.schema.json` was stale (the schema file was edited for
  the `[0.0.5]` SemVer `pattern` addition, but the manifest was never
  regenerated afterwards). Every one of the three new clients' own
  integrity check caught this independently; fixed by re-running
  `contracts/generate_manifest.py` and correcting the one stale digest.

## [0.0.7] - Real JSON wire shape for BridgeJob/GateDecision

### Added

- **`bridge_contract.py`** - `job_to_dict()`/`job_from_dict()`/
  `decision_to_dict()`, the real shared JSON shape for a `BridgeJob`/
  `GateDecision` now that `HYDRA-UMC-BRIDGE-CNC`/`-LASER`/`-OPENPNP`/
  `-PRINTER3D`/`-ROS2` all reach `HYDRA-UMC-MQTT-BROKER`: one wire format
  every bridge parses/serializes identically, instead of each one
  reinventing its own ad-hoc JSON mapping for the same dataclass.
  `job_from_dict()` fails closed with `BridgeError` (never a bare
  `KeyError`/`ValueError`/`AttributeError`) on malformed input - the real
  parse boundary for a job arriving over an untrusted external transport
  (an MQTT PUBLISH payload, in practice). 8 new tests, including a real
  round-trip and every rejected-input case.

## [0.0.6] - Dependency-free mock server for testing without hardware

### Added

- **`hydra-umc-sdk-mock-server`** (`mock_server.py`, new) - a real,
  stdlib-only HTTP server that serves one example payload per known
  contract (`GET /mock/<Contract>`, plus `GET /mock/` for the contract
  list), so a UI, adapter or integration test can be written and exercised
  against a real HTTP endpoint before any actual CM5/robot/MCU hardware
  exists to talk to. Every example is proven, by this module's own tests,
  to pass this SDK's real `validate()` for its declared contract - the
  mock can never silently drift from what the SDK itself considers valid.
  Fails loudly at import time (not silently at first request) if a
  contract and its example payload ever fall out of 1:1 sync. Not a fake
  robot or a device-behavior simulation: every route is a static GET,
  nothing is ever accepted as a write, and no claim about real timing,
  concurrency, or physical state is made. 6 new tests, including a real
  end-to-end HTTP round-trip per contract over an ephemeral port.
- Added a named `HYDRA-UMC-OS` producer-fixture index and extended the
  contract matrix to validate every producer-declared contract payload. This
  makes producer evidence executable rather than unexamined JSON alongside
  the generic valid/invalid fixtures.

## [0.0.5] - Strict semver enforcement on UpdateManifest.version, wider fixture coverage

### Fixed

- **`validation.py`** - `UpdateManifest.version` was only checked for a
  matching `sha256`; a value like `"latest"` or `"v1"` passed straight
  through. It's now validated against the same `SEMVER_PATTERN` already
  used elsewhere in this file, and `update-manifest.schema.json` gained
  the matching JSON Schema `pattern`, so the reference validator and the
  published schema agree again.

### Added

- **Invalid conformance fixtures for every contract that was missing
  one** (`device-descriptor.invalid.json`, `event-envelope.invalid.json`,
  `safety-state.invalid.json`/`.valid.json`,
  `server-discovery.invalid.json`,
  `update-manifest.invalid.json`/`.valid.json`) - the compatibility
  matrix's own claim to check "one accepted and one rejected payload per
  contract" (see `docs/CONTRACTS.md`) wasn't true yet for these; now it
  is. New `CONTRACT_MATRIX_UPDATE_VERSION` check in
  `tools/verify_contract_matrix.py` proves the non-semver rejection
  directly. 35/35 tests passing, 14/14 fixtures across all 7 contracts.

## External machine bridge contract (no odometer bump)

Landed after [0.0.4] and before [0.0.5] above without going through the
odometer build script - `evaluate_job()` and `BridgeJob` were already in
use by [0.0.5]'s "all 7 contracts" fixture count, and [0.0.7] later
extends this same contract with its real JSON wire shape.

### Added

- Public, dependency-free Python v0 external-machine bridge contract:
  `BridgeJob`, bridge/machine/cell state enums and `evaluate_job()` safety
  gate. It is the shared high-level boundary for the ROS 2, OpenPnP, 3D
  printer, CNC and laser integrations; it does not expose motion control.
- `docs/BRIDGE_CONTRACT.md` and five focused unit tests proving productive
  work is rejected when either side is not ready while `ABORT` remains
  requestable through the authorised safety path.

### Fixed

- UpdateManifest validation now requires an HTTPS artifact URL with a real
  hostname, rejecting malformed strings such as `https:///artifact.deb`.

- The dependency-free Python validator now rejects invalid RFC 3339
  `timestamp_utc` values and JSON booleans supplied where the `EventEnvelope`
  sequence or `ServerDiscovery` numeric counters require integers. Python
  treats `bool` as an `int` subclass, which previously let invalid contract
  payloads pass reference validation.

## [0.0.4] - Automatic contract/validator compatibility matrix

### Added

- **`tools/verify_contract_matrix.py`** (new) - a real, automatic compatibility matrix between the published v1 JSON Schema files and this SDK's own Python reference validator. It discovers every real `*.schema.json` under `contracts/json-schema/v1/`, cross-checks that each one has a matching `validate()` entry (and vice versa - a stale validator entry with no real schema file is flagged too), runs every conformance fixture through `validate()` and confirms it's judged the way its own `.valid.json`/`.invalid.json` filename claims, and proves the two negative cases this matrix specifically guards: an unknown contract name and an incompatible `schema_version`.
- **`ProjectManifest` contract validation** (`validation.py`) - the matrix immediately found a real, concrete gap it was built to catch: `project-manifest.schema.json` (the `hydra-umc.project.json` contract every repository in this ecosystem publishes) had no corresponding entry in the Python validator at all - it could never actually be validated. Added the real required-field/enum/pattern checks mirroring the schema (`ecosystem`, `name` pattern, semver `version`, `role`/`deployment_target`/`maturity` enums, non-empty unique `technologies`, nullable `parent`, `native_version`'s string-or-component `pattern`), plus real conformance fixtures (`project-manifest.valid.json`/`.invalid.json`).
- 22 new tests (`test_validation.py`) = 30 total.

### Fixed

- `tools/build_test.py`'s non-mutating `build-test.sh` check compiled Python sources but never actually ran the real conformance test suite (`clients/python/tests`) or the new contract matrix - both are now wired in, so the "test" step genuinely tests something.

### Changed

- Automated build version increment from 0.0.3.

## Documentation

### Added

- `docs/PYTHON_CLIENT.md` - full reference for the `validate()` function
  and `hydra-umc-contract-validate` CLI in `clients/python`: the exact
  required-fields and extra-validation-rule table for all 6 contracts
  (`DeviceDescriptor`, `HealthReport`, `SafetyState`, `UpdateManifest`,
  `EventEnvelope`, `ServerDiscovery`), previously only readable from
  `validation.py`'s own source. Verified live against the real function
  and CLI. Linked from `docs/CONTRACTS.md`. Documentation-only - no code
  changed, no version bump.

## [0.0.3]

### Changed

- Automated build version increment from 0.0.2.

## [0.0.2]

### Added

- JSON Schema v1 for `DeviceDescriptor`, `HealthReport`, `SafetyState`, and
  `UpdateManifest`.
- Dependency-free Python reference validator and command-line entry point.
- Valid and invalid conformance fixtures plus four host-side validation tests.
- Runnable Python example for `HealthReport` validation.

### Limits

- Protobuf, OpenAPI, package publication, and non-Python clients are not part
  of this initial contract release.

## [0.0.1]

### Added

- Initial SDK documentation, multilingual README files, and target layout.
- Contract, API, conformance, and adapter-boundary specifications.

# Changelog

## [0.1.5] - New `ScenarioOutcome` contract + the T07/I60 before/after check

### Added

- **`contracts/json-schema/v1/scenario-outcome.schema.json`** - one run
  of a fixed reproduction scenario, `before` or `after` a candidate fix:
  a stable `scenario_id` + `repro_case` say WHAT is reproduced, `run_id`
  + `base_fingerprint` pin THIS run to an exact source state, and
  `observed.outcome` (`reproduced` / `not-reproduced` / `error`) says
  what happened. Vendored into the Go/Rust/TypeScript client
  `schemas/`; `conformance/fixtures/v1/scenario-outcome.{valid,invalid}.json`
  added; `validation.py` gained the matching `ScenarioOutcome` entry so
  `tools/verify_contract_matrix.py` still passes (`contracts=8`).
- **`clients/python/src/hydra_umc_sdk/scenario.py`** - `compare_runs(before,
  after) -> ScenarioComparison`, the reference consumer. It is the same
  "apparent success" control HYDRA-UMC-DEV-SERVER's own DS08 repair cycle
  applies, published once so every promotion path (DEV-SERVER,
  HYDRA-UMC-OPS-AGENT) judges a pair the same way. Verdicts:
  `regression-fixed` (reproduced before, not after, **and the base
  genuinely moved**), `still-broken`, `apparent-success` (stopped
  reproducing but the base fingerprint never changed - nothing was
  applied), `inconclusive` (phases out of order, a different
  `scenario_id`/`repro_case` - evidence for the wrong case - the
  after-run errored, or the before-run never reproduced the failure).
  Only a genuine `regression-fixed` is `is_promotable`.
- `examples/python/compare_scenario_runs.py` - two real recorded runs
  (an `apparent-success` and a `regression-fixed`) and the verdict for
  each.
- 12 new tests (`clients/python/tests/test_scenario.py` + `ScenarioOutcome`
  cases in `test_validation.py`).

## [0.1.4] - docs/BRIDGE_CONTRACT.md: list all 8 bridges that actually use it

### Fixed

- `docs/BRIDGE_CONTRACT.md`'s own scope line only listed 5 of the 8
  bridges that genuinely import `bridge_contract.py`/call
  `evaluate_job()` - `HYDRA-UMC-BRIDGE-AMR`, `HYDRA-UMC-BRIDGE-DROIDS`
  and `HYDRA-UMC-BRIDGE-UAV` were missing despite using the same real
  contract, confirmed by grepping every bridge's own source. Added,
  plus their own bridge-specific meaning entries.
- Removed a private-document allusion from `CHANGELOG.md`'s own 0.1.3
  entry and from `validation.py`'s own comment for the same change - a
  compatible manifest extension is documented on its own real merits,
  never by citing an unnamed external plan's section number.

## [0.1.3] - ProjectManifest: new `deployment_target` value `dev-server`

### Added

- `clients/python/src/hydra_umc_sdk/validation.py` - `"dev-server"` added
  to `PROJECT_MANIFEST_ENUMS["deployment_target"]` for the new
  HYDRA-UMC-DEV-SERVER project (a Raspberry Pi 5/CM5 host dedicated to
  development and task execution, distinct from `"cm5"`, the operational
  node that talks to real machines/robots). A compatible manifest
  extension - no existing value changed meaning, no consumer needs to
  change. New test `test_accepts_dev_server_deployment_target`.

## [0.1.2] - REV-009: BridgeJob's direct constructor now validates `parameters` before using it

### Fixed

- **`clients/python/src/hydra_umc_sdk/bridge_contract.py`'s `BridgeJob`**
  (found in a second review pass, P2; same class of gap as
  [0.1.1]'s SDK-01 above, this time on `parameters` instead of
  `phase`/`machine_state`): `parameters` is typed as `Mapping[str, str]`
  in the dataclass annotation, but Python never enforces that at
  runtime. `job_from_dict()` already guarded this before ever
  constructing a `BridgeJob` (its own `isinstance(parameters, Mapping)`
  check), but the public constructor's own `__post_init__` called
  `self.parameters.items()` directly with no equivalent guard -
  constructing `BridgeJob(..., parameters=[])` directly used to raise a
  bare `AttributeError: 'list' object has no attribute 'items'` instead
  of the intended `BridgeError` every other invalid-shape input on this
  same constructor already raises. `__post_init__` now checks
  `isinstance(self.parameters, Mapping)` first, so every construction
  path fails the same clean way. 2 new regression tests reproduce the
  finding's own exact scenario (a list, and a real mapping with a
  non-string value, both rejected with `BridgeError`).
  **Checked for the same ecosystem-wide breakage SDK-01 caused (5
  consumer bridges' own tests broke on that fix):** every real
  `BridgeJob(...)` call site across the ecosystem (all 9 bridges plus
  CONNECTOR-HUB's `sdk_gate.py`) was grepped - every one already passes
  a real `dict`/`{}` or another job's own already-valid `.parameters`,
  never a list or other non-mapping. No consumer breakage from this
  fix. `PYTHONPATH=clients/python/src python -m unittest discover -s
  clients/python/tests -v`: 53/53 passing.

## [0.1.1] - SDK-01: enforce real enum membership at the BridgeJob constructor

### Fixed

- **`clients/python/src/hydra_umc_sdk/bridge_contract.py`'s `BridgeJob`**
  (P1): `phase`/`machine_state` are typed as `JobPhase`/`MachineState` in the
  dataclass annotation, but Python never enforces that at runtime -
  constructing `BridgeJob` directly (not through `job_from_dict`, which
  already validated this) with an unrecognised string for either field
  used to construct successfully, and `evaluate_job` could then return
  `allowed=True` for a phase it never actually recognised (`job.phase is
  JobPhase.ABORT` is simply `False` for a garbage value, falling through
  to the same "ready" path a real, known phase would take).
  `__post_init__` now rejects a non-`JobPhase`/non-`MachineState` value
  outright, so the public constructor and `job_from_dict` reject the
  exact same invalid input identically. 2 new regression tests reproduce
  the finding's own exact scenario. `PYTHONPATH=clients/python/src
  python -m unittest discover -s clients/python/tests -v`: 51/51
  passing.

## [0.1.0] - Real first OpenAPI v1 slice for HYDRA-UMC-SERVER's own HTTP surface

### Added

- **`contracts/openapi/v1/server.openapi.json`** (new) - the SDK's own charter
  (`docs/API_DESIGN.md`) commits to publishing "the OpenAPI source and typed
  clients"; this is its first real slice, hand-verified against
  HYDRA-UMC-SERVER's own `src/server.ts`, not a placeholder. Covers
  discovery (`GET /api/hydra-info`), authentication (`POST /api/login`), the
  fleet roster (`GET`/`POST /api/settings`), and the real-time command plane
  (`POST /api/robot/{id}/command`, all 13 real command types: stop, play,
  pause, jog, reset, jogStep, reset3D, tool, valve, pump, speed, trajectory,
  vision - each modeled as its own `oneOf` variant with a `command`
  discriminator). Deliberately does not cover every route in `server.ts`:
  admin-only account/log/integration management, camera process
  supervision, CAN-OTA transfer, and power/system-service control are real
  but operational rather than SDK-contract surface, left for a later slice.
  Honestly documents one real discrepancy instead of papering over it:
  `docs/API_DESIGN.md`'s own command-result vocabulary
  (`ACCEPTED`/`REJECTED`/`RUNNING`/`COMPLETED`/`FAILED` plus a correlation
  identifier) is not what `POST /api/robot/{id}/command` actually returns -
  the real implementation replies with a plain `{success, affectedCount}`
  once the mutation is already applied and broadcast. Fixing that gap is
  Server-side product work, out of scope for this SDK.
- **`tools/verify_openapi.py`** (new) - dependency-free structural gate
  (stdlib `json` only, matching `verify_contract_matrix.py`'s own
  convention): every declared path has a real HTTP method, and every
  `$ref`/discriminator mapping target actually resolves inside the
  document. Also validated once by hand against `openapi-spec-validator`'s
  real OAS 3.1 validator while authoring the document (not vendored as a
  dependency here, to keep this repository's own tooling dependency-free).
  Wired into both `tools/build_test.py` and `.github/workflows/ci.yml`.

### Fixed

- **`.github/workflows/ci.yml`** - found while wiring in the check above:
  `tools/verify_contract_matrix.py` was already documented
  (`docs/CONTRACTS.md`) as this SDK's "mandatory compatibility gate", but
  this repository's own real CI workflow never actually ran it - only the
  local, non-CI `tools/build_test.py` did. Real CI now runs both
  `verify_contract_matrix.py` and the new `verify_openapi.py`.
- **`bump_version.py`** - its own auto-generated CHANGELOG stub entry
  embedded a literal calendar date (`date.today().isoformat()`) into this
  public file - every real entry in this CHANGELOG is dated only by its
  position, never a literal date. Removed before it could ever actually
  land one (this repository's version history shows no prior real build
  ran the script mechanically without hand-editing the stub first).

## [0.0.9] - Fix the TypeScript client's real CI failure on Node 20

### Fixed

- **`clients/typescript`** - the real GitHub Actions run for `[0.0.8]`
  failed: `npm test` executed `tests/*.test.mts` directly via `node
  --test`, relying on Node's unflagged TypeScript type stripping (only
  available from Node v22.18/v23.6 onward). It passed locally only
  because local development happened on a newer Node than this
  repository's own CI pins (`node-version: "20"` in
  `.github/workflows/ci.yml`, matching `package.json`'s declared
  `"engines": {"node": ">=20"}`) - so it broke silently until the actual
  workflow run was checked, not just simulated locally. Fixed by adding
  `tsconfig.test.json` (a second, test-only config compiling
  `tests/**/*.mts` to a git-ignored `dist-tests/`) and having `npm test`
  run the compiled `.mjs` output instead of the TypeScript source, so the
  test run no longer depends on that newer runtime feature at all.
  Re-verified against a clean `npm ci --ignore-scripts` (matching CI
  exactly, not a reused local `node_modules`): `npm run typecheck`,
  `npm test` (22/22), and `npm run lint --if-present` all pass.

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

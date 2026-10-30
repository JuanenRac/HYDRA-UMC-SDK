# Python reference client

Real, dependency-free validator for the contracts listed in
[CONTRACTS.md](CONTRACTS.md), implemented in
[`clients/python/src/hydra_umc_sdk/validation.py`](../clients/python/src/hydra_umc_sdk/validation.py).
The JSON Schema files under `contracts/json-schema/v1/` remain the
normative source - this module validates the same *required v1 subset*
in pure Python, for early adopters before generated schema-based clients
exist.

## Install

```bash
pip install -e clients/python
```

## `validate(contract: str, payload: dict) -> None`

```python
from hydra_umc_sdk.validation import validate, ContractValidationError

payload = {
    "schema_version": "1.0",
    "node_id": "hydra-umc-node",
    "profile": "base",
    "hostname": "cm5-arm-3",
    "machine": "aarch64",
    "operating_system": "Linux",
    "kernel": "6.6.31",
    "interfaces": ["eth0"],
}
validate("DeviceDescriptor", payload)  # raises ContractValidationError if invalid
```

Raises `ContractValidationError` (a `ValueError` subclass) on the first rule violated; returns `None` (no exception) on a valid v1 payload. Unknown fields beyond the required set are always allowed (additive-fields-are-safe, per CONTRACTS.md's compatibility rule) - this function only checks that the *required* v1 subset is present and well-formed.

**Every contract's `payload` must include `"schema_version": "1.0"`** - checked before any contract-specific rule.

### Required fields and extra rules per contract

| Contract | Required fields | Extra rules |
|---|---|---|
| `DeviceDescriptor` | `schema_version`, `node_id`, `profile`, `hostname`, `machine`, `operating_system`, `kernel`, `interfaces` | `interfaces` must be an array of non-empty strings. |
| `HealthReport` | `schema_version`, `state`, `timestamp_utc`, `checks` | `state` must be one of `READY`/`DEGRADED`/`INHIBITED`/`FAULT`/`SAFE_STOP`. `timestamp_utc` must be a valid RFC 3339 date-time. `checks` must be an object. |
| `SafetyState` | `schema_version`, `state`, `source`, `timestamp_utc` | `state` must be one of `READY`/`INHIBITED`/`FAULT`/`SAFE_STOP` (no `DEGRADED` - narrower than `HealthReport`'s own enum). `timestamp_utc` must be a valid RFC 3339 date-time. |
| `UpdateManifest` | `schema_version`, `project`, `version`, `artifact_url`, `sha256` | `sha256` must be a 64-character lowercase/uppercase hex digest. `artifact_url` must start with `https://`. |
| `EventEnvelope` | `schema_version`, `event_id`, `type`, `source`, `timestamp_utc`, `sequence` | `timestamp_utc` must be a valid RFC 3339 date-time. `sequence` must be a non-negative JSON integer (not a boolean). |
| `ServerDiscovery` | `schema_version`, `product`, `remoteApiVersion`, `appVersion`, `hostname`, `controllerCount`, `robotCount`, `uptimeSeconds` | `remoteApiVersion` must be a JSON integer >= 1; `controllerCount`/`robotCount`/`uptimeSeconds` must each be JSON integers >= 0 (not booleans). |
| `ProjectManifest` | `schema_version`, `ecosystem`, `name`, `version`, `role`, `stack`, `technologies`, `deployment_target`, `maturity`, `family`, `parent`, `native_version`, `build`, `notes` (optional: `service`, `deployment_target_note`; no other fields) | The real `hydra-umc.project.json` / `urtc.project.json` contract - see `_validate_project_manifest()`'s own docstring for the full set of enum/pattern/shape checks (name pattern, semver version, role/deployment_target/maturity enums, `native_version` shape). |
| `ScenarioOutcome` | `schema_version`, `scenario_id`, `run_id`, `base_fingerprint`, `phase`, `repro_case`, `observed`, `timestamp_utc` | `phase` must be `before`/`after`. `observed` must be an object whose `outcome` is `reproduced`/`not-reproduced`/`error`, with `exit_code` (if present) a JSON integer. `timestamp_utc` must be a valid RFC 3339 date-time. See `scenario.py`'s `compare_runs()` for the before/after check built on this contract. |
| `Operation` | `schema_version`, `operation_id`, `correlation_id`, `kind`, `target`, `status`, `requested_at_utc`, `updated_at_utc`, `params` | `status` must be one of `received`/`authorized`/`queued`/`sent`/`confirmed`/`terminated`/`rejected` - no `executed` bucket, by design. `target` must be an object with non-empty `kind`/`id`. `params` must be an object. `error`, if present, must be an object with non-empty `code`/`message`. `requested_at_utc`/`updated_at_utc` must each be a valid RFC 3339 date-time. `result`, if present, must be an object with non-empty `run_id`, `origin` one of `real`/`simulated`, boolean `observers_enabled`, and `outcome` one of `success`/`failure`/`unknown` - `outcome_reason` is required whenever `outcome` isn't `success`. See `operation.py`'s `validate_status_transition()` for the enforced lifecycle and `concludes_success()` for the real gate on trusting `result`. |
| `Capability` | `schema_version`, `target`, `kind`, `declared` | `target` must be an object with non-empty `kind`/`id`. `declared` must be a boolean - a static claim, never proof of anything. `last_checked_at_utc`, if present, must be a valid RFC 3339 date-time. `max_age_seconds`, if present, must be a positive number (not a boolean). `last_check_outcome`, if present, must be one of `verified`/`failed`/`unknown`. See `capability.py`'s `is_capability_usable()` for the real gate that treats `declared` and "recently, actually verified" as separate questions. |
| `Pose` | `schema_version`, `frame`, `position`, `orientation` | `frame` is `base` or `tool`. `position` has exactly finite numbers `x`, `y`, `z` (meters). `orientation` has exactly finite numbers `w`, `x`, `y`, `z` and must be a unit quaternion (length 1 within 1e-6). `euler` (roll, pitch, yaw in radians, intrinsic Z-Y-X) is deprecated: accepted next to the quaternion with a `DeprecationWarning`, and it must describe the same orientation. See `pose.py`'s `Quaternion` for the composition, the shortest-turn rotation vector and the Euler conversion. |
| `RobotState` | `schema_version`, `robot_id`, `state`, `updated_at_utc` | `state` is `idle`, `busy`, `estop`, `fault` or `offline` (a replica reports `estop` and `fault` and never clears them); `updated_at_utc` is an RFC 3339 date-time. Optional: `source` (`real` or `simulated`), `mission_id`, `battery_percent` (0 to 100) and `pose` (a `Pose`, unit quaternion included). It is the typed value that nodes replicate under the key `robot_state/<robot_id>`. See `robot_state.py`. |
| `TwinState` | `schema_version`, `source`, `frame`, `timestamp_utc`, `joint_states` | `source` is `real` or `simulated` (a consumer must never take one for the other); `frame` is `base` or `tool`; `timestamp_utc` is an RFC 3339 date-time. `joint_states` is an array of objects with a unique non-empty `name`, a finite `position` (radians, or meters for a prismatic joint) and optional finite `velocity` and `effort`. Optional: `robot_id` (non-empty), `sequence` (a non-negative integer that grows with every state of one robot) and `poses`, an array of `{name, pose}` where every `pose` is a `Pose` of the Pose contract, unit quaternion included. See `twin_state.py`. |
| `ConnectionEvent` | `schema_version`, `id`, `at_utc`, `action`, `client_kind`, `client_id` | Closed contract (no other field): a password, token or cookie cannot slip in. `id` is an integer >= 1; `at_utc` is an RFC 3339 date-time; `action` is `first_seen`, `login`, `login_failed`, `second_factor_failed`, `logout`, `session_ended` or `session_expired`; `client_kind` is `studio`, `suite`, `android`, `ios`, `dsi`, `watch`, `voice` or `other`; `client_id` is 16 lowercase hexadecimal digits. Optional: `user` (1 to 60 characters), `origin` (`local` or `remote`), `two_factor`, `app_version`, and `ip` and `agent` for administrators only. |
| `ConnectionClient` | `schema_version`, `id`, `kind`, `first_seen_utc`, `last_seen_utc`, `active_sessions`, `logins_ok`, `logins_failed` | Closed contract. `id` is 16 lowercase hexadecimal digits, `kind` as `client_kind` above, the dates are RFC 3339 and the three counters are integers >= 0. Optional: `user`, `app_version`, `origin`, `two_factor`, `last_failure_utc`, and `ip` and `agent` for administrators only. |

Every other required field not listed with an "extra rule" above just needs to be a non-empty string.

Passing a `contract` name outside this table raises `ContractValidationError: unknown contract: <name>`.

## CLI: `hydra-umc-contract-validate`

```bash
python -m hydra_umc_sdk.validation <contract> <payload.json>
```

- `<contract>` - one of the 10 names in the table above (argparse `choices`, so an invalid name is rejected before the file is even read).
- `<payload.json>` - path to a JSON file to validate.

Prints `valid <contract> v1 payload` and exits `0` on success. On failure (validation error, file not found, or invalid JSON), prints `hydra-umc-contract-validate: <message>` to stderr and exits `2`.

```bash
$ python -m hydra_umc_sdk.validation DeviceDescriptor device.json
valid DeviceDescriptor v1 payload

$ python -m hydra_umc_sdk.validation HealthReport bad.json
hydra-umc-contract-validate: missing required field: timestamp_utc
```

## CLI: `hydra-umc-sdk-mock-server`

A real, dependency-free HTTP server that serves one schema-valid example
payload per contract - built so a UI, adapter or integration test has
something real to hit over HTTP before any actual CM5/robot/MCU hardware
exists to talk to. Every example it can return is checked, by this
module's own tests, against the exact same `validate()` this file
documents above - the mock can never silently drift from what this SDK
considers a valid payload.

```bash
python -m hydra_umc_sdk.mock_server [--host HOST] [--port PORT] [--openapi FILE]
```

Defaults to `127.0.0.1:8790`. Routes:

- `GET /mock/` - `{"contracts": [...]}`, the list of contract names this instance can serve.
- `GET /mock/<Contract>` - the example payload for that contract (200), or `{"error": ...}` (404) for an unknown name.

With `--openapi contracts/openapi/v1/server.openapi.json` the same server also answers the paths and methods of that OpenAPI document, at their real paths (`POST /api/login`, `GET /api/robot/1`, ...):

- the answer is the first `2xx` response of the operation, with a body built from its schema (the `example`, `default` or first `enum` value where the schema gives one, a minimal value of the declared type otherwise) and the headers it declares (`ETag`);
- an operation that declares a bearer token answers `401` with the body of the contract when there is no `Authorization: Bearer` header;
- a method the path does not declare answers `405` with `Allow`; a path that is not in the document answers `404`;
- nothing is stored: a write is read, answered with the static example and changes nothing.

The tests prove that every operation of every published OpenAPI document is served with one of its declared success statuses and a body that conforms to its schema, so the mock cannot drift from the document.

This is not a fake robot, a fake MCU, or a simulation of real device
behavior - it never claims a machine is `READY`, never stores a write,
and every answer is a static example. It proves a client parses a real,
schema-valid HTTP response correctly; it proves nothing about actual
device behavior, timing, or concurrency.

```bash
$ python -m hydra_umc_sdk.mock_server &
hydra-umc-sdk-mock-server: serving 15 contracts on http://127.0.0.1:8790/mock/

$ curl -s http://127.0.0.1:8790/mock/HealthReport
{"schema_version": "1.0", "state": "READY", "timestamp_utc": "2026-01-01T00:00:00Z", "checks": {"storage": {"state": "PASS"}}}
```

## Tool: `tools/contract_check.py`

A read-only check of a whole workspace, for a person or a CI job that wants one report instead of fifty-six validators:

```bash
python tools/contract_check.py [WORKSPACE] [--report-only] [--tables]
```

It walks every HYDRA-UMC repository of the workspace (the parent folder of the SDK by default) and prints one JSON report: the manifest of each repository against the `ProjectManifest` validator, the manifest name against the folder name, the vendored shared tools against the canonical copies of this SDK, a `service` block against `contracts/ports.yaml`, and the OpenAPI documents of this SDK against the structural check. The exit status is 1 when anything was found, unless `--report-only` is given. With `--tables` it prints instead three Markdown tables that nobody should write by hand: the ports of the services (from the registry, ordered by port), the version and maturity of every repository (from its manifest) and the routes of the server (every path and method of the OpenAPI documents with its operation id and tag).

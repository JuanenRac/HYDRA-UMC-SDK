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
| `UpdateManifest` | `schema_version`, `project`, `version`, `artifact_url`, `sha256` | `sha256` must be a 64-character lowercase/uppercase hex digest. `artifact_url` must start with `https://`. Optional and checked when present: `signature` (128 lowercase hex characters, the Ed25519 signature over the manifest without that field written as canonical JSON: keys sorted, no spaces), `signature_alg` (`ed25519`), `key_id` (16 lowercase hex characters, the first eight bytes of the SHA-512 of the public key), `min_bootloader` (a version) and `target` (a short lowercase controller name such as `g474` or `h745-cm7`). |
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
| `EcosystemHealth` | `schema_version`, `generated_at_utc`, `available`, `summary`, `services`, `certificate`, `warnings` | Closed contract (also inside). `summary` has the six counters `total`, `ok`, `degraded`, `down`, `unknown`, `drift` (integers >= 0); every service has `name`, `family`, `role`, `state` (`ok`, `degraded`, `down` or `unknown`), `reason` (one of the 13 codes in `SERVICE_REASONS`), `version_expected` and `version_reported` (a plain version of up to 24 characters or null), `drift`, `last_seen_utc` and `latency_ms` (date-time / integer or null), and, for administrators only, `port` (1 to 65535 or null), `health_path`, `systemd_unit` and `active_state`; `certificate` is null (the server runs without TLS) or has `state` (`ok`, `expiring`, `expired`, `unreadable`), `not_after_utc`, `days_left` and `warn_days` (1 to 365) and never a path; each warning has a `code` from `WARNING_CODES` and, for a service, its `service`. See `ecosystem.py`. |
| `RobotLiveness` | `schema_version`, `stale_after_s`, `robots` | Closed contract. `stale_after_s` is an integer from 1 to 3600; each robot has `controller_id`, `robot_id` (integer >= 0) and `state` (`live`, `stale` or `unknown`) and, unless it is `unknown`, `last_update_utc`, `age_s` and `source` (`state` or `heartbeat`). It is news the server received, never the `online` flag of the settings. See `ecosystem.py`. |
| `ToolDescriptor` | `schema_version`, `tool_id`, `name`, `title`, `kind` | Closed contract (also inside). `tool_id` is an integer from 0 to 255, `name` capitals, digits and underscores, `kind` is `motion`, `actuator`, `telemetry` or `external`; `hero_metric`, `limits` (`default`, `min`, `max`), `watchdog_ms`, `features`, `expansion_board` and `min_firmware_version` are optional. `descriptor_problems` adds the order of the limits. |
| `ToolState` | `schema_version`, `tool_id`, `state`, `source`, `timestamp_utc` | Closed contract (also inside). `state` is `active`, `idle`, `fault` or `unknown`; optional `firmware_version`, `can` (`state` `ok`, `error_passive`, `bus_off` or `unknown`, with `tec`, `rec`, `bus_off_count`), `temperature_c`, `setpoint_c`, `mcu_temp_c`, `vdda_mv`, `critical_error` and `thermal_fault`. `state_problems` adds the rules that join fields and, given the descriptor, the limits and the firmware. |
| `ProductionEvent` | `schema_version`, `source_id`, `at_utc`, `good`, `cycle_time_s` | Closed contract. `source_id` (and the optional `job_id`) is 1 to 64 letters, digits, dots, colons, dashes or underscores; `at_utc` is an RFC 3339 date-time (when the cycle ended); `good` is a true boolean or false; `cycle_time_s` is a finite number greater than 0 and at most 604800 (one week). Optional: `job_id`, `reject_reason` (1 to 120 characters). `production_event_fields` gives the data lake sample (`good` as 1.0 or 0.0 and `cycleTimeS`). See `production_event.py`. |
| `CommandLifecycleEvent` | `schema_version`, `operation_id`, `robot_id`, `command`, `state`, `at_utc`, `sequence` | Closed contract. The three identifiers are 1 to 64 letters, digits, dots, colons, dashes or underscores; `state` is `ACCEPTED`, `RUNNING`, `COMPLETED`, `FAILED` or `CANCELLED`; `sequence` is an integer >= 1. `reason` (1 to 200 characters) is required for `FAILED` and `CANCELLED`. `command_state_from_operation` derives the state from an `Operation` (`terminated` is `COMPLETED` only when its result passes `concludes_success`) and `validate_state_transition` says which step may follow which. See `command_lifecycle.py`. |
| `VisualTargetRequest` | `schema_version`, `frame_id`, `current`, `target`, `confidence`, `safety_state` | Closed contract. `current` and `target` are objects with exactly `x`, `y`, `z` (meters) and `roll`, `pitch`, `yaw` (radians), all finite numbers; `confidence` is from 0 to 1; `safety_state` is a `SafetyState` value. Either `data_age_ms` (>= 0) or `captured_at_utc` must be present. Optional: `calibration_version`, `calibration_age_days`. See `servoing.py`. |
| `VelocityCommand` | `schema_version`, `vx`, `vy`, `vz`, `wroll`, `wpitch`, `wyaw`, `hold`, `issued_at_ms`, `valid_for_ms`, `seq` | Closed contract. The six velocities are finite numbers (m/s and rad/s), `hold` is a true boolean, `issued_at_ms` and `seq` are integers >= 0, `valid_for_ms` is greater than 0 and at most 60000. Optional `frame_id` (or null). `command_is_current` says whether a command may still be acted on. See `servoing.py`. |
| `FrameMeta` | `schema_version`, `frame_id`, `capture_ts_utc`, `width`, `height`, `pixel_format` | Closed contract. `width` and `height` are integers from 1 to 8192; `pixel_format` is `RGB`, `BGR`, `RGBA`, `BGRA`, `GRAY`, `YUYV`, `NV12` or `JPEG`. Optional: `session_id`, `source_id`, `stride` (>= 1), `sequence` (>= 0). See `vision_pipeline.py`. |
| `DetectionFrame` | `schema_version`, `frame_id`, `capture_ts_utc`, `box_unit`, `detections` | Closed contract. `box_unit` is `pixel` or `normalized` (0 to 1), origin at the top left corner; every detection has `class_id` (>= 0), `label`, `score` (0 to 1) and a `box` with exactly `x_min`, `y_min`, `x_max`, `y_max` (the client also checks that no corner ends before it starts). Optional `session_id` and `model`, the five fields of the compatibility record of the vision node. `box_to_pixels` converts a box. See `vision_pipeline.py`. |
| `MaintenanceIncident` | `incidentId`, `sourceNode`, `detectedAt`, `severity`, `component`, `symptom`, `evidenceRefs`, `redactionLevel`, `requestedBy`, `correlationId` | Closed contract with the camelCase names the maintenance agent writes; `schema_version` is optional. `severity` is `info`, `warning` or `critical`; `redactionLevel` is `sanitized` or `raw`; `requestedBy` is a text or null; `evidenceRefs` holds at most 50 texts. `incident_may_be_stored` refuses `raw` unless the consumer allows it. See `maintenance.py`. |
| `NodeSnapshot` | `sourceNode`, `collectedAt`, `correlationId`, `projects`, `manifestIssues`, `systemdAvailable`, `systemdUnavailableReason`, `serviceHealth`, `httpHealth`, `incidents` | Closed contract with the camelCase names the maintenance agent writes; `schema_version` is optional. `systemdAvailable` is `true`, `false` or `null` (never asked); every entry of `incidents` is checked as a `MaintenanceIncident`; the optional `hostHealth` (disks, thermal, backups) holds readings that are `null` when the machine could not give them. See `maintenance_agent.py`. |
| `ChangeProposal` | `proposalId`, `incidentId`, `correlationId`, `createdAt`, `projectName`, `description`, `diff`, `rationale`, `status` | Closed contract; `status` is `pending`, `approved` or `rejected`. The decision fields (`decidedBy`, `decidedAt`, `decisionReason`, `approvedContentDigest` as 64 lowercase hexadecimal characters, `allowProtectedPaths`, `approvalExpiresAt`, `approvedBaseCommit`, `approvalSignature`, `generatedBy`) are optional and may be null. |
| `CanaryDeployResult` | `deployId`, `proposalId`, `projectName`, `startedAt`, `finishedAt`, `promoted`, `stageReached`, `buildOutput`, `detail` | Closed contract; `stageReached` is `staged`, `diff_applied`, `build_verified`, `diff_committed`, `promoted` or `rolled_back`; `backupPath` and `patchPath` are optional and may be null. |
| `EvidenceBundle` | `componentVersions`, `relevantManifests`, `redactedLogExcerpts`, `reproductionSteps`, `failedTests`, `impact`, `actionsAttempted`, `checksum`, `date`, `localValidationResult` | Closed contract. `componentVersions` is an object; the five lists are arrays of texts and `reproductionSteps` has at least one; `impact`, `checksum` and `localValidationResult` are non-empty texts; `date` is an RFC 3339 date-time. `bundle_checksum` is the SHA-256 of the canonical JSON without `checksum`, `seal_bundle` fills it in and `bundle_matches_checksum` checks it; that no secret is inside is the job of the redaction before the bundle is built and of the reader. |
| `SafetyZonesState` | `sdkSafetyState`, `reason` | Closed contract. `sdkSafetyState` is a `SafetyState`; `reason` is a text or null; `sdkSafetyStateSignature` (optional) is `alg` (`HMAC-SHA256` or `Ed25519`), `key_id` (1 to 64), `counter` (an integer from 0) and `sig` (64 or 128 lowercase hexadecimal characters); `configSha256` is 64 lowercase hexadecimal characters; `breaches` lists at most 20 of `zone_id`, `level` and `object_id` (no positions); `breachCount` and `estopRequestCount` are integers from 0. A consumer acts on the signed state and never on the counts. |
| `VlaApproval` | `approved`, `fingerprint`, `robot_id`, `operator`, `approved_at_ms`, `expires_at_ms`, `signature` | Closed contract. `approved` is exactly `true`; `fingerprint` and `signature` are 64 lowercase hexadecimal characters; `robot_id` and `operator` are texts of 1 to 64 characters; the two times are integers of milliseconds from 1. The layer that executes the motion checks the signature, the fingerprint, the robot and the validity. |
| `FaultEvent` | `schema`, `source`, `code`, `state` | Closed contract. `schema` is exactly `fault-event/1` (this contract has no `schema_version`); `source` and `code` are texts of 1 to 64 characters; `state` is `raised` or `cleared`; `severity` (optional) is `info`, `warning`, `error` or `critical`; `robot_id` (optional) is null or a text of 1 to 64 characters; `text` (optional) is at most 240 characters. A reader is more forgiving (an unknown severity is taken as `error`, a long text is cut): an emitter checks its message against this before it publishes. |

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
hydra-umc-sdk-mock-server: serving 29 contracts on http://127.0.0.1:8790/mock/

$ curl -s http://127.0.0.1:8790/mock/HealthReport
{"schema_version": "1.0", "state": "READY", "timestamp_utc": "2026-01-01T00:00:00Z", "checks": {"storage": {"state": "PASS"}}}
```

## Hardening the bridge transport: `hydra_umc_sdk.bridge_transport`

Every limit below is **off by default**, so a bridge that sets nothing behaves as it always did.

| Setting | Where | Default | Effect |
|---|---|---|---|
| `max_queue` | `MessageDispatcher` | `None` (no limit) | How many ordinary commands may wait behind the running one. When a new one arrives with the queue full, the **oldest** waiting command is dropped and counted. The stop lane is never bounded. |
| `max_payload_bytes` | `MessageDispatcher` | `None` (no cap) | A payload over the cap is refused before it is queued, logged at warning level and counted. Stop verbs are exempt. |
| `backoff_factor`, `max_delay_seconds`, `jitter`, `rng` | `connect_with_retry` | `1.0`, `None`, `0.0` | The wait before retry *n* is `retry_delay_seconds * backoff_factor ** (n - 1)`, capped at `max_delay_seconds`, then spread by up to `jitter` (0 to 1) either way. `rng` returns a float in [0, 1) and `sleep` is injectable, so tests need no real wait. |
| `connect_backoff_factor`, `connect_max_delay_seconds`, `connect_jitter` | `open_bridge_client` | as above | Passed to `connect_with_retry` for the first connect. |
| `reconnect_min_delay_seconds`, `reconnect_max_delay_seconds` | `open_bridge_client` | `1`, `30` | Bounds of paho's own reconnect delay after the link drops (`0 < min <= max`). |

```python
dispatcher = MessageDispatcher(bridge, prefix, frozenset({"cmd/stop"}), max_queue=64, max_payload_bytes=65536)
...
dispatcher.stats()   # {"dropped": 0, "oversized": 0, "queued": 0}
```

A limit that is not a whole number of 1 or more, a `backoff_factor` below 1, a `jitter` outside 0 to 1 or inconsistent reconnect bounds raise `ValueError` at once.

## Tool: `tools/contract_check.py`

A read-only check of a whole workspace, for a person or a CI job that wants one report instead of fifty-six validators:

```bash
python tools/contract_check.py [WORKSPACE] [--report-only] [--tables]
```

It walks every HYDRA-UMC repository of the workspace (the parent folder of the SDK by default) and prints one JSON report: the manifest of each repository against the `ProjectManifest` validator, the manifest name against the folder name, the vendored shared tools against the canonical copies of this SDK, a `service` block against `contracts/ports.yaml`, and the OpenAPI documents of this SDK against the structural check. The exit status is 1 when anything was found, unless `--report-only` is given. With `--tables` it prints instead three Markdown tables that nobody should write by hand: the ports of the services (from the registry, ordered by port), the version and maturity of every repository (from its manifest) and the routes of the server (every path and method of the OpenAPI documents with its operation id and tag).

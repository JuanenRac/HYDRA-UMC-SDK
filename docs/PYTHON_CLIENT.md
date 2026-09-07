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

Every other required field not listed with an "extra rule" above just needs to be a non-empty string.

Passing a `contract` name outside this table raises `ContractValidationError: unknown contract: <name>`.

## CLI: `hydra-umc-contract-validate`

```bash
python -m hydra_umc_sdk.validation <contract> <payload.json>
```

- `<contract>` - one of the 7 names in the table above (argparse `choices`, so an invalid name is rejected before the file is even read).
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
python -m hydra_umc_sdk.mock_server [--host HOST] [--port PORT]
```

Defaults to `127.0.0.1:8790`. Routes:

- `GET /mock/` - `{"contracts": [...]}`, the list of contract names this instance can serve.
- `GET /mock/<Contract>` - the example payload for that contract (200), or `{"error": ...}` (404) for an unknown name.

This is not a fake robot, a fake MCU, or a simulation of real device
behavior - it never claims a machine is `READY`, never accepts a write,
and every route is a static GET. It proves a client parses a real,
schema-valid HTTP response correctly; it proves nothing about actual
device behavior, timing, or concurrency.

```bash
$ python -m hydra_umc_sdk.mock_server &
hydra-umc-sdk-mock-server: serving 7 contracts on http://127.0.0.1:8790/mock/

$ curl -s http://127.0.0.1:8790/mock/HealthReport
{"schema_version": "1.0", "state": "READY", "timestamp_utc": "2026-01-01T00:00:00Z", "checks": {"storage": {"state": "PASS"}}}
```

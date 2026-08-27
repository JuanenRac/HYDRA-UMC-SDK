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
| `HealthReport` | `schema_version`, `state`, `timestamp_utc`, `checks` | `state` must be one of `READY`/`DEGRADED`/`INHIBITED`/`FAULT`/`SAFE_STOP`. `checks` must be an object. |
| `SafetyState` | `schema_version`, `state`, `source`, `timestamp_utc` | `state` must be one of `READY`/`INHIBITED`/`FAULT`/`SAFE_STOP` (no `DEGRADED` - narrower than `HealthReport`'s own enum). |
| `UpdateManifest` | `schema_version`, `project`, `version`, `artifact_url`, `sha256` | `sha256` must be a 64-character lowercase/uppercase hex digest. `artifact_url` must start with `https://`. |
| `EventEnvelope` | `schema_version`, `event_id`, `type`, `source`, `timestamp_utc`, `sequence` | `sequence` must be a non-negative integer. |
| `ServerDiscovery` | `schema_version`, `product`, `remoteApiVersion`, `appVersion`, `hostname`, `controllerCount`, `robotCount`, `uptimeSeconds` | `remoteApiVersion` must be an integer >= 1; `controllerCount`/`robotCount`/`uptimeSeconds` must each be an integer >= 0. |

Every other required field not listed with an "extra rule" above just needs to be a non-empty string.

Passing a `contract` name outside this table raises `ContractValidationError: unknown contract: <name>`.

## CLI: `hydra-umc-contract-validate`

```bash
python -m hydra_umc_sdk.validation <contract> <payload.json>
```

- `<contract>` - one of the 6 names in the table above (argparse `choices`, so an invalid name is rejected before the file is even read).
- `<payload.json>` - path to a JSON file to validate.

Prints `valid <contract> v1 payload` and exits `0` on success. On failure (validation error, file not found, or invalid JSON), prints `hydra-umc-contract-validate: <message>` to stderr and exits `2`.

```bash
$ python -m hydra_umc_sdk.validation DeviceDescriptor device.json
valid DeviceDescriptor v1 payload

$ python -m hydra_umc_sdk.validation HealthReport bad.json
hydra-umc-contract-validate: missing required field: timestamp_utc
```

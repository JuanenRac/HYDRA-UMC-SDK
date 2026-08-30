<!--
=============================================================================
HYDRA-UMC-SDK - Normative contract guide
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
CC BY-SA 4.0 - see LICENSE.md
=============================================================================
-->

# Contract guide

## Rule

A service must depend on a versioned SDK contract, not on the database,
private queue, or internal source tree of another service. A contract is
defined once and then represented through Protobuf, JSON Schema, or OpenAPI
according to its use case.

## Initial contract set

| Contract | Producer examples | Consumer examples |
| --- | --- | --- |
| `DeviceDescriptor` | OS agent, MCU/URTC adapter | Server, Studio, Updater |
| `HealthReport` | OS agent, services | Server, Node Healing, Studio |
| `SafetyState` | MCU adapter, safety service | Server, UI, Job Dispatcher |
| `ToolDescriptor` | URTC adapter | Server, Smart Rack, Studio |
| `TelemetrySample` | Collector/adapters | DataLake, Reports, Anomaly Detector |
| `UpdateManifest` | Updater registry | OS agent, updater client |
| `ServerDiscovery` | Server `GET /api/hydra-info` | Studio, Suite, mobile clients, Updater |

## Implemented JSON Schema v1

The implemented contracts are published under `contracts/json-schema/v1/`.
Their v1 required fields are intentionally small, and `additionalProperties`
is enabled so producers can add compatible fields without breaking older
consumers. The Python reference validator implements the required v1 subset;
the JSON Schema files remain the normative source. See
[PYTHON_CLIENT.md](PYTHON_CLIENT.md) for the validator's full function/CLI
reference, including the exact required-fields table per contract.

## Conformance fixtures and compatibility gate

`conformance/fixtures/v1/` contains one accepted and one rejected payload for
every published v1 contract.  They are deliberately plain JSON rather than
test-framework fixtures: any implementation can consume the same examples.
The rejected cases exercise a meaningful invariant (such as a negative event
sequence, an unsupported safety state, a non-HTTPS update URL, or an
incompatible schema version), not merely malformed JSON.

`tools/verify_contract_matrix.py` is the mandatory SDK compatibility gate. It
fails when a published schema lacks a reference-validator entry, when a stale
validator entry has no schema, or when any fixture is accepted/rejected
contrary to its name. Consumers should run this gate from their own CI after
updating their SDK dependency; it is the baseline contract check, not a claim
that a real machine has been exercised.

## Event envelope

Every event needs `event_id`, `schema_version`, `type`, `source`,
`timestamp_utc`, `sequence`, and optional `correlation_id`. The collector
records reception time independently. Commands additionally require actor,
idempotency key, target, and deadline.

## Compatibility

Use SemVer. Additive fields are optional in a minor version; renaming or
removing fields requires a major version. Consumers ignore unknown fields and
producers document the minimum supported SDK version.

## Server discovery

`ServerDiscovery` formalizes the additive v1 `schema_version` field and the
existing camelCase HTTP response fields from `GET /api/hydra-info`. Its
`remoteApiVersion` remains the Server transport version; it is not the SDK
schema version. Consumers must reject a missing or unsupported
`schema_version` before using discovery metadata.

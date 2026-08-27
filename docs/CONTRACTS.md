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
the JSON Schema files remain the normative source.

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

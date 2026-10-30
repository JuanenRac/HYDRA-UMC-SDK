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
| `UpdateManifest` | Updater registry | OS agent, updater client |
| `ServerDiscovery` | Server `GET /api/hydra-info` | Studio, Suite, mobile clients, Updater |
| `EventEnvelope` | Services | Event consumers, DataLake |
| `ScenarioOutcome` | Scenario runners | OPS-AGENT, Node Healing |
| `Operation` | Server, Orchestrator, Dev Server | UIs, Job Dispatcher |
| `Capability` | Targets and their descriptors | Orchestrator, Job Dispatcher |
| `Pose` | Visual servoing, VLA engine | Server, Studio, Suite |
| `ProjectManifest` | Every repository (`hydra-umc.project.json` or `urtc.project.json`) | Updater, dashboard |

Planned, with no schema yet: `ToolDescriptor` (URTC adapter, for Server, Smart
Rack and Studio) and `TelemetrySample` (collector and adapters, for DataLake,
Reports and Anomaly Detector).

## Implemented JSON Schema v1

The implemented contracts are published under `contracts/json-schema/v1/`.
Their v1 required fields are intentionally small, and `additionalProperties`
is enabled so producers can add compatible fields without breaking older
consumers. `ProjectManifest` is the exception: it is closed (only the listed
fields, with `service` and `deployment_target_note` optional), because every
repository publishes it and a typo in a field name should fail early. The Python reference validator implements the required v1 subset;
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

## OpenAPI v1

`contracts/openapi/v1/server.openapi.json` is a real, hand-verified OpenAPI
3.1 description of HYDRA-UMC-SERVER's own public HTTP surface - discovery
(`GET /api/hydra-info`), authentication (`POST /api/login`), the fleet roster
(`GET`/`POST /api/settings`), and the real-time command plane
(`POST /api/robot/{id}/command`, all 13 real command types), and the control
routes of the server contract v2, block 1: `claim`, `release`, `jog-arm`,
`GET /api/claims`, `GET /api/safety-limits` and `PUT /api/admin/safety-limits`,
with the optional `controllerId` and the stable error codes (see
[SERVER_CLIENT.md](SERVER_CLIENT.md)). It deliberately covers only that SDK-contract surface, not every route in `server.ts` -
admin-only account/log/integration management, camera process supervision,
CAN-OTA transfer, and power/system-service control are real but operational
rather than contract material, and are left for a later slice. It also
honestly documents one real discrepancy: this guide's [Compatibility](#compatibility)
section and `docs/API_DESIGN.md` describe command results using
`ACCEPTED`/`REJECTED`/`RUNNING`/`COMPLETED`/`FAILED` plus a correlation
identifier, but `POST /api/robot/{id}/command`'s real implementation replies
with a plain `{success, affectedCount}` once the mutation has already been
applied - the document describes that real behavior, not the aspirational
envelope. `tools/verify_openapi.py` is a dependency-free structural gate
(every path has a real HTTP method, every `$ref`/discriminator mapping
resolves) wired into both `tools/build_test.py` and CI; a full OpenAPI 3.1
validation (via `openapi-spec-validator`) was run by hand while authoring it
but is not vendored as a dependency here, matching this repository's
dependency-free tooling convention.

`contracts/openapi/v1/server.full.openapi.json` is a copy of the OpenAPI that
the server generates from its routes (every route, with the status codes and
the names of the body fields). The typed slice above never invents a route
that this copy does not have; the tests check it.

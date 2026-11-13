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
| `RobotState` | Swarm sync, orchestrator, dashboard | Server, Studio, Suite |
| `TwinState` | Digital twin, physics replica, HIL bridge | Server, Studio, Suite |
| `ConnectionEvent` | Server (history of the clients that connect) | Studio, Suite, apps |
| `ConnectionClient` | Server (list of the clients it has seen) | Studio, Suite, apps |
| `EcosystemHealth` | Server (`GET /api/ecosystem/health`, off until an administrator turns it on) | Studio, Suite, apps, dashboard |
| `RobotLiveness` | Server (`GET /api/robots/liveness`) | Studio, Suite, apps, OPC UA server |
| `RobotRoster` | Any reader of the settings of the server (adapters, gateways, tools) | Adapters, gateways, tools |
| `ProductionEvent` | Orchestrator, bridges, robots (one finished cycle) | Production reports, Data Lake |
| `CommandLifecycleEvent` | Server (the step a robot command reached: accepted, running, completed, failed, cancelled) | Studio, Suite, apps |
| `VisualTargetRequest` | Callers of visual servoing | Visual servoing service |
| `VelocityCommand` | Visual servoing service | Robot controllers, Server |
| `FrameMeta` | Vision node, vision streamer | Detection services |
| `DetectionFrame` | Detection services (vision node, Hailo detection) | Visual servoing, Studio, Suite |
| `PoseEstimate` | Pose estimation services (the pose of the detections of a frame) | Visual servoing, Studio, Suite |
| `MaintenanceIncident` | Maintenance agent of a node | Development server, local technician, dashboard |
| `NodeSnapshot` | Maintenance agent of a node (what its edge side saw in one pass, with the incidents and, when switched on, the readings of the machine) | Development server, local technician, dashboard |
| `ChangeProposal` | Maintenance agent of a node (a change a person reviews: diff, rationale, decision and signature) | Development server, local technician |
| `CanaryDeployResult` | Maintenance agent of a node (how far an approved change got on one node) | Development server, local technician, dashboard |
| `EvidenceBundle` | Local technician and maintenance agent (what a node hands to a development node when an incident needs a change of code: versions, manifests, redacted logs, reproduction steps, impact, a checksum of the content) | Development node, development server |
| `SafetyZonesState` | HYDRA-UMC-SAFETY-ZONES (the answer of `GET /state`: the latest signed verdict, the reason, the configuration hash and the short list of breaches) | Visual servoing, orchestrator, bridges and the panels of STUDIO and SUITE |
| `VlaApproval` | HYDRA-UMC-VLA-ENGINE (the answer of `POST /confirmations/<id>/confirm`: the signed approval of a person for exactly one trajectory) | The layer that executes the motion; the confirmation screens of the apps |
| `FaultEvent` | Every service that raises a fault (the message `fault-event/1` on the broker under `hydra/faults/`; the field that names it is `schema`) | Server (active faults and history), MTConnect and OPC UA feeds |
| `ToolDescriptor` | URTC tool table (one catalogue entry per tool head profile) | Server, Smart Rack, Studio, telemetry collector |
| `ToolState` | URTC adapter or gateway (one reading of a connected tool head) | Server, Smart Rack, Studio, telemetry collector |
| `Kinematics` | The SDK (`contracts/kinematics.json`: the range of every joint, the home pose and, where it is known, the chain of the arm as a URDF writes it) | The solvers and panels of STUDIO and SUITE and the planner of the SERVER, in place of the copy each one keeps |
| `JointPoses` | HYDRA-UMC-PHYSICS-REPLICA (the answer of forward kinematics, `POST /fk` and `fk --envelope`: the position and the unit quaternion of every joint, listed from the root to the tip, in the frame `base`) | TWIN, PATH-PLANNER-3D, SAFETY-ZONES and the panels of STUDIO and SUITE |
| `CanIds` | The SDK (`contracts/can_ids.json`: the emergency stop identifier, the slot windows of the stack bus and the messages of a slot with the one node that sends each) | The firmware and its host tools of HYDRA-UMC, HYDRA-UMC-TELEMETRY-COLLECTOR |
| `ToolArms` | HYDRA-UMC-SAFETY-ZONES (the answer of `GET /tool-arms`: the last report of each pair of robot and tool, with its age) | The panels of STUDIO, SUITE and DSI |
| `ProjectManifest` | Every repository (`hydra-umc.project.json` or `urtc.project.json`) | Updater, dashboard |

Planned, with no schema yet: `TelemetrySample` (collector and adapters, for
DataLake, Reports and Anomaly Detector).

`ToolDescriptor` is static (the profile number, name, kind, the metric the tool is judged
by, its limits, watchdog and features, as the URTC tool table has them) and `ToolState` is
one reading of a connected head (the active tool, its firmware, the state and error counters
of its CAN controller, temperatures and faults). Both are closed. A JSON Schema cannot say
that the limits are ordered or that a thermal fault means the state `fault`, so
`descriptor_problems` and `state_problems` of the Python client state those rules and
return the problems as texts. The schemas were written from the frames and the tool table of
URTC-COMMON (`spec/tools.json`, the health profile and the thermal telemetry) and are checked
against that table when it is next to the SDK; a head that has not been connected to this
contract yet is still a head, not a state. How the contracts of A.R.M.O.R. are read in these
words is in [ARMOR_ALIGNMENT.md](ARMOR_ALIGNMENT.md).

## Implemented JSON Schema v1

The implemented contracts are published under `contracts/json-schema/v1/`.
Their v1 required fields are intentionally small, and `additionalProperties`
is enabled so producers can add compatible fields without breaking older
consumers. `ProjectManifest` is the exception: it is closed (only the listed
fields, with `service`, `deployment_target_note` and `depends_on` optional), because every
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

Both documents carry the routes that the server added after the connection pilot: `GET /api/ecosystem/health`
(closed `EcosystemHealth` schema), `GET /api/robots/liveness` (closed `RobotLiveness` schema),
`POST /api/robot/{id}/heartbeat` and `POST /api/stop-all/release` (answer `{success, announced}`: whether the
retained `READY` went out on the MQTT bridge). The full copy also lists `GET /api/connections/clients`,
`GET /api/connections/events` and the public `GET /health`. The typed slice (document version 1.5.0) describes the
four routes above with the two closed schemas as components, so a typed client can use them without reading the
full copy. What a route answers when it is switched off is part of its description: `GET /api/ecosystem/health`
answers a plain `404` with no body until an administrator turns `ecosystemHealth.enabled` on (a viewer gets `403`).
The two schemas are closed like the connection ones, so an address, a path or a key cannot slip into them;
the port, health path, unit and active state of a service are optional because only an administrator receives them.

`GET /api/rul/config` (typed slice and full copy; the closed `RulConfig` answer `{enabled, maxPoints, timeoutMs}`) lets any signed-in account read whether the relay of the remaining-useful-life estimate is open to operators and how large a request it accepts. It is read only, carries nothing else, and is fail-closed: a configuration that is missing or unreadable gives `enabled` false with the default limits instead of an error, and a server without the route answers `404`, which a client reads as closed.

## Contract sources (pilot)

The routes of the connections (`GET /api/connections/clients` and `GET /api/connections/events`) are declared in `contracts/sources/connections.routes.json` and the OpenAPI document `contracts/openapi/v1/server.connections.openapi.json` is generated from it, together with the closed `ConnectionClient` and `ConnectionEvent` schemas. `python tools/contract_source.py --check` fails when the generated document, a vendored schema copy, the server or a client drifts from it. [CONTRACT_SOURCE.md](CONTRACT_SOURCE.md) describes the design of making the SDK the source of the whole server contract and the phases to get there.

## Generated types and the lint

`python tools/generate_types.py` turns every closed schema of `contracts/json-schema/v1` into a TypeScript interface (`generated/hydra-contracts.ts`), a Kotlin data class (`generated/HydraContracts.kt`) and a Dart class with `fromJson` and `toJson` (`generated/hydra_contracts.dart`). The files are never edited by hand: `--check` fails when one is out of date, and a client that copies the file it needs runs the same check against a checkout of the SDK. Keywords that a type cannot say (`anyOf`, `allOf`, `if`/`then`) stay with the validators of the SDK.

`contracts/topics.json` is the registry of the topics that every bridge shares (direction, retained flag, QoS and the schema of the payload). `python tools/hydra_contract_lint.py` runs, in one command, the check of the whole tree of repositories, the check of the route sources and the check of the generated types; `--tables` prints the ports, versions, routes and topics tables that must not be written by hand.

## Answers generated for the apps

`python tools/make_app_fixtures.py` writes `conformance/app-fixtures/v1/server-answers.json` from the shapes of `contracts/openapi/v1/server.full.openapi.json`: for every route that names the shape of an answer, one `minimal` body (the required fields) and one `full` body (every declared field), per status code. An app replays these answers against its own models, so the inventory is the one description of the server that every client is tested with; `--check` fails when the file is not what the inventory produces, and a test proves that every body conforms to its shape.

## Kinematic data of the robot models

`contracts/kinematics.json` is the one document of the joint ranges (degrees), the home pose (degrees) and, where it is known, the chain of the arm of each robot model; the closed schema `kinematics.schema.json` describes it. A chain is written as a URDF writes its joints (the offset in meters from the parent, the rotation in radians, the axis) together with the numbers it was built from (the Denavit-Hartenberg values of the maker). The three classic Universal Robots arms carry a chain today; the other models carry their ranges and home pose and the chain is added as it is checked against the solver of each. A test checks that the ranges are ordered, that every home pose is inside its range, that a chain follows its own numbers, and that the copies of the ranges that the apps keep are the same when their repositories are next to this one. An app moves to this document by taking it from the SDK it is pinned to; until it does, its copy is checked against this one.

## CAN identifiers of the stack bus

`contracts/can_ids.json` is the one document of the identifiers of the HYDRA-UMC stack bus: the emergency stop identifier, the base and width of the slot windows, the number of slots and the messages of a slot (an offset inside the window and the one node that sends it). The identifier of a message is `slot_base + slot * slot_window + offset`. The closed schema `can-ids.schema.json` describes it and the Python validator checks the rest. It also holds, as optional sections, the 8-byte frame of the emergency stop (`estop_frame`) and the identifiers of the URTC tool head protocol (`tool_head`, copied from the URTC spec and compared with it by a test). A firmware table or a reader of the bus (the telemetry collector) is to be written against this document.

## gRPC contracts

`contracts/proto/` holds the Protocol Buffers sources of the services that speak gRPC: `hydra_telemetry.proto` (the telemetry ingest). A service keeps the code generated from the file it uses.

## Catalogue of the URTC tools

`contracts/urtc_tools.json` is the common list of the tool modes of the URTC family (identifier, constant name, title and whether an expansion board is needed), with the identifier that means "no tool". A service or app resolves a tool by number, name or title from this one list instead of keeping its own. A test checks that the ids are consecutive, that names and titles are unique and that the copy equals the one of the documentation repository when both are checked out side by side.

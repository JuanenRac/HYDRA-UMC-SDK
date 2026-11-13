# Changelog

## [Unreleased]

- **The evidence bundle travels in a typed signed envelope (`hydra_umc_sdk.incident_transport`):** `build_incident_message()` and `verify_incident_message()` define the `incident-transport/1` message (version, kind, destination node, time, nonce, escalation id, the sealed bundle and an HMAC-SHA256 over the canonical JSON), so that the technician that writes it and the development node that reads it share one definition. The reader checks the signature first, then the destination, the clock, the shape and the checksum of the bundle, and remembers the nonce last, so a refused message never uses one up; a replay is refused and no secret ever appears in an error.

- **One shared reading of the state word of a GRBL report (`hydra_umc_sdk.grbl_status`):** `grbl_machine_state()` drops the numeric substate (`Hold:0`, `Door:1`, `Alarm:1`), ignores the case and maps the words of GRBL v1.1 to the machine state of the bridge contract; anything unknown or not text is OFFLINE and only `Idle` maps to the state in which work may start. A bridge can add words of its own. The CNC and the laser bridge keep their own copies until they adopt it.

- **Declare the routes of the update of the programs from Studio in the contract:** `GET /api/admin/self-update`, `GET /api/admin/self-update/jobs/{id}`, `POST /api/admin/self-update/apply` and `POST /api/admin/self-update/rollback` (administrator; the look is off until the server turns on its look at the newest versions and applying until it turns on maintenance), with the three shapes of their answers (`SelfUpdateStatus`, `SelfUpdateItem`, `SelfUpdateJob`: the programs against the newest signed release, and a job with its steps checking, downloading, verifying, applying, restarting, done or failed and the reason when it failed). The generated document, the route tables and the fixtures follow.

- **The job intake keeps a key per source, can give a key back and looks a job in doubt up instead of running it again (`hydra_umc_sdk.job_intake`):** `IdempotencyStore.claim/remember/recall` take an optional `source` so that two senders that use the same key text no longer shadow each other (without it the behaviour and the stored files are unchanged), `release(key)` returns a key that never got an answer so that the retry after a failure that did nothing is a new job, and `JobIntake(..., in_doubt_policy="consult", status_query=...)` answers a repeat whose first attempt left no answer with the state the machine reports (policy `consult`, the default) or refuses it (`refuse`); there is no policy that retries.

- **The canonical document-policy module has the same time limits as the copies:** `clients/python/src/hydra_umc_sdk/doc_policy.py` is the source `sync_doc_policy.py` copies to every repository as `tools/_doc_policy.py`, and it did not yet carry the `timeout` on its `git` calls that the copy of this repository had, so the next sync would have taken them out again and the weekly Sync check would have reported the drift.
- **Every child process of the shared tools has a time limit, and the jobs of the workflow templates have one too:** `hydra_project_tool.py`, `ci_validate.py`, `build_test.py`, `_doc_policy.py` and `make_structure.py` pass a `timeout` to every `subprocess` call: `HYDRA_UMC_GIT_TIMEOUT_S` (default 120 s, for git) and `HYDRA_UMC_COMMAND_TIMEOUT_S` (default 3600 s, for builds, tests and the glance check) change them, and anything that is not a positive number means the default. A step that runs out of time ends with a message (exit code 124 in the project tool, a failed `BUILD_TEST` in the build test, `could not check` in the documentation policy) instead of holding a runner for hours. The notifier of the dashboard (`notify`, 10 minutes) and the baseline job (30 minutes) of the workflow templates carry `timeout-minutes`, as do the jobs of this repository that can. `clients/python/tests/test_subprocess_timeouts.py` (13 tests) fails if a call without a timeout is added to those files or a job loses its limit. The copies in the other repositories follow in a later batch of the shared-tools sync.
- **More tests for the pose, the operation result, the signed commands and the MCU error vocabulary:** 26 tests of refusals and boundaries (unit quaternions, rotation vectors with a fixed seed, every refusal of a pose payload including the deprecated Euler angles, the order of the success gate of an operation result, every verdict of a signed command, key file problems). The MCU error tests were bare functions that the unittest run of the CI never executed; they are now unittest cases and run.
- **The Dart client tells a read-only server from a robot in safe mode:** `HydraApiException.isServerReadOnly` is true for the code `server-read-only`, `isRobotDisabled` no longer takes that 423 for a robot in safe mode, and `HydraErrorKind.serverReadOnly` is added (at the end of the list) so the apps can give it a sentence of their own. The shared vectors are unchanged. Test in `clients/dart_app_common/test/hydra_error_test.dart`.
- **The status feed of the developer server has its new name in the contract:** `POST /api/ingest/dev-server/status` and `GET /api/dev-server/status` (schema `dev-server-status/1`) are in the OpenAPI document, the route tables for TypeScript, Kotlin and Dart, the app fixtures and the stand-in server. The old `/api/ingest/developer-node/status` and `/api/developer-node/status` stay as deprecated aliases for one version (marked `deprecated` in the inventory, the stand-in server still accepts the old path and the old schema `developer-node-status/1`), so nothing installed breaks.

## [0.6.2] - The emergency stop frame and the tool head identifiers in the CAN contract, the pose, telemetry and TLS contracts and shared app packages

- **README: the platform statement:** a note says that where the README speaks of the CM5 it means the pilot bench that runs today, and that the target platform of HYDRA-UMC, an NVIDIA Jetson Orin NX 16 GB, is a design that has not been built or tested.
- **The tool head bus is 1 Mbit/s in the CAN contract (decision of the owner):** `tool_head.bit_rate_bps` is 1000000, like STACK A, and the optional `legacy_bit_rate_bps` (500000) keeps the number of the earlier URTC protocol, documented, for heads that were not updated yet. The URTC spec and the head firmware move to 1 Mbit/s on the URTC side; until the spec says so, the test that compares the contract with the spec accepts its rate as the legacy value.

- **The CAN contract carries the frame of the emergency stop and the identifiers of the tool heads:** `contracts/can_ids.json` now also holds `estop_frame` (the 8 bytes of the frame on identifier 0x001 in order, the three kinds TRIP, RELEASE and ALIVE, the eight reasons of a TRIP and the sources: the brain 0, the slot boards 1 to 8, the bridge 16) and `tool_head` (the 106 messages of the URTC protocol with their identifier, name and direction, from `spec/can_protocol.json` of URTC-COMMON, the bit rate of that bus, 500 kbit/s, and the protocol version). Both sections are optional in the closed schema `can-ids.schema.json` (copies, manifests and generated types refreshed); the Python validator checks the kinds, reasons and sources (no value twice, the brain is 0, the slot boards are a range below the bridge) and the tool head identifiers (unique, 11 bits, unique names, the direction), and 4 new tests include one that compares the 106 messages with the URTC spec when URTC-COMMON is next to this repository. The bit rate of the tool head bus in the URTC spec (500 kbit/s) is not the 1 Mbit/s that `docs/bus_contract.json` of HYDRA-UMC gives to the downlink: the contract records the number of the spec and does not decide which one the boards use.

- **The search for servers on the local network is shared in the Dart package:** `discovery` (`discoverMdns` over the `_hydra._tcp.local` service, `scanSubnets` over the /24 networks of the device with the mobile-data and VPN interfaces left out on request, `candidatePrefixes`, `prefixesOfInterfaces`, `isMobileOrVpnInterface`). Each app hands in its own probe (the read of the identity of the server, with its TLS rules), so a match is verified the same way on both paths and nothing here knows the app's API client; a probe that throws counts as no answer. The package now depends on `multicast_dns`, which is pure Dart. `test/discovery_test.dart` has 6 tests with a fake probe and fake interfaces. The apps replace their copy with it at the next tag.

- **The CAN identifiers of the stack bus are a closed contract (`CanIds`):** `contracts/can_ids.json` holds the identifier of the emergency stop, the base and the width of the slot windows, the number of slots and every message of a slot as an offset with the one node that sends it (taken from the reference table of the firmware, 19 messages). `can-ids.schema.json` (with its copies in the Go, Rust and TypeScript clients, the manifests and the generated types), a Python validator that also checks what a schema cannot say (every identifier fits in 11 bits, an offset is inside the window and used once, the stop identifier is outside the slots), a valid and an invalid fixture and 10 tests, one of which compares the document with `tools/can_ids.py` of HYDRA-UMC when it is next to this repository. The firmware and HYDRA-UMC-TELEMETRY-COLLECTOR read this one document instead of keeping a table each.

- **The telemetry ingest has a gRPC contract (`contracts/proto/hydra_telemetry.proto`):** the service `hydra.telemetry.v1.TelemetryIngest` with `Push` (one sample) and `PushStream` (many, a bad one is counted and the stream goes on) and the messages `Sample` and `PushAck`, the same sample and rules as the HTTP ingest of HYDRA-UMC-TELEMETRY-COLLECTOR. The file is the source; the collector keeps the generated copy.

- **The TLS settings of the Flutter apps are shared in the Dart package:** `tls_settings` (HTTPS first, plain HTTP only when allowed and local, the SHA-256 fingerprint pin, the custom CA, the pinned `HttpClient`, the reading of a server certificate, the telling of a TLS failure) was an identical copy in two apps; it now lives in `hydra_umc_app_common`, and its storage goes through `TlsPrefsCore` over the `PrefsStore` seam with the keys the apps already write. 17 tests, among them a real TLS server with a self-signed certificate (refused without the pin, accepted with it, accepted as trusted CA).

- **The pose of every joint is a closed contract (`JointPoses`):** `joint-poses.schema.json` (with its copies in the Go, Rust and TypeScript clients, the manifests, the generated types, the Python validator, a valid and an invalid fixture and 8 tests) describes the answer of forward kinematics of the physics replica: `schema_version`, the `frame` the poses are written in (`base`, the root link of the model), optional `checked` and `note`, and `poses`, from the root to the tip, each with the joint name, the position in meters and the unit quaternion (w, x, y, z) within 1e-5. The schema is closed, so a consumer such as the digital twin, the path planner or the safety zones reads one shape instead of guessing one.

- **The stand-in server issues camera tickets (`POST /api/camera/ticket`):** the fake server of the conformance suite answers the route with `{ticket, expiresInSeconds: 300}` for a signed-in account (a request with no session is `401`), keeps the tickets with their account and expiry on the test clock (`tickets`, `ticket_valid`), and a ticket stops being valid when the test moves the clock past it. Before, the route fell through to the inventory, which has no body for it, so a client could not test the ticket against the shared server. 1 test.

- **A weekly workflow checks that the shared tooling of every repository still agrees:** `sync-check.yml` clones every HYDRA-UMC and URTC repository next to the SDK and runs `tools/sync_repo_tools.py --check --all` (the canonical copies of the shared tools and of the baseline action, the document policy, the README parity check and the script banners). Nothing is written; a repository whose copy drifted fails the run, which names it. It runs on Mondays and by hand.

## [0.6.1] - The F-RAM erase and self-test of the kinematic brain are in the contract: `POST /api/hardware/fram/erase` (admin role; the body is `{ "confirm": "ERASE" }`) and `POST /api/hardware/fram/selftest` (admin role) are declared in `contracts/sources/hardware.routes

- **The F-RAM erase and self-test of the kinematic brain are in the contract:** `POST /api/hardware/fram/erase` (admin role; the body is `{ "confirm": "ERASE" }`) and `POST /api/hardware/fram/selftest` (admin role) are declared in `contracts/sources/hardware.routes.json`, and `GET /api/hardware/canota/version` already carries `capabilities.fram_erase`, true only when the SPI bridge and the server both offer the operation. Both routes are off by default on the server (403 while its switch is off). The union of the sources, the route tables of the clients and the fixtures of the apps are regenerated.

- **The kinematic data of the robot models is one document of the contract:** `contracts/kinematics.json` holds the range of every joint, the home pose and, where it is known, the chain of the arm as a URDF writes it (the offset, the rotation and the axis of each joint, with the numbers it was built from; the three classic Universal Robots arms carry one), and the closed schema `Kinematics` (`kinematics.schema.json`, with valid and invalid fixtures and the generated types) describes it. The Python client validates it, and the tests check that the ranges are ordered, that every home pose is inside its range, that a chain follows its own numbers and that the copies the apps keep of the ranges are the same. The apps take it from the SDK they are pinned to once a tag carries it.

- **More tests for the Go and TypeScript server clients:** every call of each client is checked against a double of the server (the route, the token, the controller id of the session and the one of the call), every request that cannot be built is refused before anything is sent, each parser refuses a body that is not its shape, the error answers become the most specific typed error whatever the body is, a connection that is refused or a body that is cut in the middle fails the call, and the extra fields of the operation, capability and result records survive a decode and an encode without overriding a named field. The Go client goes from 81 % to 96 % of statements and the TypeScript client from 96.6 % to 97.9 % of lines; the floors that `hydra_project_tool.py coverage` compares them with go from 75 % to 95 % and from 90 % to 97 %.

- **More tests for the tool arms contract, the serial port opening and the mock server:** every refusal of the ToolArms checks is exercised one field at a time (list size, robot id, tool id range, booleans, counts, closed schema), the opening of a serial port is checked with the library replaced (the control lines are declared off before the port opens, a missing library says what to install, a USB identifier resolves to the path it has now or fails), and the mock server is run on a small OpenAPI document of its own (405 with the allowed methods, 404, the 401 of a protected operation, the entity tag, a body that is read and ignored, the command line). The Python client goes from 96 % to 97 % line coverage, and the three modules from 79 %, 86 % and 82 % to 95 %, 94 % and 100 %; the floor that `hydra_project_tool.py coverage` compares it with goes from 90 % to 95 %.

## [0.6.0] - The Live Activity of a robot on the lock screen is in the contract: `POST /api/push/live-activities` (the phone sends the token of the activity it started for a robot) and `DELETE /api/push/live-activities/{token}` answer 404 while the switch `push.liveActivit

- **The Live Activity of a robot on the lock screen is in the contract:** `POST /api/push/live-activities` (the phone sends the token of the activity it started for a robot) and `DELETE /api/push/live-activities/{token}` answer 404 while the switch `push.liveActivity.enabled` is off, which is the default; `PushStatus` carries `liveActivity` (whether it is sent, the level it may show: `status`, `progress` or `full`, with `status` the default, and how many activities are registered). The level is applied by the server before anything leaves it.

- **The reset of the arm state of one URTC tool changer is in the contract:** `POST /api/tool-arms/reset` (admin role) takes the robot, the tool and the robot id typed again as the confirmation, and answers with the robot and the tool that were reset. The reset puts back the arm state the tool changer reports and moves nothing mechanical; it is accepted only while the robot is stopped and disarmed (409 otherwise), it answers 404 while its switch is off, 502 when the tool changer service rejects it and 503 when that service is not configured or not reachable.

- **The read route of the arm state of the URTC tools is in the contract:** `GET /api/tool-arms` (any signed-in account) carries the answer of `GET /tool-arms` of the safety zones service to the panels of the screen, with the shape `ToolArmsReport`; the route answers 503 until the server is told the address of that service, and the TypeScript, Kotlin and Dart route tables and the OpenAPI document are regenerated.

- **A pull request that changes the contract or a client runs the container bench:** `integration.yml` calls the reusable workflow of HYDRA-UMC-DEV-SERVER (pinned by commit hash) that starts the swarm cell as real containers and runs its scenarios; it also runs by hand and never on a push to main.

- **The arm state of the URTC tools and the maintenance routes of the server are in the contract:** `ToolArms` is the closed schema of the answer of `GET /tool-arms` of the safety zones service (the last report of each robot and tool, with its age and whether it is stale), and `/api/admin/maintenance/status`, `/install`, `/rollback` and `/prune` are declared with the shape `MaintenanceOutcome`.

## [0.5.9] - The routes of the device tokens, of the newest published versions and the addresses of the discovery answer are in the contract: POST / GET /api/admin/device-tokens, DELETE /api/admin/device-tokens/{id} and POST... (and 1 more changes)

- **The routes of the device tokens, of the newest published versions and the addresses of the discovery answer are in the contract:** `POST` / `GET /api/admin/device-tokens`, `DELETE /api/admin/device-tokens/{id}` and `POST /api/device/login` (a token issued for one device, exchanged for a short sign-in), `GET /api/admin/updates` (the installed version of each program against its newest release) and the optional `addresses` of `GET /api/hydra-info`, each with its shapes (`DeviceTokenIssued`, `DeviceTokenView`, `DeviceTokenList`, `DeviceTokenRevoked`, `UpdateReport`, `UpdateItem`) and the generated route tables.
- **The verdict of the safety zones service and the approval of a VLA trajectory are closed contracts of the SDK:** `SafetyZonesState` is what `GET /state` answers (the signed safety state and its signature, the reason, the configuration hash, at most 20 breaches without positions and the counts) and `VlaApproval` is the answer of the confirmation of a proposal (the fingerprint of exactly one trajectory, the robot, the operator, the two times and an HMAC-SHA256 signature). Both have a closed JSON Schema, a valid and an invalid fixture, a Python validator that gives the same verdict as the schema, the generated TypeScript, Kotlin and Dart types, the registrations of the Go, Rust and TypeScript clients and a sample in the mock server.

## [0.5.8] - The HTTP client of the Flutter apps is in the shared Dart package, with injected interfaces and no plugin: HydraApiCore (headers, bearer token, controller id, If-Match, the numbering of motion commands, the error answers as... (and 1 more changes)

- **The HTTP client of the Flutter apps is in the shared Dart package, with injected interfaces and no plugin:** `HydraApiCore` (headers, bearer token, controller id, `If-Match`, the numbering of motion commands, the error answers as `HydraApiException`, and the endpoints every app calls) speaks through an `HttpTransport` that each app provides; `RenewingTransport` renews an expired session once and repeats the request; `CommandSequence` numbers the motion commands. `conformance/api-client/vectors.json` and `api_client_test.dart` check numbering, error reading and the renewal conversation; `docs/APP_API_CLIENT.md` describes the pieces.
- **The error type, the connection history, the server access options and the preferences of the Flutter apps are shared too:** `HydraError` and `HydraErrorKind` (the typed error without text; each app keeps its own wording), `ConnectionHistory` (times in milliseconds with `DateTime` views), `ServerSecurity` (the same static functions plus instance methods, and `OptionSource.defaultValue`), and `PrefsStore`, `ClientPrefsCore` and `AuthPrefsCore` (the ordinary preferences and the last server over an injected store).

## [0.5.7] - The stored session of the mobile apps has one schema, one set of rules and shared vectors: docs/SESSIONSTORE.md lists what is kept (access token, user name, refresh token, the sign-out marker, the installation marker), where,... (and 1 more changes)

- **The stored session of the mobile apps has one schema, one set of rules and shared vectors:** `docs/SESSION_STORE.md` lists what is kept (access token, user name, refresh token, the sign-out marker, the installation marker), where, and the seven rules (secure storage only, a failed save reverts what it wrote, a renewal keeps the refresh token while a sign-in replaces it, the marker is set before the delete, no invented session, move a plain legacy copy in, do not resume the session of a previous installation). `SessionStore` in `clients/dart_app_common` implements them over two seams, `SecureTokenBackend` and `SessionPlainStore`, and `conformance/session-store/vectors.json` is a list of sequences (sign in, renew, sign out, restart, failing storage) that the Dart package and the Android app both replay.

- **The server entry and the views over the settings tree are in the shared Dart package:** `ServerInfo` (one entry of the discovery list, with the TLS flag only a real probe sets) and `HydraState`, `ControllerView` and `RobotView` (thin, write-through views over the raw settings tree that keep every field they have no accessor for) moved to `clients/dart_app_common` with their tests. The iOS and the DSI app both re-export them instead of keeping a copy; the DSI app gains `RobotView.setOnline`, which the iOS app already had.

## [0.5.6] - The typed slice server.openapi.json is generated from a source of the SDK: contracts/sources/slice holds the header of the document, the closed schemas and one file of operations per tag, and python tools/contractsource.py... (and 1 more changes)

- **The typed slice `server.openapi.json` is generated from a source of the SDK:** `contracts/sources/slice` holds the header of the document, the closed schemas and one file of operations per tag, and `python tools/contract_source.py` writes the document byte-for-byte as it was when it was written by hand. `--check` fails when the document is out of date, when a route of it is not in the full inventory or when the access differs; the tests inject each drift.

- **Route tables for the clients are generated from the contract:** `python tools/generate_routes.py` writes `generated/hydra-routes.json`, `hydra-routes.ts`, `HydraRoutes.kt` and `hydra_routes.dart` (method, path, access, group, query parameters and status codes of the 111 routes), checked in the build and in CI, so a client tests the routes it calls against a table and not against a list of its own.

## [0.5.5] - The reading of a pairing link is in the shared Dart package: PairingLink, PairingOffer, PairingProblem and normalizeFingerprint (host, port, SHA-256 fingerprint and a bounded name, no repeated fields, the fingerprint required)... (and 4 more changes)

- **The reading of a pairing link is in the shared Dart package:** `PairingLink`, `PairingOffer`, `PairingProblem` and `normalizeFingerprint` (host, port, SHA-256 fingerprint and a bounded name, no repeated fields, the fingerprint required) moved to `clients/dart_app_common` with their tests, and the limits are a `PairingLimits` value that defaults to the ones of the command contract. The iOS and the DSI app both take it from there instead of keeping a copy.

- **`fault-event/1` is a contract of the SDK and not only what the parser of the server accepts:** `FaultEvent` is a closed JSON Schema in `contracts/json-schema/v1` and in the Go, Rust and TypeScript clients (`schema`, `source`, `code`, `state`, and optionally `severity`, `robot_id` and `text`), with a valid and an invalid fixture, a Python validator (`validate_fault_event`) that gives the same verdict as the schema, the generated TypeScript, Kotlin and Dart types and a sample in the mock server. An emitter checks its message against it before it publishes.

- **The evidence bundle of an incident is a contract of the SDK:** `EvidenceBundle` (versions, manifests, redacted log excerpts, reproduction steps, failed tests, impact, what was tried, the checksum of the content, the date and the local validation) is a closed JSON Schema in `contracts/json-schema/v1` and in the Go, Rust and TypeScript clients, with a valid and an invalid fixture, a Python validator, `bundle_checksum` / `seal_bundle` / `bundle_matches_checksum`, the generated types and a sample in the mock server. The shape used to live only in the development node; the checksum is the one it already reads.

- **A scenario outcome says what its fingerprint is the fingerprint of:** `ScenarioOutcome` takes an optional `fingerprint_kind`, `manifest` (the default: a state of the source) or `live-service` (the identity of a check on a running service), in the schema, the three clients' copies, the generated types and the Python validator. `compare_runs` never calls a pair with a `live-service` run fixed: it is inconclusive.

- **`tools/pin_sdk.py` pins every place that names the SDK:** besides `pyproject.toml` and `ci.yml` it now covers every other workflow of a consumer (the SITL and install-smoke ones, also when the owner is `${{ github.repository_owner }}`), a dependency installed from the release tarball, the `ref` of a Flutter `git:` dependency in `pubspec.yaml` and the `ref` / `resolved-ref` pair of `pubspec.lock` (written with the commit of the tag). Each form has a test.

## [0.5.4] - The shared Kotlin module also carries the text helper and the release gate: JsonText (optStr, a JSON null is the fallback and not the word "null") and ReleaseMetadataParser (stable tag, newer than the installed version, the... (and 1 more changes)

- **The shared Kotlin module also carries the text helper and the release gate:** `JsonText` (`optStr`, a JSON null is the fallback and not the word "null") and `ReleaseMetadataParser` (stable tag, newer than the installed version, the exact HTTPS asset, the SHA-256 digest) with the result types of the update check. The gate works on an already-read release (`ReleaseInfo`), so an app that reads the feed with another JSON library gets the same verdict; the app that reads it with `org.json` calls `parseLatestStable`. Both Android apps compile a pinned copy.

- **The stand-in server can run as a process for an app test:** `--port 0` takes a free port and the first line says which (flushed), and `HYDRA_FAKE_ANSWERS` names the copy of the answers an app carries next to its tests. A test of the repository starts it that way.

## [0.5.3] - The stand-in server answers the feeds of the sibling services: GET /api/faults (the faults a test raises), POST /api/ingest/scenario-outcome, POST /api/ingest/developer-node/status (the token of a node, not a user account) and... (and 21 more changes)

- **The stand-in server answers the feeds of the sibling services:** `GET /api/faults` (the faults a test raises), `POST /api/ingest/scenario-outcome`, `POST /api/ingest/developer-node/status` (the token of a node, not a user account) and `POST /api/trajectory/proposals/verify` (a listed key and a fixed fake signature; no cryptography), so a client of these routes is tested against a server that keeps state.

- **The update manifest can carry its signature and what it needs from the board, all optional:** `signature`, `signature_alg` (`ed25519`), `key_id`, `min_bootloader` and `target` are named in `UpdateManifest` and in its types for Go, Rust, TypeScript, Kotlin, Dart and Python, so an installer can check that a manifest comes from the owner of the image keys and refuse an artifact built for another controller or for a bootloader that is too old. A manifest without them is valid as before, and the version stays `1.0`.

- **The routes of the feeds that the services hand to the server are declared in the contract:** the scenario outcomes, the status of the developer node, the faults, the anomaly verdicts, the signed record of the voice commands and the check of a signed trajectory proposal are a source of their own, so the generated server inventory, the app fixtures and the check against the server cover them.

- **The Dart package carries the second contract, the HOME/RESET rules and the WebSocket client too:** `contract_v2` (conditional writes, the `table` command, the audit chain) with the reservations and safety limits it uses, the rules of HOME/RESET without the phrases (those need the localizations of each app), and the WebSocket client with its errors as a small type of its own and the HTTP client of the TLS choices injected, so the pure Dart tests of the connection (handshake, reconnect with back-off, the token only as a subprotocol, the 1008 close) run here too. Version 0.2.0 of the package.

- **A Kotlin module for the code the Android apps share:** `clients/kotlin_app_common` holds the stable release version the update check compares, with its test; an app compiles a pinned copy and its validator checks the copy against a lock of SHA-256 digests (and against this directory when it is at hand).

- **One stand-in server with state for every app and client:** `conformance/fake-server/hydra_fake_server.py` answers sign-in, refresh turn-over, reservations by account and controller, revisions with `If-Match`, the armed jog, safe mode and the global STOP with the stable refusal codes, and every other route of the inventory with its `full` answer; `tests/integration/test_fake_server.py` tests it.

- **The routes of the switch that requires a pass verdict of the twin are declared in the contract:** `GET` and `POST /api/hil-bridge/settings` (changed by an administrator only, with a confirmation in both directions) are a source of their own, so the generated server inventory, the app fixtures and the check against the server cover them.

- **The routes of the proposals of the node watchdog are declared in the contract:** `GET /api/ops-agent/proposals` and `POST /api/ops-agent/proposals/decide` (administrators only; approving needs a confirmation) are a source of their own, so the generated server inventory, the app fixtures and the check against the server cover them.

- **The build test of the repository compiles only on CI or when allowed:** for the stacks that compile (`rust`, `go`, `android`, `flutter`, `firmware-c`), `tools/build_test.py` asks `tools/local_build.py` first (or the same rule inline when a repository does not carry the helper) and prints `BUILD_TEST=SKIPPED` with exit status 2 on a plain PC, never a pass; `ALLOW_LOCAL_BUILD=1` allows it and a CI runner always may. The `python` and `node` stacks are not locked.

- **The routes of the settings of the semantic planner are declared in the contract:** `GET` and `POST /api/semantic-planner/settings` (the switch that relaxes the identity of the approval of a plan, changed by an administrator only, with a confirmation to relax it) are a source of their own, so the generated server inventory, the app fixtures and the check against the server cover them.

- **The route of the identity of the server in its calls to the services is in the contract:** `GET /api/admin/service-identity` (administrators) with the new named shape `ServiceIdentityStatus` (the switch, where it comes from, whether the key can sign, the state, which services take the identity and the codes of the safe order), and the app fixtures regenerated from the inventory.

- **Nothing compiles on the PC of the developer by accident:** a build that needs a C compiler, Cargo, Go, Gradle or an npm build runs only on a CI runner (`CI` or `GITHUB_ACTIONS` set) or when `ALLOW_LOCAL_BUILD=1` says so; anywhere else it says SKIPPED, never passed. The check is `tools/local_build.py`, one canonical text kept by `tools/sync_repo_tools.py` (`--check` compares the copies) (`tools/canonical/local_build.py`, carried by the core, the documentation hub, the orchestrator and this repository); the Go and Rust client tests of `tools/extra_build_steps.py` and the Go program the safety-chain scenarios build are skipped on a plain PC. Tests of the lock added.

- **The canonical secret redaction finds private-key blocks in one linear pass:** a text with thousands of private-key BEGIN markers (with or without an END marker) was quadratic to redact; the truncated and the complete block are now each found with one search for the markers, and a test with 20000 markers bounds the time. The copies in the ops agent, the local technician and the vision streamer carry the same text.

- **The routes of the decision gate of the connector hub are declared in the contract:** `GET /api/connector-hub/gate/audit`, `POST /api/connector-hub/gate/evaluate` and, new, `GET` and `POST /api/connector-hub/gate/settings` (the switch for a caller with no identity, changed by an administrator only) are a source of their own, so the generated server inventory and the check against the server cover them.

- **The identity of the server reaches twelve Python services, closes the health path with it on and refuses a doubtful expiry:** the canonical copy lists the services that carry it, `GET /health` of the canonical health route asks for the identity too when the key is on, a token whose expiry is not a finite number or that was issued in the future is refused, and `python -m <package>.server_identity probe --port PORT --key-file FILE` is the probe for a container, which signs a short-lived token of its own.

- **The signed token of the server as the identity of a caller of a service, off by default:** `tools/canonical/server_identity.py` (standard library only, vendored by `tools/sync_repo_tools.py` into the cognitive node, the vision node and the VLA engine as a first step) verifies the JWT that HYDRA-UMC-SERVER issues at login (HS256 only, signature in constant time, `exp` required, `nbf` honoured, role `admin`, `operator` or `viewer`). Without a key file nothing changes; with `--identity-key-file` (or `HYDRA_UMC_<SERVICE>_IDENTITY_KEY_FILE`) a valid token of the server is accepted next to the token of the service, a viewer may read but not change, and a request with no credential is refused even on loopback. 9 tests.

- **A Dart package for the code the two Flutter apps kept as identical copies:** `clients/dart_app_common` (`hydra_umc_app_common`, pure Dart) holds the SHA-256 of the audit chain, the result of the global STOP and the rules of the PLAY confirmation, with its own tests and a workflow that analyzes and tests it. IOS-CONTROL and DSI depend on it instead of carrying a copy each.

- **The snapshot, the change proposal and the canary result of the maintenance agent are contracts:** `NodeSnapshot` (what the edge side saw in one pass, with its incidents and the optional readings of the machine), `ChangeProposal` (the diff a person reviews, with the decision and the signature) and `CanaryDeployResult` (how far an approved change got on one node) are closed, camelCase schemas in `contracts/json-schema/v1` and in the Go, Rust and TypeScript clients, with a valid and an invalid fixture each, a Python validator (`maintenance_agent.py`) that gives the same verdict as the schema, the generated TypeScript, Kotlin and Dart types and a sample in the mock server. The development server and the local technician can validate what they load instead of copying the shape by hand.

- **The registry declares `/health` as the health route of the eight services that serve it behind a switch:** `contracts/ports.yaml` lists `/health` (was `/stats`) for ANOMALY-DETECTOR, COGNITIVE-NODE, DETECTION-HEF, DOCS-QA, SAFETY-ZONES, SEMANTIC-PLANNER, VISION-NODE and VISUAL-SERVOING-API. Those services keep the route closed (404) until their own switch opens it, so the checks that read the registry ask `/stats` after a 404 on `/health`.

- **Answers of the server generated for the apps:** `tools/make_app_fixtures.py` writes `conformance/app-fixtures/v1/server-answers.json` (a minimal and a full body for every status code that names its shape, 90 routes) from the full inventory, with `--check` and a test that every body conforms to its shape, so an app can replay the same answers against its models.

- **The catalogue of the URTC tools is part of the contract:** `contracts/urtc_tools.json` (25 tool modes and the identifier that means no tool) with a test of its structure and of its equality with the documentation copy.

- **The weights probe is vendored byte for byte into the two services that ask it:** `tools/canonical/model_weights.py` (the same text as `hydra_umc_sdk.model_weights`, compared by a test) is listed in `PER_REPOSITORY_FILES` for COGNITIVE-NODE and VLA-ENGINE, so both use one walk instead of two copies, without taking the SDK package as a dependency.

## [0.5.2] - The TypeScript server client drops the trailing slashes of its address in one pass: a base address ending in a very long run of slashes could take quadratic time with the regular expression used before; a test with a hostile... (and 5 more changes)

- **The TypeScript server client drops the trailing slashes of its address in one pass:** a base address ending in a very long run of slashes could take quadratic time with the regular expression used before; a test with a hostile address covers it.

- **The contract declares the optional asymmetric sign-in tokens:** the new group `jwks` has the public `GET /.well-known/jwks.json` (`JwksDocument`, a JWK Set of Ed25519 keys; `404` while the server signs HS256, the default) and the admin group has `GET /api/admin/jwt-keys` (`JwtKeys`) and `POST /api/admin/jwt-keys/rotate` (`JwtKeyRotated`); `PUT /api/admin/server-config` lists its new `500`.

- **The full inventory declares the global robot ids:** `GET /api/robot/{id}`, `POST /api/robot/{id}/heartbeat` and `GET /api/safety-limits` list the `409` (`robot_id_ambiguous`: more than one robot uses that id), and the new admin route `GET /api/admin/robot-ids` (`ok`, `ambiguousCount` and the `ambiguous` ids with their controllers) is declared in the `admin` source; `server.full.openapi.json` is regenerated and `python tools/contract_source.py --check` passes again. The clients keep an unknown error code as a plain `ApiError`, so none changes; the error table of `docs/SERVER_CLIENT.md` names the code.

- **The settings group declares `PUT /api/settings`:** the save of the whole configuration with a mandatory `If-Match` (the ETag of `GET /api/settings`), answering `428` without it and `412` when the settings changed since they were read; the generated full inventory follows.

- **The Go client has its own tag, `clients/go/v0.1.0`:** the module `github.com/JuanenRac/HYDRA-UMC-SDK/clients/go` can be fetched at that version (a Go module in a subfolder is tagged with the folder in front); the tags `vX.Y.Z` stay for the SDK as a whole.

- **Three more services carry the common `GET /health`:** `PER_REPOSITORY_FILES` of `tools/sync_repo_tools.py` now lists the data lake, the production reports and the development server for `tools/canonical/health_route.py`, so their copy is kept identical to the canonical one like the other eight (the first two used to answer `/health` to anybody and now close it by default).

## [0.5.1] - One canonical health route for the services, the named shapes of the operator presence routes, the kiosk unit of the Pi in the port registry and the registry of the gRPC health port

- **The presence routes answer with named shapes:** `server.shapes.json` now carries `OperatorPresence` (the state of the operator seen by the server) and `OperatorPresenceAck` (the answer to a heartbeat), and the `operator` source names them instead of declaring the answers inline, so the server and the inventory share one definition. The full inventory keeps the same routes; its answers are now references to those shapes.

- **The port registry lists the kiosk of the Pi:** `contracts/ports.yaml` now carries the unit `hydra-umc-dsi.service` of HYDRA-UMC-DSI (a service without a port, because the app does not serve HTTP), so the check of the installers finds every unit they name.

- **The uniform `GET /health` of the Python services, written once (`tools/canonical/health_route.py`):** closed by default (`404`), opened with `--health-open` or `HYDRA_UMC_<SERVICE>_HEALTH_OPEN`, answered on loopback or with the bearer token, with a body that names the service and its version and nothing else. It needs only the standard library and takes the name of the service and of the environment variable from the package it sits in, so the eight copies that the services carried are now one text; it is vendored byte for byte into those services through `PER_REPOSITORY_FILES` of `sync_repo_tools.py`, with tests against a real server.

## [0.5.0] - The full server inventory follows the server again, the error vocabulary of the MCU adapters is defined once, the port registry carries the gRPC health port and the safety chain runs end to end in simulation

- **The full server inventory follows the server again:** `contracts/openapi/v1/server.full.openapi.json` now lists `GET` and `POST /api/operator/presence` (the numbered heartbeat of the operator and its state) and `GET` and `PUT /api/telemetry/downsample-plan` (the tier plan of the data lake, with the `preview` query parameter), declared in the new `operator` source and in the `telemetry` source. An inventory source may now give the answer of a status code inline (`"schema"`) instead of naming a shape, as the server does for the presence routes. `python tools/contract_source.py --check` passes against the current server again (34 sources, 87 routes).

- **The error vocabulary of the MCU adapters, defined once (`mcu_errors.py`):** the seven codes (`INVALID_STATE`, `OUT_OF_RANGE`, `ESTOP_ACTIVE`, `TOOL_INCOMPATIBLE`, `TIMEOUT`, `UNSUPPORTED`, `GRIP_LOST_SEAL`) with their meaning and the safe action proposed for each, `is_known_mcu_error`, `describe_mcu_error` and `default_mcu_error_action`; a code outside the list is never guessed and escalates to an operator. Python only for now; the planner and the other consumers adopt it with the next release of the package. 3 tests.

- **The port registry carries the gRPC health port:** the `service` block of a manifest accepts the optional `grpc_port` and `grpc_service` (for example `hydra.common.v1.HealthService`), `tools/sync_ports.py` writes them to `contracts/ports.yaml` only for the services that declare them (the orchestrator on 50114 and the job dispatcher on 50090), and `--check` reports a gRPC port that clashes with an HTTP port or with another gRPC port, a `grpc_port` without `grpc_service` (or the reverse) and a gRPC port outside 1 to 65535. The `ProjectManifest` schema (and its copies in the Go, Rust and TypeScript clients), the generated types and the Python validator accept the two keys; a manifest without them is valid as before.

- **The safety chain, run in simulation (`tests/integration/`, started by `tools/run_safety_chain_sim.py`):** the real zone service, planner gate, operator dead-man and watchdog program run together on loopback ports that the system gives, with a stand-in for the global stop of the orchestrator and for the cell. A signed, fresh `READY` releases a plan; an unsigned, altered, old, replayed or wrongly keyed state, a missing key, a silent service and every state other than `READY` refuse with the reason; the global stop blocks dispatch with 423 and the orchestrator reports DEGRADED until an administrator releases it; a lost operator heartbeat lowers the speed and warns; the watchdog marks failing nodes UNHEALTHY, UNREACHABLE, INVALID or MISCONFIGURED, never HEALTHY, and requests no recovery unless the cell confirms the robots are stopped. The run says `passed in simulation`: nothing here ran on hardware. `docs/TESTING_STRATEGY.md` says how to start it.

## [0.4.9] - Contracts for tool descriptors and tool states with validators in four languages, an alignment with the ARMOR message formats and a shape for the signed info tickets

- **Two contracts for the tool heads of URTC:** `ToolDescriptor` (a catalogue entry: profile number, name, kind, the metric the tool is judged by, its limits, watchdog and features) and `ToolState` (one reading of a connected head: active tool, firmware, state and error counters of its CAN controller, temperatures, critical error and thermal fault) are published as closed JSON Schemas with a valid and an invalid fixture each, in the Python, Go, Rust and TypeScript clients, in the mock server and in the generated TypeScript, Kotlin and Dart types. The Python client adds `descriptor_problems` and `state_problems` for the rules that join fields, and a test reads the real tool table of URTC when it is next to the SDK. `docs/CONTRACTS.md` no longer lists `ToolDescriptor` as planned.

- **A reading of the contracts of A.R.M.O.R. in the words of this SDK:** `docs/ARMOR_ALIGNMENT.md` sets the conventions side by side (time, identity, version, closed messages) and the Python client converts them: `armor_timestamp_ms_to_utc` and `utc_to_armor_timestamp_ms`, `armor_state_to_event_envelope` (any state message of A.R.M.O.R. becomes an `EventEnvelope` that keeps the original body) and `armor_alarm_to_safety_state`, whose table is a parameter and whose default makes a sounding alarm `INHIBITED` and never `SAFE_STOP`.

- **The route that issues the signed ticket of the information routes is part of the contract:** `POST /api/info/ticket` of the server (404 until an administrator turns the option on) is declared in `contracts/sources/info.routes.json` and in the generated full OpenAPI document.

- **The HTTP helpers of the Python services, written once (`tools/canonical/http_common.py`):** the JSON body read with a limit (an oversized one is read and thrown away in small pieces, a `Content-Length` that is not a number or is negative is refused, `NaN` and the infinities are refused, a body that is not UTF-8 is a `ValueError`), the JSON answers with their length, the query string (refusing a name that occurs twice, or taking the first), the optional bearer token compared in constant time, the socket timeout value and `BoundedThreadingHTTPServer`, which answers `503` with `Retry-After` to a request beyond `max_threads` (32 by default) instead of starting one more thread. It is vendored byte for byte into the services that list it in `PER_REPOSITORY_FILES` of `sync_repo_tools.py` (VLA-ENGINE and COGNITIVE-NODE for now; the check of the script keeps the copies identical), with tests against a real server.

## [0.4.8] - A gateway to the machine bridges is declared in the contract, types generated from the closed schemas for the clients that are not Python, a registry of the bridge topics with one lint command, the /metrics of the Rust and Go services and the baseline workflow with a node-checks input

- **The gateway to the machine bridges is declared:** a new inventory source `bridges` (`GET /api/bridges`, `GET /api/bridges/{name}/state`, `POST /api/bridges/{name}/cmd/{verb}`) and the shapes `BridgeList`, `BridgeState` and `BridgeCommandAccepted` in `contracts/sources/server.shapes.json`; the full OpenAPI document is regenerated (32 sources, 82 routes). The server answers a bare `404` on all three while its gateway switch is off.

- **Types generated from the closed schemas, for the clients that are not Python:** `python tools/generate_types.py` writes `generated/hydra-contracts.ts`, `generated/HydraContracts.kt` and `generated/hydra_contracts.dart` (one type per schema, nested objects named after the parent and the field, `enum` and `const` as literal unions in TypeScript, `fromJson`/`toJson` in Dart); `--check` fails when a file is out of date and runs in the CI of the SDK. A client copies the file it needs into its own `generated/` folder and runs the same `--check` against a checkout of the SDK. The TypeScript file compiles in strict mode, the Dart file analyses clean and round-trips the valid conformance fixtures; the Kotlin file is not compiled on this host.
- **A registry of the bridge topics and one lint command:** `contracts/topics.json` declares the topic family of the bridges (direction, retained, QoS and the contract each carries) and `python tools/contract_check.py --tables` prints it as a fourth generated table next to the ports, versions and routes; the check fails on a repeated topic, a bad QoS or a contract that is not a schema. `python tools/hydra_contract_lint.py` runs the workspace check, the source check and the generated types check in one command (`--tables`, `--write-tables FILE`).

- **The `/metrics` of the Rust and Go services:** `tools/canonical/service_metrics.rs` (for `tiny_http`) and `tools/canonical/service_metrics.go` (for `net/http`) publish the same series as the Python helper (the version, the uptime, the responses by class of status and the aggregate health of the checks the service declares), with the token when one is set and `401` without it, and nothing a request carried. Both are vendored byte for byte into the services that list them, and the sync reports a copy that drifted.

- **`node-checks: none` in the baseline action:** a repository whose Node checks need steps of their own between the setup of Node.js and its validation (other repositories to clone, environment variables, a download to verify) lets the action skip the two Node steps and runs them itself after it. The default (`full`) changes nothing for the other repositories.

- **A dependency audit that reads what the repositories commit:** `tools/dependency_audit.py` lists the packages of the lock files and manifests of the three ecosystems, writes a CycloneDX 1.5 bill of materials per repository and, with `--check`, reports the OSV advisories with the version that fixes each (a Python range is judged by its lower bound; a failed request is a problem, never a clean result). 6 tests.

- **One `/metrics` for the Python services:** `tools/canonical/service_metrics.py` (vendored byte for byte, drift reported by the sync) gives a standard library HTTP handler `GET /metrics` in the text format of Prometheus with the version, the uptime, the responses by class of status and the aggregate health of the checks the service declares; nothing a request carried can reach the text. 9 tests against a real server.


- **The baseline steps of every workflow are one composite action:** `tools/canonical/hydra-baseline-action.yml` is copied by `sync_repo_tools.py` to `.github/actions/hydra-baseline/action.yml` of each repository (and reported when edited or left behind). It holds the steps the workflows repeated (Python with the pip cache, the validator, the compilation of the sources, the Python tests, the lint and type check, and the Node, Rust, Go, Flutter, Android and firmware checks), with the npm, Cargo, Gradle and Flutter caches, and the one pin of ruff and mypy; `--check` also ends with `LINT_PINS=PASS|FAIL`. It replaces the reusable workflow and its caller, which no repository used: a repository needs steps of its own after the baseline, and a reusable workflow cannot take them.

## [0.4.7] - Six new closed contracts in the four clients (the lifecycle of a robot command, visual servoing, the vision pipeline and the maintenance incident), signed bridge commands that expire and bridge health on a retained topic, both behind switches that are off

- **Commands on a bridge topic can be signed and can expire, behind a switch that is off:** `hydra_umc_sdk.signed_commands` signs a command (`sign_command`: `issued_at_ms`, `expires_in_ms` and an HMAC-SHA256 `signature` over the topic and the payload) and checks it (`verify_command`, `CommandVerifier`): an unsigned, forged, altered, expired, future-dated or too-long-lived command is refused with the reason, and a retained one is ignored before that. `JobIntake(store, verifier)` asks for the signature when the service switched it on (`HYDRA_UMC_<NAME>_SIGNED_COMMANDS=yes`, with `..._COMMAND_KEY_FILE`, `..._COMMAND_MAX_SKEW_MS` and `..._COMMAND_MAX_EXPIRES_MS`); a misspelt switch, or a switch on with no usable key, stops the start of the service instead of leaving the bridge open, and with the switch off nothing changes and no key is read. 33 tests (with the two items below).

- **The bridges can publish their health on one retained topic, behind a switch that is off:** `hydra_umc_sdk.bridge_health` (`BridgeHealth`, `health_topic`, `health_report`, `read_health`) publishes `hydra/bridges/<name>/health` in the shape of `HealthReport` (retained, QoS 1): `READY` with the check `link` when the connection is accepted, the other states with their checks, and `FAULT` as the Last Will. `open_bridge_client(..., health=BridgeHealth(name))` puts the will there and clears the retained `availability` message of an earlier run, since a connection has one Last Will; with `HYDRA_UMC_<NAME>_BRIDGE_HEALTH` off the client behaves exactly as before.

- **One reading of a `cmd/job` message for every bridge:** `read_job_message` does the first half of the handler that the bridges each wrote for themselves (retained ignored, size limit, JSON, intake, the stored answer to a repeat or the refusal for one in doubt) and never raises; the bridge only decides about the job. The bridges adopt it when they pin the tag that carries it.

- **The lifecycle of a robot command is a contract:** `CommandLifecycleEvent` is the event a server publishes for every step of a command after it has accepted it (`ACCEPTED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`), keyed by the `operation_id` of the `Operation` that carries the command and growing by `sequence`; `FAILED` and `CANCELLED` must say why. `command_state_from_operation` derives the state from an `Operation` without a second state machine (`sent` is `RUNNING`; `terminated` is `COMPLETED` only when its result passes `concludes_success`, otherwise `FAILED` with the reason of the gate) and `validate_state_transition` says which step may follow which. The route of the server keeps answering as it does until the server adopts the events.

- **Visual servoing has its schemas:** `VisualTargetRequest` (both poses in meters and radians with exactly `x`, `y`, `z`, `roll`, `pitch`, `yaw`, the frame, the confidence, the safety state and the age of the estimate, given as `data_age_ms` or as `captured_at_utc`) and `VelocityCommand` (the velocities in m/s and rad/s, `hold`, when it was issued, how long it is valid and its `seq`). `command_is_current` says whether a consumer may still act on a command; a command issued in the future is not current. Both ends validate with the same rules.

- **The vision pipeline has a data contract:** `FrameMeta` (the frame a camera produced) and `DetectionFrame` (the detections a model found in it, tied by `frame_id` and `capture_ts_utc`) carry the convention in the data: `box_unit` is `pixel` or `normalized`, the origin is the top left corner and a box is given by `x_min`, `y_min`, `x_max`, `y_max`. A normalized box outside 0 to 1 is refused by the schema itself, the clients also refuse a box that ends before it starts, and `model` is the compatibility record of the vision node. `box_to_pixels` converts any box to pixels.

- **The maintenance incident has a schema:** `MaintenanceIncident` is the closed, camelCase form that the maintenance agent writes, so the development server and the local technician stop keeping their own copies (one of them had drifted to `incident_id`). `redactionLevel` is `sanitized` or `raw`, and `incident_may_be_stored` refuses `raw` unless the consumer allows it.

- **The six contracts are everywhere the others are:** the schemas are vendored and registered in the Go, Rust and TypeScript clients with the manifest of hashes regenerated in the four places, each has a valid and an invalid conformance fixture and an example in the mock server (now 24), and the schema/validator differential tests (fixed cases and the damage of every field of each fixture) cover them. The small checks that closed contracts repeat live in one module (`contract_rules.py`).

- **The Go client is importable from another repository, and a test keeps it so:** `clients/go/module_test.go` checks that `go.mod` names the module path of the subdirectory, asks for no more than Go 1.22 and carries no `toolchain`, `replace`, `exclude` or `retract` directive; the README of the client says how to add it (`go get github.com/JuanenRac/HYDRA-UMC-SDK/clients/go@clients/go/vX.Y.Z`; a module in a subdirectory resolves only from a tag of that form).

## [0.4.6] - The push notification routes and shapes are declared in the contract, the header and banner of the launcher scripts are generated from one file, one version bumper serves the HYDRA-UMC and URTC families and a cross-family check compares the sources the families share

- **The header and the banner of the launcher scripts are generated from one file:** `tools/sync_script_banners.py` writes them from `tools/canonical/script_banners.json` (the licence line that still said GPL-3.0 in some repositories is now GPL-3.0-or-later; the four launchers of the eight bridges are one script apart from the name, with the box of `build-test` lined up). `sync_repo_tools.py --all` runs it in check mode.
- **One version bumper for the HYDRA-UMC and URTC families:** `tools/canonical/bump_manifest_version.py` finds the manifest of the family by its name (`hydra-umc.project.json` or `urtc.project.json`) and prints the family in its messages; the behaviour for HYDRA-UMC repositories is the same.

- **The push notification routes are declared:** a new inventory source `push` (`POST /api/push/devices`, `DELETE /api/push/devices/{token}`, `GET /api/admin/push`) and the shapes `PushDeviceRegistered`, `PushDeviceRemoved` and `PushStatus`, so the phone apps can register their device token for the push notifications of the server. `PushStatus` tells an administrator whether the credentials of the push service are usable and why not, never the credentials or the tokens.
- **`sync_repo_tools.py --check` compares the sources the families share:** when URTC-DEVTOOLS is next to this repository, the files that its registry (`tools/tooling_registry.json`) lists as the same text in several families (the live panel, the README layout check, the picture code) are compared across the sources of the families and the report ends with `CROSS_FAMILY=PASS` or `CROSS_FAMILY=FAIL`; without the registry the comparison is skipped. Read only: nothing is written to another repository and no repository needs the new version.

## [0.4.5] - The whole route inventory of the server is declared in the SDK, one copy of the global stop guard for every bridge, the hardening of the bridge transport set from the environment and the typed document at version 1.5.0

- **The whole route inventory of the server is declared in the SDK and the full document is generated from it:** 29 inventory sources (`contracts/sources/<group>.routes.json`, `"kind": "inventory"`, 74 routes) next to the connections pilot, and `contracts/sources/server.shapes.json` with the 40 shapes of the answers, the title of the document and its security scheme. `python tools/contract_source.py` generates `contracts/openapi/v1/server.full.openapi.json` as the union of the sources (alphabetical, key order of the server); `--check` fails when the file is out of date, when a route of the server is declared by no source, when a route differs from the server (method, access, status codes, query parameters, now also for the inventory) and when a shape of the server inventory differs from the one of the SDK. The two connection routes in that document now carry the typed query parameters of the pilot; every other operation is unchanged. 19 new tests (`tests/test_contract_inventory.py`) hold the union, the order, the security of public routes, the shapes and every kind of drift.
- **One copy of the global stop guard for every bridge:** `hydra_umc_sdk.global_stop` (`GlobalStopGuard`, `GlobalStopSettings`, `settings_from_environment`, `follow_on_connect`, `process_wide_guard`) is the module the CNC, laser, OpenPnP, 3D-printer, ROS 2 and AMR bridges each carried an identical copy of. Off by default, SAFE_STOP refuses what moves, only a clear READY ends it, anything unreadable fails closed, an abort and the withdrawal of a line are always let through. 30 tests; the bridges drop their copies once they pin the tag that carries this.
- **The hardening of the bridge transport can be set from the environment of the service:** `BridgeHardening` and `hardening_from_environment(name)` read `HYDRA_UMC_<NAME>_HARDENED` (a plain yes switches it on; off by default and then nothing changes) and tune `_MAX_QUEUE`, `_MAX_PAYLOAD_BYTES`, `_CONNECT_BACKOFF_FACTOR`, `_CONNECT_MAX_DELAY_SECONDS` and `_CONNECT_JITTER`; a wrong value raises `ValueError` naming the variable (a misspelt limit is not taken for no limit), and `dispatcher_kwargs()` and `connect_kwargs()` hand the limits to `MessageDispatcher` and `open_bridge_client`. 36 tests.

## [0.4.4] - The contract carries the setting of the remaining-useful-life relay and the route inventory and the typed slice agree on the health route and on numeric ids

- **The contract carries the setting of the remaining-useful-life relay:** `GET /api/rul/config` (any signed-in account, read only) is in the full copy of the inventory and in the typed slice, with the closed `RulConfig` answer `{enabled, maxPoints, timeoutMs}`: whether the relay of the estimate is open to operators and how large a request it accepts, closed with the default limits when the configuration is missing or unreadable. New `test_openapi_rul_config.py`.
- **The route inventory and the typed slice agree on the health route and on numeric ids:** `contracts/openapi/v1/server.full.openapi.json` is refreshed from the inventory of the server, which now lists the bare `404` that `GET /api/ecosystem/health` answers while its option is off (and the `403` for a viewer) and types the `{id}` of the robot and camera routes as an integer; `server.openapi.json` lists the same `403` and `404` on that route. New cases in `test_openapi_ecosystem_routes.py`.

## [0.4.3] - The contracts of the routes added to the server (ecosystem health, liveness, connections, heartbeat, release of the global stop), a hardened message dispatcher, the contract source pilot and the shared CI and community templates

- **The contract carries the routes that the server added after the connection pilot, with typed clients:** `contracts/openapi/v1/server.full.openapi.json` is refreshed from the server's inventory (it now lists `GET /api/ecosystem/health`, `GET /api/robots/liveness`, `POST /api/robot/{id}/heartbeat`, `POST /api/stop-all/release`, `GET /api/connections/clients`, `GET /api/connections/events` and the public `GET /health`, and the fields the server added to `StopAllResult` and `VoiceReply`), and the typed slice (document version 1.4.0) describes the first four with their answers. Two new closed JSON Schema v1 contracts, `EcosystemHealth` (the services of the ecosystem with their state, reason code and version drift, the state of the server certificate and the warnings; the port, health path, unit and active state only for administrators) and `RobotLiveness` (live, stale or unknown for every robot, with the age and the source of the last news), are validated by the Python client (`validate_ecosystem_health`, `validate_robot_liveness`) and vendored and registered in the Go, Rust and TypeScript clients, with a manifest of hashes regenerated in the four places, a valid and an invalid conformance fixture each, mock server examples and differential tests between the schemas and the Python validator (fixed cases plus the automatic mutation of every field). The SDK now has 18 contracts and the mock server serves 18. `docs/CONTRACTS.md` and `docs/PYTHON_CLIENT.md` describe them. The Studio and the Suite drop their "not yet in the contract" exemptions after they repin to the version that carries this (see `docs/CONTRACT_SOURCE.md`).

- **The bridge transport can be hardened, every limit off by default:** `MessageDispatcher(..., max_queue=N, max_payload_bytes=N)` bounds the commands waiting behind the running one (when it is full the OLDEST waiting command is dropped and counted) and refuses a payload over the cap before it is queued (logged and counted); the stop lane is never bounded and stop verbs are exempt from the cap. `MessageDispatcher.stats()` returns the `dropped`, `oversized` and `queued` counters. `connect_with_retry` takes `backoff_factor`, `max_delay_seconds`, `jitter` and an injectable `rng` for an exponential wait with jitter between the retries of the first connect, and `open_bridge_client` passes them on as `connect_backoff_factor`, `connect_max_delay_seconds` and `connect_jitter` and takes `reconnect_min_delay_seconds` / `reconnect_max_delay_seconds` (1 and 30, as before) for paho's reconnect delay. With nothing set the behaviour is exactly the old one (no limits, a fixed wait); tests cover a flooded queue with a slow client, a giant payload, a broker that stays down and an injected random source.

- **The SDK is the source of a group of server routes (pilot: the connection routes):** `contracts/sources/connections.routes.json` declares `GET /api/connections/clients` and `GET /api/connections/events` (access, status codes, query parameters with their enums and patterns) on top of the closed `ConnectionClient` and `ConnectionEvent` schemas, and `python tools/contract_source.py` generates `contracts/openapi/v1/server.connections.openapi.json` from it. `python tools/contract_source.py --check` fails when the generated document is out of date, when a vendored copy of the schemas or its hash manifest differs, when the server's route inventory or the enums in its sources drift from the source, or when a client mentions an undeclared connection route or query parameter. Characterization tests pin the routes the server offers today and inject each kind of drift; the check runs in the CI and in the local build test. `docs/CONTRACT_SOURCE.md` is the design for moving the rest of the contract the same way, in phases, without breaking the repositories pinned to a tag. The other contract documents are unchanged.

- **The version-tool sync leaves a bump script alone when it already hands over to the shared utility:** a repository whose own `bump_version.py` loads `bump_manifest_version.py` itself is no longer reported as out of date by `tools/sync_version_tools.py --check`, and the sync no longer adds a second delegation to it.

## [0.4.2] - A reusable CI workflow, canonical issue forms, the QoS of an MQTT publish and the ProductionEvent, ConnectionEvent and ConnectionClient contracts

- **A reusable CI workflow:** `.github/workflows/reusable-ci.yml` is the CI baseline as a `workflow_call` workflow (Python, Node, Rust, Go, Flutter, Android and firmware steps, each switched on by the files the repository has, builds that never bump a version) and it validates through `python tools/hydra_project_tool.py validate`, the command a developer runs locally. `tools/canonical/ci-caller.yml` is the short `ci.yml` a repository would carry to call it; the repositories adopt it once the SDK carries a tag to pin.

- **The issue forms and the pull request template are canonical:** the five issue forms and the pull request template are the same text in every repository, so `tools/sync_repo_tools.py` now keeps them identical (`tools/canonical/community/`) and `--check` reports a copy that drifts, such as the licence line of the 17 repositories that still said `GPL-3.0`.

- **`contains_model_artifact`:** one probe of "does this models directory hold a real weight file" for the services that each had their own copy (a non-empty regular file with an accepted suffix, symbolic links never followed, a bound on the files inspected, a filesystem error counts as not present), with the suffix lists `ANY_WEIGHT_SUFFIXES` and `COMPILED_MODEL_SUFFIXES`.

- **`MqttPublish` carries its QoS:** `MqttPublish(topic, payload, retain=False, qos=0)` takes 0, 1 or 2 (anything else, a boolean included, is refused), compares and hashes by it, and the shared dispatcher publishes each answer with it, so a bridge can ask for QoS 1 on its state and results. A publish without the field still goes out at QoS 0.

- **The `ProductionEvent` contract:** one finished production cycle of one machine or robot (who, when it ended, how long it took in seconds and whether the part was good, plus an optional job and reject reason). It is what the production reports turn into OEE, and it is closed, so nothing else can slip in. The Python client validates it (`validate_production_event`) and gives the two numbers in the form the data lake stores them (`production_event_fields`: `good` as 1.0 or 0.0 and `cycleTimeS`); the schema is vendored and registered in the Go, Rust and TypeScript clients, the mock server serves an example and the conformance fixtures and the differential tests of the four copies cover it.

- **The `ConnectionEvent` and `ConnectionClient` contracts:** the common model of the history of the clients that connect to a server (first seen, signed in, refused, wrong second factor, signed out, session ended or expired) and of the list of the clients it has seen (kind, last seen, open sessions, sign-ins that worked or were refused). Both are closed, so a password, a token or a cookie cannot slip into them; the address and the user agent are for administrators only. The Python client validates them (`validate_connection_event`, `validate_connection_client`), the schemas are vendored and registered in the Go, Rust and TypeScript clients, the mock server serves an example of each and the conformance fixtures cover them.

- **`tools/contract_check.py --tables`:** prints the ports, the versions and the routes of the ecosystem as Markdown tables generated from the port registry, the manifests and the OpenAPI documents, so those tables are no longer written by hand. The topics of the bridges are still not generated.

- **The project manifest accepts `depends_on`:** an optional list of the repositories that must be installed or updated before this one, so a batch of the updater can order itself by what each repository declares. The names follow the rule of `name`, are unique and never include the repository itself (the clients check that, a schema cannot). A compatible extension: a manifest without it stays valid. The schema is vendored in the Go, Rust and TypeScript clients and the differential tests cover it.

## [0.4.1] - The RobotState, TwinState and Pose contracts, the enable and disable commands of a robot, the STOPPED machine state, versions each toolchain accepts, the ecosystem release table and a boundary check that works without Git

- **The `RobotState` contract:** `robot-state.schema.json` describes what one robot reports about itself in the form in which nodes replicate it: its id, its state (`idle`, `busy`, `estop`, `fault`, `offline`), when that was true, and optionally the mission, the battery and its `Pose`. The Python client validates it (`validate_robot_state`), the schema is vendored and registered in the Go, Rust and TypeScript clients, the mock server serves an example and the conformance fixtures cover it.
- **The `TwinState` contract:** `twin-state.schema.json` describes the state a digital twin exchanges: the joint states (name, position, velocity, effort), the named poses (each one a `Pose`), the instant, the frame and, required and with two values only, whether the state is of the real robot or of a simulation (`source`). The Python client validates it (`validate_twin_state`, the unit length of every quaternion included), the schema is vendored and registered in the Go, Rust and TypeScript clients, the mock server serves an example and the conformance fixtures cover it.
- **The `Pose` contract (position and a unit quaternion):** `pose.schema.json` describes a pose as a position in meters and an orientation as a quaternion `(w, x, y, z)` in a declared frame (`base` or `tool`); the earlier roll, pitch and yaw (`euler`) is deprecated and only accepted next to the quaternion. The Python client has `Quaternion` (Hamilton product, shortest-turn rotation vector, Euler conversion with the gimbal lock handled) and `Pose`, the schema is vendored and registered in the Go, Rust and TypeScript clients, and the conformance fixtures cover it. The unit length of the quaternion is checked by the clients, a schema cannot express it.
- **`tools/ecosystem_release.py` and `ecosystem-release.json`:** one file, written by the SDK for each release of the family and published in the documentation repository, that lists the version and the commit of every repository. The shared validator checks the entry of the repository it runs in (the listed version is not ahead of the manifest and the commit is in the history) whenever the documentation checkout is at hand.
- **The version utility writes npm versions with three components:** `package.json` and `package-lock.json` receive `a.b.c` (npm only accepts semver), as Cargo and Flutter already receive their own form; a `package.json` that still holds four components is accepted until the next bump rewrites it.
- **The public/private boundary check works without Git:** in a checkout that is not a Git working tree, or without Git installed, `_doc_policy.py` reads the text files itself and applies the same three rules, so `ci_validate.py` also runs on a source archive.
- **The `enable` and `disable` commands of a robot (safe mode):** the typed OpenAPI describes `CommandDisable` and `CommandEnable`, the `423` (`robot-disabled`) that every other command of a disabled robot gets, and the refusals of `enable` (`enable-not-allowed`, `admin-required`). The clients send them with the generic command request.
- **`MachineState.STOPPED`:** the state of a machine that is stopped and does not go on until an operator resets it (the MTConnect `STOPPED`). It is not `IDLE`, so no job is allowed on it, and it is not `HOLDING`, so it cannot be resumed.
- **The version utility writes what each toolchain accepts:** a `Cargo.toml` version (and the package entry of `Cargo.lock`) is written as `a.b.c` or `a.b.c+d` (semver build metadata), and a Flutter `pubspec.yaml` keeps `a.b.c+N`, with `N` raised by one on every bump and `lib/app_version.dart` regenerated from it. The translation is fixed and the manifest and this changelog keep their own form.
- **`hydra_project_tool.py bump` and `doctor` refuse a native version its toolchain would reject** (Cargo or Flutter) with a clear message instead of leaving a broken build; a Flutter app is bumped by the shared utility, not by a Dart script.

## [0.4.0] - Types for operations and capabilities in every client, a doctor command, a mock from the OpenAPI, a contract check and the two-step sign-in contract

- **The sign-in of the contract carries the second step:** the typed OpenAPI describes the optional 	otp field of POST /api/login and the 	otpRequired flag of the refusal an account with the second step on gets, and the full copy of the server's OpenAPI is refreshed (it lacked the second-step and voice-confirmation routes).
- **The mock server answers the routes of an OpenAPI document:** `python -m hydra_umc_sdk.mock_server --openapi contracts/openapi/v1/server.openapi.json` serves every path and method of the document at its real path, with the first success status, a body built from the schema and the declared headers; an operation that needs a bearer token answers 401 without one, a method the path does not declare answers 405 and an unknown path 404. Tests prove that every operation of every published OpenAPI document is served with a declared status and a body that conforms to its schema.
- **`tools/contract_check.py`:** a read-only report, in JSON, of the contracts of a whole workspace (manifest against the validator, manifest name against the folder, vendored shared tools against the canonical copies, `service` blocks against the port registry and the structural check of the OpenAPI documents); it exits with 1 when anything was found.
- **Typed `Operation`, `Capability` and `ScenarioOutcome` in the Go, Rust and TypeScript clients:** the three contracts that were handled as loose maps now have their own types (with the enums of status, origin, outcome, phase and check result), keep the fields they do not name, and go through the same shared conformance fixtures as the other contracts.
- **The manifest `deployment_target` values `dev-server` and `mcu` exist in the Go, Rust and TypeScript types,** as the schema already allowed; a test now fails when a type file lacks a value of the schema enums.
- **`hydra_project_tool.py doctor`:** a read-only check of one repository (manifest, README layout, At a glance, CHANGELOG note, shared tools and SDK pin) that prints the fix for every problem; `sync_repo_tools.py` gains `drift_of_repository()` for it.
- **`hydra_project_tool.py coverage`:** measures the tests of the Python, Go and Node clients against `tools/coverage_floor.json` and warns below the floor; it is not part of the CI yet.

## [0.3.9] - The shared validator checks the notes, the glance and the changelog, and the serial link reconnects

- **The shared validator checks three more things:** a hand-written test count in the manifest `notes` fails (the README holds the counts and they are checked against the code), the CHANGELOG must have a note under the heading of the manifest version (and, on a tag build, the tag must name that version), and the "At a glance" / "Project status" sections are checked with `make_glance.py --check --repo <name>` when the documentation repository is checked out next to the repository. The canonical validator also carries the README layout check that every repository already ran.
- The reconnecting serial link (`ReconnectingSerialConnection`) also reopens the device when discarding the input buffer fails, so a status query after the cable was pulled out reconnects instead of failing.
- **README in the universal layout:** the README and its seven translations follow the layout that the four families share (22 sections in a fixed order), with an architecture picture and a repository-structure picture drawn from `docs/architecture.json` and `docs/structure.json`; the CI validator checks both pictures and the file tree.

## [0.3.8] - The shared bridge answers keep their QoS, and the manifest accepts mcu

- **The project manifest accepts `mcu` as a deployment target:** the firmware that runs on a microcontroller (an STM32 board) can say so instead of using the nearest value. It is a compatible extension: no existing value changed meaning. The schema of every client and the validation of the Python client know it.
- **The layout of the README is checked in the CI:** the validator runs `tools/universal_readme_check.py` and lists, as a warning, what differs from the universal layout of the README.
- **The shared tools sync also carries `tools/universal_readme_check.py`** (one canonical copy in `tools/canonical/`), so every repository has the same README check.
- The shared bridge dispatcher publishes an answer with the QoS the bridge gave it (an answer without one stays at QoS 0), so a bridge can ask for QoS 1 on its results.

## [0.3.7]

### Changed

- Automated build version increment from 0.3.6.

All notable changes to this project are documented here.

## [0.3.7] - A shared phase coordinator and a shared GRBL serial link

- **A shared phase coordinator** (`hydra_umc_sdk.phase_coordinator`): the mapping of a job phase onto a named action, the parameter checks, the fail-closed gate, the actions that are always forwarded to reach a safe state, and the static action vocabulary, once, for the UAV, AMR and droid bridges. The gate is unchanged. Tests in `test_phase_coordinator.py`.
- **A shared GRBL serial link** (`hydra_umc_sdk.serial_link`): `SerialLike`, the lazy pyserial open without a reset, lookup of a device by a stable id, the reconnecting connection, the status query that returns the answer to its own `?`, the parser of a status report and the real-time byte writer that tells a short or untrusted write from a sent one, moved out of the CNC bridge so that the laser bridge reads GRBL with the same code. Tests in `test_serial_link.py`.
- **The README version check reads the French and Japanese status lines**: the labels `Statut :` / `Statut:` and `状態:` / `状態：` were missing, so a `README_fra.md` or `README_jpn.md` with an old version number passed. The shared validator has them now (with a test), and the two repositories that were caught had their French and Japanese lines corrected.
- The port registry (`contracts/ports.yaml`) now carries a health route for every service that speaks HTTP (22 of 24: the status route `/stats` where a service has no `/health`, the page of the dashboard for the dashboard; only the MQTT broker and the OPC-UA server have none on their port), and `sync_repo_tools.py` keeps a copy of it in `HYDRA-UMC-OS/provisioning/ports.yaml`, where the installers and the runtime check read it.
- **One build test and one validator for every repository, with a place for what a repository has of its own.** `tools/canonical/build_test.py` joins `tools/canonical/ci_validate.py`: `sync_repo_tools.py` now adopts both by the same rule (a copy that holds nothing of its own is rewritten, a text kept in `tools/canonical/previous/` counts as an older canonical copy, not as an adaptation). The validator runs `check(root)` of `tools/extra_checks.py` as its last step and the build test runs `tools/extra_build_steps.py` after the stack, when the repository has them. The bridges, the URDF editor and STUDIO no longer carry a copy of their own; the tests, verifiers and extra toolchains of the SDK, the OS, the watch, the vision streamer, the suite and the bridges moved to `tools/extra_build_steps.py`. The validator also accepts the bump script of the bridges (`tools/bump_version.py`) and the install/development headings the URDF editor used. Only `HYDRA-UMC` (firmware) keeps its own build test. Tests for the hooks, the previous text and the build test rule.
- The port registry now carries the health path of the orchestrator, the swarm sync and the VLA engine, whose manifests declare it.
- **Clients for blocks 2 to 5 of the second server contract, in Python, TypeScript, Go and Rust.** `GET /api/robot/{id}` with its revision, `If-Match` on `command`, `claim` and `release` (the `412` is a `RevisionMismatchError` that carries the current revision), the atomic `table` command with its refusals (`TableMoveError`), `GET /api/audit` and the `claims` message of the WebSocket; `claim`, `release` and `command` answers carry the new `revision` and the claims carry `jogArmedUntil`. Purely additive.
- **Shared conformance cases for them**: `conformance/server-routes/cases_v2.json`, replayed by the four clients (requests with their headers, invalid requests, errors, responses).
- **OpenAPI 1.3.0** of the typed slice (the new routes, `IfMatchHeader`, `RevisionConflict`, `CommandTable`, `AuditView`, `ClaimsEvent` and the new stable codes) and a new copy of the server's generated openapi.
- The service-port registry can be consumed: the server completes its ecosystem status from it and the node watchdog builds its node registry from it; `sync_repo_tools.py` also keeps the shared secret redaction in HYDRA-UMC-VISION-STREAMER.
- **One validator for the repositories.** `tools/canonical/ci_validate.py` is the shared validator and `sync_repo_tools.py` gives it to every repository whose own copy holds nothing of its own (the project, the documentation project and this one were behind); the repositories with checks of their own are listed as adaptations. `HYDRA-UMC/tools/hydra_project_tool.py` is the canonical copy again.
- **One secret redaction.** `tools/canonical/redaction.py` (the stricter of the two copies that existed) and the shared cases `contracts/redaction/vectors.json` (text, JSON and multi-line cases); `sync_repo_tools.py` vendors both into the ops agent and the local technician and fails on drift.
- **Port registry.** `contracts/ports.yaml`, generated by the new `tools/sync_ports.py`, with a `--check` that catches a stale registry, a shared port, a manifest and a unit that disagree, a missing unit file and an installer that names an unknown unit.
- **Clients for the server's claim, release, jog-arm, claims and safety-limit routes, in Python, TypeScript, Go and Rust.** `POST /api/robot/{id}/claim`, `.../release`, `.../jog-arm`, `GET /api/claims`, `GET /api/safety-limits` and `PUT /api/admin/safety-limits`, plus the optional `controllerId` (body field or `X-Controller-Id` header) of `command`. Each language has request builders and response parsers that never touch the network (Python also exports them as `hydra_umc_sdk.server_api`), and Python, TypeScript and Go add a thin client over an injectable transport with a default controller id; the Rust module builds and reads only. A request without a controller id is the v1 request, unknown response fields are ignored.
- **Typed errors.** `409` `other-account` and `other-controller` (`ClaimConflictError`, with the blocking reservation), `controller-id-required` (`ControllerIdRequiredError`, also a claim conflict; `409` or `400`), `invalid-controller-id`, `403` `jog-not-armed` (`JogNotArmedError`); a `409` with a reservation and no code from an older server is still a claim conflict, and an unknown code stays a plain `ApiError` with the code kept. The controller id is checked (1 to 64 characters of letters, digits and `. _ : -`) before anything is sent.
- **Shared conformance cases.** `conformance/server-routes/cases.json` is replayed by the four clients, so they build the same requests and tell the same errors apart; the Python tests also check each route against both OpenAPI documents and the controller-id pattern against the schema.
- **OpenAPI.** `server.openapi.json` (now 1.2.0) describes the seven routes, the `X-Controller-Id` parameter, the `Reservation`, claim, arming and safety-limit schemas, the `code` of error answers, and `403` and the three conflict codes on `command`. New `server.full.openapi.json` is a copy of the openapi the server generates from its routes; the typed slice never invents a route it lacks.
- New `docs/SERVER_CLIENT.md`, a note in `CONTRACTS.md` and `CONFORMANCE.md`, and a line in the eight READMEs.
- Building no longer changes the version; raising it is the explicit `bump` command (`python tools/hydra_project_tool.py bump`). The build scripts only report the version they built, and CI fails if a build script runs a bump.

## [0.3.6] - The bridge gate fails closed, and the bridges share one MQTT transport

- The banner follows the animated style of the ecosystem banners, with the name, the kind and the technologies of the project.
- **The bridge gate fails closed.** `evaluate_job` refuses a productive job when the bridge did not pass the state it read from its machine (`observed_machine_state`): the `machine_state` of a job is a claim in a message anybody on the broker may publish, so it no longer lets a job through on its own. `allow_unobserved=True` is the explicit, temporary opt-in of a bridge that cannot observe its machine yet; abort is always forwarded.
- **Python package metadata.** `py.typed` ships with the package, `pyproject.toml` declares the licence with the SPDX expression, keywords, classifiers and project URLs, and the package root now exports `job_to_dict`, `job_from_dict`, `decision_to_dict` and the MQTT connection helpers.
- **`BoundedLog` keeps its entries in a `collections.deque`,** so dropping the oldest entry no longer costs a list shift; the drop counter behaves as before.
- **`tools/verify_openapi.py` also checks** that every `operationId` is unique and that every 2xx response with content declares a schema, and it decodes the `~0` and `~1` escapes of JSON Pointers; `test_verify_openapi.py` damages a document in each of those ways.
- **`tools/build_test.py` runs the Go, TypeScript and Rust client tests** when the toolchain is installed and says so when it is skipped.
- **`hydra_umc_sdk.bridge_transport`.** The MQTT transport that the CNC, laser, OpenPnP, 3D-printer and ROS 2 bridges each carried their own copy of: `MqttPublish`, `connect_with_retry` (retries a refused connection, never a TLS failure), `MessageDispatcher` (commands in order on one lane, stop verbs on a second lane, a retained replay never taken as a request) and `open_bridge_client` (credentials and TLS from the environment, Last Will on `availability`, subscribe and announce after every connect). Eighteen tests; a mutation of the stop lane and of the retained check each make a test fail. The five bridges were migrated locally against it and their existing tests pass unchanged; they move to it once a release carries this module.
- **`contracts/trust/release_key.pub`.** The public key that signs the component packages of the CM5 (the private key is never in a repository).

## [0.3.5] - One place for the shared tooling of the repositories

- **`tools/sync_repo_tools.py`.** Keeps the files every repository must carry identical: `bump_manifest_version.py`, `tools/hydra_project_tool.py` and `.github/workflows/dashboard-dispatch.yml` have ONE canonical copy in `tools/canonical/`; `--check` fails when a repository differs, a plain run rewrites them. `tools/ci_validate.py`, `tools/build_test.py` and `.github/workflows/ci.yml` legitimately differ by technology, so they are only grouped into families (the fingerprint ignores line endings, the licence line and the repository name in the banner) and printed, which makes a stray one-off copy visible. `--all` runs the three older sync scripts in the same mode.
- **`tools/canonical/hydra_project_tool.py`.** The same commands in every repository: `validate` (the CI baseline), `test` (the build and tests), `ci` (both), `version`, `status` (clean tree, version not older than the last tag) and `bump`. The checks run with `HYDRA_UMC_CI=1` and fail if the manifest version changed while they ran; `bump` is the only command that changes the version, refuses a dirty tree unless told otherwise, and follows the repository's own bump script when it has one.
- **`tools/pin_sdk.py`.** Moves every reference to this SDK (the dependency line of `pyproject.toml` and the `ref:` of the contract checkout in `ci.yml`) from a branch, a commit or an older tag to the newest release tag; `--check` lists what is not on it. All twenty references in the family are on `v0.3.4`.
- The canonical `bump_manifest_version.py` carries the `GPL-3.0-or-later` notice like the repositories that hold it; sixteen test cases cover the three tools against throwaway repositories (`test_repo_tools.py`, `test_project_tool.py`), and the README `tools/` row says what they do in the eight languages.

## [0.3.4] - The Python validator refuses malformed values instead of crashing

- A list or an object where an enumerated value belongs (`status`, `phase`, `observed.outcome`, `state`, `ecosystem`, `role`, `deployment_target`, `maturity`, `result.origin`, `result.outcome`, `last_check_outcome`) made the Python validator raise `TypeError` instead of `ContractValidationError`, so a service that catches the contract error crashed on a hostile payload. Every enumerated field now goes through one check that accepts only a string from the allowed set.
- The Python validator now checks three optional text fields that the schemas already required to be strings: `Operation.status_reason`, `Capability.checked_configuration` and `ScenarioOutcome.observed.evidence`. The Go, TypeScript and Rust clients, which validate with the schemas, already refused them.
- New `test_schema_mutation_differential.py` damages every field of every valid conformance fixture (removed, wrong type, empty, out of range, extra field) and requires the Python validator and the JSON Schema to give the same verdict; a second set of tests checks that no malformed payload raises anything but `ContractValidationError`. New `test_promotion_journal_failures.py` covers a failed atomic write, an unmovable corrupt journal and the health-check error paths.

## [0.3.3] - HYDRA-UMC-DOCS in the related projects

- The Related Projects section of the README, in the eight languages, lists HYDRA-UMC-DOCS: the repository that holds the architecture, the interfaces, the security baseline, the capability matrix and the project catalogue generated from every manifest.

## [0.3.2] - Safer recovery and evidence gates, schemas that match the validator, and a current OpenAPI slice

- **Promotion journal.** `recover()` now looks at the disk for a promotion recorded as `STARTED`: when the live directory had already been set aside it is restored (a crash between the rename and `advance()` no longer loses it). A corrupt or unreadable journal is kept as `<name>.corrupt-<time>` and reported by `recover()` instead of being overwritten, one unreadable record no longer hides the others, one failed restore no longer stops the rest, and the journal file and its directory are synced to disk on every write. `check_service_health()` accepts only `http` and `https`.
- **Evidence gates.** `concludes_success()` refuses a `simulated` result unless the caller passes `allow_simulated=True`. `OperationResult` and `parse_operation_result()` reject a non-boolean `observers_enabled` (the text "false" used to count as true), non-string identifiers, missing fields and bad timestamps with `ContractValidationError`. `is_capability_usable()` needs a recorded `verified` outcome, and capability ages accept a naive "now" as UTC.
- **Schemas and validator agree.** `ProjectManifest` accepts `dev-server` and the `URTC` ecosystem, the optional `service` and `deployment_target_note` fields that real manifests carry, and is closed to other fields in both the schema and the Python validator. `UpdateManifest.artifact_url` must start with `https://` and `DeviceDescriptor.interfaces` items must not be empty in the schema too; the Python validator accepts lowercase `t`/`z` in timestamps and checks the types of `correlation_id`, `result.outcome_reason` and `result.revision`. The schemas were re-vendored into the Go, TypeScript and Rust clients and `manifest.json` regenerated. New `test_schema_differential.py` compares the Python validator with the schemas (it needs the optional `jsonschema` package) on the fixtures, on boundary cases and on the real manifests of sibling repositories.
- **OpenAPI.** `server.openapi.json` (now 1.1.0) matches the server: bearer authentication on `GET /api/settings`, `refreshToken` on sign-in, `POST /api/refresh` and `POST /api/logout`, rate limit `429`, `ETag`/`If-Match` with `409` and `revision` on settings, `warnings`, `400` and `409` on robot commands, and response objects that may gain fields.
- **Go client.** The compiled-schema cache is guarded by a mutex (concurrent validation crashed the process), a concurrency test was added, CI runs `go test -race`, and `go.mod` asks for Go 1.22 instead of 1.26.7.
- **Job intake and MQTT.** A duplicate whose key never got a stored answer comes back with `in_doubt=True`; the idempotency file uses WAL and a busy timeout. `hydra_umc_sdk.mqtt_connection` also reads `HYDRA_MQTT_TLS` (system CAs) and `HYDRA_MQTT_TLS_CERT`/`HYDRA_MQTT_TLS_KEY` (mutual TLS), refuses a password given without a user name, and explains an unreadable password file.
- **Tooling.** `tools/sync_doc_policy.py` and `tools/sync_readme_parity.py` include the firmware repository `HYDRA-UMC`; `tools/sync_version_tools.py --check` reports drift of `update-from-github.sh`; the version-label list of `tools/ci_validate.py` covers Portuguese and its dead code is gone; `ruff` runs in CI; `.gitignore` covers `.env.*`; `*.json` keeps LF line endings; `LICENSE` holds the full GPL-3.0 text and the notice moved to `LICENSE.md`.
- **Documentation.** The READMEs in the 8 languages no longer advertise Protobuf as available, say that `/api/v1` is a design goal, list the eight bridges, and describe `docs/` and `examples/` as they are; `docs/CONTRACTS.md`, `API_DESIGN.md`, `ADAPTERS.md`, `CONFORMANCE.md`, `TESTING_STRATEGY.md`, `PYTHON_CLIENT.md`, `PROJECT_MANIFEST.md`, `BRIDGE_CONTRACT.md` and `CONTRIBUTING.md` were corrected, real network addresses were removed from `docs/PROJECT_MANIFEST.md`, and the mock server now serves `INHIBITED` examples.

## [0.3.1] - The Portuguese README is required by the parity check

- The README parity check now requires the Portuguese README: `readme_parity.DEFAULT_LANGUAGE_FILES` includes `README_por.md`, a new `REQUIRED_LANGUAGE_FILES` makes its absence a reported problem (pass `required=()` to switch that off), and a Portuguese README is compared with the English one for section structure and external links like the other six translations.
- `tools/sync_readme_parity.py` also adds `README_por.md` to each repository's `REQUIRED_DOCUMENTS`, understands the one-line-per-several-names form of that tuple, and leaves a repository that has no `README_por.md` yet on the previous rule (reported as `skipped-no-readme-por`) so its CI is not broken before the file exists.
- Tests for the required, missing, structure and link cases (229 in total); the vendored copy was propagated to the repositories that carry it.

## [0.3.0] - MQTT credentials and TLS for bridges from the environment

- New `hydra_umc_sdk.mqtt_connection`: the credentials (`HYDRA_MQTT_USERNAME`, `HYDRA_MQTT_PASSWORD` or `HYDRA_MQTT_PASSWORD_FILE`) and the TLS CA (`HYDRA_MQTT_TLS_CA`) a bridge uses to reach a broker that demands them, read from the environment of the service; a password without a user name is refused, and an explicit user name from the caller never pairs with an environment password.
- `docs/BRIDGE_CONTRACT.md` documents the variables and that the broker evaluates its ACL for the identity of the credential, not for the client ID the client chose.
- Unit tests for the settings and for how they are put on a paho client.

## [0.2.9] - The gate uses the machine state the bridge observes, and bridges get a job intake

- **Observed state.** `evaluate_job(job, cell_state, observed_machine_state=None)`: when the bridge passes the state it just read from its machine, that is what the gate uses; the `machine_state` inside the job is only a claim by whoever published it (a message anybody on the broker may send), and a gate that trusted it let "IDLE" through while the machine was running. Without an observation the claim is still used, so existing bridges keep working until they pass theirs.
- **Job intake.** `hydra_umc_sdk.job_intake`: `JobIntake` ignores retained messages (the broker replays them at every reconnect, which started a physical action again each time) and refuses malformed jobs; `IdempotencyStore` remembers the idempotency keys (SQLite when given a file, so a restart does not forget; in memory otherwise; 24 hours and 10 000 keys by default) and the answer given to each, so a repeat is answered again instead of being run again. The contract document asked bridges to do this and none did.
- **Bounded jobs.** A job carries at most 32 parameters (names up to 64 characters, values up to 1024) and identifiers up to 128 characters.
- Tests for all of it (218 in the package).

## [0.2.8] - Separate-field version patterns may carry a build entry

- `native_version.pattern`'s object form accepts an optional `build` regex (JSON
  schemas, Python validator, and the Go, Rust and TypeScript types); the contract
  manifest hashes were regenerated.
- `tools/sync_version_tools.py` also reports repositories whose object-form
  pattern has no `build` entry.

## [0.2.7] - Version fields accept an optional fourth component

- Manifest and update-manifest `version` fields (the JSON schemas in every client
  and the Python validator) accept an optional fourth numeric component.
- The shared version tooling used by the sibling repositories is kept here under
  `tools/canonical/` and pushed out with `tools/sync_version_tools.py`.

## [0.2.6] - real cross-language contract round-trip tests

New round-trip tests in all 4 reference clients (Python, Go, Rust,
TypeScript), each decoding the same real `conformance/fixtures/v1/*.valid.json`
fixtures the existing schema-validation tests already use, re-encoding
them, and asserting the result is structurally identical to the original -
a different, complementary check from schema validation: a payload can
validate cleanly against its schema while still losing or reordering data
on its way through a language's own encode/decode path. Go and Rust decode
into their own hand-written structs for the 7 contracts that have one
(catching a real risk those two languages specifically have: a struct
missing a field would silently drop it on round trip); the 3 newer
contracts with no dedicated struct yet (Capability, Operation,
ScenarioOutcome) round-trip through the same generic representation each
client's own validator already uses for them. Evaluated
`contracts/openapi/v1/server.openapi.json` for auto-generation from the
JSON Schema contracts: confirmed hand-maintained, but skipped adding a
generator - only 1 of its 23 `components/schemas` entries maps to a real
published JSON Schema contract, the other 22 describe REST-only request/
response bodies with no schema source to generate from.

## [0.2.5] - PROM-G02/G03: a real evidence and promotion-gate standard, describing what the ecosystem's own real closures already do

Two new sections in `docs/PROJECT_MANIFEST.md`, right after "Maturity
levels": "Promotion evidence" and "Promotion gate". Same spirit as
0.2.4's own maturity glossary - neither invents a new process, both
name the real practice this ecosystem's own actual closures already
follow, so it stops being tribal knowledge.

"Promotion evidence" names what a real change's own record should be
able to answer (scope, exact command/test run, environment, result,
known limitations, affected consumers), reusing each repository's own
existing `CHANGELOG.md`/CI rather than a second registry, and keeps 4
real evidence kinds distinct rather than letting a lighter one stand in
for a heavier one: a unit test, a real-process loopback/integration
test, an emulation (proves this code's own handling of a simulated
condition, never that real hardware/a real driver works), and a real
physical-bench/supervised-operation result.

"Promotion gate" is the real checklist this ecosystem's own actual
maturity changes already apply before changing `maturity`: close real
blockers on the dependency path, run the affected real consumer's own
tests too (not just this repository in isolation), a real
non-incremental build/test, install/run the produced package OUTSIDE
its own checkout, exercise one real good case and one real bad case,
and bring manifest/`CHANGELOG.md`/README (all 7 languages)/usage docs
back in sync with what actually shipped - `established` additionally
requires a real restart/cancellation/lost-dependency/recovery within
the promoted scope.

## [0.2.4] - PROM-G01: a real maturity-level glossary, describing what the ecosystem already does

`maturity` (`scaffolding`/`functional`/`established`/`production`) has
been a validated manifest enum since the beginning, but nothing ever
wrote down what actually distinguishes the four values - each
repository's own choice was a judgment call, not a checked criterion.

New "Maturity levels" section in `docs/PROJECT_MANIFEST.md`, grounded in
the real, current split across all 60 manifests (53 `established`, 5
`scaffolding`, 1 `functional`, 0 `production`) rather than inventing a
new rule: `scaffolding` means real, tested code not yet exercised in
its own real operational context (physical hardware, sustained
deployment) - even a repository whose own delivery plan is 100% shipped
(`HYDRA-UMC-DEV-SERVER`) stays `scaffolding` until that happens;
`functional` means real capability validated against SOME real physical
target, not yet at `established`'s breadth (`URTC`); `established` is
real code AND real, sustained use in this ecosystem's own actual
deployment; `production` is reserved, unclaimed by any repository today.
Descriptive, not a new mandate - no repository's own `maturity` value
changes because of this.

## [0.2.3] - real, automatic README section-structure parity between languages

The ecosystem's own Related Projects catalog gap was found by
manual audit - nothing automatically checked whether a translation's
own README structure actually matched its English original.

- New `hydra_umc_sdk.readme_parity` module: `check_readme_section_parity()`
  compares README.md's own ordered `## <emoji>` heading signature
  against every translation's - reports a missing section, an extra
  one, a reordered one, or a mismatched heading emoji, without caring
  about the translated prose at all. Reuses what already exists in
  every repo (the emoji itself is never translated) instead of
  inventing a new `canonical:start/end` marker convention that would
  duplicate information hundreds of files already encode. 9 new unit
  tests.
- New `tools/sync_readme_parity.py`: same real distribution design as
  's `sync_doc_policy.py` (a vendored `tools/_readme_parity.py`
  copy per repo, no live runtime dependency added to any repo's own
  per-commit CI) - adds a real call right after this project's own check in
  each sibling's `ci_validate.py`.
- Ran it against the whole ecosystem while building it: found and fixed
  2 real, tiny structural bugs it was designed to catch (`HYDRA-UMC-SDK`
  and `HYDRA-UMC-OS`'s own `README_ita.md` each had `## 🚧Stato` missing
  the space after the emoji, present nowhere in this or 6 other
  languages) - the exact class of drift this check exists to catch
  automatically instead of by manual audit.

## [0.2.2] - the public/private documentation boundary check is a real, tested, canonical module now

Every one of this ecosystem's ~60 repos carried its own byte-for-byte
copy of the same public/private documentation boundary check inside its
own `tools/ci_validate.py` - a real future rule change would have meant
hand-editing ~60 files, since nothing here was a single source of truth.

- New `hydra_umc_sdk.doc_policy` module: `check_public_private_boundary()`,
  the exact same two-part check (a bare private-marker name, and a set
  of private-planning-material phrases) every repo's own CI already ran,
  now real, tested, canonical code instead of ~60 independent copies. 7
  new unit tests against a real throwaway git repository (this check
  shells out to `git grep`, so a fake filesystem alone would never
  exercise the real command it runs).
- New `tools/sync_doc_policy.py`: propagates a vendored copy
  (`tools/_doc_policy.py`, never hand-edited there) into every sibling
  repo, and rewrites each one's own `ci_validate.py` to call it instead
  of carrying an independent copy. Deliberately NOT a live runtime
  dependency on this package for every repo's own per-commit CI - most
  of them are not Python projects at all, and this ecosystem's own CI
  already has enough real fragility from cross-repo checkouts. A future
  rule change now means: edit the one canonical module, run this script
  once.

## [0.2.1] - New docs/TESTING_STRATEGY.md: shared test levels, evidence, and fixture conventions

- Published the shared test-level (per-commit/contract-change/scheduled/
  release-candidate), platform-matrix, minimum-evidence-per-result,
  reproducible-campaign target, fixture-independence, and cost/storage
  conventions every repository's own `build-test`/`ci_validate` already
  approximates on its own - previously only living as a private planning
  document, now a real, linkable guide. Cross-references
  `compare_runs()`/`ScenarioOutcome` as the reproducible-scenario
  level's own "was it actually fixed" check.
- Linked from README.md's "Further documentation" list in all 7
  languages.

## [0.2.0] - Operation.result + Capability, and 2 real cross-client drift bugs fixed along the way

A real evidence-of-execution contract, distinct from a merely declared
capability: an Operation reaching a terminal status was never, by
itself, proof anything really happened - a queue can report
`status: "terminated"` with observation entirely disabled. New optional
`result` on the `Operation` contract (`run_id`, `revision`, `origin`
real/simulated, `observers_enabled`, `accepted_at_utc`/`executed_at_utc`/
`observed_at_utc`, `outcome` success/failure/unknown with a required
`outcome_reason` whenever it isn't success) plus `operation.py`'s new
`concludes_success()` - the real gate that refuses to conclude success
from a result belonging to a different run, one produced with observers
disabled, or one never actually observed. New standalone `Capability`
contract (`target`, `kind`, `declared`, `last_checked_at_utc`,
`checked_configuration`, `max_age_seconds`, `last_check_outcome`) plus
`capability.py`'s `is_capability_usable()` - whether a target *declares*
support for an operation kind at all is now modeled as data distinct
from whether that support was *recently, actually verified*; a declared
but never-checked or gone-stale capability is never treated as usable.
Both mirror this ecosystem's own established calibration/observation
freshness pattern (HYDRA-UMC-SAFETY-ZONES' `calibration.py`/
`observation.py`). 10 real contracts now, vendored across all 4
reference clients (Python/Go/TypeScript/Rust) with matching conformance
fixtures.

Also fixed two real, unrelated drift bugs found while doing this work:

- This repository's own `hydra-umc.project.json` declared `native_version.file`
  as `CHANGELOG.md` with a bare `(\d+)\.(\d+)\.(\d+)` pattern - a
  self-referential, tautological check that could never actually catch
  the native version (`clients/python/pyproject.toml`) drifting out of
  sync with the manifest, which is exactly what had already happened:
  the previous 0.1.9 release bumped the manifest and `CHANGELOG.md` but
  never `pyproject.toml`/`__init__.py` themselves. Fixed the manifest to
  point at the real file, and synced the real native version to 0.1.9
  before bumping to this release.
- `clients/rust/src/validation.rs`'s `CONTRACT_FILES` map (and the test
  suite's own `CONTRACT_FIXTURE_STEM`) had silently never gained
  `ScenarioOutcome` or `Operation` entries, even though both schemas
  were correctly embedded - `validate("Operation", ...)` returned
  "unknown contract" for every real payload in the Rust client, through
  two whole prior contract additions, because `tools/verify_contract_matrix.py`'s
  cross-client coverage check only ever compared Go and TypeScript
  against the published schemas, never Rust. Both contracts restored;
  the matrix script now also cross-checks Rust, so this drift class is
  caught automatically going forward for all three non-Python clients.

22 new Python tests (`test_capability.py`, `test_operation.py`,
`test_validation.py`), Go/Rust/TypeScript fixture-loop coverage extended
automatically via their existing dynamic fixture maps. Verified: python
161 passed + 20 subtests, go test ok, cargo test 9/9, npm test 28/28
(tsc clean), verify_contract_matrix PASS contracts=10 (incl. new Rust
coverage check), ci_validate PASS. README x7 synced (9 -> 10 contracts).

## [0.1.9] - Recover a health check left pending by a crash, not just a rename

Checkpoints backed by real postconditions, not just a rename: a
promotion that finishes its 2 renames is not necessarily a HEALTHY
promotion - the real postcondition is that the service was actually
checked, not merely that files were moved. `PromotionRecord`
gains an optional `health_check_url` (only set when a project's own
`hydra-umc.project.json` declares a `service_health_path`); new
`check_service_health(url)` does a real, minimal HTTP GET - deliberately
STRICTER than a bare reachability probe (compare
HYDRA-UMC-LOCAL-TECHNICIAN's own `network.connectivity`, where any real
HTTP response counts as reachable): here, only a real 2xx counts as
healthy, since a 4xx/5xx means the freshly-promoted code IS running but
is not well, and must not be waved through as success.

`recover()`'s own PROMOTED branch used to say "nothing to recover" for
every promoted record - now, when a `health_check_url` is set, it runs
the real pending check right now (never repeating the actual clone/build)
and only marks the promotion `COMPLETE` if it genuinely passes; a check
that still fails leaves the record pending for a human/next run instead
of announcing success prematurely - the acceptance test:
cut the process after promoting and before checking health, restart,
and the pending check runs for real rather than being silently skipped.

8 new tests (`test_promotion_journal.py`, `CheckServiceHealthTests` +
extensions to `RecoverTests`): a real local HTTP server answering 200
(health check passes, promotion completes), one answering 500 (fails,
stays pending), a real closed port (fails, stays pending), `health_check_url`
surviving `advance()` across phase transitions, and an older-shaped
journal file (no `health_check_url` key at all) still loading with it
defaulting to `None`.

## [0.1.8] - A durable, transactional promotion journal

- **`clients/python/src/hydra_umc_sdk/promotion_journal.py`** - the real,
  durable version of the mitigation HYDRA-UMC-UPDATER's own
  `install.py` already carries inline (previously an honest, bounded
  mitigation rather than the full transactional journal/rollback, which
  needed designing once and sharing with HYDRA-UMC-OPS-AGENT's own
  `canary_deploy.py`). Both installers stage a verified candidate, then
  promote it over a live installation with 2 back-to-back directory
  renames; each already added its own in-process self-heal for the
  narrow gap between them, but that only survives an exception inside
  the same Python call stack - a full process crash, `kill -9`, power
  loss, or a reboot mid-promotion leaves nothing to run.
  `PromotionJournal` writes a `PromotionRecord` to a small JSON file,
  atomically (write-to-temp + `os.replace`), BEFORE the first real
  filesystem mutation - `begin()`/`advance()`/`complete()`/`pending()`.
  `recover(journal)` finds every promotion left short of `COMPLETE` and
  applies the same real self-heal rule those installers' own inline code
  already uses (restore `backup_path` -> `target_path` if the crash
  happened right after the first rename; nothing to do if it happened
  after the second), generalized so it also survives the process itself
  having died - runnable the NEXT time an installer starts, not only
  within the same run. A record whose filesystem state genuinely can't
  be resolved (neither `target_path` nor `backup_path` exist) is left
  pending for a human rather than silently pruned.
- 16 new tests (`test_promotion_journal.py`), including a real crash
  simulation restored by a completely fresh `PromotionJournal` instance,
  a corrupt-journal-file degradation path, and an unresolvable case left
  pending on purpose. New example
  (`examples/python/recover_interrupted_promotion.py`).

## [0.1.7] - Cross-service failure tracing + a real observability toolkit

- **`clients/python/src/hydra_umc_sdk/lifecycle.py`** - a real observability
  deliverable. `ProcessLifecycleState` (`alive`/`ready`/`degraded`/
  `disconnected`/`unknown`) - 5 real, distinct process-liveness
  states, never collapsed into a boolean "up"/"down". Distinct
  from `HealthReport`/`SafetyState` (a ROBOT's or MACHINE's own safety
  state) - a different, complementary concern.
  `StructuredLogEntry(component, correlation_id, version, timestamp_utc,
  level, message, error_cause, caused_by)` - the payload a service puts
  inside an existing `EventEnvelope`, not a competing wire shape.
  `caused_by` is the field that makes real cross-service tracing
  possible: `trace_first_failure()` walks a `caused_by` chain
  across however many services' own log entries back to the ACTUAL first
  component that failed - not whichever entry a caller happened to look
  at first (in practice, usually the LAST service to notice and report
  it, since that's typically the one an operator gets paged for). Stops
  honestly at the earliest entry actually collected if the chain extends
  further back than what was gathered, and never loops forever on a
  cyclic `caused_by` reference in malformed input.
  `StructuredLogEntry.redacted(redactor)` - exporting a sanitized
  diagnostic as real code: only `message`/`error_cause` are ever passed
  through a redactor, every structural field (`component`/
  `correlation_id`/`version`/`caused_by`) is left untouched, since those
  are identifiers, never where a real secret would land.
  `BoundedLog(max_entries)` - bounding the size of logs, queues and
  retries as enforced behavior: drops the OLDEST entry once over
  capacity (same drop-oldest policy this ecosystem's own bounded queues
  already use elsewhere, e.g. HYDRA-UMC's `RelayRxQueue`), tracks
  `dropped_count`.
- 14 new tests (`test_lifecycle.py`), including a real multi-service
  cause-chain trace (`urtc-relay` -> `hydra-umc-server` -> `studio`) and
  a new example (`examples/python/trace_first_failure.py`) walking that
  exact scenario end to end, redaction included.

## [0.1.6] - New `Operation` contract: shared, strict, versioned lifecycle

- **`contracts/json-schema/v1/operation.schema.json`** - a shared shape for anything crossing
  a service boundary in this ecosystem (SERVER, ORCHESTRATOR, DEV-SERVER,
  OPS-AGENT, ...) to report its own real progress through 6 genuinely
  distinct states - `received`, `authorized`, `queued`, `sent`,
  `confirmed`, `terminated` (plus `rejected`) - instead of collapsing
  everything into a single "executed" bucket. `target` names what the
  operation is directed at (`kind`/`id`, domain-agnostic on purpose);
  `correlation_id` ties related operations together; `params` carries the
  operation-specific payload; `error` is optional and only meaningful
  once `rejected`.
- **`clients/python/src/hydra_umc_sdk/operation.py`** - the real,
  enforced lifecycle: `validate_status_transition(previous, next)` is the
  concrete enforcement of that idea - never collapsing every real state into
  a single "executed" bucket - the only
  legal forward path is received -> authorized -> queued -> sent ->
  confirmed -> terminated, `rejected` is reachable from any non-terminal
  status but nothing is ever reachable FROM a terminal one. `is_terminal()`
  and a small validated `OperationRecord` dataclass round out the module.
  Distinct from `bridge_contract.py`'s own `BridgeJob`/`JobPhase` (a
  narrower, domain-specific safety gate for external machine bridges) -
  the two are not redundant.
- Vendored to `clients/{go,rust,typescript}/schemas/`, `manifest.json`
  regenerated in all 4 locations, `conformance/fixtures/v1/operation.
  {valid,invalid}.json` (the invalid fixture uses `status: "executed"` -
  exactly the collapsed bucket this contract exists to forbid), and a new
  example (`examples/python/operation_lifecycle.py`).
- 12 new Python tests (`test_operation.py` + `test_validation.py`), 1 new
  Rust conformance test (embedded schema), 4 new TypeScript fixture tests,
  1 new Go fixture round-trip.

- **Real cross-client drift found while adding this contract**:
  `ScenarioOutcome` (added in 0.1.5) had a published schema and a working
  Python validator entry, but was never added to the Go client's
  `contractFiles` map or the TypeScript client's `ContractName` type/
  `CONTRACT_FILES` map - `tools/verify_contract_matrix.py` only ever
  cross-checked the Python validator against the schema files, so this
  went uncaught through a whole prior contract addition. Both clients
  fixed (`ScenarioOutcome` and `Operation` now both wired end to end in
  all 4 languages); `verify_contract_matrix.py` extended with a real
  Go/TypeScript coverage cross-check so this drift class can't recur
  silently again. `docs/PYTHON_CLIENT.md`'s own required-fields table was
  also missing `ProjectManifest` and `ScenarioOutcome` rows (pre-existing
  gaps, unrelated to this specific drift) - added, alongside the new
  `Operation` row.

## [0.1.5] - New `ScenarioOutcome` contract + a real before/after check

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

- `clients/python/src/hydra_umc_sdk/validation.py` - `"dev-server"` added
  to `PROJECT_MANIFEST_ENUMS["deployment_target"]` for the new
  HYDRA-UMC-DEV-SERVER project (a Raspberry Pi 5/CM5 host dedicated to
  development and task execution, distinct from `"cm5"`, the operational
  node that talks to real machines/robots). A compatible manifest
  extension - no existing value changed meaning, no consumer needs to
  change. New test `test_accepts_dev_server_deployment_target`.

## [0.1.2] - BridgeJob's direct constructor now validates `parameters` before using it

- **`clients/python/src/hydra_umc_sdk/bridge_contract.py`'s `BridgeJob`**
  (found in a second review pass; same class of gap as
  the [0.1.1] fix below, this time on `parameters` instead of
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
  **Checked for the same ecosystem-wide breakage the [0.1.1] fix caused
  (5 consumer bridges' own tests broke on that fix):** every real
  `BridgeJob(...)` call site across the ecosystem (all 9 bridges plus
  CONNECTOR-HUB's `sdk_gate.py`) was grepped - every one already passes
  a real `dict`/`{}` or another job's own already-valid `.parameters`,
  never a list or other non-mapping. No consumer breakage from this
  fix. `PYTHONPATH=clients/python/src python -m unittest discover -s
  clients/python/tests -v`: 53/53 passing.

## [0.1.1] - Enforce real enum membership at the BridgeJob constructor

- **`clients/python/src/hydra_umc_sdk/bridge_contract.py`'s `BridgeJob`:**
  `phase`/`machine_state` are typed as `JobPhase`/`MachineState` in the
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

- **`validation.py`** - `UpdateManifest.version` was only checked for a
  matching `sha256`; a value like `"latest"` or `"v1"` passed straight
  through. It's now validated against the same `SEMVER_PATTERN` already
  used elsewhere in this file, and `update-manifest.schema.json` gained
  the matching JSON Schema `pattern`, so the reference validator and the
  published schema agree again.

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

## [0.0.4] - Automatic contract/validator compatibility matrix

- **`tools/verify_contract_matrix.py`** (new) - a real, automatic compatibility matrix between the published v1 JSON Schema files and this SDK's own Python reference validator. It discovers every real `*.schema.json` under `contracts/json-schema/v1/`, cross-checks that each one has a matching `validate()` entry (and vice versa - a stale validator entry with no real schema file is flagged too), runs every conformance fixture through `validate()` and confirms it's judged the way its own `.valid.json`/`.invalid.json` filename claims, and proves the two negative cases this matrix specifically guards: an unknown contract name and an incompatible `schema_version`.
- **`ProjectManifest` contract validation** (`validation.py`) - the matrix immediately found a real, concrete gap it was built to catch: `project-manifest.schema.json` (the `hydra-umc.project.json` contract every repository in this ecosystem publishes) had no corresponding entry in the Python validator at all - it could never actually be validated. Added the real required-field/enum/pattern checks mirroring the schema (`ecosystem`, `name` pattern, semver `version`, `role`/`deployment_target`/`maturity` enums, non-empty unique `technologies`, nullable `parent`, `native_version`'s string-or-component `pattern`), plus real conformance fixtures (`project-manifest.valid.json`/`.invalid.json`).
- 22 new tests (`test_validation.py`) = 30 total.

- `tools/build_test.py`'s non-mutating `build-test.sh` check compiled Python sources but never actually ran the real conformance test suite (`clients/python/tests`) or the new contract matrix - both are now wired in, so the "test" step genuinely tests something.

- Automated build version increment from 0.0.3.

## [0.0.3]

- Automated build version increment from 0.0.2.

## [0.0.2]

- JSON Schema v1 for `DeviceDescriptor`, `HealthReport`, `SafetyState`, and
  `UpdateManifest`.
- Dependency-free Python reference validator and command-line entry point.
- Valid and invalid conformance fixtures plus four host-side validation tests.
- Runnable Python example for `HealthReport` validation.

- Protobuf, OpenAPI, package publication, and non-Python clients are not part
  of this initial contract release.

## [0.0.1]

- Initial SDK documentation, multilingual README files, and target layout.
- Contract, API, conformance, and adapter-boundary specifications.

## Earlier history

### External machine bridge contract (no odometer bump)

Landed after [0.0.4] and before [0.0.5] above without going through the
odometer build script - `evaluate_job()` and `BridgeJob` were already in
use by [0.0.5]'s "all 7 contracts" fixture count, and [0.0.7] later
extends this same contract with its real JSON wire shape.

- Public, dependency-free Python v0 external-machine bridge contract:
  `BridgeJob`, bridge/machine/cell state enums and `evaluate_job()` safety
  gate. It is the shared high-level boundary for the ROS 2, OpenPnP, 3D
  printer, CNC and laser integrations; it does not expose motion control.
- `docs/BRIDGE_CONTRACT.md` and five focused unit tests proving productive
  work is rejected when either side is not ready while `ABORT` remains
  requestable through the authorised safety path.

- UpdateManifest validation now requires an HTTPS artifact URL with a real
  hostname, rejecting malformed strings such as `https:///artifact.deb`.

- The dependency-free Python validator now rejects invalid RFC 3339
  `timestamp_utc` values and JSON booleans supplied where the `EventEnvelope`
  sequence or `ServerDiscovery` numeric counters require integers. Python
  treats `bool` as an `int` subclass, which previously let invalid contract
  payloads pass reference validation.

### Documentation

- `docs/PYTHON_CLIENT.md` - full reference for the `validate()` function
  and `hydra-umc-contract-validate` CLI in `clients/python`: the exact
  required-fields and extra-validation-rule table for all 6 contracts
  (`DeviceDescriptor`, `HealthReport`, `SafetyState`, `UpdateManifest`,
  `EventEnvelope`, `ServerDiscovery`), previously only readable from
  `validation.py`'s own source. Verified live against the real function
  and CLI. Linked from `docs/CONTRACTS.md`. Documentation-only - no code
  changed, no version bump.

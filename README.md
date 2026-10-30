<!-- =============================================================================
HYDRA-UMC-SDK - Shared contracts and integration toolkit
Copyright (C) JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-SDK banner" width="100%">
</p>

# 🧰 HYDRA-UMC-SDK

<p align="center">🇺🇸 <b>English</b> | <a href="README_spa.md">🇪🇸 Español</a> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | <a href="README_jpn.md">🇯🇵 日本語</a> | <a href="README_por.md">🇵🇹 Português</a></p>

### 🧰 Shared Contracts, Reference Clients and Integration Tools for HYDRA-UMC

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Contracts-JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="Contracts">
  <img src="https://img.shields.io/badge/Reference%20clients-Python%20%7C%20Go%20%7C%20TypeScript%20%7C%20Rust-blueviolet.svg" alt="Reference%20clients">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="Integration">
  <img src="https://img.shields.io/badge/Tests-506%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.4.1-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-established-2EA44F.svg" alt="Maturity">
</p>

---

> **Honesty check - what actually runs today:** the ten JSON Schema v1 contracts with a valid and an invalid fixture each, the Python validator, the first OpenAPI v1 slice of HYDRA-UMC-SERVER, the Go, TypeScript and Rust clients that enforce the same schemas, the bridge helpers and the compatibility matrix are real and tested on a computer (506 Python tests, plus the suites of the other three clients). Protobuf is not published yet, the job gate is a shared software function and not a certified safety function, and nothing here has run on real hardware.

---

> **Safety and security status:** this ecosystem is not a certified safety system. There is no hardware E-STOP path, no firmware-enforced limits or interlocks and no verified motion command yet; firmware images are checked with CRC-32 and an Ed25519 signature, and a release build refuses the published development keys (the tool heads and expansion boards behind the relay still run URTC bootloaders, which take a shared-key HMAC-SHA256 instead of a signature); TLS and mutual TLS are optional and off by default; no custom board has been populated or tested yet. Read the [security baseline](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md) and the [threat model](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md) before relying on any statement here for the safety of a person.

---

## 📋 At a glance

| | |
|---|---|
| Version | `0.4.1` |
| Maturity | Established |
| Tests | 506 (`python -m unittest discover -s clients/python/tests`) |
| Stack | Python / TypeScript / Go / Rust / JSON Schema |
| On real hardware | Not yet: no run on real hardware is recorded for this version |

**Jump to:** [Overview](#-overview) · [Architecture](#-architecture) · [Features](#-features) · [Security & Safety](#-security--safety) · [Interfaces](#-interfaces) · [Configuration](#-configuration) · [Quick start](#-quick-start) · [Testing](#-testing) · [Troubleshooting](#-troubleshooting) · [Repository Structure](#-repository-structure) · [Related Projects](#-related-projects)

## 🚦 Project status

Each line is one part of this repository and the light says how far it is today. It is written from what the repository can show (tests, builds, runs), not from what is planned.

🟢 Done and verified · 🟡 Works, with known limits · 🟠 Partly done or not verified yet · 🔴 Not done or not working

| Area | State | What it means here |
|---|---|---|
| Software | 🟢 | Complete for its purpose and stable; the honesty check above lists the known limits |
| Tests | 🟢 | 506 automated tests, run on every change |
| Real hardware | 🔴 | Not yet: no run on real hardware is recorded for this version |
| Documentation | 🟢 | README in eight languages, checked against the manifest on every change |

## 🎯 Overview

HYDRA-UMC-SDK defines the stable language shared by HYDRA-UMC services,
clients, CM5 adapters, and URTC integrations. It owns normative contracts, a
dependency-free Python reference validator, conformance fixtures, and
integration guidance. It does not
replace official APIs for Raspberry Pi OS, Hailo, ROS 2, MQTT, OPC-UA, or
MTConnect.

## 🧩 Role in HYDRA-UMC

**HYDRA-UMC-SDK** is the shared language of the ecosystem: the JSON Schema v1 contracts, the first OpenAPI slice of the server, reference clients in Python, Go, TypeScript and Rust, the bridge helpers every bridge and the connector hub use, and the tools that keep the tooling of every repository identical. It runs no service of its own and replaces no official API.

## 🏛️ Architecture

<p align="center">
  <img src="images/architecture.svg" alt="HYDRA-UMC-SDK architecture" width="100%">
</p>

## ✨ Features

### Status

JSON Schema v1 contracts, valid/invalid fixtures, a Python validation client,
host-side tests, and a real first OpenAPI v1 slice for HYDRA-UMC-SERVER's own
HTTP surface (`contracts/openapi/v1/server.openapi.json` - see
[docs/CONTRACTS.md](docs/CONTRACTS.md#openapi-v1)) are implemented. Protobuf publication is a later compatibility milestone; the Go, TypeScript and Rust clients already exist.

A real, automatic compatibility matrix (`tools/verify_contract_matrix.py`)
cross-checks every published schema against the Python validator's own
contract list - it found and fixed a real gap where `project-manifest.schema.json`
(the `hydra-umc.project.json` contract every repository in this ecosystem
publishes) had no validator entry at all, and now proves every conformance
fixture is judged the way its own filename claims, plus the unknown-contract
and incompatible-schema-version cases.

More contracts have since shipped beyond the four in the first milestone
below: a public `BridgeJob`/`GateDecision` external-machine bridge
contract (see [docs/BRIDGE_CONTRACT.md](docs/BRIDGE_CONTRACT.md)), shared
by `HYDRA-UMC-BRIDGE-ROS2`/`-OPENPNP`/`-PRINTER3D`/`-CNC`/`-LASER`/`-AMR`/`-DROIDS`/`-UAV` and
given its own real JSON wire shape (`job_to_dict()`/`job_from_dict()`/
`decision_to_dict()`), plus the machine state the bridge itself observes, which the gate uses instead of the one the requester claims, and a job intake (`JobIntake`/`IdempotencyStore`) that ignores retained messages and never runs an idempotency key twice; a `ScenarioOutcome` contract plus
`compare_runs()`, a shared "was it actually fixed" check that
returns `apparent-success` (not `regression-fixed`) when a failure
stopped reproducing but the base fingerprint never moved; an `Operation`
contract plus `validate_status_transition()`, the shared
goal/job/operation lifecycle - `received`/`authorized`/`queued`/`sent`/
`confirmed`/`terminated`/`rejected`, never a single collapsed "executed"
bucket; an optional `result` on `Operation` plus `concludes_success()` -
real evidence (`run_id`/`origin`/`observers_enabled`/`outcome`)
that refuses to conclude success from a stale/replayed result or a run
with observation disabled; a standalone `Capability` contract plus
`is_capability_usable()` - whether a target even *declares*
support for an operation `kind` is modeled as data distinct from
whether that support was *recently, actually verified*
(`last_checked_at_utc`/`checked_configuration`/`max_age_seconds`), so a
declared-but-never-checked or gone-stale capability is never silently
treated as usable; and a `hydra-umc-sdk-mock-server` (`mock_server.py`)
that serves one contract-valid example payload per known contract over
plain HTTP, for a UI or adapter to develop against before any real
CM5/robot/MCU hardware is available. All 13 contracts have at least one
valid and one invalid conformance fixture, verified by the compatibility
matrix above.

## 🔒 Security & Safety

| Threat | Defence | Where |
|---|---|---|
| A bridge command outside its contract | A job carries at most 32 parameters, names of 64 characters, values of 1024 and identifiers of 128; the machine state the bridge observes is used instead of the one the requester claims | `bridge_contract.py` |
| The same command run twice, or a retained message replayed | The job intake ignores retained messages and never runs an idempotency key twice | `job_intake.py` |
| A stop waiting behind a long command | Ordinary commands run one at a time on one lane and the stop verbs run on a second lane | `bridge_transport.py` |
| Broker credentials in a configuration file, or an unverified broker | User and password come from the environment or from a file, TLS can verify the broker against a CA, and a client certificate and key turn on mutual TLS | `mqtt_connection.py` |
| A schema changed without the validator following | A compatibility matrix checks every published schema against the validator's contract list and judges every fixture by what its file name claims | `tools/verify_contract_matrix.py` |

**What it never does:** act as a certified safety function. The job gate is one software implementation shared by the bridges, not a safety certification.

## 🔌 Interfaces

| Topic or route | What it carries |
|---|---|
| `contracts/json-schema/v1/` | ten JSON Schema v1 contracts: capability, device descriptor, event envelope, health report, operation, project manifest, safety state, scenario outcome, server discovery, update manifest |
| `contracts/openapi/v1/server.openapi.json` | the first OpenAPI v1 slice of HYDRA-UMC-SERVER: discovery, sign-in, settings and commands (a subset of the server's own `docs/openapi.json`) |
| `contracts/ports.yaml` | the registry of the port, health path and systemd unit of every service, generated by `tools/sync_ports.py` |
| `hydra/bridges/<name>/cmd/#` | where a bridge listens; it answers on `.../<verb>/result` |
| `hydra-umc-contract-validate`, `hydra-umc-sdk-mock-server` | the validator on the command line (exit code 2 on failure) and a mock server on `127.0.0.1:8790` that serves one valid example per contract |

## ⚙️ Configuration

| Variable | Default | What it sets |
|---|---|---|
| `HYDRA_MQTT_USERNAME`, `HYDRA_MQTT_PASSWORD` | no credential | the broker credential; the password only together with the user name |
| `HYDRA_MQTT_PASSWORD_FILE` | - | the password read from a file (a Docker or systemd secret); ignored when the variable above is set |
| `HYDRA_MQTT_TLS`, `HYDRA_MQTT_TLS_CA` | no TLS | `HYDRA_MQTT_TLS=1` verifies the broker against the system CAs; `HYDRA_MQTT_TLS_CA` names the CA file that signed its certificate |
| `HYDRA_MQTT_TLS_CERT`, `HYDRA_MQTT_TLS_KEY` | - | the client certificate and key for a broker that demands mutual TLS; both are needed and they turn TLS on |
| `--host`, `--port` | `127.0.0.1`, `8790` | where the mock server listens |
| `HYDRA_UMC_SDK_ROOT` | the sibling folder | where the tests of the other repositories find this one |

## 🚀 Quick start

Requires Python 3.11 or newer. The Go, TypeScript and Rust clients are built and tested too when their toolchain is installed.

```bash
PYTHONPATH=clients/python/src python -m unittest discover -s clients/python/tests  # the Python client tests
python tools/verify_contract_matrix.py                                             # every schema against the validator and every fixture
PYTHONPATH=clients/python/src python -m hydra_umc_sdk.validation --help            # the contract validator on the command line
./build-test.sh                                                                    # the non-mutating build check (build-test.bat on Windows)
```

## 🧪 Testing

506 automated tests run with `python -m unittest discover -s clients/python/tests`. The other clients have their own suites: 28 tests in Go (`go test ./...`), 105 in TypeScript (`npm test`) and 31 in Rust (`cargo test`), run by `tools/extra_build_steps.py` when the toolchain is installed. None needs hardware.

The CI runs `HYDRA_UMC_CI=1 python tools/ci_validate.py`, which checks the manifest, the documents, the eight READMEs and the pictures.

## 🏗️ Build & Release

Use the non-versioning build check before a release build:

| Action | Windows | Linux / macOS |
|---|---|---|
| Build check (no version or CHANGELOG change) | `build-test.bat` | `./build-test.sh` |
| Run / development (when provided) | `run*.bat` or `dev*.bat` | `./run*.sh` or `./dev*.sh` |

`build-test.bat` and `build-test.sh` compile or validate the project stack without incrementing `hydra-umc.project.json` or modifying `CHANGELOG.md`. They may create normal compiler output only. Existing `build*.bat`, `build*.sh`, `run*` and `dev*` scripts retain their project-specific, versioned or runtime behavior; use them when that behavior is required.

## 🩺 Troubleshooting

| You see | Because | Do |
|---|---|---|
| `hydra-umc-contract-validate: missing required field: ...` | The payload breaks the contract; the command ends with exit code 2 | Compare the file with the example the mock server serves for that contract |
| `verify_contract_matrix.py` fails | A schema was added or changed and the validator's contract list or a fixture was not updated | Add the validator entry and a valid and an invalid fixture for it |
| `go test ./...` is skipped | The build check runs the Go, TypeScript and Rust clients only when `go`, `npm` and `cargo` are on the path | Install the toolchain; the check prints which client was skipped |

## 📂 Repository Structure

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of HYDRA-UMC-SDK" width="100%">
</p>

<details>
<summary>Text version of the tree</summary>

```text
HYDRA-UMC-SDK/
├── contracts/                 JSON Schema v1 sources, the OpenAPI slice and the port registry
├── clients/                   the Python, Go, TypeScript and Rust reference clients
├── conformance/               valid and invalid fixtures for every contract
├── docs/                      contract, API and development guides
├── examples/                  runnable Python examples
├── tools/                     contract matrix, OpenAPI gate, tooling sync, build check
├── .github/                   CI workflow and issue templates
├── images/                    banner and the pictures of the README
├── CHANGELOG.md               what changed in each version
├── build-test.sh              non-mutating build check
├── build.sh                   builds and checks; never changes the version
├── bump_manifest_version.py   syncs the manifest version
├── bump_version.py            explicit version bump
├── hydra-umc.project.json     manifest: version, maturity, family
├── run.sh                     starts the program
└── test.sh                    runs the tests
```

</details>

`tools/`: `verify_contract_matrix.py` (schema/validator compatibility matrix), `verify_openapi.py` (dependency-free OpenAPI structural gate), and the non-mutating `build-test` engine. `sync_repo_tools.py` keeps the shared tooling of every repository identical, `pin_sdk.py` pins the consumers of the SDK to a release tag, and `canonical/` holds the single copies they vendor (including the `hydra_project_tool.py` command that validates, tests and, only when asked, bumps the version). `sync_ports.py` generates and checks `contracts/ports.yaml`, the registry of the port, health path and systemd unit of every service; the shared secret redaction (`canonical/redaction.py`, with its cases in `contracts/redaction/vectors.json`) is vendored into the projects that send text out.

## 🗺️ Roadmap & Known limits

**Known limits today**

* Protobuf is not published yet, and the OpenAPI slice covers discovery, sign-in, settings and commands only.
* The routes of the server are not versioned today; `/api/v1` is the design goal described in `docs/API_DESIGN.md`.
* Nothing here has run on real hardware, and the job gate is a software function, not a certified safety function.

**Next:** publish Protobuf where an integration needs it and widen the OpenAPI slice to the rest of the routes of the server.

## 🌍 Languages

This README and the documents of the repository exist in eight languages: English, Spanish, German, French, Italian, Japanese, Chinese and Portuguese (Portugal). They are written together and checked in the CI so that the eight files have the same sections and the same links. This repository has no screen or message catalogue of its own, so there are no interface strings to translate.

## 🔗 Related Projects

This project is part of the HYDRA-UMC robotics ecosystem by the same author (JuanenRac / Electro Hobby 3D). Worth knowing about, since a request might actually be about one of these rather than this repository.

**Parent Project**
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — reproducible Raspberry Pi OS product layer for the CM5: read-only agent, validated config/profiles, WiFi first-contact provisioning; a device agent consumer of this SDK's own device, health, safety, and update contracts.
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — declarative adapter-manifest registry and validator for external-machine connectors; extends the SDK's own contract idea to external machines without replacing the industrial-gateway projects.

**Directly Related**
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — the real headless backend (REST/WebSocket) every control client actually talks to — an authenticated API producer and consumer governed by this SDK's own contracts.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — administrative desktop tool that discovers, clones and updates every repo in this ecosystem — publishes version and compatibility metadata consumed by this SDK's own contract-aware clients.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — Windows/Linux desktop tool that builds a ready-to-flash CM5 image pre-loaded with the ecosystem's most current versions, with Raspberry-Pi-Imager-style first-boot Wi-Fi/user/SSH configuration.
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — maintenance-incident coordinator: a low-privilege edge role collects a sanitized inventory/health snapshot, a control-plane role renders it read-only and asks an AI provider to suggest a diagnosis - never applies a patch or deploys anything.
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — reproducible development host (Raspberry Pi 5 / CM5) that stores the ecosystem's source and runs bounded build/test tasks under a durable queue; a dedicated dev role, explicitly not an operational CM5.
- **[HYDRA-UMC-DOCS](https://github.com/JuanenRac/HYDRA-UMC-DOCS)** — the documentation and tooling hub of the ecosystem: architecture, interfaces, security baseline, capability matrix and a project catalogue generated from every manifest.
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — the robot-arm motherboard design: CM5 host + dual-core STM32H745, meant to orchestrate up to 8 tool arms over CAN-OTA/SPI-OTA (firmware at an early stage; no populated board yet).
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware for the physical Universal Robot Tool Controller PCB, 25+ tool profiles over CAN bus — an independent tool-controller platform connected through this SDK's own versioned integration adapters.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — coordinator with a lazily imported rclpy ROS 2 transport (not yet run against a ROS 2 installation) — uses this SDK's own common BridgeJob gate for ROS 2 observation, inspection and cancellable cell work.
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — safe high-level board-flow coordinator for OpenPnP pick-and-place — uses this SDK's own correlated, idempotent jobs for traceable PCB hand-offs.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — safe coordination boundary for Moonraker/Klipper 3D printers, with real gated job commands — uses this SDK's own gate around native printer readiness; it does not expose heater or motion control.
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — high-level CNC-cell coordinator with GRBL status/control-byte access (tested against an emulator only) — uses this SDK's own gate to coordinate only alongside an idle, safeguarded CNC.
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — laser-cell coordinator reading 3 key/enclosure/interlock GPIO signals (tested against a fake chip only; it cannot arm or fire a laser) — uses this SDK's own gate for auxiliaries while preserving laser safety authority.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — coordination boundary for AGV/AMR fleets via a VDA 5050 MQTT publisher (tested against an emulated fleet only) — also validates its own commands against this same shared job-and-safety gate.
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — coordination boundary for legged/humanoid droids, with a Boston Dynamics Spot command sender (tested against an emulator only) — also validates its own commands against this same shared job-and-safety gate.
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — coordination boundary for camera-equipped UAVs, with a MAVLink command sender (tested against an emulator only) — also validates its own commands against this same shared job-and-safety gate.

**Also Part of the Ecosystem**

*Core Backend & Clients*
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — web control dashboard with real-time multi-robot 3D visualization.
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — desktop (PySide6) swarm command center for multiple servers at once, packaged as a standalone executable.
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — native Android control app with biometric login and a paired Wear OS companion.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — iOS/iPadOS control app (Flutter) with real-time WebSocket sync.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — native touch UI for the onboard 7" DSI touchscreen, embedded on the CM5 itself.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — desktop graphical URDF creator/editor that pushes finished models into STUDIO's own catalog.
- **[HYDRA-UMC-EDITOR-STL](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-STL)** — desktop STL model editor, transforming/replacing/removing/adding real parts in the same model catalog HYDRA-UMC-EDITOR-URDF also edits.

*URTC Tool Platform*
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — desktop GUI flashing tool for URTC boards, CAN-OTA plus full-chip SWD/JTAG.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — desktop live CAN-bus diagnostic tool for URTC boards, one panel per tool profile.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — browser-based alternative to URTC-TESTER via the Web Serial API, no local install needed.
- **[URTC-GATEWAY](https://github.com/JuanenRac/URTC-GATEWAY)** — gateway in front of the URTC CAN bus: an allowed list of identifiers, a rate limit and a session key; software tested on a computer, not yet on a real bus.

*Vision AI Node (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — integration hub for the Hailo-8 vision pipeline, with a real per-stage hardware-readiness check.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — real compiled-model registry with Hailo-architecture/checksum safe-load verification.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — real GStreamer pipeline + MediaMTX config generator with a real HailoRT integration boundary.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — Position-Based Visual Servoing correction law with authorisation gated on the zone state; no camera pose estimation yet.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — v0 zone-breach, calibration-freshness and E-STOP-request logic that takes object positions from a file; no detector feeds it and no physical E-STOP is wired to it yet.

*Cognitive AI Node (Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — integration hub for the Hailo-10 cognitive pipeline (LLM/VLA/voice orchestration).
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — real action-token encoding/decoding and trajectory generation for a Vision-Language-Action model.
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — real voice front-end (VAD + intent parser) with a bounded, confirmation-gated Watch relay.
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — real rule-based task decomposition and semantic error recovery over MCU error codes.
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — real stdlib-only TF-IDF document search over this ecosystem's own Markdown docs.
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — local, policy-gated AI maintenance technician for the ecosystem itself - observes, diagnoses and proposes fixes; the two highest risk levels are deliberately not implemented yet.

*Orchestration & Swarm*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — integration hub with a real gRPC/Protobuf health-report contract and mission state machine.
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — real priority-based job queue with deduplication, over a real HTTP API.
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — real gRPC-based fleet health watchdog with retry/backoff and identity-mismatch detection.
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — real RRT-based 3D path planner with real obstacle/workspace collision validation.
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — real CRDT LWW-Element-Map state sync, property-tested for multi-cell convergence.

*Digital Twin & Simulation*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — integration hub for the digital-twin engine, with a real version-compatibility sync contract.
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — hardware-in-the-loop router with a software collision interlock between simulation and real hardware (tested without real hardware).
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — real forward kinematics and joint-limit validation over a real URDF subset.
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — real procedural 2D scene generator with YOLO/COCO annotation export.

*Data & Analytics*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — real sqlite3-backed time-series store with a real ingest/query HTTP API.
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — real FFT + statistical baseline anomaly detector with drift monitoring.
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — real OEE/availability calculation over DATALAKE history, with reproducible CSV export.
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — real CAN/WebSocket ingestion pipeline into DATALAKE, with sequence deduplication.

*Industrial Gateway*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — integration hub relaying to industrial protocols, with a real command allowlist/backpressure layer.
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — real OPC-UA address space, verified with a real binary-protocol client session.
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — real MQTT broker with optional per-client authentication and topic ACLs.
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — real MTConnect `/probe` and `/current` XML endpoints with degraded-mode output.

*Complementary Tools & Ecosystem Operations*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — Smart Summaries and Anomaly Highlighting panels over DATALAKE/ANOMALY-DETECTOR, with an honest statistical fallback.
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — fleet CLI with a real, stable exit-code contract, a genuine live client of HYDRA-UMC-SERVER's own API.
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — WearOS companion app with haptic alert patterns and a paired-phone voice relay (not yet run on a physical watch).
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware for a board-mounting rack with real tool-ID decoding and Smart Idle pre-heating logic.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware plus a real Python vision companion for a thermal/RGB inspection tool head.

## 📚 Documentation

Where to read more:

* [Security baseline of the ecosystem](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)
* [Threat model of the ecosystem](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)
* [Changelog of this repository](CHANGELOG.md)
* [License of this repository](LICENSE.md)

## 🤝 Contributing & Community

* Before a pull request run `HYDRA_UMC_CI=1 py -3 tools/ci_validate.py` (or `HYDRA_UMC_CI=1 python3 tools/ci_validate.py`): it must print `CI_VALIDATION=PASS`. Do not run `build.sh` or `build.bat` for this check; building is not a check.
* The eight READMEs are written from one source in HYDRA-UMC-DOCS; do not edit them by hand. Change the source and write them again with `tools/make_readmes.py`.
* Do not state in a README what has not run: say "simulated" or "not tried on hardware" where that is the truth.
* See [CONTRIBUTING.md](CONTRIBUTING.md), the [code of conduct](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md) and [SUPPORT.md](SUPPORT.md).

## 👤 AUTHOR

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 LICENSE

GPL-3.0-or-later - [LICENSE](LICENSE).

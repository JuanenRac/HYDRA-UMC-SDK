<!--
=============================================================================
HYDRA-UMC-SDK - Public contract and integration toolkit overview
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
CC BY-SA 4.0 - see LICENSE.md
=============================================================================
-->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-SDK banner" width="100%">
</p>

<p align="center">
  🇺🇸 <b>English</b> |
  <a href="README_spa.md">🇪🇸 Español</a> |
  <a href="README_fra.md">🇫🇷 Français</a> |
  <a href="README_ita.md">🇮🇹 Italiano</a> |
  <a href="README_deu.md">🇩🇪 Deutsch</a> |
  <a href="README_zho.md">🇨🇳 简体中文</a> |
  <a href="README_jpn.md">🇯🇵 日本語</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0-blue.svg" alt="License: GPL 3.0">
  <img src="https://img.shields.io/badge/Contracts-Protobuf%20%7C%20JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="Contracts: Protobuf | JSON Schema | OpenAPI">
  <img src="https://img.shields.io/badge/Reference%20client-Python-blueviolet.svg" alt="Reference client: Python">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="Integration: CM5 | URTC">
</p>

# HYDRA-UMC-SDK

## 🧩 Shared contracts and integration toolkit for HYDRA-UMC

HYDRA-UMC-SDK defines the stable language shared by HYDRA-UMC services,
clients, CM5 adapters, and URTC integrations. It owns normative contracts, a
dependency-free Python reference validator, conformance fixtures, and
integration guidance. It does not
replace official APIs for Raspberry Pi OS, Hailo, ROS 2, MQTT, OPC-UA, or
MTConnect.

## 🚧 Status

JSON Schema v1 contracts, valid/invalid fixtures, a Python validation client,
and host-side tests are implemented. Protobuf/OpenAPI publication and clients
for further languages are subsequent compatibility milestones.

## 🎯 First milestone

1. Publish `DeviceDescriptor`, `HealthReport`, `SafetyState`, and
   `UpdateManifest` JSON Schema v1.
2. Validate valid and invalid fixtures with the Python reference client.
3. Add a producer/consumer compatibility matrix in CI.
4. Publish Protobuf/OpenAPI representations where the integration requires it.
5. Add TypeScript, Go, and Rust clients from stable contracts.

## 📂 Repository layout

<p align="center">
  <img src="images/REPOSITORY_LAYOUT.svg" alt="Visual map of the HYDRA-UMC-SDK repository layout" width="100%">
</p>

| Path | Purpose |
| --- | --- |
| `contracts/` | Normative JSON Schema v1 sources; further representations follow stable contracts. |
| `clients/` | Dependency-free Python reference validator and future language clients. |
| `conformance/` | Valid and invalid v1 fixtures used by compatibility tests. |
| `docs/` | Contract, API, security, and development specifications. |
| `examples/` | Runnable Python validation example. |

Read [the contract guide](docs/CONTRACTS.md) before defining a new message.

## 🔗 Related Projects

> Canonical public ecosystem relationship map.

| Project | Relationship with HYDRA-UMC-SDK |
| --- | --- |
| [HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS) | Device agent consumer of device, health, safety, and update contracts. |
| [HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER) | Authenticated API producer and consumer governed by SDK contracts. |
| [HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER) | Publishes version and compatibility metadata consumed by contract-aware clients. |
| [HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC) | Hardware/firmware platform exposed through bounded CM5 and MCU adapter contracts. |
| [URTC](https://github.com/JuanenRac/URTC) | Independent tool-controller platform connected through versioned integration adapters. |

**Rest of the ecosystem:** explore the seven public layers in the [JuanenRac ecosystem dashboard](https://juanenrac.github.io/JuanenRac/).

## 📜 License

Code is GPL-3.0-or-later; documentation is CC BY-SA 4.0. See [LICENSE](LICENSE).

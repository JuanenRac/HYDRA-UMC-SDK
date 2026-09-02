<!--
=========================================================================
HYDRA-UMC-SDK – Übersicht über das Toolkit für öffentliche Verträge und Integration
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
CC BY-SA 4.0 – siehe LICENSE.md
=========================================================================
-->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-SDK-Banner" width="100%">
</p>

<p align="center">
  <a href="README.md">🇺🇸 English</a> |
  <a href="README_spa.md">🇪🇸 Spanisch</a> |
  <a href="README_fra.md">🇫🇷 Französisch</a> |
  <a href="README_ita.md">🇮🇹 Italienisch</a> |
  <a href="README_deu.md">🇩🇪 Deutsch</a> |
  <a href="README_zho.md">🇨🇳 简体中文</a> |
  <a href="README_jpn.md">🇯🇵 日本語</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0-blue.svg" alt="Lizenz: GPL 3.0">
  <img src="https://img.shields.io/badge/Contracts-Protobuf%20%7C%20JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="Verträge: Protobuf | JSON Schema | OpenAPI">
  <img src="https://img.shields.io/badge/Reference%20client-Python-blueviolet.svg" alt="Referenzclient: Python">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="Integration: CM5 | URTC">
</p>

# HYDRA-UMC-SDK

## 🧩 Gemeinsame Verträge und Integrations-Toolkit für HYDRA-UMC

HYDRA-UMC-SDK definiert die stabile Sprache, die von HYDRA-UMC-Diensten,
Clients, CM5-Adaptern und URTC-Integrationen gemeinsam genutzt wird. Es besitzt normative Verträge, einen
abhängigkeitsfreien Python-Referenzvalidator, Konformitäts-Fixtures und
Integrationsberatung. Es ersetzt nicht die offiziellen APIs für Raspberry Pi OS, Hailo, ROS 2, MQTT, OPC-UA oder
MTConnect.

## 🚧 Status

JSON Schema v1-Verträge, gültige/ungültige Fixtures, ein Python-Validierungsclient,
und hostseitige Tests werden implementiert. Protobuf/OpenAPI-Veröffentlichung und Clients
für weitere Sprachen sind spätere Kompatibilitätsmeilensteine.

Eine echte, automatische Kompatibilitätsmatrix (`tools/verify_contract_matrix.py`)
gleicht jedes veröffentlichte Schema mit der eigenen Vertragsliste des
Python-Validators ab - sie fand und behob eine echte Lücke, bei der
`project-manifest.schema.json` (der Vertrag für `hydra-umc.project.json`, den
jedes Repository in diesem Ökosystem veröffentlicht) keinen Validator-Eintrag
hatte, und beweist nun, dass jede Konformitäts-Fixture so beurteilt wird, wie
es ihr eigener Dateiname behauptet, ebenso wie die Fälle unbekannter Vertrag
und inkompatible Schema-Version.

## 🎯 Erster Meilenstein

1. Veröffentlichen Sie `DeviceDescriptor`, `HealthReport`, `SafetyState` und
   `UpdateManifest` JSON-Schema v1.
2. Validieren Sie gültige und ungültige Fixtures mit dem Python-Referenzclient.
3. Fügen Sie in CI eine Produzenten-/Konsumenten-Kompatibilitätsmatrix hinzu.
4. Veröffentlichen Sie Protobuf/OpenAPI-Darstellungen dort, wo die Integration dies erfordert.
5. Fügen Sie TypeScript-, Go- und Rust-Clients aus stabilen Verträgen hinzu.

## 📂 Repository-Layout

<p align="center">
  <img src="images/REPOSITORY_LAYOUT.svg" alt="Visuelle Karte des HYDRA-UMC-SDK-Repository-Layouts" width="100%">
</p>

| Pfad | Zweck |
| --- | --- |
| `contracts/` | Normative JSON-Schema-v1-Quellen; weitere Darstellungen folgen stabilen Verträgen. |
| `clients/` | Abhängigkeitsfreier Python-Referenzvalidator und zukünftige Sprachclients. |
| `conformance/` | Gültige und ungültige v1-Fixtures, die von Kompatibilitätstests verwendet werden. |
| `docs/` | Vertrags-, API-, Sicherheits- und Entwicklungsspezifikationen. |
| `examples/` | Beispiel für eine ausführbare Python-Validierung. |

Lesen Sie [den Vertragsleitfaden](docs/CONTRACTS.md), bevor Sie eine neue Nachricht definieren.

## 🛠️ BUILD UND AUSFÜHRUNG

Verwenden Sie den Build-Check ohne Versionierung vor einem Release-Build:

| Aktion | Windows | Linux / macOS |
|---|---|---|
| Build-Check (ohne Änderung von Version oder CHANGELOG) | `build-test.bat` | `./build-test.sh` |
| Ausführung / Entwicklung (falls vorhanden) | `run*.bat` oder `dev*.bat` | `./run*.sh` oder `./dev*.sh` |

`build-test.bat` und `build-test.sh` kompilieren oder validieren den Projekt-Stack, ohne `hydra-umc.project.json` zu erhöhen oder `CHANGELOG.md` zu verändern. Sie dürfen nur normale Compiler-Ausgaben erzeugen. Die vorhandenen Skripte `build*.bat`, `build*.sh`, `run*` und `dev*` behalten ihr projektbezogenes Versions- oder Laufzeitverhalten bei; verwenden Sie sie, wenn dieses Verhalten benötigt wird.

## 🔗 Verwandte Projekte

> Kanonische Karte der öffentlichen Ökosystembeziehungen.

| Projekt | Beziehung mit HYDRA-UMC-SDK |
| --- | --- |
| [HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS) | Geräteagent-Verbraucher von Geräte-, Gesundheits-, Sicherheits- und Updateverträgen. |
| [HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER) | Authentifizierter API-Produzent und -Konsumer, der durch SDK-Verträge geregelt wird. |
| [HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER) | Veröffentlicht Versions- und Kompatibilitätsmetadaten, die von vertragsbewussten Clients verwendet werden. |
| [HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC) | Hardware-/Firmware-Plattform wird durch begrenzte CM5- und MCU-Adapterverträge verfügbar gemacht. |
| [URTC](https://github.com/JuanenRac/URTC) | Unabhängige Tool-Controller-Plattform, verbunden über versionierte Integrationsadapter. |
| [HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2) | Nutzt das gemeinsame BridgeJob-Gate für ROS-2-Beobachtung, Prüfung und abbrechbare Zellarbeit. |
| [HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP) | Nutzt korrelierte und idempotente Jobs für nachverfolgbare PCB-Übergaben. |
| [HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D) | Nutzt das Gate um die native Druckerbereitschaft, ohne Heizungs- oder Bewegungssteuerung freizugeben. |
| [HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC) | Nutzt das Gate nur neben einer stillstehenden, geschützten CNC. |
| [HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER) | Nutzt das Gate für Hilfsfunktionen und bewahrt die Laser-Sicherheitsautorität. |

**Rest des Ökosystems:** Erkunden Sie die sieben öffentlichen Ebenen im [JuanenRac-Ökosystem-Dashboard](https://juanenrac.github.io/JuanenRac/).

## 👤 AUTOR
**JuanenRac** (Electro Hobby 3D)
📧 electrohobby3d@gmail.com
📺 [youtube.com/@electrohobby3d](https://youtube.com/@electrohobby3d)

## 📜 LIZENZ

Code ist GPL-3.0-or-later; Die Dokumentation ist CC BY-SA 4.0. Siehe [LICENSE](LICENSE).

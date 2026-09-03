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

Seit dem ersten Meilenstein unten sind zwei weitere Verträge
hinzugekommen: ein öffentlicher `BridgeJob`/`GateDecision`-Vertrag für
externe Maschinenanbindung (siehe
[docs/BRIDGE_CONTRACT.md](docs/BRIDGE_CONTRACT.md)), gemeinsam genutzt
von `HYDRA-UMC-BRIDGE-ROS2`/`-OPENPNP`/`-PRINTER3D`/`-CNC`/`-LASER` und
mit einer eigenen echten JSON-Wire-Form (`job_to_dict()`/
`job_from_dict()`/`decision_to_dict()`); und ein
`hydra-umc-sdk-mock-server` (`mock_server.py`), der für jeden bekannten
Vertrag ein gültiges Beispiel-Payload über einfaches HTTP bereitstellt,
damit eine UI oder ein Adapter entwickelt werden kann, bevor echte
CM5-/Roboter-/MCU-Hardware verfügbar ist. Alle 7 Verträge besitzen
mindestens eine gültige und eine ungültige Konformitäts-Fixture, geprüft
durch die obige Kompatibilitätsmatrix.

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
| `tools/` | `verify_contract_matrix.py` (Schema-/Validator-Kompatibilitätsmatrix) und die nicht verändernde `build-test`-Engine. |

Lesen Sie [den Vertragsleitfaden](docs/CONTRACTS.md), bevor Sie eine neue Nachricht definieren.

## 📖 Weitere Dokumentation

- **[docs/CONTRACTS.md](docs/CONTRACTS.md)** — der normative Vertragsleitfaden: vor dem Definieren einer neuen Nachricht lesen.
- **[docs/PYTHON_CLIENT.md](docs/PYTHON_CLIENT.md)** — vollständige Referenz für die Funktion `validate()` und die CLI `hydra-umc-contract-validate`, mit der Tabelle der Pflichtfelder und Zusatzregeln je Vertrag.
- **[docs/CONFORMANCE.md](docs/CONFORMANCE.md)** — was ein gültiges/abwärtskompatibles/fehlerhaftes/unsicheres Fixture-Set je Vertrag abdecken muss, und was die implementierte v1-Suite heute abdeckt.
- **[docs/BRIDGE_CONTRACT.md](docs/BRIDGE_CONTRACT.md)** — die gemeinsame v0-Grenze `BridgeJob`/`GateDecision`, genutzt von `HYDRA-UMC-BRIDGE-ROS2`, `-OPENPNP`, `-PRINTER3D`, `-CNC` und `-LASER`.
- **[docs/ADAPTERS.md](docs/ADAPTERS.md)** — die CM5-MCU/URTC-Adaptergrenze: Transport-, Framing-, Protokoll- und Service-Schichten, und warum der MCU für physische Grenzen und den sicheren Halt maßgeblich bleibt.
- **[docs/API_DESIGN.md](docs/API_DESIGN.md)** — die Konventionen, denen die eigene öffentliche HTTP/WebSocket-API von HYDRA-UMC-SERVER folgt: versionierte `/api/v1`-Routen und die `ACCEPTED`/`REJECTED`/`RUNNING`/`COMPLETED`/`FAILED`-Form des Befehlsergebnisses.
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** — der Schema-First-Workflow, unter dem die eigenen Verträge dieses SDKs entwickelt werden, und was eine Vertragsänderung erfordert (Changelog-Eintrag, Kompatibilitätsentscheidung, Beispiele, Tests).
- **[docs/PROJECT_MANIFEST.md](docs/PROJECT_MANIFEST.md)** — der `hydra-umc.project.json`-Vertrag, den jedes Repository in diesem Ökosystem veröffentlicht.
- **[docs/HEADER_CONVENTION.md](docs/HEADER_CONVENTION.md)** — der erforderliche Copyright-/Lizenz-Header für neue Quell- und Dokumentationsdateien in diesem gesamten Ökosystem.

## 🛠️ BUILD UND AUSFÜHRUNG

Verwenden Sie den Build-Check ohne Versionierung vor einem Release-Build:

| Aktion | Windows | Linux / macOS |
|---|---|---|
| Build-Check (ohne Änderung von Version oder CHANGELOG) | `build-test.bat` | `./build-test.sh` |
| Ausführung / Entwicklung (falls vorhanden) | `run*.bat` oder `dev*.bat` | `./run*.sh` oder `./dev*.sh` |

`build-test.bat` und `build-test.sh` kompilieren oder validieren den Projekt-Stack, ohne `hydra-umc.project.json` zu erhöhen oder `CHANGELOG.md` zu verändern. Sie dürfen nur normale Compiler-Ausgaben erzeugen. Die vorhandenen Skripte `build*.bat`, `build*.sh`, `run*` und `dev*` behalten ihr projektbezogenes Versions- oder Laufzeitverhalten bei; verwenden Sie sie, wenn dieses Verhalten benötigt wird.

## 🔗 Verwandte Projekte

Dieses Projekt ist Teil des HYDRA-UMC-Robotik-Ökosystems desselben Autors (JuanenRac / Electro Hobby 3D). Gut zu wissen, da eine Anfrage eigentlich eines dieser Projekte betreffen könnte statt dieses Repositorys.

**Übergeordnetes Projekt**
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — reproduzierbare Raspberry-Pi-OS-Produktschicht für den CM5: schreibgeschützter Agent, validierte Konfiguration/Profile, WiFi-Ersteinrichtung; ein Geräte-Agent, der die eigenen Geräte-, Health-, Sicherheits- und Update-Verträge dieses SDKs konsumiert.

**Direkt verwandt**
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — das reale Headless-Backend (REST/WebSocket), mit dem jeder Steuerungsclient tatsächlich spricht — ein authentifizierter API-Produzent und -Konsument, der den eigenen Verträgen dieses SDKs unterliegt.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — administratives Desktop-Tool, das jedes Repository in diesem Ökosystem entdeckt, klont und aktualisiert — veröffentlicht Versions- und Kompatibilitätsmetadaten, die von den eigenen vertragskundigen Clients dieses SDKs konsumiert werden.
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — das physische Motherboard des Roboterarms: CM5-Host + Dual-Core-STM32H745, koordiniert bis zu 8 Werkzeugarme über CAN-OTA/SPI-OTA — die Hardware-/Firmware-Plattform, die über die eigenen begrenzten CM5- und MCU-Adapterverträge dieses SDKs freigelegt wird.
- **[URTC](https://github.com/JuanenRac/URTC)** — Firmware für die physische Universal-Robot-Tool-Controller-Platine, 25+ Werkzeugprofile über CAN-Bus — eine unabhängige Werkzeugcontroller-Plattform, verbunden über die eigenen versionierten Integrationsadapter dieses SDKs.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — Sicherheitskoordinator mit einem echten, träge importierten rclpy-ROS-2-Transport — nutzt das eigene gemeinsame BridgeJob-Gate dieses SDKs für ROS-2-Beobachtung, -Inspektion und abbrechbare Zellarbeit.
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — sicherer High-Level-Koordinator für den Leiterplattenfluss von OpenPnP Pick-and-Place — nutzt die eigenen korrelierten, idempotenten Jobs dieses SDKs für nachverfolgbare Leiterplattenübergaben.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — sichere Koordinationsschranke für Moonraker/Klipper-3D-Drucker, mit echten gesicherten Job-Befehlen — nutzt das eigene Gate dieses SDKs rund um die native Druckerbereitschaft; es legt weder Heizungs- noch Bewegungssteuerung offen.
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — High-Level-Koordinator für CNC-Zellen mit echtem GRBL-Status-/Steuerbyte-Zugriff — nutzt das eigene Gate dieses SDKs, um nur neben einer inaktiven, gesicherten CNC zu koordinieren.
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — Sicherheitskoordinator für Laserzellen, liest 3 echte Schlüssel-/Gehäuse-/Verriegelungs-GPIO-Sicherungen — nutzt das eigene Gate dieses SDKs für Hilfsfunktionen, während die Sicherheitsautorität des Lasers erhalten bleibt.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — Koordinationsschranke für AGV-/AMR-Flotten über einen echten VDA-5050-MQTT-Publisher — validiert seine eigenen Befehle ebenfalls gegen dieselbe gemeinsame Job-und-Sicherheits-Schranke.
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — Koordinationsschranke für laufende/humanoide Droiden, mit einem echten Boston-Dynamics-Spot-Befehlssender — validiert seine eigenen Befehle ebenfalls gegen dieselbe gemeinsame Job-und-Sicherheits-Schranke.
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — Koordinationsschranke für kameraausgestattete UAVs, mit einem echten MAVLink-Befehlssender — validiert seine eigenen Befehle ebenfalls gegen dieselbe gemeinsame Job-und-Sicherheits-Schranke.

**Ebenfalls Teil des Ökosystems**

*Kern-Backend & Clients*
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — Web-Steuerungs-Dashboard mit Echtzeit-3D-Visualisierung mehrerer Roboter.
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — Desktop-Schwarmleitstand (PySide6) für mehrere Server gleichzeitig, verpackt als eigenständige ausführbare Datei.
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — native Android-Steuerungs-App mit biometrischem Login und einer gekoppelten Wear-OS-Begleit-App.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — iOS/iPadOS-Steuerungs-App (Flutter) mit Echtzeit-WebSocket-Synchronisierung.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — native Touch-UI für das eingebaute 7"-DSI-Touchscreen, direkt auf dem CM5 eingebettet.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — grafischer Desktop-URDF-Ersteller/-Editor, der fertige Modelle in STUDIOs eigenen Katalog überträgt.

*URTC-Werkzeugplattform*
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — Desktop-GUI-Flash-Tool für URTC-Platinen, CAN-OTA plus Full-Chip-SWD/JTAG.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — Desktop-Live-CAN-Bus-Diagnosetool für URTC-Platinen, ein Panel pro Werkzeugprofil.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — browserbasierte Alternative zu URTC-TESTER über die Web-Serial-API, ohne lokale Installation.

*Vision-KI-Knoten (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — Integrationsknoten für die Hailo-8-Vision-Pipeline, mit einer echten stufenweisen Hardware-Bereitschaftsprüfung.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — echte Registry für kompilierte Modelle mit Hailo-Architektur-/Prüfsummen-Safe-Load-Verifizierung.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — echter GStreamer-Pipeline- + MediaMTX-Konfigurationsgenerator mit einer echten HailoRT-Integrationsschranke.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — echtes Position-Based-Visual-Servoing-Korrekturgesetz, sicherheitsgesteuert nach vorgelagertem Zonenstatus.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — echte Zonenverletzungsprüfung und E-STOP-Anforderung, mit erzwungener Kalibrierungsaktualität.

*Kognitiver KI-Knoten (Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — Integrationsknoten für die Hailo-10-Cognitive-Pipeline (LLM-/VLA-/Sprach-Orchestrierung).
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — echte Aktions-Token-Kodierung/-Dekodierung und Trajektoriengenerierung für ein Vision-Language-Action-Modell.
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — echtes Sprach-Frontend (VAD + Intent-Parser) mit einem begrenzten, bestätigungsgesicherten Watch-Relay.
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — echte regelbasierte Aufgabenzerlegung und semantische Fehlerbehebung über MCU-Fehlercodes.
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — echte, nur auf der Standardbibliothek basierende TF-IDF-Dokumentensuche über die eigenen Markdown-Dokumente dieses Ökosystems.

*Orchestrierung & Schwarm*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — Integrationsknoten mit einem echten gRPC/Protobuf-Health-Report-Vertrag und einer Missions-Zustandsmaschine.
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — echte prioritätsbasierte Job-Queue mit Deduplizierung, über eine echte HTTP-API.
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — echter gRPC-basierter Flotten-Health-Watchdog mit Retry/Backoff und Identitäts-Mismatch-Erkennung.
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — echter RRT-basierter 3D-Pfadplaner mit echter Hindernis-/Arbeitsraum-Kollisionsvalidierung.
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — echte CRDT-LWW-Element-Map-Zustandssynchronisation, eigenschaftsgetestet auf Multi-Zellen-Konvergenz.

*Digitaler Zwilling & Simulation*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — Integrationsknoten für die Digital-Twin-Engine, mit einem echten Versionskompatibilitäts-Sync-Vertrag.
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — echte Hardware-in-the-Loop-Sicherheitsverriegelung, die Befehle zwischen Simulation und echter Hardware routet.
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — echte Vorwärtskinematik und Gelenkgrenzenvalidierung über eine echte URDF-Teilmenge.
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — echter prozeduraler 2D-Szenengenerator mit YOLO/COCO-Annotationsexport.

*Daten & Analytik*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — echter sqlite3-gestützter Zeitreihenspeicher mit einer echten Ingest-/Abfrage-HTTP-API.
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — echter FFT- + statistischer Basislinien-Anomaliedetektor mit Drift-Überwachung.
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — echte OEE-/Verfügbarkeitsberechnung über den DATALAKE-Verlauf, mit reproduzierbarem CSV-Export.
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — echte CAN/WebSocket-Ingestion-Pipeline in DATALAKE, mit Sequenz-Deduplizierung.

*Industrie-Gateway*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — Integrationsknoten, der zu Industrieprotokollen weiterleitet, mit einer echten Befehls-Allowlist-/Backpressure-Schicht.
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — echter OPC-UA-Adressraum, verifiziert mit einer echten Binärprotokoll-Client-Session.
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — echter MQTT-Broker mit optionaler Pro-Client-Authentifizierung und Topic-ACLs.
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — echte MTConnect-`/probe`- und `/current`-XML-Endpunkte mit Degraded-Mode-Ausgabe.

*Ergänzende Tools & Ökosystembetrieb*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — Smart-Summaries- und Anomaly-Highlighting-Panels über DATALAKE/ANOMALY-DETECTOR, mit einem ehrlichen statistischen Fallback.
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — Flotten-CLI mit einem echten, stabilen Exit-Code-Vertrag, ein echter Live-Client der eigenen API von HYDRA-UMC-SERVER.
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — WearOS-Begleit-App mit echten haptischen Alarmen und einem Sprach-Relay zum gekoppelten Telefon.
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — Firmware für ein Platinenmontagegestell mit echter Werkzeug-ID-Dekodierung und Smart-Idle-Vorheizlogik.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — Firmware plus ein echter Python-Vision-Begleiter für einen Thermal-/RGB-Inspektionswerkzeugkopf.

---

## 📚 Dokumentation & Community

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Technologie-Stack und Coding-Richtlinien für einen Pull Request.
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** — die in dieser Community erwarteten Verhaltensstandards.
- **[SECURITY.md](SECURITY.md)** — wie man eine Schwachstelle meldet, und die echten Sicherheitsschwerpunkte dieses Projekts.
- **[SUPPORT.md](SUPPORT.md)** — wo man Fragen stellt und Fehler meldet.

## 👤 AUTOR
**JuanenRac** (Electro Hobby 3D)
📧 electrohobby3d@gmail.com
📺 [youtube.com/@electrohobby3d](https://youtube.com/@electrohobby3d)

## 📜 LIZENZ

Code ist GPL-3.0-or-later; Die Dokumentation ist CC BY-SA 4.0. Siehe [LICENSE](LICENSE).

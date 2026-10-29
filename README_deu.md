<!-- =============================================================================
HYDRA-UMC-SDK - Shared contracts and integration toolkit
Copyright (C) JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-SDK banner" width="100%">
</p>

# 🧰 HYDRA-UMC-SDK

<p align="center"><a href="README.md">🇺🇸 English</a> | <a href="README_spa.md">🇪🇸 Español</a> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | 🇩🇪 <b>Deutsch</b> | <a href="README_zho.md">🇨🇳 简体中文</a> | <a href="README_jpn.md">🇯🇵 日本語</a> | <a href="README_por.md">🇵🇹 Português</a></p>

### 🧰 Gemeinsame Verträge, Referenz-Clients und Integrationswerkzeuge für HYDRA-UMC

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Contracts-JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="Contracts">
  <img src="https://img.shields.io/badge/Reference%20clients-Python%20%7C%20Go%20%7C%20TypeScript%20%7C%20Rust-blueviolet.svg" alt="Reference%20clients">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="Integration">
  <img src="https://img.shields.io/badge/Tests-463%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.3.8-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-established-2EA44F.svg" alt="Maturity">
</p>

---

> **Ehrlichkeitscheck - was heute wirklich läuft:** die zehn JSON-Schema-v1-Verträge mit je einer gültigen und einer ungültigen Fixture, der Python-Validator, der erste OpenAPI-v1-Ausschnitt von HYDRA-UMC-SERVER, die Go-, TypeScript- und Rust-Clients, die dieselben Schemas durchsetzen, die Bridge-Helfer und die Kompatibilitätsmatrix sind echt und auf einem Rechner getestet (463 Python-Tests, dazu die Suiten der anderen drei Clients). Protobuf ist noch nicht veröffentlicht, das Job-Gate ist eine gemeinsame Software-Funktion und keine zertifizierte Sicherheitsfunktion, und nichts davon lief auf echter Hardware.

---

> **Stand von Sicherheit (Safety) und Security:** Dieses Ökosystem ist kein zertifiziertes Sicherheitssystem. Es gibt noch keinen Hardware-E-STOP-Pfad, keine von der Firmware durchgesetzten Grenzen oder Verriegelungen und keinen verifizierten Bewegungsbefehl; Firmware-Images werden mit CRC32 und einem HMAC-SHA256 mit gemeinsamem Schlüssel geprüft, nicht mit einer asymmetrischen Signatur; TLS und gegenseitiges TLS sind optional und standardmäßig aus; noch keine eigene Platine wurde bestückt oder getestet. Lesen Sie die [Sicherheitsbasis](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md) und das [Bedrohungsmodell](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md), bevor Sie sich für die Sicherheit einer Person auf eine Aussage hier verlassen.

---

## 📋 Auf einen Blick

| | |
|---|---|
| Version | `0.3.8` |
| Reifegrad | Etabliert |
| Tests | 463 (`python -m unittest discover -s clients/python/tests`) |
| Technik | Python / TypeScript / Go / Rust / JSON Schema |
| Auf echter Hardware | Noch nicht: für diese Version ist kein Lauf auf echter Hardware vermerkt |

**Springe zu:** [Überblick](#-überblick) · [Architektur](#-architektur) · [Funktionen](#-funktionen) · [Sicherheit und Schutz](#-sicherheit-und-schutz) · [Schnittstellen](#-schnittstellen) · [Konfiguration](#-konfiguration) · [Schnellstart](#-schnellstart) · [Tests](#-tests) · [Fehlerbehebung](#-fehlerbehebung) · [Struktur des Repositorys](#-struktur-des-repositorys) · [Verwandte Projekte](#-verwandte-projekte)

## 🚦 Projektstatus

Jede Zeile ist ein Teil dieses Repositorys, und die Ampel sagt, wie weit er heute ist. Sie beruht auf dem, was das Repository zeigen kann (Tests, Builds, Läufe), nicht auf dem, was geplant ist.

🟢 Fertig und überprüft · 🟡 Funktioniert, mit bekannten Grenzen · 🟠 Teilweise fertig oder noch nicht überprüft · 🔴 Nicht gemacht oder funktioniert nicht

| Bereich | Stand | Was das hier bedeutet |
|---|---|---|
| Software | 🟢 | Für seinen Zweck vollständig und stabil; die Ehrlichkeitsprüfung oben nennt die bekannten Grenzen |
| Tests | 🟢 | 463 automatische Tests, bei jeder Änderung ausgeführt |
| Echte Hardware | 🔴 | Noch nicht: für diese Version ist kein Lauf auf echter Hardware vermerkt |
| Dokumentation | 🟢 | README in acht Sprachen, bei jeder Änderung gegen das Manifest geprüft |

## 🎯 Überblick

HYDRA-UMC-SDK definiert die stabile Sprache, die von HYDRA-UMC-Diensten,
Clients, CM5-Adaptern und URTC-Integrationen gemeinsam genutzt wird. Es besitzt normative Verträge, einen
abhängigkeitsfreien Python-Referenzvalidator, Konformitäts-Fixtures und
Integrationsberatung. Es ersetzt nicht die offiziellen APIs für Raspberry Pi OS, Hailo, ROS 2, MQTT, OPC-UA oder
MTConnect.

## 🧩 Rolle in HYDRA-UMC

**HYDRA-UMC-SDK** ist die gemeinsame Sprache des Ökosystems: die JSON-Schema-v1-Verträge, der erste OpenAPI-Ausschnitt des Servers, Referenz-Clients in Python, Go, TypeScript und Rust, die Bridge-Helfer, die jede Bridge und der Connector-Hub nutzen, und die Werkzeuge, die das Tooling jedes Repositorys identisch halten. Er betreibt keinen eigenen Dienst und ersetzt keine offizielle API.

## 🏛️ Architektur

<p align="center">
  <img src="images/architecture.svg" alt="HYDRA-UMC-SDK architecture" width="100%">
</p>

## ✨ Funktionen

### Status

JSON Schema v1-Verträge, gültige/ungültige Fixtures, ein Python-Validierungsclient,
und hostseitige Tests werden implementiert, ebenso ein echter erster OpenAPI-v1-Ausschnitt
für die eigene HTTP-Oberfläche von HYDRA-UMC-SERVER (`contracts/openapi/v1/server.openapi.json`
- siehe [docs/CONTRACTS.md](docs/CONTRACTS.md#openapi-v1)). Die Protobuf-Veröffentlichung ist ein späterer Kompatibilitätsmeilenstein; die Clients für Go, TypeScript und Rust gibt es bereits.

Eine echte, automatische Kompatibilitätsmatrix (`tools/verify_contract_matrix.py`)
gleicht jedes veröffentlichte Schema mit der eigenen Vertragsliste des
Python-Validators ab - sie fand und behob eine echte Lücke, bei der
`project-manifest.schema.json` (der Vertrag für `hydra-umc.project.json`, den
jedes Repository in diesem Ökosystem veröffentlicht) keinen Validator-Eintrag
hatte, und beweist nun, dass jede Konformitäts-Fixture so beurteilt wird, wie
es ihr eigener Dateiname behauptet, ebenso wie die Fälle unbekannter Vertrag
und inkompatible Schema-Version.

Seit dem ersten Meilenstein unten sind weitere Verträge
hinzugekommen: ein öffentlicher `BridgeJob`/`GateDecision`-Vertrag für
externe Maschinenanbindung (siehe
[docs/BRIDGE_CONTRACT.md](docs/BRIDGE_CONTRACT.md)), gemeinsam genutzt
von `HYDRA-UMC-BRIDGE-ROS2`/`-OPENPNP`/`-PRINTER3D`/`-CNC`/`-LASER`/`-AMR`/`-DROIDS`/`-UAV` und
mit einer eigenen echten JSON-Wire-Form (`job_to_dict()`/
`job_from_dict()`/`decision_to_dict()`), dazu der Zustand der Maschine, den der Bridge selbst beobachtet und den das Tor statt des vom Anfragenden behaupteten verwendet, und eine Auftragsannahme (`JobIntake`/`IdempotencyStore`), die zurückgehaltene Nachrichten ignoriert und einen Idempotenzschlüssel nie zweimal ausführt; ein `ScenarioOutcome`-Vertrag
plus `compare_runs()`, eine gemeinsame Prüfung "wurde es wirklich
behoben", die `apparent-success` (nicht `regression-fixed`) zurückgibt,
wenn ein Fehler nicht mehr reproduzierbar ist, sich der Basis-Fingerabdruck
aber nie geändert hat; ein `Operation`-Vertrag plus
`validate_status_transition()`, der gemeinsame Ziel-/Auftrags-/
Operations-Lebenszyklus - `received`/`authorized`/`queued`/`sent`/
`confirmed`/`terminated`/`rejected`, niemals ein einziger
"ausgeführt"-Sammeltopf; ein optionales `result` auf `Operation` plus
`concludes_success()` - echte Evidenz (`run_id`/`origin`/
`observers_enabled`/`outcome`), die sich weigert, aus einem veralteten/
wiederholten Ergebnis oder einem Lauf mit deaktivierter Beobachtung
Erfolg zu schließen; ein eigenständiger `Capability`-Vertrag plus
`is_capability_usable()` - ob ein Ziel Unterstützung für eine
Operations-`kind` überhaupt *deklariert*, wird als Datum modelliert, das
sich von der Frage unterscheidet, ob diese Unterstützung *kürzlich
tatsächlich verifiziert* wurde
(`last_checked_at_utc`/`checked_configuration`/`max_age_seconds`), sodass
eine deklarierte, aber nie geprüfte oder veraltete Fähigkeit niemals
stillschweigend als nutzbar behandelt wird; und ein
`hydra-umc-sdk-mock-server` (`mock_server.py`), der für jeden bekannten
Vertrag ein gültiges Beispiel-Payload über einfaches HTTP bereitstellt,
damit eine UI oder ein Adapter entwickelt werden kann, bevor echte
CM5-/Roboter-/MCU-Hardware verfügbar ist. Alle 10 Verträge besitzen
mindestens eine gültige und eine ungültige Konformitäts-Fixture, geprüft
durch die obige Kompatibilitätsmatrix.

## 🔒 Sicherheit und Schutz

| Bedrohung | Abwehr | Wo |
|---|---|---|
| Ein Bridge-Befehl außerhalb seines Vertrags | Ein Job trägt höchstens 32 Parameter, Namen mit 64 Zeichen, Werte mit 1024 und Kennungen mit 128; es gilt der Maschinenzustand, den die Bridge beobachtet, nicht der vom Anfrager behauptete | `bridge_contract.py` |
| Derselbe Befehl zweimal ausgeführt oder eine behaltene Nachricht wiederholt | Die Job-Annahme ignoriert behaltene Nachrichten und führt einen Idempotenzschlüssel nie zweimal aus | `job_intake.py` |
| Ein Stopp, der hinter einem langen Befehl wartet | Gewöhnliche Befehle laufen nacheinander auf einer Spur, die Stopp-Verben auf einer zweiten | `bridge_transport.py` |
| Broker-Zugangsdaten in einer Konfigurationsdatei oder ein ungeprüfter Broker | Benutzer und Passwort kommen aus der Umgebung oder einer Datei, TLS kann den Broker gegen eine CA prüfen, und Client-Zertifikat samt Schlüssel schalten gegenseitiges TLS ein | `mqtt_connection.py` |
| Ein Schema geändert, ohne dass der Validator folgt | Eine Kompatibilitätsmatrix prüft jedes veröffentlichte Schema gegen die Vertragsliste des Validators und beurteilt jede Fixture nach dem, was ihr Dateiname behauptet | `tools/verify_contract_matrix.py` |

**Was er nie tut:** als zertifizierte Sicherheitsfunktion dienen. Das Job-Gate ist eine von den Bridges gemeinsam genutzte Software-Implementierung, keine Sicherheitszertifizierung.

## 🔌 Schnittstellen

| Topic oder Route | Was es trägt |
|---|---|
| `contracts/json-schema/v1/` | zehn JSON-Schema-v1-Verträge: Fähigkeit, Gerätedeskriptor, Ereignis-Umschlag, Gesundheitsbericht, Operation, Projektmanifest, Sicherheitszustand, Szenarioergebnis, Server-Erkennung, Update-Manifest |
| `contracts/openapi/v1/server.openapi.json` | der erste OpenAPI-v1-Ausschnitt von HYDRA-UMC-SERVER: Erkennung, Anmeldung, Einstellungen und Befehle (eine Teilmenge der `docs/openapi.json` des Servers selbst) |
| `contracts/ports.yaml` | das Register von Port, Gesundheitspfad und systemd-Unit jedes Dienstes, erzeugt von `tools/sync_ports.py` |
| `hydra/bridges/<name>/cmd/#` | wo eine Bridge lauscht; sie antwortet auf `.../<verb>/result` |
| `hydra-umc-contract-validate`, `hydra-umc-sdk-mock-server` | der Validator auf der Kommandozeile (Exit-Code 2 bei Fehler) und ein Mock-Server auf `127.0.0.1:8790`, der je Vertrag ein gültiges Beispiel liefert |

## ⚙️ Konfiguration

| Variable | Standard | Was sie festlegt |
|---|---|---|
| `HYDRA_MQTT_USERNAME`, `HYDRA_MQTT_PASSWORD` | keine Zugangsdaten | die Broker-Zugangsdaten; das Passwort nur zusammen mit dem Benutzernamen |
| `HYDRA_MQTT_PASSWORD_FILE` | - | das Passwort aus einer Datei (ein Docker- oder systemd-Secret); wird ignoriert, wenn die Variable oben gesetzt ist |
| `HYDRA_MQTT_TLS`, `HYDRA_MQTT_TLS_CA` | kein TLS | `HYDRA_MQTT_TLS=1` prüft den Broker gegen die System-CAs; `HYDRA_MQTT_TLS_CA` nennt die CA-Datei, die sein Zertifikat signiert hat |
| `HYDRA_MQTT_TLS_CERT`, `HYDRA_MQTT_TLS_KEY` | - | Client-Zertifikat und Schlüssel für einen Broker mit gegenseitigem TLS; beide sind nötig und schalten TLS ein |
| `--host`, `--port` | `127.0.0.1`, `8790` | worauf der Mock-Server lauscht |
| `HYDRA_UMC_SDK_ROOT` | der Nachbarordner | wo die Tests der anderen Repositorys dieses finden |

## 🚀 Schnellstart

Benötigt Python 3.11 oder neuer. Die Clients für Go, TypeScript und Rust werden ebenfalls gebaut und getestet, wenn ihre Toolchain installiert ist.

```bash
PYTHONPATH=clients/python/src python -m unittest discover -s clients/python/tests  # the Python client tests
python tools/verify_contract_matrix.py                                             # every schema against the validator and every fixture
PYTHONPATH=clients/python/src python -m hydra_umc_sdk.validation --help            # the contract validator on the command line
./build-test.sh                                                                    # the non-mutating build check (build-test.bat on Windows)
```

## 🧪 Tests

463 automatische Tests laufen mit `python -m unittest discover -s clients/python/tests`. Los demás clientes tienen sus propias suites: 26 Tests in Go (`go test ./...`), 104 in TypeScript (`npm test`) und 28 in Rust (`cargo test`), ausgeführt von `tools/extra_build_steps.py`, wenn die Toolchain installiert ist. Keiner braucht Hardware.

Die CI führt `HYDRA_UMC_CI=1 python tools/ci_validate.py` aus; das prüft das Manifest, die Dokumente, die acht READMEs und die Bilder.

## 🏗️ Build und Veröffentlichung

Verwenden Sie den Build-Check ohne Versionierung vor einem Release-Build:

| Aktion | Windows | Linux / macOS |
|---|---|---|
| Build-Check (ohne Änderung von Version oder CHANGELOG) | `build-test.bat` | `./build-test.sh` |
| Ausführung / Entwicklung (falls vorhanden) | `run*.bat` oder `dev*.bat` | `./run*.sh` oder `./dev*.sh` |

`build-test.bat` und `build-test.sh` kompilieren oder validieren den Projekt-Stack, ohne `hydra-umc.project.json` zu erhöhen oder `CHANGELOG.md` zu verändern. Sie dürfen nur normale Compiler-Ausgaben erzeugen. Die vorhandenen Skripte `build*.bat`, `build*.sh`, `run*` und `dev*` behalten ihr projektbezogenes Versions- oder Laufzeitverhalten bei; verwenden Sie sie, wenn dieses Verhalten benötigt wird.

## 🩺 Fehlerbehebung

| Du siehst | Weil | Tu |
|---|---|---|
| `hydra-umc-contract-validate: missing required field: ...` | Die Nutzlast verletzt den Vertrag; der Befehl endet mit Exit-Code 2 | Die Datei mit dem Beispiel vergleichen, das der Mock-Server für diesen Vertrag liefert |
| `verify_contract_matrix.py` schlägt fehl | Ein Schema wurde hinzugefügt oder geändert, aber die Vertragsliste des Validators oder eine Fixture nicht nachgezogen | Den Validator-Eintrag sowie eine gültige und eine ungültige Fixture ergänzen |
| `go test ./...` wird übersprungen | Die Build-Prüfung führt die Go-, TypeScript- und Rust-Clients nur aus, wenn `go`, `npm` und `cargo` im Pfad liegen | Die Toolchain installieren; die Prüfung nennt den übersprungenen Client |

## 📂 Struktur des Repositorys

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of HYDRA-UMC-SDK" width="100%">
</p>

<details>
<summary>Textversion des Baums</summary>

```text
HYDRA-UMC-SDK/
├── contracts/                 JSON-Schema-v1-Quellen, OpenAPI-Ausschnitt und Port-Register
├── clients/                   die Referenz-Clients in Python, Go, TypeScript und Rust
├── conformance/               gültige und ungültige Fixtures für jeden Vertrag
├── docs/                      Leitfäden zu Verträgen, API und Entwicklung
├── examples/                  lauffähige Python-Beispiele
├── tools/                     Vertragsmatrix, OpenAPI-Gate, Tooling-Sync, Build-Prüfung
├── .github/                   CI-Workflow und Issue-Vorlagen
├── images/                    Banner und Bilder der README
├── CHANGELOG.md               was sich in jeder Version geändert hat
├── build-test.sh              Build-Prüfung ohne Änderungen
├── build.sh                   baut und prüft; ändert nie die Version
├── bump_manifest_version.py   gleicht die Manifest-Version an
├── bump_version.py            ausdrückliche Versionserhöhung
├── hydra-umc.project.json     Manifest: Version, Reifegrad, Familie
├── run.sh                     startet das Programm
└── test.sh                    führt die Tests aus
```

</details>

`tools/`: `verify_contract_matrix.py` (Schema-/Validator-Kompatibilitätsmatrix), `verify_openapi.py` (abhängigkeitsfreie OpenAPI-Strukturprüfung) und die nicht verändernde `build-test`-Engine. `sync_repo_tools.py` hält die gemeinsamen Werkzeuge aller Repositories identisch, `pin_sdk.py` bindet die Verbraucher des SDK an ein Release-Tag, und `canonical/` enthält die einzigen Vorlagen, die verteilt werden (darunter der Befehl `hydra_project_tool.py`, der prüft, testet und die Version nur auf ausdrücklichen Wunsch erhöht). `sync_ports.py` erzeugt und prüft `contracts/ports.yaml`, das Verzeichnis von Port, Health-Pfad und systemd-Unit jedes Dienstes; die gemeinsame Schwärzung von Geheimnissen (`canonical/redaction.py`, mit ihren Fällen in `contracts/redaction/vectors.json`) wird in die Projekte übernommen, die Text nach außen senden.

## 🗺️ Roadmap und bekannte Grenzen

**Bekannte Grenzen heute**

* Protobuf ist noch nicht veröffentlicht, und der OpenAPI-Ausschnitt deckt nur Erkennung, Anmeldung, Einstellungen und Befehle ab.
* Die Routen des Servers sind heute nicht versioniert; `/api/v1` ist das in `docs/API_DESIGN.md` beschriebene Entwurfsziel.
* Nichts davon lief auf echter Hardware, und das Job-Gate ist eine Software-Funktion, keine zertifizierte Sicherheitsfunktion.

**Als Nächstes:** Protobuf veröffentlichen, wo eine Integration es braucht, und den OpenAPI-Ausschnitt auf die übrigen Routen des Servers ausweiten.

## 🌍 Sprachen

Diese README und die Dokumente des Repositorys gibt es in acht Sprachen: Englisch, Spanisch, Deutsch, Französisch, Italienisch, Japanisch, Chinesisch und Portugiesisch (Portugal). Sie entstehen gemeinsam, und die CI prüft, dass die acht Dateien dieselben Abschnitte und dieselben Links haben. Dieses Repository hat weder eine eigene Oberfläche noch einen eigenen Meldungskatalog, es gibt also keine Oberflächentexte zu übersetzen.

## 🔗 Verwandte Projekte

Dieses Projekt ist Teil des HYDRA-UMC-Robotik-Ökosystems desselben Autors (JuanenRac / Electro Hobby 3D). Gut zu wissen, da eine Anfrage eigentlich eines dieser Projekte betreffen könnte statt dieses Repositorys.

**Übergeordnetes Projekt**
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — reproduzierbare Raspberry-Pi-OS-Produktschicht für den CM5: schreibgeschützter Agent, validierte Konfiguration/Profile, WiFi-Ersteinrichtung; ein Geräte-Agent, der die eigenen Geräte-, Health-, Sicherheits- und Update-Verträge dieses SDKs konsumiert.
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — deklaratives Adapter-Manifest-Register und Validator für Konnektoren externer Maschinen; erweitert die eigene Vertragsidee des SDK auf externe Maschinen, ohne die Industrie-Gateway-Projekte zu ersetzen.

**Direkt verwandt**
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — das reale Headless-Backend (REST/WebSocket), mit dem jeder Steuerungsclient tatsächlich spricht — ein authentifizierter API-Produzent und -Konsument, der den eigenen Verträgen dieses SDKs unterliegt.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — administratives Desktop-Tool, das jedes Repository in diesem Ökosystem entdeckt, klont und aktualisiert — veröffentlicht Versions- und Kompatibilitätsmetadaten, die von den eigenen vertragskundigen Clients dieses SDKs konsumiert werden.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — Windows/Linux-Desktop-Tool, das ein flashbereites CM5-Image baut, vorgeladen mit den aktuellsten Versionen des Ökosystems, mit Ersteinrichtungs-Konfiguration für WLAN/Benutzer/SSH im Stil von Raspberry Pi Imager.
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — Wartungsvorfall-Koordinator: eine Edge-Rolle mit niedrigem Privileg sammelt einen bereinigten Inventar-/Gesundheits-Snapshot, eine Control-Plane-Rolle rendert ihn schreibgeschützt und bittet einen KI-Anbieter um einen Diagnosevorschlag - wendet nie einen Patch an und stellt nie etwas bereit.
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — reproduzierbarer Entwicklungshost (Raspberry Pi 5 / CM5), der den Quellcode des Ökosystems vorhält und begrenzte Build-/Test-Aufgaben über eine dauerhafte Warteschlange ausführt; eine dedizierte Entwicklerrolle, ausdrücklich kein operativer CM5.
- **[HYDRA-UMC-DOCS](https://github.com/JuanenRac/HYDRA-UMC-DOCS)** — das Dokumentations- und Werkzeugzentrum des Ökosystems: Architektur, Schnittstellen, Sicherheitsbasis, Fähigkeitenmatrix und ein aus jedem Manifest erzeugter Projektkatalog.
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — der Entwurf des Motherboards des Roboterarms: CM5-Host + Dual-Core-STM32H745, gedacht zur Koordination von bis zu 8 Werkzeugarmen über CAN-OTA/SPI-OTA (Firmware in einer frühen Phase; noch keine bestückte Platine).
- **[URTC](https://github.com/JuanenRac/URTC)** — Firmware für die physische Universal-Robot-Tool-Controller-Platine, 25+ Werkzeugprofile über CAN-Bus — eine unabhängige Werkzeugcontroller-Plattform, verbunden über die eigenen versionierten Integrationsadapter dieses SDKs.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — Koordinator mit einem träge importierten rclpy-ROS-2-Transport (noch nicht gegen eine ROS-2-Installation ausgeführt) — nutzt das eigene gemeinsame BridgeJob-Gate dieses SDKs für ROS-2-Beobachtung, -Inspektion und abbrechbare Zellarbeit.
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — sicherer High-Level-Koordinator für den Leiterplattenfluss von OpenPnP Pick-and-Place — nutzt die eigenen korrelierten, idempotenten Jobs dieses SDKs für nachverfolgbare Leiterplattenübergaben.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — sichere Koordinationsschranke für Moonraker/Klipper-3D-Drucker, mit echten gesicherten Job-Befehlen — nutzt das eigene Gate dieses SDKs rund um die native Druckerbereitschaft; es legt weder Heizungs- noch Bewegungssteuerung offen.
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — High-Level-Koordinator für CNC-Zellen mit GRBL-Status-/Steuerbyte-Zugriff (nur gegen einen Emulator getestet) — nutzt das eigene Gate dieses SDKs, um nur neben einer inaktiven, gesicherten CNC zu koordinieren.
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — Koordinator für Laserzellen, liest 3 Schlüssel-/Gehäuse-/Verriegelungs-GPIO-Signale (nur gegen einen simulierten Chip getestet; kann keinen Laser scharfschalten oder auslösen) — nutzt das eigene Gate dieses SDKs für Hilfsfunktionen, während die Sicherheitsautorität des Lasers erhalten bleibt.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — Koordinationsschranke für AGV-/AMR-Flotten über einen VDA-5050-MQTT-Publisher (nur gegen eine emulierte Flotte getestet) — validiert seine eigenen Befehle ebenfalls gegen dieselbe gemeinsame Job-und-Sicherheits-Schranke.
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — Koordinationsschranke für laufende/humanoide Droiden, mit einem Boston-Dynamics-Spot-Befehlssender (nur gegen einen Emulator getestet) — validiert seine eigenen Befehle ebenfalls gegen dieselbe gemeinsame Job-und-Sicherheits-Schranke.
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — Koordinationsschranke für kameraausgestattete UAVs, mit einem MAVLink-Befehlssender (nur gegen einen Emulator getestet) — validiert seine eigenen Befehle ebenfalls gegen dieselbe gemeinsame Job-und-Sicherheits-Schranke.

**Ebenfalls Teil des Ökosystems**

*Kern-Backend & Clients*
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — Web-Steuerungs-Dashboard mit Echtzeit-3D-Visualisierung mehrerer Roboter.
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — Desktop-Schwarmleitstand (PySide6) für mehrere Server gleichzeitig, verpackt als eigenständige ausführbare Datei.
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — native Android-Steuerungs-App mit biometrischem Login und einer gekoppelten Wear-OS-Begleit-App.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — iOS/iPadOS-Steuerungs-App (Flutter) mit Echtzeit-WebSocket-Synchronisierung.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — native Touch-UI für das eingebaute 7"-DSI-Touchscreen, direkt auf dem CM5 eingebettet.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — grafischer Desktop-URDF-Ersteller/-Editor, der fertige Modelle in STUDIOs eigenen Katalog überträgt.
- **[HYDRA-UMC-EDITOR-STL](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-STL)** — Desktop-STL-Modelleditor, der echte Teile im selben Modellkatalog transformiert/ersetzt/entfernt/hinzufügt, den auch HYDRA-UMC-EDITOR-URDF bearbeitet.

*URTC-Werkzeugplattform*
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — Desktop-GUI-Flash-Tool für URTC-Platinen, CAN-OTA plus Full-Chip-SWD/JTAG.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — Desktop-Live-CAN-Bus-Diagnosetool für URTC-Platinen, ein Panel pro Werkzeugprofil.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — browserbasierte Alternative zu URTC-TESTER über die Web-Serial-API, ohne lokale Installation.
- **[URTC-GATEWAY](https://github.com/JuanenRac/URTC-GATEWAY)** — Gateway vor dem CAN-Bus von URTC: Liste erlaubter Kennungen, Ratenbegrenzung und Sitzungsschlüssel; Software auf dem Computer getestet, noch nicht an einem echten Bus.

*Vision-KI-Knoten (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — Integrationsknoten für die Hailo-8-Vision-Pipeline, mit einer echten stufenweisen Hardware-Bereitschaftsprüfung.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — echte Registry für kompilierte Modelle mit Hailo-Architektur-/Prüfsummen-Safe-Load-Verifizierung.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — echter GStreamer-Pipeline- + MediaMTX-Konfigurationsgenerator mit einer echten HailoRT-Integrationsschranke.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — Position-Based-Visual-Servoing-Korrekturgesetz mit Freigabe abhängig vom Zonenstatus; noch keine Posenschätzung per Kamera.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — v0-Logik für Zonenverletzung, Kalibrierungsaktualität und E-STOP-Anforderung, die Objektpositionen aus einer Datei nimmt; kein Detektor speist sie, und noch kein physischer E-STOP ist angeschlossen.

*Kognitiver KI-Knoten (Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — Integrationsknoten für die Hailo-10-Cognitive-Pipeline (LLM-/VLA-/Sprach-Orchestrierung).
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — echte Aktions-Token-Kodierung/-Dekodierung und Trajektoriengenerierung für ein Vision-Language-Action-Modell.
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — echtes Sprach-Frontend (VAD + Intent-Parser) mit einem begrenzten, bestätigungsgesicherten Watch-Relay.
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — echte regelbasierte Aufgabenzerlegung und semantische Fehlerbehebung über MCU-Fehlercodes.
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — echte, nur auf der Standardbibliothek basierende TF-IDF-Dokumentensuche über die eigenen Markdown-Dokumente dieses Ökosystems.
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — lokaler, richtlinien-gesteuerter KI-Wartungstechniker für das Ökosystem selbst - beobachtet, diagnostiziert und schlägt Korrekturen vor; die zwei höchsten Risikostufen sind absichtlich noch nicht implementiert.

*Orchestrierung & Schwarm*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — Integrationsknoten mit einem echten gRPC/Protobuf-Health-Report-Vertrag und einer Missions-Zustandsmaschine.
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — echte prioritätsbasierte Job-Queue mit Deduplizierung, über eine echte HTTP-API.
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — echter gRPC-basierter Flotten-Health-Watchdog mit Retry/Backoff und Identitäts-Mismatch-Erkennung.
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — echter RRT-basierter 3D-Pfadplaner mit echter Hindernis-/Arbeitsraum-Kollisionsvalidierung.
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — echte CRDT-LWW-Element-Map-Zustandssynchronisation, eigenschaftsgetestet auf Multi-Zellen-Konvergenz.

*Digitaler Zwilling & Simulation*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — Integrationsknoten für die Digital-Twin-Engine, mit einem echten Versionskompatibilitäts-Sync-Vertrag.
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — Hardware-in-the-Loop-Router mit einer Software-Kollisionsverriegelung zwischen Simulation und echter Hardware (ohne echte Hardware getestet).
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
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — WearOS-Begleit-App mit haptischen Alarmmustern und einem Sprach-Relay zum gekoppelten Telefon (noch nicht auf einer physischen Uhr ausgeführt).
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — Firmware für ein Platinenmontagegestell mit echter Werkzeug-ID-Dekodierung und Smart-Idle-Vorheizlogik.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — Firmware plus ein echter Python-Vision-Begleiter für einen Thermal-/RGB-Inspektionswerkzeugkopf.

## 📚 Dokumentation

Hier steht mehr:

* [Sicherheitsgrundlage des Ökosystems](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)
* [Bedrohungsmodell des Ökosystems](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)
* [Änderungsprotokoll dieses Repositorys](CHANGELOG.md)
* [Lizenz dieses Repositorys](LICENSE.md)

## 🤝 Mitwirken und Community

* Führe vor einem Pull Request `HYDRA_UMC_CI=1 py -3 tools/ci_validate.py` (oder `HYDRA_UMC_CI=1 python3 tools/ci_validate.py`) aus: Es muss `CI_VALIDATION=PASS` ausgeben. Führe dafür nicht `build.sh` oder `build.bat` aus; Bauen ist keine Prüfung.
* Die acht READMEs entstehen aus einer einzigen Quelle in HYDRA-UMC-DOCS; bearbeite sie nicht von Hand. Ändere die Quelle und schreibe sie mit `tools/make_readmes.py` neu.
* Behaupte in einer README nichts, was nicht gelaufen ist: Schreibe „simuliert“ oder „nicht auf Hardware erprobt“, wo das stimmt.
* Siehe [CONTRIBUTING.md](CONTRIBUTING.md), den [Verhaltenskodex](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md) und [SUPPORT.md](SUPPORT.md).

## 👤 AUTOR

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 LIZENZ

GPL-3.0-or-later - [LICENSE](LICENSE).

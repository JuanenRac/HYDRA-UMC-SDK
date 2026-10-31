<!-- =============================================================================
HYDRA-UMC-SDK - Shared contracts and integration toolkit
Copyright (C) JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-SDK banner" width="100%">
</p>

# 🧰 HYDRA-UMC-SDK

<p align="center"><a href="README.md">🇺🇸 English</a> | 🇪🇸 <b>Español</b> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | <a href="README_jpn.md">🇯🇵 日本語</a> | <a href="README_por.md">🇵🇹 Português</a></p>

### 🧰 Contratos compartidos, clientes de referencia y herramientas de integración para HYDRA-UMC

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Contracts-JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="Contracts">
  <img src="https://img.shields.io/badge/Reference%20clients-Python%20%7C%20Go%20%7C%20TypeScript%20%7C%20Rust-blueviolet.svg" alt="Reference%20clients">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="Integration">
  <img src="https://img.shields.io/badge/Tests-675%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.4.3-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-established-2EA44F.svg" alt="Maturity">
</p>

---

> **Comprobación de honestidad - qué funciona realmente hoy:** los dieciocho contratos JSON Schema v1 con un fixture válido y otro inválido cada uno, el validador de Python, el primer corte OpenAPI v1 de HYDRA-UMC-SERVER, los clientes de Go, TypeScript y Rust que aplican los mismos esquemas, las ayudas para puentes y la matriz de compatibilidad son reales y están probados en un ordenador (675 pruebas de Python, más las suites de los otros tres clientes). Protobuf aún no se publica, la puerta de trabajos es una función de software compartida y no una función de seguridad certificada, y nada de esto se ha ejecutado en hardware real.

---

> **Estado de seguridad física y de ciberseguridad:** este ecosistema no es un sistema de seguridad certificado. Todavía no existe una ruta de E-STOP por hardware, ni límites ni enclavamientos aplicados por el firmware, ni un comando de movimiento verificado; las imágenes de firmware se comprueban con CRC-32 y una firma Ed25519, y una compilación de versión rechaza las claves de desarrollo publicadas (los cabezales de herramienta y las placas de expansión detrás del relé siguen con cargadores de URTC, que usan un HMAC-SHA256 de clave compartida en lugar de una firma); TLS y TLS mutuo son opcionales y están desactivados por defecto; aún no se ha poblado ni probado ninguna placa propia. Lee la [línea base de seguridad](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md) y el [modelo de amenazas](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md) antes de fiarte de cualquier afirmación de aquí para la seguridad de una persona.

---

## 📋 De un vistazo

| | |
|---|---|
| Versión | `0.4.3` |
| Madurez | Establecido |
| Tests | 675 (`python -m unittest discover -s clients/python/tests`) |
| Tecnología | Python / TypeScript / Go / Rust / JSON Schema |
| En hardware real | Todavía no: no consta ninguna ejecución en hardware real para esta versión |

**Ir a:** [Resumen](#-resumen) · [Arquitectura](#-arquitectura) · [Funciones](#-funciones) · [Seguridad y protección](#-seguridad-y-protección) · [Interfaces](#-interfaces) · [Configuración](#-configuración) · [Inicio rápido](#-inicio-rápido) · [Pruebas](#-pruebas) · [Resolución de problemas](#-resolución-de-problemas) · [Estructura del repositorio](#-estructura-del-repositorio) · [Proyectos relacionados](#-proyectos-relacionados)

## 🚦 Estado del proyecto

Cada línea es una parte de este repositorio y la luz dice hasta dónde llega hoy. Se escribe con lo que el repositorio puede demostrar (pruebas, compilaciones, ejecuciones), no con lo previsto.

🟢 Hecho y verificado · 🟡 Funciona, con límites conocidos · 🟠 Hecho a medias o sin verificar · 🔴 Sin hacer o sin funcionar

| Área | Estado | Qué significa aquí |
|---|---|---|
| Software | 🟢 | Completo para su propósito y estable; la comprobación de honestidad de arriba lista los límites conocidos |
| Pruebas | 🟢 | 675 pruebas automáticas, ejecutadas en cada cambio |
| Hardware real | 🔴 | Todavía no: no consta ninguna ejecución en hardware real para esta versión |
| Documentación | 🟢 | README en ocho idiomas, comprobado contra el manifiesto en cada cambio |

## 🎯 Resumen

HYDRA-UMC-SDK define el lenguaje estable compartido por los servicios de HYDRA-UMC,
clientes, adaptadores CM5 e integraciones URTC. Posee contratos normativos, un
validador de referencia de Python libre de dependencias, accesorios de conformidad y
orientación de integración. No reemplaza las API oficiales de Raspberry Pi OS, Hailo, ROS 2, MQTT, OPC-UA o
MTConnect.

## 🧩 Papel en HYDRA-UMC

**HYDRA-UMC-SDK** es el lenguaje común del ecosistema: los contratos JSON Schema v1, el primer corte de OpenAPI del servidor, clientes de referencia en Python, Go, TypeScript y Rust, las ayudas para puentes que usan todos los puentes y el concentrador de conectores, y las herramientas que mantienen idénticas las herramientas de cada repositorio. No ejecuta ningún servicio propio ni sustituye ninguna API oficial.

## 🏛️ Arquitectura

<p align="center">
  <img src="images/architecture.svg" alt="HYDRA-UMC-SDK architecture" width="100%">
</p>

## ✨ Funciones

### Estado

Los contratos JSON Schema v1, los accesorios válidos/no válidos, un cliente de validación en Python
y las pruebas del lado del host ya están implementados, junto con una primera porción real de
OpenAPI v1 para la superficie HTTP propia de HYDRA-UMC-SERVER (`contracts/openapi/v1/server.openapi.json`
- ver [docs/CONTRACTS.md](docs/CONTRACTS.md#openapi-v1)). La publicación de Protobuf es un hito de compatibilidad posterior; los clientes Go, TypeScript y Rust ya existen.

Una matriz de compatibilidad real y automática (`tools/verify_contract_matrix.py`)
contrasta cada esquema publicado con la propia lista de contratos del validador
de Python - encontró y corrigió una brecha real en la que `project-manifest.schema.json`
(el contrato de `hydra-umc.project.json` que publica cada repositorio de este
ecosistema) no tenía ninguna entrada de validador, y ahora demuestra que cada
accesorio de conformidad se evalúa tal como afirma su propio nombre de archivo,
además de los casos de contrato desconocido e incompatibilidad de versión de esquema.

Desde el primer hito de abajo se han añadido más contratos: un contrato
público de puente a máquinas externas `BridgeJob`/`GateDecision` (ver
[docs/BRIDGE_CONTRACT.md](docs/BRIDGE_CONTRACT.md)), compartido por
`HYDRA-UMC-BRIDGE-ROS2`/`-OPENPNP`/`-PRINTER3D`/`-CNC`/`-LASER`/`-AMR`/`-DROIDS`/`-UAV` y con su
propia forma JSON real (`job_to_dict()`/`job_from_dict()`/
`decision_to_dict()`), más el estado de la máquina que el propio bridge observa, que la puerta usa en lugar del que declara quien pide, y una admisión de trabajos (`JobIntake`/`IdempotencyStore`) que ignora los mensajes retenidos y nunca ejecuta dos veces una clave de idempotencia; un contrato `ScenarioOutcome` más `compare_runs()`,
una comprobación compartida de "se arregló de verdad" que
devuelve `apparent-success` (no `regression-fixed`) cuando un fallo dejó
de reproducirse pero la huella base nunca se movió; un contrato
`Operation` más `validate_status_transition()`, el ciclo de vida
compartido de objetivo/trabajo/operación -
`received`/`authorized`/`queued`/`sent`/`confirmed`/`terminated`/
`rejected`, nunca un único cajón "ejecutado"-; un `result` opcional en
`Operation` más `concludes_success()` - evidencia real
(`run_id`/`origin`/`observers_enabled`/`outcome`) que se niega a
concluir éxito a partir de un resultado obsoleto/repetido o de una
ejecución con la observación desactivada; un contrato `Capability`
independiente más `is_capability_usable()` - que un objetivo
*declare* soportar un `kind` de operación se modela como un dato
distinto de si ese soporte fue *comprobado de verdad recientemente*
(`last_checked_at_utc`/`checked_configuration`/`max_age_seconds`), de
modo que una capacidad declarada pero nunca comprobada o ya caducada
nunca se trate silenciosamente como utilizable; y un
`hydra-umc-sdk-mock-server` (`mock_server.py`) que sirve un payload de
ejemplo válido por cada contrato conocido sobre HTTP plano, para que una
UI o un adaptador puedan desarrollarse antes de que exista hardware
CM5/robot/MCU real. Los 15 contratos tienen al menos un accesorio de
conformidad válido e inválido, verificados por la matriz de
compatibilidad de arriba.

### Fuente de rutas, contratos de mensajería y un transporte de puentes endurecible

- **Una fuente para un grupo de rutas del servidor (piloto: las rutas de conexiones):** `contracts/sources/connections.routes.json` declara `GET /api/connections/clients` y `GET /api/connections/events` (acceso, códigos de estado, parámetros de consulta) sobre los esquemas cerrados `ConnectionClient` y `ConnectionEvent`, y `python tools/contract_source.py` genera a partir de ella `contracts/openapi/v1/server.connections.openapi.json`. `--check` falla si el documento generado está desactualizado, si una copia de los esquemas difiere o si las rutas o enumeraciones del servidor se desvían de la fuente. Véase [`docs/CONTRACT_SOURCE.md`](docs/CONTRACT_SOURCE.md).
- **Contratos de mensajería:** `MqttPublish` lleva un `qos` (0, 1 o 2) y `ProductionEvent` describe un ciclo terminado (`source_id`, `at_utc`, `good`, `cycle_time_s`), que los informes de producción convierten en OEE.
- **Las rutas que el servidor añadió tras el piloto, con contratos tipados:** `contracts/openapi/v1/server.full.openapi.json` lista `GET /api/ecosystem/health`, `GET /api/robots/liveness`, `POST /api/robot/{id}/heartbeat`, `POST /api/stop-all/release`, las rutas de conexiones y el `GET /health` público, y el corte tipado describe las cuatro primeras. Dos contratos cerrados nuevos, `EcosystemHealth` (estado, código de motivo y desfase de versión de cada servicio y estado del certificado del servidor) y `RobotLiveness` (vivo, caducado o desconocido para cada robot), los valida el cliente de Python y están incluidos en los clientes de Go, Rust y TypeScript con sus hashes, fixtures y pruebas diferenciales. Ver [`docs/CONTRACTS.md`](docs/CONTRACTS.md).
- **Un transporte de puentes que se puede endurecer, con todos los límites desactivados por defecto:** `MessageDispatcher(..., max_queue=N, max_payload_bytes=N)` acota las órdenes que esperan tras la que se ejecuta (se descarta y cuenta la más antigua) y rechaza una carga demasiado grande; el carril de parada nunca se acota y los verbos de parada están exentos del tope. `stats()` devuelve los contadores `dropped`, `oversized` y `queued`. `connect_with_retry` y `open_bridge_client` admiten una espera exponencial con jitter en la primera conexión, y `reconnect_min_delay_seconds` / `reconnect_max_delay_seconds` fijan el retardo de reconexión del cliente MQTT. Véase [`docs/PYTHON_CLIENT.md`](docs/PYTHON_CLIENT.md).

## 🔒 Seguridad y protección

| Amenaza | Defensa | Dónde |
|---|---|---|
| Una orden de puente fuera de su contrato | Un trabajo lleva como mucho 32 parámetros, nombres de 64 caracteres, valores de 1024 e identificadores de 128; se usa el estado de máquina que observa el puente, no el que dice el solicitante | `bridge_contract.py` |
| El mismo comando ejecutado dos veces, o un mensaje retenido repetido | La admisión de trabajos ignora los mensajes retenidos y nunca ejecuta dos veces una clave de idempotencia | `job_intake.py` |
| Una parada esperando tras una orden larga | Las órdenes normales se ejecutan de una en una en un carril y los verbos de parada en un segundo carril | `bridge_transport.py` |
| Una avalancha de órdenes, una carga enorme o un broker que sigue caído | Límites opcionales, apagados por defecto: una cola acotada que descarta la orden en espera más antigua y la cuenta, un tope de tamaño de carga (los verbos de parada quedan exentos), espera exponencial con jitter en la primera conexión y límites de reconexión configurables | `bridge_transport.py` |
| Credenciales del broker en un fichero de configuración, o un broker sin verificar | Usuario y contraseña vienen del entorno o de un fichero, TLS puede verificar el broker contra una CA, y un certificado de cliente con su clave activa TLS mutuo | `mqtt_connection.py` |
| Un esquema cambiado sin que el validador lo siga | Una matriz de compatibilidad comprueba cada esquema publicado contra la lista de contratos del validador y juzga cada fixture según lo que dice su nombre de fichero | `tools/verify_contract_matrix.py` |

**Lo que nunca hace:** actuar como función de seguridad certificada. La puerta de trabajos es una implementación de software compartida por los puentes, no una certificación de seguridad.

## 🔌 Interfaces

| Topic o ruta | Qué lleva |
|---|---|
| `contracts/json-schema/v1/` | dieciocho contratos JSON Schema v1: capacidad, descriptor de dispositivo, sobre de evento, informe de salud, operación, manifiesto de proyecto, estado de seguridad, resultado de escenario, descubrimiento de servidor, manifiesto de actualización, cliente de conexión, evento de conexión, pose, evento de producción, estado del robot, estado del gemelo, salud del ecosistema, señal de vida del robot |
| `contracts/openapi/v1/server.openapi.json` | el primer corte OpenAPI v1 de HYDRA-UMC-SERVER: descubrimiento, inicio de sesión, ajustes y órdenes (un subconjunto del `docs/openapi.json` del propio servidor) |
| `contracts/ports.yaml` | el registro del puerto, la ruta de salud y la unidad systemd de cada servicio, generado por `tools/sync_ports.py` |
| `hydra/bridges/<name>/cmd/#` | donde escucha un puente; responde en `.../<verbo>/result` |
| `hydra-umc-contract-validate`, `hydra-umc-sdk-mock-server` | el validador en línea de órdenes (código de salida 2 si falla) y un servidor simulado en `127.0.0.1:8790` que sirve un ejemplo válido por contrato |

## ⚙️ Configuración

| Variable | Por defecto | Qué fija |
|---|---|---|
| `HYDRA_MQTT_USERNAME`, `HYDRA_MQTT_PASSWORD` | sin credencial | la credencial del broker; la contraseña solo junto con el usuario |
| `HYDRA_MQTT_PASSWORD_FILE` | - | la contraseña leída de un fichero (un secreto de Docker o systemd); se ignora si la variable anterior está definida |
| `HYDRA_MQTT_TLS`, `HYDRA_MQTT_TLS_CA` | sin TLS | `HYDRA_MQTT_TLS=1` verifica el broker con las CA del sistema; `HYDRA_MQTT_TLS_CA` indica el fichero de la CA que firmó su certificado |
| `HYDRA_MQTT_TLS_CERT`, `HYDRA_MQTT_TLS_KEY` | - | el certificado de cliente y su clave para un broker que exige TLS mutuo; hacen falta los dos y activan TLS |
| `--host`, `--port` | `127.0.0.1`, `8790` | dónde escucha el servidor simulado |
| `HYDRA_UMC_SDK_ROOT` | la carpeta hermana | dónde encuentran este repositorio las pruebas de los demás repositorios |

## 🚀 Inicio rápido

Requiere Python 3.11 o superior. Los clientes de Go, TypeScript y Rust también se compilan y prueban si su cadena de herramientas está instalada.

```bash
PYTHONPATH=clients/python/src python -m unittest discover -s clients/python/tests  # the Python client tests
python tools/verify_contract_matrix.py                                             # every schema against the validator and every fixture
PYTHONPATH=clients/python/src python -m hydra_umc_sdk.validation --help            # the contract validator on the command line
./build-test.sh                                                                    # the non-mutating build check (build-test.bat on Windows)
```

## 🧪 Pruebas

675 pruebas automáticas se ejecutan con `python -m unittest discover -s clients/python/tests`. Los otros clientes tienen sus propias suites: 28 pruebas en Go (`go test ./...`), 121 en TypeScript (`npm test`) y 31 en Rust (`cargo test`), que ejecuta `tools/extra_build_steps.py` si la cadena de herramientas está instalada. Ninguna necesita hardware.

El CI ejecuta `HYDRA_UMC_CI=1 python tools/ci_validate.py`, que comprueba el manifiesto, los documentos, los ocho README y las imágenes.

## 🏗️ Compilación y publicación

Usa la comprobación de compilación sin versionado antes de una compilación de publicación:

| Acción | Windows | Linux / macOS |
|---|---|---|
| Comprobación de compilación (sin cambiar versión ni CHANGELOG) | `build-test.bat` | `./build-test.sh` |
| Ejecución / desarrollo (cuando exista) | `run*.bat` o `dev*.bat` | `./run*.sh` o `./dev*.sh` |

`build-test.bat` y `build-test.sh` compilan o validan el stack del proyecto sin incrementar `hydra-umc.project.json` ni modificar `CHANGELOG.md`. Solo pueden crear salidas normales del compilador. Los scripts existentes `build*.bat`, `build*.sh`, `run*` y `dev*` conservan su comportamiento específico de versión o ejecución; úsalos cuando necesites ese comportamiento.

## 🩺 Resolución de problemas

| Ves | Porque | Haz |
|---|---|---|
| `hydra-umc-contract-validate: missing required field: ...` | La carga rompe el contrato; la orden termina con código de salida 2 | Compara el fichero con el ejemplo que sirve el servidor simulado para ese contrato |
| `verify_contract_matrix.py` falla | Se añadió o cambió un esquema y no se actualizó la lista de contratos del validador o un fixture | Añade la entrada del validador y un fixture válido y otro inválido |
| `go test ./...` se omite | La comprobación de compilación ejecuta los clientes de Go, TypeScript y Rust solo si `go`, `npm` y `cargo` están en el PATH | Instala la cadena de herramientas; la comprobación imprime qué cliente se omitió |

## 📂 Estructura del repositorio

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of HYDRA-UMC-SDK" width="100%">
</p>

<details>
<summary>Versión en texto del árbol</summary>

```text
HYDRA-UMC-SDK/
├── contracts/                 fuentes JSON Schema v1, el corte OpenAPI y el registro de puertos
├── clients/                   los clientes de referencia de Python, Go, TypeScript y Rust
├── conformance/               fixtures válidos e inválidos de cada contrato
├── docs/                      guías de contratos, API y desarrollo
├── examples/                  ejemplos de Python ejecutables
├── tools/                     matriz de contratos, puerta OpenAPI, sincronización de herramientas, comprobación de compilación
├── .github/                   flujo de CI y plantillas de incidencias
├── images/                    banner e imágenes del README
├── CHANGELOG.md               qué cambió en cada versión
├── build-test.sh              comprobación de compilación sin cambios
├── build.sh                   compila y comprueba; nunca cambia la versión
├── bump_manifest_version.py   sincroniza la versión del manifiesto
├── bump_version.py            subida de versión explícita
├── hydra-umc.project.json     manifiesto: versión, madurez, familia
├── run.sh                     arranca el programa
└── test.sh                    ejecuta las pruebas
```

</details>

`tools/`: `verify_contract_matrix.py` (matriz de compatibilidad esquema/validador), `verify_openapi.py` (validación estructural de OpenAPI sin dependencias) y el motor no destructivo de `build-test`. `sync_repo_tools.py` mantiene idénticas las herramientas compartidas de todos los repositorios, `pin_sdk.py` fija los consumidores del SDK a una etiqueta de versión y `canonical/` guarda las copias únicas que se replican (entre ellas el comando `hydra_project_tool.py`, que valida, prueba y, solo si se le pide, sube la versión). `sync_ports.py` genera y comprueba `contracts/ports.yaml`, el registro del puerto, la ruta de salud y la unidad systemd de cada servicio; la redacción de secretos compartida (`canonical/redaction.py`, con sus casos en `contracts/redaction/vectors.json`) se copia en los proyectos que envían texto hacia fuera.

## 🗺️ Hoja de ruta y límites conocidos

**Límites conocidos hoy**

* Protobuf aún no se publica, y el corte OpenAPI cubre solo descubrimiento, inicio de sesión, ajustes y órdenes.
* Las rutas del servidor no están versionadas hoy; `/api/v1` es el objetivo de diseño descrito en `docs/API_DESIGN.md`.
* Nada de esto se ha ejecutado en hardware real, y la puerta de trabajos es una función de software, no una función de seguridad certificada.

**Siguiente:** publicar Protobuf donde una integración lo necesite y ampliar el corte OpenAPI al resto de las rutas del servidor.

## 🌍 Idiomas

Este README y los documentos del repositorio existen en ocho idiomas: inglés, español, alemán, francés, italiano, japonés, chino y portugués (Portugal). Se escriben a la vez y el CI comprueba que los ocho ficheros tengan las mismas secciones y los mismos enlaces. Este repositorio no tiene pantalla ni catálogo de mensajes propios, así que no hay cadenas de interfaz que traducir.

## 🔗 Proyectos relacionados

Este proyecto es parte del ecosistema de robótica HYDRA-UMC del mismo autor (JuanenRac / Electro Hobby 3D). Vale la pena conocerlo, ya que una petición podría en realidad ser sobre alguno de estos en vez de sobre este repositorio.

**Proyecto Padre**
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — capa de producto reproducible sobre Raspberry Pi OS para el CM5: agente de solo lectura, config/perfiles validados, aprovisionamiento WiFi de primer contacto; un agente de dispositivo consumidor de los propios contratos de dispositivo, salud, seguridad y actualización de este SDK.
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — registro declarativo y validador de manifiestos de adaptador para conectores de máquinas externas; extiende la propia idea de contrato del SDK a máquinas externas sin sustituir a los proyectos de pasarela industrial.

**Directamente Relacionados**
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — el backend headless real (REST/WebSocket) con el que habla de verdad cada cliente de control — un productor y consumidor de API autenticado gobernado por los propios contratos de este SDK.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — herramienta administrativa de escritorio que descubre, clona y actualiza cada repositorio de este ecosistema — publica metadatos de versión y compatibilidad consumidos por los propios clientes de este SDK que conocen el contrato.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — herramienta de escritorio Windows/Linux que construye una imagen de la CM5 lista para grabar, precargada con las versiones más actuales del ecosistema, con configuración de primer arranque de Wi-Fi/usuario/SSH al estilo de Raspberry Pi Imager.
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — coordinador de incidencias de mantenimiento: un rol edge de bajo privilegio recopila un snapshot de inventario/salud saneado, un rol control-plane lo renderiza de solo lectura y pide a un proveedor de IA que sugiera un diagnóstico - nunca aplica un parche ni despliega nada.
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — host de desarrollo reproducible (Raspberry Pi 5 / CM5) que almacena el código del ecosistema y ejecuta tareas acotadas de compilación/pruebas bajo una cola duradera; un rol de desarrollo dedicado, explícitamente distinto de un CM5 operativo.
- **[HYDRA-UMC-DOCS](https://github.com/JuanenRac/HYDRA-UMC-DOCS)** — el centro de documentación y herramientas del ecosistema: arquitectura, interfaces, base de seguridad, matriz de capacidades y un catálogo de proyectos generado a partir de cada manifiesto.
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — el diseño de la placa madre del brazo robótico: host CM5 + coprocesador STM32H745 de doble núcleo, pensado para coordinar hasta 8 brazos herramienta por CAN-OTA/SPI-OTA (firmware en fase temprana; todavía no hay ninguna placa poblada).
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware para la placa física del Universal Robot Tool Controller, más de 25 perfiles de herramienta por bus CAN — una plataforma de control de herramientas independiente conectada a través de los propios adaptadores de integración versionados de este SDK.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — coordinador con un transporte ROS 2 rclpy importado de forma perezosa (todavía no ejecutado contra una instalación de ROS 2) — usa la propia barrera común BridgeJob de este SDK para observación, inspección y trabajo de celda cancelable en ROS 2.
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — coordinador de alto nivel seguro para el flujo de placas de pick-and-place OpenPnP — usa los propios trabajos correlacionados e idempotentes de este SDK para traspasos de PCB trazables.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — barrera de coordinación segura para impresoras 3D Moonraker/Klipper, con comandos de trabajo reales y controlados — usa la propia barrera de este SDK en torno a la disponibilidad nativa de la impresora; no expone control de calentador ni de movimiento.
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — coordinador de alto nivel para celdas CNC con acceso a estado/bytes de control GRBL (probado solo contra un emulador) — usa la propia barrera de este SDK para coordinar solo junto a un CNC inactivo y protegido.
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — coordinador de celdas láser que lee 3 señales GPIO de llave/carcasa/enclavamiento (probado solo contra un chip simulado; no puede armar ni disparar un láser) — usa la propia barrera de este SDK para auxiliares, preservando la autoridad de seguridad del láser.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — barrera de coordinación para flotas AGV/AMR mediante un publicador MQTT VDA 5050 (probado solo contra una flota emulada) — también valida sus propios comandos contra esta misma barrera compartida de trabajos y seguridad.
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — barrera de coordinación para droides con patas/humanoides, con un emisor de comandos para Boston Dynamics Spot (probado solo contra un emulador) — también valida sus propios comandos contra esta misma barrera compartida de trabajos y seguridad.
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — barrera de coordinación para UAV equipados con cámara, con un emisor de comandos MAVLink (probado solo contra un emulador) — también valida sus propios comandos contra esta misma barrera compartida de trabajos y seguridad.

**También Forma Parte del Ecosistema**

*Backend Central y Clientes*
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — panel de control web con visualización 3D multi-robot en tiempo real.
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — centro de mando de enjambre de escritorio (PySide6) para varios servidores a la vez, empaquetado como ejecutable independiente.
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — app nativa de control para Android con inicio de sesión biométrico y un compañero Wear OS emparejado.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — app de control para iOS/iPadOS (Flutter) con sincronización en tiempo real por WebSocket.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — interfaz táctil nativa para la pantalla táctil DSI de 7" a bordo, embebida en el propio CM5.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — creador/editor gráfico de URDF de escritorio que envía los modelos terminados al propio catálogo de STUDIO.
- **[HYDRA-UMC-EDITOR-STL](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-STL)** — editor de escritorio de modelos STL, que transforma/reemplaza/quita/añade piezas reales en el mismo catálogo de modelos que también edita HYDRA-UMC-EDITOR-URDF.

*Plataforma de Herramientas URTC*
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — herramienta de escritorio con GUI para flashear placas URTC, CAN-OTA más SWD/JTAG de chip completo.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — herramienta de escritorio de diagnóstico CAN-bus en vivo para placas URTC, un panel por perfil de herramienta.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — alternativa basada en navegador a URTC-TESTER mediante la Web Serial API, sin instalación local.
- **[URTC-GATEWAY](https://github.com/JuanenRac/URTC-GATEWAY)** — pasarela delante del bus CAN de URTC: lista de identificadores permitidos, límite de tasa y clave de sesión; software probado en ordenador, aún no en un bus real.

*Nodo IA de Visión (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — nodo de integración para el pipeline de visión Hailo-8, con una comprobación real de disponibilidad de hardware por etapa.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — registro real de modelos compilados con verificación de carga segura por arquitectura Hailo/checksum.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — generador real de pipeline GStreamer + config MediaMTX, con una frontera de integración HailoRT real.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — ley de corrección Position-Based Visual Servoing con autorización condicionada al estado de zona; todavía sin estimación de pose por cámara.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — lógica v0 de invasión de zona, vigencia de calibración y solicitud de E-STOP que toma las posiciones de los objetos de un fichero; ningún detector la alimenta y todavía no hay un E-STOP físico conectado.

*Nodo IA Cognitivo (Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — nodo de integración para el pipeline cognitivo Hailo-10 (orquestación de LLM/VLA/voz).
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — codificación/decodificación real de tokens de acción y generación de trayectoria para un modelo Vision-Language-Action.
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — front-end de voz real (VAD + analizador de intención) con un relé a Watch acotado y con confirmación.
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — descomposición real de tareas basada en reglas y recuperación semántica de errores sobre códigos de error del MCU.
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — búsqueda real de documentos TF-IDF (solo librería estándar) sobre los propios documentos Markdown de este ecosistema.
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — técnico de mantenimiento con IA local y con puertas de política para el propio ecosistema - observa, diagnostica y propone arreglos; los dos niveles de riesgo más altos están deliberadamente sin implementar todavía.

*Orquestación y Enjambre*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — nodo de integración con un contrato real de informe de salud gRPC/Protobuf y una máquina de estados de misión.
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — cola de trabajos real basada en prioridad con deduplicación, sobre una API HTTP real.
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — watchdog de salud de flota real basado en gRPC, con reintento/backoff y detección de discrepancia de identidad.
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — planificador de rutas 3D real basado en RRT, con validación real de colisión de obstáculos/espacio de trabajo.
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — sincronización de estado real mediante CRDT LWW-Element-Map, con pruebas de propiedades para convergencia multi-celda.

*Gemelo Digital y Simulación*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — nodo de integración para el motor de gemelo digital, con un contrato real de sincronización por compatibilidad de versión.
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — enrutador hardware-in-the-loop con un enclavamiento de software por colisión entre simulación y hardware real (probado sin hardware real).
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — cinemática directa real y validación de límites articulares sobre un subconjunto real de URDF.
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — generador real de escenas 2D procedurales con exportación de anotaciones YOLO/COCO.

*Datos y Analítica*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — almacén de series temporales real respaldado por sqlite3, con una API HTTP real de ingesta/consulta.
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — detector de anomalías real basado en FFT + línea base estadística, con monitorización de deriva.
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — cálculo real de OEE/disponibilidad sobre el histórico de DATALAKE, con exportación CSV reproducible.
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — pipeline real de ingesta CAN/WebSocket hacia DATALAKE, con deduplicación por secuencia.

*Pasarela Industrial*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — nodo de integración que retransmite a protocolos industriales, con una capa real de lista blanca de comandos/contrapresión.
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — espacio de direcciones OPC-UA real, verificado con una sesión de cliente real del protocolo binario.
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — broker MQTT real con autenticación por cliente opcional y ACL de tópicos.
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — endpoints XML reales `/probe` y `/current` de MTConnect, con salida en modo degradado.

*Herramientas Complementarias y Operaciones del Ecosistema*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — paneles de Resúmenes Inteligentes y Resaltado de Anomalías sobre DATALAKE/ANOMALY-DETECTOR, con un respaldo estadístico honesto.
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — CLI de flota con un contrato real y estable de códigos de salida, cliente real y en vivo de la propia API de HYDRA-UMC-SERVER.
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — app compañera de WearOS con patrones de alerta háptica y un relé de voz al teléfono emparejado (todavía no ejecutada en un reloj físico).
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware para un rack de montaje de placas con decodificación real de ID de herramienta y lógica de precalentamiento Smart Idle.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware más un compañero de visión real en Python para un cabezal de inspección térmica/RGB.

## 📚 Documentación

Dónde leer más:

* [Base de seguridad del ecosistema](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)
* [Modelo de amenazas del ecosistema](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)
* [Historial de cambios de este repositorio](CHANGELOG.md)
* [Licencia de este repositorio](LICENSE.md)

## 🤝 Contribuir y comunidad

* Antes de un pull request ejecuta `HYDRA_UMC_CI=1 py -3 tools/ci_validate.py` (o `HYDRA_UMC_CI=1 python3 tools/ci_validate.py`): debe imprimir `CI_VALIDATION=PASS`. No ejecutes `build.sh` ni `build.bat` para esta comprobación; compilar no es comprobar.
* Los ocho README se escriben desde una sola fuente en HYDRA-UMC-DOCS; no los edites a mano. Cambia la fuente y vuelve a escribirlos con `tools/make_readmes.py`.
* No afirmes en un README lo que no se ha ejecutado: di «simulado» o «sin probar en hardware» cuando esa sea la verdad.
* Mira [CONTRIBUTING.md](CONTRIBUTING.md), el [código de conducta](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md) y [SUPPORT.md](SUPPORT.md).

## 👤 AUTOR

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 LICENCIA

GPL-3.0-or-later - [LICENSE](LICENSE).

<!--
================================================================================
HYDRA-UMC-SDK: descripción general del conjunto de herramientas de integración y contratos públicos
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
CC BY-SA 4.0 - ver LICENCIA.md
================================================================================
-->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="banner HYDRA-UMC-SDK" width="100%">
</p>

<p align="center">
  <a href="README.md">🇺🇸 English</a> |
  <a href="README_spa.md">🇪🇸 Español</a> |
  <a href="README_fra.md">🇫🇷 Francés</a> |
  <a href="README_ita.md">🇮🇹 Italiano</a> |
  <a href="README_deu.md">🇩🇪 Alemán</a> |
  <a href="README_zho.md">🇨🇳 简体中文</a> |
  <a href="README_jpn.md">🇯🇵 日本語</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0-blue.svg" alt="Licencia: GPL 3.0">
  <img src="https://img.shields.io/badge/Contracts-Protobuf%20%7C%20JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="Contratos: Protobuf | Esquema JSON | OpenAPI">
  <img src="https://img.shields.io/badge/Reference%20client-Python-blueviolet.svg" alt="Cliente de referencia: Python">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="Integración: CM5 | URTC">
</p>

# HYDRA-UMC-SDK

## 🧩 Contratos compartidos y kit de herramientas de integración para HYDRA-UMC

HYDRA-UMC-SDK define el lenguaje estable compartido por los servicios de HYDRA-UMC,
clientes, adaptadores CM5 e integraciones URTC. Posee contratos normativos, un
validador de referencia de Python libre de dependencias, accesorios de conformidad y
orientación de integración. No reemplaza las API oficiales de Raspberry Pi OS, Hailo, ROS 2, MQTT, OPC-UA o
MTConnect.

## 🚧 Estado

Los contratos JSON Schema v1, los accesorios válidos/no válidos, un cliente de validación en Python
y las pruebas del lado del host ya están implementados. La publicación de Protobuf/OpenAPI y los clientes
para otros idiomas son los siguientes hitos de compatibilidad.

Una matriz de compatibilidad real y automática (`tools/verify_contract_matrix.py`)
contrasta cada esquema publicado con la propia lista de contratos del validador
de Python - encontró y corrigió una brecha real en la que `project-manifest.schema.json`
(el contrato de `hydra-umc.project.json` que publica cada repositorio de este
ecosistema) no tenía ninguna entrada de validador, y ahora demuestra que cada
accesorio de conformidad se evalúa tal como afirma su propio nombre de archivo,
además de los casos de contrato desconocido e incompatibilidad de versión de esquema.

Desde el primer hito de abajo se han añadido dos contratos más: un
contrato público de puente a máquinas externas `BridgeJob`/`GateDecision`
(ver [docs/BRIDGE_CONTRACT.md](docs/BRIDGE_CONTRACT.md)), compartido por
`HYDRA-UMC-BRIDGE-ROS2`/`-OPENPNP`/`-PRINTER3D`/`-CNC`/`-LASER` y con su
propia forma JSON real (`job_to_dict()`/`job_from_dict()`/
`decision_to_dict()`); y un `hydra-umc-sdk-mock-server` (`mock_server.py`)
que sirve un payload de ejemplo válido por cada contrato conocido sobre
HTTP plano, para que una UI o un adaptador puedan desarrollarse antes de
que exista hardware CM5/robot/MCU real. Los 7 contratos tienen al menos
un accesorio de conformidad válido e inválido, verificados por la matriz
de compatibilidad de arriba.

## 🎯 Primer hito

1. Publicar el Esquema JSON v1 de `DeviceDescriptor`, `HealthReport`, `SafetyState` y
   `UpdateManifest`.
2. Validar accesorios válidos e inválidos con el cliente de referencia de Python.
3. Añadir una matriz de compatibilidad productor/consumidor en CI.
4. Publicar representaciones de Protobuf/OpenAPI cuando la integración lo requiera.
5. Añadir clientes de TypeScript, Go y Rust a partir de contratos estables.

## 📂 Diseño del repositorio

<p align="center">
  <img src="images/REPOSITORY_LAYOUT.svg" alt="Mapa visual del diseño del repositorio de HYDRA-UMC-SDK" width="100%">
</p>

| Ruta | Propósito |
| --- | --- |
| `contracts/` | Fuentes normativas del esquema JSON v1; otras representaciones siguen contratos estables. |
| `clients/` | Validador de referencia de Python libre de dependencias y futuros clientes de otros lenguajes. |
| `conformance/` | Fixtures v1 válidos e inválidos utilizados por las pruebas de compatibilidad. |
| `docs/` | Especificaciones de contrato, API, seguridad y desarrollo. |
| `examples/` | Ejemplo de validación de Python ejecutable. |
| `tools/` | `verify_contract_matrix.py` (matriz de compatibilidad esquema/validador) y el motor no destructivo de `build-test`. |

Lea [la guía del contrato](docs/CONTRACTS.md) antes de definir un nuevo mensaje.

## 📖 Más documentación

- **[docs/CONTRACTS.md](docs/CONTRACTS.md)** — la guía normativa de contratos: léela antes de definir un nuevo mensaje.
- **[docs/PYTHON_CLIENT.md](docs/PYTHON_CLIENT.md)** — referencia completa de la función `validate()` y la CLI `hydra-umc-contract-validate`, con la tabla de campos requeridos y reglas extra por contrato.
- **[docs/CONFORMANCE.md](docs/CONFORMANCE.md)** — qué debe cubrir un conjunto de accesorios válido/retrocompatible/mal formado/inseguro por contrato, y qué cubre hoy la suite v1 implementada.
- **[docs/BRIDGE_CONTRACT.md](docs/BRIDGE_CONTRACT.md)** — el límite compartido v0 `BridgeJob`/`GateDecision` usado por `HYDRA-UMC-BRIDGE-ROS2`, `-OPENPNP`, `-PRINTER3D`, `-CNC` y `-LASER`.
- **[docs/ADAPTERS.md](docs/ADAPTERS.md)** — el límite de adaptadores CM5-MCU/URTC: capas de transporte, framing, protocolo y servicio, y por qué el MCU sigue siendo autoritativo para los límites físicos y la parada segura.
- **[docs/API_DESIGN.md](docs/API_DESIGN.md)** — las convenciones que sigue la propia API pública HTTP/WebSocket de HYDRA-UMC-SERVER: rutas `/api/v1` versionadas, y la forma `ACCEPTED`/`REJECTED`/`RUNNING`/`COMPLETED`/`FAILED` del resultado de un comando.
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** — el flujo de trabajo schema-first bajo el que se desarrollan los propios contratos de este SDK, y qué requiere un cambio de contrato (entrada de changelog, decisión de compatibilidad, ejemplos, pruebas).
- **[docs/PROJECT_MANIFEST.md](docs/PROJECT_MANIFEST.md)** — el contrato `hydra-umc.project.json` que publica cada repositorio de este ecosistema.
- **[docs/HEADER_CONVENTION.md](docs/HEADER_CONVENTION.md)** — la cabecera de copyright/licencia requerida para los nuevos ficheros de código y documentación en todo este ecosistema.

## 🛠️ BUILD Y EJECUCIÓN

Usa la comprobación de compilación sin versionado antes de una compilación de publicación:

| Acción | Windows | Linux / macOS |
|---|---|---|
| Comprobación de compilación (sin cambiar versión ni CHANGELOG) | `build-test.bat` | `./build-test.sh` |
| Ejecución / desarrollo (cuando exista) | `run*.bat` o `dev*.bat` | `./run*.sh` o `./dev*.sh` |

`build-test.bat` y `build-test.sh` compilan o validan el stack del proyecto sin incrementar `hydra-umc.project.json` ni modificar `CHANGELOG.md`. Solo pueden crear salidas normales del compilador. Los scripts existentes `build*.bat`, `build*.sh`, `run*` y `dev*` conservan su comportamiento específico de versión o ejecución; úsalos cuando necesites ese comportamiento.

## 🔗 Proyectos Relacionados

Este proyecto es parte del ecosistema de robótica HYDRA-UMC del mismo autor (JuanenRac / Electro Hobby 3D). Vale la pena conocerlo, ya que una petición podría en realidad ser sobre alguno de estos en vez de sobre este repositorio.

**Proyecto Padre**
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — capa de producto reproducible sobre Raspberry Pi OS para el CM5: agente de solo lectura, config/perfiles validados, aprovisionamiento WiFi de primer contacto; un agente de dispositivo consumidor de los propios contratos de dispositivo, salud, seguridad y actualización de este SDK.

**Directamente Relacionados**
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — el backend headless real (REST/WebSocket) con el que habla de verdad cada cliente de control — un productor y consumidor de API autenticado gobernado por los propios contratos de este SDK.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — herramienta administrativa de escritorio que descubre, clona y actualiza cada repositorio de este ecosistema — publica metadatos de versión y compatibilidad consumidos por los propios clientes de este SDK que conocen el contrato.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — herramienta de escritorio Windows/Linux que construye una imagen de la CM5 lista para grabar, precargada con las versiones más actuales del ecosistema, con configuración de primer arranque de Wi-Fi/usuario/SSH al estilo de Raspberry Pi Imager.
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — la placa madre física del brazo robótico: host CM5 + coprocesador STM32H745 de doble núcleo, coordinando hasta 8 brazos herramienta por CAN-OTA/SPI-OTA — la plataforma de hardware/firmware expuesta a través de los propios contratos de adaptador CM5 y MCU acotados de este SDK.
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware para la placa física del Universal Robot Tool Controller, más de 25 perfiles de herramienta por bus CAN — una plataforma de control de herramientas independiente conectada a través de los propios adaptadores de integración versionados de este SDK.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — coordinador de seguridad con un transporte ROS 2 rclpy real, importado de forma perezosa — usa la propia barrera común BridgeJob de este SDK para observación, inspección y trabajo de celda cancelable en ROS 2.
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — coordinador de alto nivel seguro para el flujo de placas de pick-and-place OpenPnP — usa los propios trabajos correlacionados e idempotentes de este SDK para traspasos de PCB trazables.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — barrera de coordinación segura para impresoras 3D Moonraker/Klipper, con comandos de trabajo reales y controlados — usa la propia barrera de este SDK en torno a la disponibilidad nativa de la impresora; no expone control de calentador ni de movimiento.
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — coordinador de alto nivel para celdas CNC con acceso real a estado/bytes de control GRBL — usa la propia barrera de este SDK para coordinar solo junto a un CNC inactivo y protegido.
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — coordinador de seguridad para celdas láser que lee 3 salvaguardas GPIO reales de llave/carcasa/enclavamiento — usa la propia barrera de este SDK para auxiliares, preservando la autoridad de seguridad del láser.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — barrera de coordinación para flotas AGV/AMR mediante un publicador MQTT VDA 5050 real — también valida sus propios comandos contra esta misma barrera compartida de trabajos y seguridad.
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — barrera de coordinación para droides con patas/humanoides, con un emisor de comandos real para Boston Dynamics Spot — también valida sus propios comandos contra esta misma barrera compartida de trabajos y seguridad.
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — barrera de coordinación para UAV equipados con cámara, con un emisor de comandos MAVLink real — también valida sus propios comandos contra esta misma barrera compartida de trabajos y seguridad.

**También Forma Parte del Ecosistema**

*Backend Central y Clientes*
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — panel de control web con visualización 3D multi-robot en tiempo real.
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — centro de mando de enjambre de escritorio (PySide6) para varios servidores a la vez, empaquetado como ejecutable independiente.
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — app nativa de control para Android con inicio de sesión biométrico y un compañero Wear OS emparejado.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — app de control para iOS/iPadOS (Flutter) con sincronización en tiempo real por WebSocket.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — interfaz táctil nativa para la pantalla táctil DSI de 7" a bordo, embebida en el propio CM5.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — creador/editor gráfico de URDF de escritorio que envía los modelos terminados al propio catálogo de STUDIO.

*Plataforma de Herramientas URTC*
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — herramienta de escritorio con GUI para flashear placas URTC, CAN-OTA más SWD/JTAG de chip completo.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — herramienta de escritorio de diagnóstico CAN-bus en vivo para placas URTC, un panel por perfil de herramienta.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — alternativa basada en navegador a URTC-TESTER mediante la Web Serial API, sin instalación local.

*Nodo IA de Visión (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — nodo de integración para el pipeline de visión Hailo-8, con una comprobación real de disponibilidad de hardware por etapa.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — registro real de modelos compilados con verificación de carga segura por arquitectura Hailo/checksum.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — generador real de pipeline GStreamer + config MediaMTX, con una frontera de integración HailoRT real.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — ley de corrección real de Position-Based Visual Servoing, con puerta de seguridad según el estado de zona previo.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — comprobación real de invasión de zona y solicitud de E-STOP, con exigencia de vigencia de calibración.

*Nodo IA Cognitivo (Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — nodo de integración para el pipeline cognitivo Hailo-10 (orquestación de LLM/VLA/voz).
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — codificación/decodificación real de tokens de acción y generación de trayectoria para un modelo Vision-Language-Action.
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — front-end de voz real (VAD + analizador de intención) con un relé a Watch acotado y con confirmación.
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — descomposición real de tareas basada en reglas y recuperación semántica de errores sobre códigos de error del MCU.
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — búsqueda real de documentos TF-IDF (solo librería estándar) sobre los propios documentos Markdown de este ecosistema.

*Orquestación y Enjambre*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — nodo de integración con un contrato real de informe de salud gRPC/Protobuf y una máquina de estados de misión.
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — cola de trabajos real basada en prioridad con deduplicación, sobre una API HTTP real.
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — watchdog de salud de flota real basado en gRPC, con reintento/backoff y detección de discrepancia de identidad.
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — planificador de rutas 3D real basado en RRT, con validación real de colisión de obstáculos/espacio de trabajo.
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — sincronización de estado real mediante CRDT LWW-Element-Map, con pruebas de propiedades para convergencia multi-celda.

*Gemelo Digital y Simulación*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — nodo de integración para el motor de gemelo digital, con un contrato real de sincronización por compatibilidad de versión.
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — enclavamiento de seguridad real hardware-in-the-loop que enruta comandos entre simulación y hardware real.
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
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — app compañera de WearOS con alertas hápticas reales y un relé de voz al teléfono emparejado.
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware para un rack de montaje de placas con decodificación real de ID de herramienta y lógica de precalentamiento Smart Idle.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware más un compañero de visión real en Python para un cabezal de inspección térmica/RGB.

---

## 📚 Documentación y Comunidad

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — stack tecnológico y pautas de codificación para un pull request.
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** — los estándares de comportamiento esperados en esta comunidad.
- **[SECURITY.md](SECURITY.md)** — cómo reportar una vulnerabilidad, y las áreas reales de enfoque en seguridad de este proyecto.
- **[SUPPORT.md](SUPPORT.md)** — dónde hacer preguntas y reportar errores.
- **[LICENSE.md](LICENSE.md)** — la licencia propia de este proyecto.

## 👤 AUTOR
**JuanenRac** (Electro Hobby 3D)
📧 electrohobby3d@gmail.com
📺 [youtube.com/@electrohobby3d](https://youtube.com/@electrohobby3d)

## 📜 LICENCIA

El código es GPL-3.0 o posterior; la documentación es CC BY-SA 4.0. Consulte [LICENCIA](LICENSE).

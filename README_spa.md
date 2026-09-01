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
  <a href="README.md">???? English</a> |
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
Clientes, adaptadores CM5 e integraciones URTC. Posee contratos normativos, un
validador de referencia de Python libre de dependencias, accesorios de conformidad y
orientación de integración. no lo hace
reemplace las API oficiales para Raspberry Pi OS, Hailo, ROS 2, MQTT, OPC-UA o
MTConnect.

## 🚧 Estado

Contratos JSON Schema v1, accesorios válidos/no válidos, un cliente de validación Python,
y se implementan pruebas del lado del host. Publicación y clientes de Protobuf/OpenAPI
para otros idiomas son los hitos de compatibilidad posteriores.

Una matriz de compatibilidad real y automática (`tools/verify_contract_matrix.py`)
contrasta cada esquema publicado con la propia lista de contratos del validador
de Python - encontró y corrigió una brecha real en la que `project-manifest.schema.json`
(el contrato de `hydra-umc.project.json` que publica cada repositorio de este
ecosistema) no tenía ninguna entrada de validador, y ahora demuestra que cada
accesorio de conformidad se evalúa tal como afirma su propio nombre de archivo,
además de los casos de contrato desconocido e incompatibilidad de versión de esquema.

## 🎯 Primer hito

1. Publicar `DeviceDescriptor`, `HealthReport`, `SafetyState` y
   Esquema JSON `UpdateManifest` v1.
2. Validar dispositivos válidos e inválidos con el cliente de referencia de Python.
3. Agregue una matriz de compatibilidad productor/consumidor en CI.
4. Publicar representaciones de Protobuf/OpenAPI cuando la integración lo requiera.
5. Agregue clientes TypeScript, Go y Rust desde contratos estables.

## 📂 Diseño del repositorio

<p align="center">
  <img src="images/REPOSITORY_LAYOUT.svg" alt="Mapa visual del diseño del repositorio de HYDRA-UMC-SDK" width="100%">
</p>

| Camino | Propósito |
| --- | --- |
| `contratos/` | Fuentes normativas del esquema JSON v1; Otras representaciones siguen contratos estables. |
| `clientes/` | Validador de referencia de Python libre de dependencias y futuros clientes de idiomas. |
| `conformidad/` | Dispositivos v1 válidos e inválidos utilizados por las pruebas de compatibilidad. |
| `docs/` | Especificaciones de contrato, API, seguridad y desarrollo. |
| `ejemplos/` | Ejemplo de validación de Python ejecutable. |

Lea [la guía del contrato](docs/CONTRACTS.md) antes de definir un nuevo mensaje.

## 🛠️ BUILD Y EJECUCIÓN

Usa la comprobación de compilación sin versionado antes de una compilación de publicación:

| Acción | Windows | Linux / macOS |
|---|---|---|
| Comprobación de compilación (sin cambiar versión ni CHANGELOG) | `build-test.bat` | `./build-test.sh` |
| Ejecución / desarrollo (cuando exista) | `run*.bat` o `dev*.bat` | `./run*.sh` o `./dev*.sh` |

`build-test.bat` y `build-test.sh` compilan o validan el stack del proyecto sin incrementar `hydra-umc.project.json` ni modificar `CHANGELOG.md`. Solo pueden crear salidas normales del compilador. Los scripts existentes `build*.bat`, `build*.sh`, `run*` y `dev*` conservan su comportamiento específico de versión o ejecución; úsalos cuando necesites ese comportamiento.

## 🔗 Proyectos relacionados

> Mapa canónico de relaciones entre ecosistemas públicos.

| Proyecto | Relación con HYDRA-UMC-SDK |
| --- | --- |
| [HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS) | Agente de dispositivos consumidor de contratos de dispositivos, salud, seguridad y actualización. |
| [HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER) | Productor y consumidor de API autenticado regido por contratos de SDK. |
| [HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER) | Publica metadatos de versión y compatibilidad consumidos por clientes con reconocimiento de contrato. |
| [HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC) | Plataforma de hardware/firmware expuesta a través de contratos de adaptadores CM5 y MCU vinculados. |
| [URTC](https://github.com/JuanenRac/URTC) | Plataforma independiente de controlador de herramientas conectada a través de adaptadores de integración versionados. |
| [HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2) | Usa la puerta común BridgeJob para observación ROS 2, inspección y trabajo de celda cancelable. |
| [HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP) | Usa trabajos correlacionados e idempotentes para entregas de PCB trazables. |
| [HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D) | Usa la puerta alrededor de la disponibilidad nativa de impresora; no expone control de heaters ni movimiento. |
| [HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC) | Usa la puerta para coordinar solo junto a una CNC inactiva y protegida. |
| [HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER) | Usa la puerta para auxiliares conservando la autoridad de seguridad láser. |

**Resto del ecosistema:** explore las siete capas públicas en el [panel del ecosistema JuanenRac](https://juanenrac.github.io/JuanenRac/).

## 📜 Licencia

El código es GPL-3.0 o posterior; La documentación es CC BY-SA 4.0. Consulte [LICENCIA](LICENSE).

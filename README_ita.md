<!--
==============================================================================
HYDRA-UMC-SDK - Panoramica del toolkit per gli appalti pubblici e l'integrazione
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
CC BY-SA 4.0 - vedere LICENZA.md
==============================================================================
-->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-SDK banner" width="100%">
</p>

<p align="center">
  <a href="README.md">???? English</a> |
  <a href="README_spa.md">🇪🇸 Español</a> |
  <a href="README_fra.md">🇫🇷 Français</a> |
  <a href="README_ita.md">🇮🇹 Italiano</a> |
  <a href="README_deu.md">🇩🇪 Tedesco</a> |
  <a href="README_zho.md">🇨🇳 简体中文</a> |
  <a href="README_jpn.md">🇯🇵 日本語</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0-blue.svg" alt="Licenza: GPL 3.0">
  <img src="https://img.shields.io/badge/Contracts-Protobuf%20%7C%20JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="Contratti: Protobuf | JSON Schema | OpenAPI">
  <img src="https://img.shields.io/badge/Reference%20client-Python-blueviolet.svg" alt="Client di riferimento: Python">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="Integrazione: CM5 | URTC">
</p>

# HYDRA-UMC-SDK

## 🧩 Contratti condivisi e toolkit di integrazione per HYDRA-UMC

HYDRA-UMC-SDK definisce il linguaggio stabile condiviso dai servizi HYDRA-UMC,
client, adattatori CM5 e integrazioni URTC. Possiede contratti normativi, a
validatore di riferimenti Python senza dipendenze, dispositivi di conformità e
guida all'integrazione. Non è così
sostituire le API ufficiali per il sistema operativo Raspberry Pi, Hailo, ROS 2, MQTT, OPC-UA o
MTConnect.

## 🚧Stato

Contratti JSON Schema v1, dispositivi validi/non validi, un client di convalida Python,
e vengono implementati i test lato host. Pubblicazione e client Protobuf/OpenAPI
per ulteriori lingue sono successivi traguardi di compatibilità.

Una matrice di compatibilità reale e automatica (`tools/verify_contract_matrix.py`)
verifica incrociando ogni schema pubblicato con l'elenco dei contratti del
validatore Python stesso - ha individuato e corretto una lacuna reale in cui
`project-manifest.schema.json` (il contratto di `hydra-umc.project.json` che
ogni repository di questo ecosistema pubblica) non aveva alcuna voce di
validatore, e ora dimostra che ogni dispositivo di conformità viene giudicato
come afferma il proprio nome file, oltre ai casi di contratto sconosciuto e
versione di schema incompatibile.

## 🎯 Primo traguardo

1. Pubblica "DeviceDescriptor", "HealthReport", "SafetyState" e
   Schema JSON "UpdateManifest" v1.
2. Convalidare le apparecchiature valide e non valide con il client di riferimento Python.
3. Aggiungere una matrice di compatibilità produttore/consumatore in CI.
4. Pubblicare rappresentazioni Protobuf/OpenAPI laddove l'integrazione lo richiede.
5. Aggiungi client TypeScript, Go e Rust da contratti stabili.

## 📂 Layout del repository

<p align="center">
  <img src="images/REPOSITORY_LAYOUT.svg" alt="Mappa visiva del layout del repository HYDRA-UMC-SDK" width="100%">
</p>

| Percorso | Scopo |
| --- | --- |
| `contratti/` | Origini dello schema JSON normativo v1; ulteriori rappresentanze seguono contratti stabili. |
| `clienti/` | Validatore di riferimenti Python senza dipendenze e futuri client linguistici. |
| `conformità/` | Fixture v1 valide e non valide utilizzate dai test di compatibilità. |
| `documenti/` | Specifiche di contratto, API, sicurezza e sviluppo. |
| `esempi/` | Esempio di validazione Python eseguibile. |

Leggi [la guida al contratto](docs/CONTRACTS.md) prima di definire un nuovo messaggio.

## 🔗Progetti correlati

> Mappa delle relazioni canoniche dell'ecosistema pubblico.

| Progetto | Rapporto con HYDRA-UMC-SDK |
| --- | --- |
| [HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS) | Consumatore dell'agente del dispositivo dei contratti relativi al dispositivo, all'integrità, alla sicurezza e all'aggiornamento. |
| [HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER) | Produttore e consumatore di API autenticati regolati da contratti SDK. |
| [HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER) | Pubblica i metadati di versione e compatibilità utilizzati dai client consapevoli del contratto. |
| [HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC) | Piattaforma hardware/firmware esposta tramite contratti vincolati per adattatori CM5 e MCU. |
| [URTC](https://github.com/JuanenRac/URTC) | Piattaforma strumento-controller indipendente connessa tramite adattatori di integrazione con versione. |
| [HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2) | Usa la porta BridgeJob comune per osservazione ROS 2, ispezione e lavoro di cella annullabile. |
| [HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP) | Usa lavori correlati e idempotenti per passaggi PCB tracciabili. |
| [HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D) | Usa la porta attorno alla disponibilità nativa della stampante senza esporre controllo di heater o movimento. |
| [HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC) | Usa la porta solo accanto a una CNC inattiva e protetta. |
| [HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER) | Usa la porta per ausiliari preservando l'autorità di sicurezza laser. |

**Resto dell'ecosistema:** esplora i sette livelli pubblici nella [dashboard dell'ecosistema JuanenRac](https://juanenrac.github.io/JuanenRac/).

## 📜 Licenza

Il codice è GPL-3.0 o successivo; la documentazione è CC BY-SA 4.0. Vedere [LICENZA](LICENSE).

## 🛠️ BUILD & RUN

Usa il controllo di compilazione senza versionamento prima di una compilazione di rilascio:

| Azione | Windows | Linux / macOS |
|---|---|---|
| Controllo di compilazione (senza modificare versione o CHANGELOG) | `build-test.bat` | `./build-test.sh` |
| Esecuzione / sviluppo (se disponibile) | `run*.bat` o `dev*.bat` | `./run*.sh` o `./dev*.sh` |

`build-test.bat` e `build-test.sh` compilano o convalidano lo stack del progetto senza incrementare `hydra-umc.project.json` né modificare `CHANGELOG.md`. Possono creare solo i normali output del compilatore. Gli script esistenti `build*.bat`, `build*.sh`, `run*` e `dev*` mantengono il comportamento specifico di versione o esecuzione; usali quando tale comportamento è necessario.

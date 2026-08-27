<!--
=============================================================================
HYDRA-UMC-SDK - Présentation de la boîte à outils pour les contrats publics et l'intégration
Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
CC BY-SA 4.0 - voir LICENSE.md
=============================================================================
-->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="Bannière HYDRA-UMC-SDK" width="100%">
</p>

<p align="center">
  <a href="README.md">???? English</a> |
  <a href="README_spa.md">🇪🇸 Español</a> |
  <a href="README_fra.md">🇫🇷 Français</a> |
  <a href="README_ita.md">🇮🇹 Italien</a> |
  <a href="README_deu.md">🇩🇪 Allemand</a> |
  <a href="README_zho.md">🇨🇳 简体中文</a> |
  <a href="README_jpn.md">🇯🇵 日本語</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0-blue.svg" alt="Licence : GPL 3.0">
  <img src="https://img.shields.io/badge/Contracts-Protobuf%20%7C%20JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="Contrats : Protobuf | Schéma JSON | OpenAPI">
  <img src="https://img.shields.io/badge/Reference%20client-Python-blueviolet.svg" alt="Client de référence : Python">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="Intégration : CM5 | URTC">
</p>

# HYDRA-UMC-SDK

## 🧩 Contrats partagés et boîte à outils d'intégration pour HYDRA-UMC

HYDRA-UMC-SDK définit le langage stable partagé par les services HYDRA-UMC,
clients, adaptateurs CM5 et intégrations URTC. Elle possède des contrats normatifs, un
validateur de référence Python sans dépendance, dispositifs de conformité et
un accompagnement pour l'intégration. Ce n'est pas le cas
remplacer les API officielles pour Raspberry Pi OS, Hailo, ROS 2, MQTT, OPC-UA ou
MTConnect.

## 🚧 Statut

Contrats JSON Schema v1, luminaires valides/invalides, un client de validation Python,
et des tests côté hôte sont implémentés. Publication et clients Protobuf/OpenAPI
pour d'autres langues, il y a des étapes de compatibilité ultérieures.

## 🎯 Premier jalon

1. Publiez `DeviceDescriptor`, `HealthReport`, `SafetyState` et
   Schéma JSON `UpdateManifest` v1.
2. Validez les appareils valides et invalides avec le client de référence Python.
3. Ajoutez une matrice de compatibilité producteur/consommateur dans CI.
4. Publiez les représentations Protobuf/OpenAPI là où l'intégration l'exige.
5. Ajoutez des clients TypeScript, Go et Rust à partir de contrats stables.

## 📂 Disposition du référentiel

<p align="center">
  <img src="images/REPOSITORY_LAYOUT.svg" alt="Carte visuelle de la disposition du référentiel HYDRA-UMC-SDK" width="100%">
</p>

| Chemin | Objectif |
| --- | --- |
| `contrats/` | Sources normatives du schéma JSON v1 ; d'autres représentations suivent des contrats stables. |
| `clients/` | Validateur de référence Python sans dépendance et futurs clients de langage. |
| `conformité/` | Appareils v1 valides et invalides utilisés par les tests de compatibilité. |
| `docs/` | Spécifications du contrat, de l’API, de la sécurité et du développement. |
| `exemples/` | Exemple de validation Python exécutable. |

Lisez [le guide du contrat](docs/CONTRACTS.md) avant de définir un nouveau message.

## 🔗 Projets connexes

> Carte canonique des relations entre les écosystèmes publics.

| Projet | Relation avec HYDRA-UMC-SDK |
| --- | --- |
| [HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS) | Agent d’appareil consommateur de contrats d’appareil, de santé, de sécurité et de mise à jour. |
| [HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER) | Producteur et consommateur d'API authentifiés régis par des contrats SDK. |
| [HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER) | Publie les métadonnées de version et de compatibilité consommées par les clients sensibles aux contrats. |
| [HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC) | Plateforme matérielle/micrologicielle exposée via des contrats d'adaptateur CM5 et MCU limités. |
| [URTC](https://github.com/JuanenRac/URTC) | Plateforme de contrôleur d'outils indépendante connectée via des adaptateurs d'intégration versionnés. |

**Reste de l'écosystème :** explorez les sept couches publiques dans le [tableau de bord de l'écosystème JuanenRac](https://juanenrac.github.io/JuanenRac/).

## 📜 Licence

Le code est GPL-3.0 ou version ultérieure ; la documentation est CC BY-SA 4.0. Voir [LICENCE](LICENSE).
## 🛠️ BUILD & RUN

Utilisez la vérification de compilation sans versionnement avant une compilation de publication :

| Action | Windows | Linux / macOS |
|---|---|---|
| Vérification de compilation (sans modifier la version ni le CHANGELOG) | `build-test.bat` | `./build-test.sh` |
| Exécution / développement (si disponible) | `run*.bat` ou `dev*.bat` | `./run*.sh` ou `./dev*.sh` |

`build-test.bat` et `build-test.sh` compilent ou valident la pile du projet sans incrémenter `hydra-umc.project.json` ni modifier `CHANGELOG.md`. Ils peuvent uniquement créer les sorties normales du compilateur. Les scripts existants `build*.bat`, `build*.sh`, `run*` et `dev*` conservent leur comportement spécifique de versionnement ou d'exécution ; utilisez-les lorsque ce comportement est requis.
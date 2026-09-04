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
  <a href="README.md">🇺🇸 English</a> |
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
  <img src="https://img.shields.io/badge/Reference%20clients-Python%20%7C%20Go%20%7C%20TypeScript%20%7C%20Rust-blueviolet.svg" alt="Clients de référence : Python | Go | TypeScript | Rust">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="Intégration : CM5 | URTC">
</p>

# HYDRA-UMC-SDK

## 🧩 Contrats partagés et boîte à outils d'intégration pour HYDRA-UMC

HYDRA-UMC-SDK définit le langage stable partagé par les services HYDRA-UMC,
clients, adaptateurs CM5 et intégrations URTC. Elle possède des contrats normatifs, un
validateur de référence Python sans dépendance, des fixtures de conformité et
un accompagnement pour l'intégration. Il ne remplace pas les API officielles de Raspberry Pi OS, Hailo, ROS 2, MQTT, OPC-UA ou
MTConnect.

## 🚧 Statut

Les contrats JSON Schema v1, les fixtures valides/invalides, un client de validation Python
et les tests côté hôte sont implémentés. La publication Protobuf/OpenAPI et les clients
pour d'autres langages sont les prochaines étapes de compatibilité.

Une matrice de compatibilité réelle et automatique (`tools/verify_contract_matrix.py`)
recoupe chaque schéma publié avec la propre liste de contrats du validateur
Python - elle a trouvé et corrigé une lacune réelle où `project-manifest.schema.json`
(le contrat `hydra-umc.project.json` que chaque dépôt de cet écosystème publie)
n'avait aucune entrée de validateur, et prouve désormais que chaque fixture
de conformité est jugée comme son propre nom de fichier l'affirme, ainsi que les
cas de contrat inconnu et de version de schéma incompatible.

Deux contrats supplémentaires ont été livrés depuis le premier jalon
ci-dessous : un contrat public de pont vers des machines externes
`BridgeJob`/`GateDecision` (voir
[docs/BRIDGE_CONTRACT.md](docs/BRIDGE_CONTRACT.md)), partagé par
`HYDRA-UMC-BRIDGE-ROS2`/`-OPENPNP`/`-PRINTER3D`/`-CNC`/`-LASER` et doté
de sa propre forme JSON réelle (`job_to_dict()`/`job_from_dict()`/
`decision_to_dict()`) ; et un `hydra-umc-sdk-mock-server`
(`mock_server.py`) qui sert un exemple de payload valide par contrat
connu via HTTP simple, pour qu'une UI ou un adaptateur puisse être
développé avant qu'un vrai matériel CM5/robot/MCU soit disponible. Les 7
contrats disposent chacun d'au moins une fixture de conformité valide et
une invalide, vérifiées par la matrice de compatibilité ci-dessus.

## 🎯 Premier jalon

1. Publiez le schéma JSON v1 de `DeviceDescriptor`, `HealthReport`, `SafetyState` et
   `UpdateManifest`.
2. Validez les fixtures valides et invalides avec le client de référence Python.
3. Ajoutez une matrice de compatibilité producteur/consommateur dans CI.
4. Publiez les représentations Protobuf/OpenAPI là où l'intégration l'exige.
5. Ajoutez des clients TypeScript, Go et Rust réels et testés, validant les contrats v1 stables.

## 📂 Disposition du référentiel

<p align="center">
  <img src="images/REPOSITORY_LAYOUT.svg" alt="Carte visuelle de la disposition du référentiel HYDRA-UMC-SDK" width="100%">
</p>

| Chemin | Objectif |
| --- | --- |
| `contracts/` | Sources normatives du schéma JSON v1 ; d'autres représentations suivent des contrats stables. |
| `clients/` | Clients de référence réels et testés en Python, Go, TypeScript et Rust, validant chacun les mêmes schémas v1 publiés. |
| `conformance/` | Fixtures v1 valides et invalides utilisées par les tests de compatibilité. |
| `docs/` | Spécifications du contrat, de l’API, de la sécurité et du développement. |
| `examples/` | Exemple de validation Python exécutable. |
| `tools/` | `verify_contract_matrix.py` (matrice de compatibilité schéma/validateur) et le moteur non destructif de `build-test`. |

Lisez [le guide du contrat](docs/CONTRACTS.md) avant de définir un nouveau message.

## 📖 Documentation complémentaire

- **[docs/CONTRACTS.md](docs/CONTRACTS.md)** — le guide normatif des contrats : à lire avant de définir un nouveau message.
- **[docs/PYTHON_CLIENT.md](docs/PYTHON_CLIENT.md)** — référence complète de la fonction `validate()` et de la CLI `hydra-umc-contract-validate`, avec le tableau des champs requis et règles supplémentaires par contrat.
- **[docs/CONFORMANCE.md](docs/CONFORMANCE.md)** — ce qu'un jeu de fixtures valide/rétrocompatible/malformé/dangereux doit couvrir par contrat, et ce que couvre la suite v1 implémentée aujourd'hui.
- **[docs/BRIDGE_CONTRACT.md](docs/BRIDGE_CONTRACT.md)** — la frontière partagée v0 `BridgeJob`/`GateDecision` utilisée par `HYDRA-UMC-BRIDGE-ROS2`, `-OPENPNP`, `-PRINTER3D`, `-CNC` et `-LASER`.
- **[docs/ADAPTERS.md](docs/ADAPTERS.md)** — la frontière d'adaptateur CM5-MCU/URTC : couches transport, framing, protocole et service, et pourquoi le MCU reste l'autorité pour les limites physiques et l'arrêt sûr.
- **[docs/API_DESIGN.md](docs/API_DESIGN.md)** — les conventions suivies par la propre API publique HTTP/WebSocket de HYDRA-UMC-SERVER : routes versionnées `/api/v1`, et la forme `ACCEPTED`/`REJECTED`/`RUNNING`/`COMPLETED`/`FAILED` du résultat d'une commande.
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** — le flux de travail schema-first sous lequel les propres contrats de ce SDK sont développés, et ce qu'exige un changement de contrat (entrée de changelog, décision de compatibilité, exemples, tests).
- **[docs/PROJECT_MANIFEST.md](docs/PROJECT_MANIFEST.md)** — le contrat `hydra-umc.project.json` que publie chaque dépôt de cet écosystème.
- **[docs/HEADER_CONVENTION.md](docs/HEADER_CONVENTION.md)** — l'en-tête de copyright/licence requis pour les nouveaux fichiers source et de documentation dans tout cet écosystème.

## 🛠️ BUILD ET EXÉCUTION

Utilisez la vérification de compilation sans versionnement avant une compilation de publication :

| Action | Windows | Linux / macOS |
|---|---|---|
| Vérification de compilation (sans modifier la version ni le CHANGELOG) | `build-test.bat` | `./build-test.sh` |
| Exécution / développement (si disponible) | `run*.bat` ou `dev*.bat` | `./run*.sh` ou `./dev*.sh` |

`build-test.bat` et `build-test.sh` compilent ou valident la pile du projet sans incrémenter `hydra-umc.project.json` ni modifier `CHANGELOG.md`. Ils peuvent uniquement créer les sorties normales du compilateur. Les scripts existants `build*.bat`, `build*.sh`, `run*` et `dev*` conservent leur comportement spécifique de versionnement ou d'exécution ; utilisez-les lorsque ce comportement est requis.

## 🔗 Projets Liés

Ce projet fait partie de l'écosystème robotique HYDRA-UMC du même auteur (JuanenRac / Electro Hobby 3D). Bon à savoir, car une demande pourrait en réalité concerner l'un de ceux-ci plutôt que ce dépôt.

**Projet Parent**
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — couche produit reproductible sur Raspberry Pi OS pour le CM5 : agent en lecture seule, config/profils validés, provisionnement WiFi de premier contact ; un agent d'appareil consommateur des propres contrats d'appareil, de santé, de sécurité et de mise à jour de ce SDK.

**Directement Liés**
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — le vrai backend headless (REST/WebSocket) auquel parle réellement chaque client de contrôle — un producteur et consommateur d'API authentifié gouverné par les propres contrats de ce SDK.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — outil administratif de bureau qui découvre, clone et met à jour chaque dépôt de cet écosystème — publie des métadonnées de version et de compatibilité consommées par les propres clients de ce SDK conscients du contrat.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — outil de bureau Windows/Linux qui construit une image de la CM5 prête à graver, préchargée avec les versions les plus actuelles de l'écosystème, avec une configuration de premier démarrage Wi-Fi/utilisateur/SSH façon Raspberry Pi Imager.
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — la carte mère physique du bras robotique : hôte CM5 + coprocesseur STM32H745 double cœur, coordonnant jusqu'à 8 bras-outils via CAN-OTA/SPI-OTA — la plateforme matérielle/firmware exposée via les propres contrats d'adaptateur CM5 et MCU délimités de ce SDK.
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware pour la carte physique Universal Robot Tool Controller, plus de 25 profils d'outil sur bus CAN — une plateforme de contrôleur d'outil indépendante connectée via les propres adaptateurs d'intégration versionnés de ce SDK.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — coordinateur de sécurité avec un vrai transport ROS 2 rclpy à importation paresseuse — utilise la propre barrière commune BridgeJob de ce SDK pour l'observation, l'inspection et le travail de cellule annulable ROS 2.
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — coordinateur haut niveau sûr pour le flux de cartes du pick-and-place OpenPnP — utilise les propres tâches corrélées et idempotentes de ce SDK pour des passations de PCB traçables.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — frontière de coordination sûre pour imprimantes 3D Moonraker/Klipper, avec de vraies commandes de tâche contrôlées — utilise la propre barrière de ce SDK autour de la disponibilité native de l'imprimante ; elle n'expose ni le contrôle du chauffage ni celui du mouvement.
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — coordinateur haut niveau pour cellules CNC avec accès réel au statut/octets de contrôle GRBL — utilise la propre barrière de ce SDK pour ne coordonner qu'aux côtés d'une CNC inactive et sécurisée.
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — coordinateur de sécurité pour cellules laser lisant 3 vraies sécurités GPIO de clé/enceinte/verrouillage — utilise la propre barrière de ce SDK pour les auxiliaires, tout en préservant l'autorité de sécurité du laser.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — frontière de coordination pour les flottes AGV/AMR via un éditeur MQTT VDA 5050 réel — valide également ses propres commandes contre cette même barrière partagée de tâches et de sécurité.
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — frontière de coordination pour droïdes à pattes/humanoïdes, avec un véritable émetteur de commandes Boston Dynamics Spot — valide également ses propres commandes contre cette même barrière partagée de tâches et de sécurité.
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — frontière de coordination pour UAV équipés de caméra, avec un véritable émetteur de commandes MAVLink — valide également ses propres commandes contre cette même barrière partagée de tâches et de sécurité.

**Fait Également Partie de l'Écosystème**

*Backend Central & Clients*
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — tableau de bord de contrôle web avec visualisation 3D multi-robot en temps réel.
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — centre de commande d'essaim de bureau (PySide6) pour plusieurs serveurs à la fois, empaqueté en exécutable autonome.
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — application de contrôle Android native avec connexion biométrique et un compagnon Wear OS jumelé.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — application de contrôle iOS/iPadOS (Flutter) avec synchronisation WebSocket en temps réel.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — interface tactile native pour l'écran tactile DSI 7" embarqué, intégrée directement sur le CM5.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — créateur/éditeur graphique de bureau pour URDF qui envoie les modèles terminés vers le propre catalogue de STUDIO.

*Plateforme d'Outils URTC*
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — outil de bureau à interface graphique pour flasher les cartes URTC, CAN-OTA plus SWD/JTAG puce complète.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — outil de bureau de diagnostic CAN-bus en direct pour cartes URTC, un panneau par profil d'outil.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — alternative basée navigateur à URTC-TESTER via la Web Serial API, sans installation locale.

*Nœud IA de Vision (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — hub d'intégration pour le pipeline de vision Hailo-8, avec une vraie vérification de disponibilité matérielle par étape.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — registre réel de modèles compilés avec vérification de chargement sécurisé par architecture Hailo/checksum.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — générateur réel de pipeline GStreamer + config MediaMTX, avec une vraie frontière d'intégration HailoRT.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — vraie loi de correction Position-Based Visual Servoing, verrouillée sur l'état de zone en amont.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — vraie vérification de violation de zone et demande d'E-STOP, avec application de la fraîcheur de calibration.

*Nœud IA Cognitif (Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — hub d'intégration pour le pipeline cognitif Hailo-10 (orchestration LLM/VLA/voix).
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — vrai encodage/décodage de jetons d'action et génération de trajectoire pour un modèle Vision-Language-Action.
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — vrai front-end vocal (VAD + analyseur d'intention) avec un relais Watch borné et soumis à confirmation.
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — vraie décomposition de tâches basée sur des règles et récupération sémantique d'erreurs sur les codes d'erreur MCU.
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — vraie recherche documentaire TF-IDF (bibliothèque standard uniquement) sur les propres documents Markdown de cet écosystème.

*Orchestration & Essaim*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — hub d'intégration avec un vrai contrat de rapport de santé gRPC/Protobuf et une machine à états de mission.
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — vraie file de tâches basée sur la priorité avec déduplication, via une vraie API HTTP.
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — vrai chien de garde de santé de flotte basé sur gRPC, avec retry/backoff et détection d'incohérence d'identité.
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — vrai planificateur de trajectoire 3D basé sur RRT, avec vraie validation des collisions obstacle/espace de travail.
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — vraie synchronisation d'état CRDT LWW-Element-Map, testée par propriétés pour la convergence multi-cellule.

*Jumeau Numérique & Simulation*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — hub d'intégration pour le moteur de jumeau numérique, avec un vrai contrat de synchronisation par compatibilité de version.
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — vrai verrouillage de sécurité hardware-in-the-loop routant les commandes entre simulation et matériel réel.
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — vraie cinématique directe et validation des limites articulaires sur un vrai sous-ensemble URDF.
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — vrai générateur procédural de scènes 2D avec export d'annotations YOLO/COCO.

*Données & Analytique*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — vrai magasin de séries temporelles basé sur sqlite3, avec une vraie API HTTP d'ingestion/requête.
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — vrai détecteur d'anomalies FFT + ligne de base statistique, avec surveillance de dérive.
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — vrai calcul OEE/disponibilité sur l'historique de DATALAKE, avec export CSV reproductible.
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — vrai pipeline d'ingestion CAN/WebSocket vers DATALAKE, avec déduplication par séquence.

*Passerelle Industrielle*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — hub d'intégration relayant vers les protocoles industriels, avec une vraie couche de liste blanche de commandes/contre-pression.
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — vrai espace d'adressage OPC-UA, vérifié avec une vraie session client du protocole binaire.
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — vrai broker MQTT avec authentification par client optionnelle et ACL de sujets.
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — vrais points de terminaison XML MTConnect `/probe` et `/current`, avec sortie en mode dégradé.

*Outils Complémentaires & Opérations de l'Écosystème*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — panneaux Smart Summaries et Anomaly Highlighting sur DATALAKE/ANOMALY-DETECTOR, avec un repli statistique honnête.
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — CLI de flotte avec un vrai contrat de codes de sortie stable, un vrai client en direct de la propre API de HYDRA-UMC-SERVER.
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — application compagnon WearOS avec de vraies alertes haptiques et un relais vocal vers le téléphone jumelé.
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware pour un rack de montage de cartes avec décodage réel d'ID d'outil et logique de préchauffage Smart Idle.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware plus un vrai compagnon de vision Python pour une tête d'outil d'inspection thermique/RGB.

---

## 📚 Documentation & Communauté

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — pile technologique et lignes directrices de codage pour une pull request.
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** — les normes de comportement attendues dans cette communauté.
- **[SECURITY.md](SECURITY.md)** — comment signaler une vulnérabilité, et les véritables axes de sécurité de ce projet.
- **[SUPPORT.md](SUPPORT.md)** — où poser des questions et signaler des bugs.

## 👤 AUTEUR
**JuanenRac** (Electro Hobby 3D)
📧 electrohobby3d@gmail.com
📺 [youtube.com/@electrohobby3d](https://youtube.com/@electrohobby3d)

## 📜 LICENCE

Le code est GPL-3.0 ou version ultérieure ; la documentation est CC BY-SA 4.0. Voir [LICENCE](LICENSE).

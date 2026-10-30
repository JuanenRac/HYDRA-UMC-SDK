<!-- =============================================================================
HYDRA-UMC-SDK - Shared contracts and integration toolkit
Copyright (C) JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-SDK banner" width="100%">
</p>

# 🧰 HYDRA-UMC-SDK

<p align="center"><a href="README.md">🇺🇸 English</a> | <a href="README_spa.md">🇪🇸 Español</a> | 🇫🇷 <b>Français</b> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | <a href="README_jpn.md">🇯🇵 日本語</a> | <a href="README_por.md">🇵🇹 Português</a></p>

### 🧰 Contrats partagés, clients de référence et outils d'intégration pour HYDRA-UMC

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Contracts-JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="Contracts">
  <img src="https://img.shields.io/badge/Reference%20clients-Python%20%7C%20Go%20%7C%20TypeScript%20%7C%20Rust-blueviolet.svg" alt="Reference%20clients">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="Integration">
  <img src="https://img.shields.io/badge/Tests-506%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.4.0-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-established-2EA44F.svg" alt="Maturity">
</p>

---

> **Vérification d'honnêteté - ce qui fonctionne réellement aujourd'hui :** les dix contrats JSON Schema v1 avec une fixture valide et une invalide chacun, le validateur Python, la première tranche OpenAPI v1 de HYDRA-UMC-SERVER, les clients Go, TypeScript et Rust qui appliquent les mêmes schémas, les aides pour passerelles et la matrice de compatibilité sont réels et testés sur un ordinateur (506 tests Python, plus les suites des trois autres clients). Protobuf n'est pas encore publié, la porte des jobs est une fonction logicielle partagée et non une fonction de sécurité certifiée, et rien ici n'a tourné sur du vrai matériel.

---

> **État de la sûreté et de la cybersécurité :** cet écosystème n'est pas un système de sécurité certifié. Il n'existe pas encore de chaîne d'E-STOP matérielle, ni de limites ou de verrouillages imposés par le firmware, ni de commande de mouvement vérifiée ; les images de firmware sont contrôlées par CRC-32 et une signature Ed25519, et une compilation de version refuse les clés de développement publiées (les têtes d'outil et les cartes d'extension derrière le relais utilisent encore les chargeurs d'URTC, qui prennent un HMAC-SHA256 à clé partagée au lieu d'une signature) ; TLS et TLS mutuel sont optionnels et désactivés par défaut ; aucune carte propre n'a encore été assemblée ni testée. Lisez la [base de sécurité](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md) et le [modèle de menaces](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md) avant de vous fier à une affirmation d'ici pour la sécurité d'une personne.

---

## 📋 En un coup d'œil

| | |
|---|---|
| Version | `0.4.0` |
| Maturité | Établi |
| Tests | 506 (`python -m unittest discover -s clients/python/tests`) |
| Technologie | Python / TypeScript / Go / Rust / JSON Schema |
| Sur matériel réel | Pas encore : aucune exécution sur du matériel réel n'est consignée pour cette version |

**Aller à :** [Présentation](#-présentation) · [Architecture](#-architecture) · [Fonctionnalités](#-fonctionnalités) · [Sécurité et protection](#-sécurité-et-protection) · [Interfaces](#-interfaces) · [Configuration](#-configuration) · [Démarrage rapide](#-démarrage-rapide) · [Tests](#-tests) · [Dépannage](#-dépannage) · [Structure du dépôt](#-structure-du-dépôt) · [Projets liés](#-projets-liés)

## 🚦 État du projet

Chaque ligne est une partie de ce dépôt et le feu dit où elle en est aujourd'hui. Elle est écrite d'après ce que le dépôt peut montrer (tests, compilations, exécutions), pas d'après ce qui est prévu.

🟢 Fait et vérifié · 🟡 Fonctionne, avec des limites connues · 🟠 À moitié fait ou pas encore vérifié · 🔴 Pas fait ou ne fonctionne pas

| Domaine | État | Ce que cela veut dire ici |
|---|---|---|
| Logiciel | 🟢 | Complet pour son usage et stable ; la vérification d'honnêteté ci-dessus liste les limites connues |
| Tests | 🟢 | 506 tests automatiques, exécutés à chaque modification |
| Matériel réel | 🔴 | Pas encore : aucune exécution sur du matériel réel n'est consignée pour cette version |
| Documentation | 🟢 | README en huit langues, vérifié par rapport au manifeste à chaque modification |

## 🎯 Présentation

HYDRA-UMC-SDK définit le langage stable partagé par les services HYDRA-UMC,
clients, adaptateurs CM5 et intégrations URTC. Elle possède des contrats normatifs, un
validateur de référence Python sans dépendance, des fixtures de conformité et
un accompagnement pour l'intégration. Il ne remplace pas les API officielles de Raspberry Pi OS, Hailo, ROS 2, MQTT, OPC-UA ou
MTConnect.

## 🧩 Rôle dans HYDRA-UMC

**HYDRA-UMC-SDK** est la langue commune de l'écosystème : les contrats JSON Schema v1, la première tranche OpenAPI du serveur, des clients de référence en Python, Go, TypeScript et Rust, les aides pour passerelles que toutes les passerelles et le hub de connecteurs utilisent, et les outils qui gardent identiques les outils de chaque dépôt. Il n'exécute aucun service propre et ne remplace aucune API officielle.

## 🏛️ Architecture

<p align="center">
  <img src="images/architecture.svg" alt="HYDRA-UMC-SDK architecture" width="100%">
</p>

## ✨ Fonctionnalités

### Statut

Les contrats JSON Schema v1, les fixtures valides/invalides, un client de validation Python
et les tests côté hôte sont implémentés, ainsi qu'une vraie première tranche OpenAPI v1
pour la surface HTTP propre de HYDRA-UMC-SERVER (`contracts/openapi/v1/server.openapi.json`
- voir [docs/CONTRACTS.md](docs/CONTRACTS.md#openapi-v1)). La publication Protobuf est une étape de compatibilité ultérieure ; les clients Go, TypeScript et Rust existent déjà.

Une matrice de compatibilité réelle et automatique (`tools/verify_contract_matrix.py`)
recoupe chaque schéma publié avec la propre liste de contrats du validateur
Python - elle a trouvé et corrigé une lacune réelle où `project-manifest.schema.json`
(le contrat `hydra-umc.project.json` que chaque dépôt de cet écosystème publie)
n'avait aucune entrée de validateur, et prouve désormais que chaque fixture
de conformité est jugée comme son propre nom de fichier l'affirme, ainsi que les
cas de contrat inconnu et de version de schéma incompatible.

Des contrats supplémentaires ont été livrés depuis le premier jalon (11 au total)
ci-dessous : un contrat public de pont vers des machines externes
`BridgeJob`/`GateDecision` (voir
[docs/BRIDGE_CONTRACT.md](docs/BRIDGE_CONTRACT.md)), partagé par
`HYDRA-UMC-BRIDGE-ROS2`/`-OPENPNP`/`-PRINTER3D`/`-CNC`/`-LASER`/`-AMR`/`-DROIDS`/`-UAV` et doté
de sa propre forme JSON réelle (`job_to_dict()`/`job_from_dict()`/
`decision_to_dict()`), plus l'état de la machine que le bridge observe lui-même, que la porte utilise à la place de celui que déclare le demandeur, et une admission des travaux (`JobIntake`/`IdempotencyStore`) qui ignore les messages retenus et n'exécute jamais deux fois une clé d'idempotence ; un contrat `ScenarioOutcome` plus
`compare_runs()`, une vérification partagée « est-ce vraiment
corrigé » qui renvoie `apparent-success` (pas `regression-fixed`) quand
un échec cesse de se reproduire mais que l'empreinte de base n'a jamais
bougé ; un contrat `Operation` plus
`validate_status_transition()`, le cycle de vie partagé
objectif/tâche/opération - `received`/`authorized`/`queued`/`sent`/
`confirmed`/`terminated`/`rejected`, jamais un seul panier « exécuté »
fourre-tout ; un `result` optionnel sur `Operation` plus
`concludes_success()` - une preuve réelle (`run_id`/`origin`/
`observers_enabled`/`outcome`) qui refuse de conclure au succès à
partir d'un résultat périmé/rejoué ou d'une exécution avec observation
désactivée ; un contrat `Capability` autonome plus
`is_capability_usable()` - le fait qu'une cible *déclare* prendre
en charge un `kind` d'opération est modélisé séparément du fait que ce
support a été *récemment et réellement vérifié*
(`last_checked_at_utc`/`checked_configuration`/`max_age_seconds`), pour
qu'une capacité déclarée mais jamais vérifiée ou périmée ne soit jamais
traitée silencieusement comme utilisable ; et un
`hydra-umc-sdk-mock-server`
(`mock_server.py`) qui sert un exemple de payload valide par contrat
connu via HTTP simple, pour qu'une UI ou un adaptateur puisse être
développé avant qu'un vrai matériel CM5/robot/MCU soit disponible. Les 11
contrats disposent chacun d'au moins une fixture de conformité valide et
une invalide, vérifiées par la matrice de compatibilité ci-dessus.

## 🔒 Sécurité et protection

| Menace | Défense | Où |
|---|---|---|
| Une commande de passerelle hors de son contrat | Un job porte au plus 32 paramètres, des noms de 64 caractères, des valeurs de 1024 et des identifiants de 128 ; l'état machine observé par la passerelle est utilisé, pas celui que prétend le demandeur | `bridge_contract.py` |
| La même commande exécutée deux fois, ou un message retenu rejoué | L'admission des jobs ignore les messages retenus et n'exécute jamais deux fois une clé d'idempotence | `job_intake.py` |
| Un arrêt qui attend derrière une longue commande | Les commandes ordinaires s'exécutent une à une sur une voie et les verbes d'arrêt sur une seconde voie | `bridge_transport.py` |
| Identifiants du broker dans un fichier de configuration, ou broker non vérifié | Utilisateur et mot de passe viennent de l'environnement ou d'un fichier, TLS peut vérifier le broker contre une CA, et un certificat client avec sa clé active le TLS mutuel | `mqtt_connection.py` |
| Un schéma modifié sans que le validateur suive | Une matrice de compatibilité vérifie chaque schéma publié contre la liste de contrats du validateur et juge chaque fixture d'après ce que dit son nom de fichier | `tools/verify_contract_matrix.py` |

**Ce qu'il ne fait jamais :** servir de fonction de sécurité certifiée. La porte des jobs est une implémentation logicielle partagée par les passerelles, pas une certification de sécurité.

## 🔌 Interfaces

| Topic ou route | Ce qu'il porte |
|---|---|
| `contracts/json-schema/v1/` | dix contrats JSON Schema v1 : capacité, descripteur d'appareil, enveloppe d'événement, rapport de santé, opération, manifeste de projet, état de sécurité, résultat de scénario, découverte de serveur, manifeste de mise à jour |
| `contracts/openapi/v1/server.openapi.json` | la première tranche OpenAPI v1 de HYDRA-UMC-SERVER : découverte, connexion, réglages et commandes (un sous-ensemble du `docs/openapi.json` du serveur lui-même) |
| `contracts/ports.yaml` | le registre du port, du chemin de santé et de l'unité systemd de chaque service, produit par `tools/sync_ports.py` |
| `hydra/bridges/<name>/cmd/#` | où une passerelle écoute ; elle répond sur `.../<verbe>/result` |
| `hydra-umc-contract-validate`, `hydra-umc-sdk-mock-server` | le validateur en ligne de commande (code de sortie 2 en cas d'échec) et un serveur factice sur `127.0.0.1:8790` qui sert un exemple valide par contrat |

## ⚙️ Configuration

| Variable | Par défaut | Ce qu'elle définit |
|---|---|---|
| `HYDRA_MQTT_USERNAME`, `HYDRA_MQTT_PASSWORD` | pas d'identifiant | l'identifiant du broker ; le mot de passe seulement avec le nom d'utilisateur |
| `HYDRA_MQTT_PASSWORD_FILE` | - | le mot de passe lu dans un fichier (un secret Docker ou systemd) ; ignoré si la variable ci-dessus est définie |
| `HYDRA_MQTT_TLS`, `HYDRA_MQTT_TLS_CA` | pas de TLS | `HYDRA_MQTT_TLS=1` vérifie le broker contre les CA du système ; `HYDRA_MQTT_TLS_CA` désigne le fichier de la CA qui a signé son certificat |
| `HYDRA_MQTT_TLS_CERT`, `HYDRA_MQTT_TLS_KEY` | - | le certificat client et sa clé pour un broker qui exige le TLS mutuel ; les deux sont nécessaires et activent TLS |
| `--host`, `--port` | `127.0.0.1`, `8790` | où écoute le serveur factice |
| `HYDRA_UMC_SDK_ROOT` | le dossier voisin | où les tests des autres dépôts trouvent celui-ci |

## 🚀 Démarrage rapide

Nécessite Python 3.11 ou plus récent. Les clients Go, TypeScript et Rust sont aussi construits et testés si leur chaîne d'outils est installée.

```bash
PYTHONPATH=clients/python/src python -m unittest discover -s clients/python/tests  # the Python client tests
python tools/verify_contract_matrix.py                                             # every schema against the validator and every fixture
PYTHONPATH=clients/python/src python -m hydra_umc_sdk.validation --help            # the contract validator on the command line
./build-test.sh                                                                    # the non-mutating build check (build-test.bat on Windows)
```

## 🧪 Tests

506 tests automatiques s'exécutent avec `python -m unittest discover -s clients/python/tests`. Les autres clients ont leurs propres suites : 28 tests en Go (`go test ./...`), 105 en TypeScript (`npm test`) et 31 en Rust (`cargo test`), lancés par `tools/extra_build_steps.py` si la chaîne d'outils est installée. Aucun n'a besoin de matériel.

La CI exécute `HYDRA_UMC_CI=1 python tools/ci_validate.py`, qui vérifie le manifeste, les documents, les huit README et les images.

## 🏗️ Compilation et publication

Utilisez la vérification de compilation sans versionnement avant une compilation de publication :

| Action | Windows | Linux / macOS |
|---|---|---|
| Vérification de compilation (sans modifier la version ni le CHANGELOG) | `build-test.bat` | `./build-test.sh` |
| Exécution / développement (si disponible) | `run*.bat` ou `dev*.bat` | `./run*.sh` ou `./dev*.sh` |

`build-test.bat` et `build-test.sh` compilent ou valident la pile du projet sans incrémenter `hydra-umc.project.json` ni modifier `CHANGELOG.md`. Ils peuvent uniquement créer les sorties normales du compilateur. Les scripts existants `build*.bat`, `build*.sh`, `run*` et `dev*` conservent leur comportement spécifique de versionnement ou d'exécution ; utilisez-les lorsque ce comportement est requis.

## 🩺 Dépannage

| Vous voyez | Parce que | Faites |
|---|---|---|
| `hydra-umc-contract-validate: missing required field: ...` | La charge utile viole le contrat ; la commande se termine avec le code de sortie 2 | Comparez le fichier avec l'exemple que sert le serveur factice pour ce contrat |
| `verify_contract_matrix.py` échoue | Un schéma a été ajouté ou modifié sans mettre à jour la liste de contrats du validateur ou une fixture | Ajoutez l'entrée du validateur et une fixture valide et une invalide |
| `go test ./...` est ignoré | La vérification de build n'exécute les clients Go, TypeScript et Rust que si `go`, `npm` et `cargo` sont dans le PATH | Installez la chaîne d'outils ; la vérification affiche quel client a été ignoré |

## 📂 Structure du dépôt

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of HYDRA-UMC-SDK" width="100%">
</p>

<details>
<summary>Version texte de l'arborescence</summary>

```text
HYDRA-UMC-SDK/
├── contracts/                 sources JSON Schema v1, tranche OpenAPI et registre des ports
├── clients/                   les clients de référence Python, Go, TypeScript et Rust
├── conformance/               fixtures valides et invalides pour chaque contrat
├── docs/                      guides des contrats, de l'API et du développement
├── examples/                  exemples Python exécutables
├── tools/                     matrice des contrats, porte OpenAPI, synchro des outils, vérification de build
├── .github/                   workflow de CI et modèles de tickets
├── images/                    bannière et images du README
├── CHANGELOG.md               ce qui a changé à chaque version
├── build-test.sh              vérification de build sans modification
├── build.sh                   construit et vérifie ; ne change jamais la version
├── bump_manifest_version.py   synchronise la version du manifeste
├── bump_version.py            montée de version explicite
├── hydra-umc.project.json     manifeste : version, maturité, famille
├── run.sh                     démarre le programme
└── test.sh                    lance les tests
```

</details>

`tools/`: `verify_contract_matrix.py` (matrice de compatibilité schéma/validateur), `verify_openapi.py` (validation structurelle OpenAPI sans dépendance) et le moteur non destructif de `build-test`. `sync_repo_tools.py` maintient identiques les outils partagés de tous les dépôts, `pin_sdk.py` fixe les consommateurs du SDK sur une étiquette de version, et `canonical/` contient les copies uniques qui sont répliquées (dont la commande `hydra_project_tool.py`, qui valide, teste et ne change la version que sur demande). `sync_ports.py` génère et vérifie `contracts/ports.yaml`, le registre du port, du chemin de santé et de l'unité systemd de chaque service ; la rédaction commune des secrets (`canonical/redaction.py`, avec ses cas dans `contracts/redaction/vectors.json`) est copiée dans les projets qui envoient du texte vers l'extérieur.

## 🗺️ Feuille de route et limites connues

**Limites connues aujourd'hui**

* Protobuf n'est pas encore publié, et la tranche OpenAPI ne couvre que la découverte, la connexion, les réglages et les commandes.
* Les routes du serveur ne sont pas versionnées aujourd'hui ; `/api/v1` est l'objectif de conception décrit dans `docs/API_DESIGN.md`.
* Rien ici n'a tourné sur du vrai matériel, et la porte des jobs est une fonction logicielle, pas une fonction de sécurité certifiée.

**Ensuite :** publier Protobuf là où une intégration en a besoin et étendre la tranche OpenAPI au reste des routes du serveur.

## 🌍 Langues

Ce README et les documents du dépôt existent en huit langues : anglais, espagnol, allemand, français, italien, japonais, chinois et portugais (Portugal). Ils sont écrits ensemble et la CI vérifie que les huit fichiers ont les mêmes sections et les mêmes liens. Ce dépôt n'a ni écran ni catalogue de messages propre, il n'y a donc aucune chaîne d'interface à traduire.

## 🔗 Projets liés

Ce projet fait partie de l'écosystème robotique HYDRA-UMC du même auteur (JuanenRac / Electro Hobby 3D). Bon à savoir, car une demande pourrait en réalité concerner l'un de ceux-ci plutôt que ce dépôt.

**Projet Parent**
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — couche produit reproductible sur Raspberry Pi OS pour le CM5 : agent en lecture seule, config/profils validés, provisionnement WiFi de premier contact ; un agent d'appareil consommateur des propres contrats d'appareil, de santé, de sécurité et de mise à jour de ce SDK.
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — registre déclaratif et validateur de manifestes d'adaptateur pour les connecteurs de machines externes ; étend la propre idée de contrat du SDK aux machines externes sans remplacer les projets de passerelle industrielle.

**Directement Liés**
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — le vrai backend headless (REST/WebSocket) auquel parle réellement chaque client de contrôle — un producteur et consommateur d'API authentifié gouverné par les propres contrats de ce SDK.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — outil administratif de bureau qui découvre, clone et met à jour chaque dépôt de cet écosystème — publie des métadonnées de version et de compatibilité consommées par les propres clients de ce SDK conscients du contrat.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — outil de bureau Windows/Linux qui construit une image de la CM5 prête à graver, préchargée avec les versions les plus actuelles de l'écosystème, avec une configuration de premier démarrage Wi-Fi/utilisateur/SSH façon Raspberry Pi Imager.
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — coordinateur d'incidents de maintenance : un rôle edge à faible privilège collecte un instantané d'inventaire/santé assaini, un rôle control-plane le rend en lecture seule et demande à un fournisseur d'IA de suggérer un diagnostic - n'applique jamais de correctif ni ne déploie rien.
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — hôte de développement reproductible (Raspberry Pi 5 / CM5) qui héberge le code source de l'écosystème et exécute des tâches de compilation/test délimitées via une file d'attente durable ; un rôle de développement dédié, explicitement distinct d'un CM5 opérationnel.
- **[HYDRA-UMC-DOCS](https://github.com/JuanenRac/HYDRA-UMC-DOCS)** — le centre de documentation et d'outils de l'écosystème : architecture, interfaces, socle de sécurité, matrice des capacités et catalogue de projets généré à partir de chaque manifeste.
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — la conception de la carte mère du bras robotique : hôte CM5 + coprocesseur STM32H745 double cœur, destinée à coordonner jusqu'à 8 bras-outils via CAN-OTA/SPI-OTA (firmware à un stade précoce ; aucune carte assemblée pour l'instant).
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware pour la carte physique Universal Robot Tool Controller, plus de 25 profils d'outil sur bus CAN — une plateforme de contrôleur d'outil indépendante connectée via les propres adaptateurs d'intégration versionnés de ce SDK.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — coordinateur avec un transport ROS 2 rclpy à importation paresseuse (pas encore exécuté contre une installation ROS 2) — utilise la propre barrière commune BridgeJob de ce SDK pour l'observation, l'inspection et le travail de cellule annulable ROS 2.
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — coordinateur haut niveau sûr pour le flux de cartes du pick-and-place OpenPnP — utilise les propres tâches corrélées et idempotentes de ce SDK pour des passations de PCB traçables.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — frontière de coordination sûre pour imprimantes 3D Moonraker/Klipper, avec de vraies commandes de tâche contrôlées — utilise la propre barrière de ce SDK autour de la disponibilité native de l'imprimante ; elle n'expose ni le contrôle du chauffage ni celui du mouvement.
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — coordinateur haut niveau pour cellules CNC avec accès au statut/octets de contrôle GRBL (testé uniquement contre un émulateur) — utilise la propre barrière de ce SDK pour ne coordonner qu'aux côtés d'une CNC inactive et sécurisée.
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — coordinateur de cellules laser lisant 3 signaux GPIO de clé/enceinte/verrouillage (testé uniquement contre une puce simulée ; il ne peut ni armer ni tirer un laser) — utilise la propre barrière de ce SDK pour les auxiliaires, tout en préservant l'autorité de sécurité du laser.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — frontière de coordination pour les flottes AGV/AMR via un éditeur MQTT VDA 5050 (testé uniquement contre une flotte émulée) — valide également ses propres commandes contre cette même barrière partagée de tâches et de sécurité.
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — frontière de coordination pour droïdes à pattes/humanoïdes, avec un émetteur de commandes Boston Dynamics Spot (testé uniquement contre un émulateur) — valide également ses propres commandes contre cette même barrière partagée de tâches et de sécurité.
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — frontière de coordination pour UAV équipés de caméra, avec un émetteur de commandes MAVLink (testé uniquement contre un émulateur) — valide également ses propres commandes contre cette même barrière partagée de tâches et de sécurité.

**Fait Également Partie de l'Écosystème**

*Backend Central & Clients*
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — tableau de bord de contrôle web avec visualisation 3D multi-robot en temps réel.
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — centre de commande d'essaim de bureau (PySide6) pour plusieurs serveurs à la fois, empaqueté en exécutable autonome.
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — application de contrôle Android native avec connexion biométrique et un compagnon Wear OS jumelé.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — application de contrôle iOS/iPadOS (Flutter) avec synchronisation WebSocket en temps réel.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — interface tactile native pour l'écran tactile DSI 7" embarqué, intégrée directement sur le CM5.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — créateur/éditeur graphique de bureau pour URDF qui envoie les modèles terminés vers le propre catalogue de STUDIO.
- **[HYDRA-UMC-EDITOR-STL](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-STL)** — éditeur de bureau de modèles STL, transformant/remplaçant/retirant/ajoutant de vraies pièces dans le même catalogue de modèles qu'édite aussi HYDRA-UMC-EDITOR-URDF.

*Plateforme d'Outils URTC*
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — outil de bureau à interface graphique pour flasher les cartes URTC, CAN-OTA plus SWD/JTAG puce complète.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — outil de bureau de diagnostic CAN-bus en direct pour cartes URTC, un panneau par profil d'outil.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — alternative basée navigateur à URTC-TESTER via la Web Serial API, sans installation locale.
- **[URTC-GATEWAY](https://github.com/JuanenRac/URTC-GATEWAY)** — passerelle devant le bus CAN d'URTC : liste d'identifiants autorisés, limite de débit et clé de session ; logiciel testé sur ordinateur, pas encore sur un bus réel.

*Nœud IA de Vision (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — hub d'intégration pour le pipeline de vision Hailo-8, avec une vraie vérification de disponibilité matérielle par étape.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — registre réel de modèles compilés avec vérification de chargement sécurisé par architecture Hailo/checksum.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — générateur réel de pipeline GStreamer + config MediaMTX, avec une vraie frontière d'intégration HailoRT.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — loi de correction Position-Based Visual Servoing avec autorisation conditionnée à l'état de zone ; pas encore d'estimation de pose par caméra.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — logique v0 de violation de zone, de fraîcheur de calibration et de demande d'E-STOP qui lit les positions d'objets dans un fichier ; aucun détecteur ne l'alimente et aucun E-STOP physique n'y est encore relié.

*Nœud IA Cognitif (Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — hub d'intégration pour le pipeline cognitif Hailo-10 (orchestration LLM/VLA/voix).
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — vrai encodage/décodage de jetons d'action et génération de trajectoire pour un modèle Vision-Language-Action.
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — vrai front-end vocal (VAD + analyseur d'intention) avec un relais Watch borné et soumis à confirmation.
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — vraie décomposition de tâches basée sur des règles et récupération sémantique d'erreurs sur les codes d'erreur MCU.
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — vraie recherche documentaire TF-IDF (bibliothèque standard uniquement) sur les propres documents Markdown de cet écosystème.
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — technicien de maintenance IA local et à portes de politique pour l'écosystème lui-même - observe, diagnostique et propose des corrections ; les deux niveaux de risque les plus élevés ne sont délibérément pas encore implémentés.

*Orchestration & Essaim*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — hub d'intégration avec un vrai contrat de rapport de santé gRPC/Protobuf et une machine à états de mission.
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — vraie file de tâches basée sur la priorité avec déduplication, via une vraie API HTTP.
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — vrai chien de garde de santé de flotte basé sur gRPC, avec retry/backoff et détection d'incohérence d'identité.
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — vrai planificateur de trajectoire 3D basé sur RRT, avec vraie validation des collisions obstacle/espace de travail.
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — vraie synchronisation d'état CRDT LWW-Element-Map, testée par propriétés pour la convergence multi-cellule.

*Jumeau Numérique & Simulation*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — hub d'intégration pour le moteur de jumeau numérique, avec un vrai contrat de synchronisation par compatibilité de version.
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — routeur hardware-in-the-loop avec un verrouillage logiciel de collision entre simulation et matériel réel (testé sans matériel réel).
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
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — application compagnon WearOS avec des motifs d'alerte haptique et un relais vocal vers le téléphone jumelé (pas encore exécutée sur une montre physique).
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware pour un rack de montage de cartes avec décodage réel d'ID d'outil et logique de préchauffage Smart Idle.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware plus un vrai compagnon de vision Python pour une tête d'outil d'inspection thermique/RGB.

## 📚 Documentation

Où lire la suite :

* [Base de sécurité de l'écosystème](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)
* [Modèle de menaces de l'écosystème](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)
* [Journal des modifications de ce dépôt](CHANGELOG.md)
* [Licence de ce dépôt](LICENSE.md)

## 🤝 Contribuer et communauté

* Avant une pull request, exécutez `HYDRA_UMC_CI=1 py -3 tools/ci_validate.py` (ou `HYDRA_UMC_CI=1 python3 tools/ci_validate.py`) : il doit afficher `CI_VALIDATION=PASS`. N'exécutez pas `build.sh` ni `build.bat` pour cette vérification ; compiler n'est pas vérifier.
* Les huit README sont écrits à partir d'une source unique dans HYDRA-UMC-DOCS ; ne les modifiez pas à la main. Changez la source et réécrivez-les avec `tools/make_readmes.py`.
* N'affirmez pas dans un README ce qui n'a pas tourné : écrivez « simulé » ou « non essayé sur matériel » quand c'est la vérité.
* Voir [CONTRIBUTING.md](CONTRIBUTING.md), le [code de conduite](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md) et [SUPPORT.md](SUPPORT.md).

## 👤 AUTEUR

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 LICENCE

GPL-3.0-or-later - [LICENSE](LICENSE).

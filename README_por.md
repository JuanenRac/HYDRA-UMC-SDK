<!-- =============================================================================
HYDRA-UMC-SDK - Shared contracts and integration toolkit
Copyright (C) JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-SDK banner" width="100%">
</p>

# 🧰 HYDRA-UMC-SDK

<p align="center"><a href="README.md">🇺🇸 English</a> | <a href="README_spa.md">🇪🇸 Español</a> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | <a href="README_jpn.md">🇯🇵 日本語</a> | 🇵🇹 <b>Português</b></p>

### 🧰 Contratos partilhados, clientes de referência e ferramentas de integração para o HYDRA-UMC

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Contracts-JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="Contracts">
  <img src="https://img.shields.io/badge/Reference%20clients-Python%20%7C%20Go%20%7C%20TypeScript%20%7C%20Rust-blueviolet.svg" alt="Reference%20clients">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="Integration">
  <img src="https://img.shields.io/badge/Tests-492%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.3.9-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-established-2EA44F.svg" alt="Maturity">
</p>

---

> **Verificação de honestidade - o que realmente funciona hoje:** os dez contratos JSON Schema v1 com uma fixture válida e outra inválida cada um, o validador Python, a primeira fatia OpenAPI v1 do HYDRA-UMC-SERVER, os clientes Go, TypeScript e Rust que aplicam os mesmos esquemas, os auxiliares de ponte e a matriz de compatibilidade são reais e testados num computador (492 testes Python, mais as suites dos outros três clientes). O Protobuf ainda não está publicado, a porta de trabalhos é uma função de software partilhada e não uma função de segurança certificada, e nada disto correu em hardware real.

---

> **Estado de segurança (safety e security):** este ecossistema não é um sistema de segurança certificado. Ainda não existe um caminho de E-STOP por hardware, nem limites ou interlocks impostos pelo firmware, nem um comando de movimento verificado; as imagens de firmware são verificadas com CRC-32 e uma assinatura Ed25519, e uma compilação de versão recusa as chaves de desenvolvimento publicadas (as cabeças de ferramenta e as placas de expansão atrás do relé ainda usam os bootloaders do URTC, que aceitam um HMAC-SHA256 de chave partilhada em vez de uma assinatura); TLS e TLS mútuo são opcionais e estão desativados por defeito; nenhuma placa própria foi ainda montada ou testada. Leia a [base de segurança](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md) e o [modelo de ameaças](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md) antes de confiar em qualquer afirmação aqui para a segurança de uma pessoa.

---

## 📋 Num relance

| | |
|---|---|
| Versão | `0.3.9` |
| Maturidade | Estabelecido |
| Testes | 492 (`python -m unittest discover -s clients/python/tests`) |
| Tecnologia | Python / TypeScript / Go / Rust / JSON Schema |
| Em hardware real | Ainda não: não há registo de execução em hardware real para esta versão |

**Ir para:** [Visão geral](#-visão-geral) · [Arquitetura](#-arquitetura) · [Funcionalidades](#-funcionalidades) · [Segurança e proteção](#-segurança-e-proteção) · [Interfaces](#-interfaces) · [Configuração](#-configuração) · [Início rápido](#-início-rápido) · [Testes](#-testes) · [Resolução de problemas](#-resolução-de-problemas) · [Estrutura do repositório](#-estrutura-do-repositório) · [Projetos relacionados](#-projetos-relacionados)

## 🚦 Estado do projeto

Cada linha é uma parte deste repositório e a luz diz até onde chega hoje. É escrita com o que o repositório consegue demonstrar (testes, compilações, execuções), não com o que está previsto.

🟢 Feito e verificado · 🟡 Funciona, com limites conhecidos · 🟠 Feito a meio ou ainda por verificar · 🔴 Por fazer ou a não funcionar

| Área | Estado | O que significa aqui |
|---|---|---|
| Software | 🟢 | Completo para o seu propósito e estável; a verificação de honestidade acima lista os limites conhecidos |
| Testes | 🟢 | 492 testes automáticos, executados a cada alteração |
| Hardware real | 🔴 | Ainda não: não há registo de execução em hardware real para esta versão |
| Documentação | 🟢 | README em oito idiomas, verificado contra o manifesto a cada alteração |

## 🎯 Visão geral

O HYDRA-UMC-SDK define a linguagem estável partilhada pelos serviços, clientes, adaptadores CM5 e integrações URTC do HYDRA-UMC. É dono dos contratos normativos, de um validador de referência em Python sem dependências, de fixtures de conformidade e de orientações de integração. Não substitui as APIs oficiais do Raspberry Pi OS, do Hailo, do ROS 2, do MQTT, do OPC-UA nem do MTConnect.

## 🧩 Papel no HYDRA-UMC

O **HYDRA-UMC-SDK** é a língua comum do ecossistema: os contratos JSON Schema v1, a primeira fatia OpenAPI do servidor, clientes de referência em Python, Go, TypeScript e Rust, os auxiliares de ponte que todas as pontes e o concentrador de conectores usam, e as ferramentas que mantêm idênticas as ferramentas de cada repositório. Não corre nenhum serviço próprio nem substitui nenhuma API oficial.

## 🏛️ Arquitetura

<p align="center">
  <img src="images/architecture.svg" alt="HYDRA-UMC-SDK architecture" width="100%">
</p>

## ✨ Funcionalidades

### Estado

Estão implementados os contratos JSON Schema v1, fixtures válidas/inválidas, um cliente de validação em Python, testes no anfitrião e uma primeira fatia real de OpenAPI v1 para a superfície HTTP do próprio HYDRA-UMC-SERVER (`contracts/openapi/v1/server.openapi.json`; ver [docs/CONTRACTS.md](docs/CONTRACTS.md#openapi-v1)). A publicação em Protobuf é um marco de compatibilidade posterior; os clientes Go, TypeScript e Rust já existem.

Uma matriz de compatibilidade real e automática (`tools/verify_contract_matrix.py`) cruza cada esquema publicado com a lista de contratos do próprio validador Python: encontrou e corrigiu uma lacuna real em que `project-manifest.schema.json` (o contrato `hydra-umc.project.json` que cada repositório deste ecossistema publica) não tinha nenhuma entrada no validador, e agora prova que cada fixture de conformidade é julgada como o seu próprio nome de ficheiro afirma, além dos casos de contrato desconhecido e de versão de esquema incompatível.

Desde então foram publicados mais contratos para além dos quatro do primeiro marco abaixo: um contrato público `BridgeJob`/`GateDecision` de bridge para máquinas externas (ver [docs/BRIDGE_CONTRACT.md](docs/BRIDGE_CONTRACT.md)), partilhado por `HYDRA-UMC-BRIDGE-ROS2`/`-OPENPNP`/`-PRINTER3D`/`-CNC`/`-LASER`/`-AMR`/`-DROIDS`/`-UAV` e com o seu próprio formato JSON real (`job_to_dict()`/`job_from_dict()`/`decision_to_dict()`), a que se juntam o estado da máquina que o próprio bridge observa, que a porta usa em vez do declarado por quem pede, e uma admissão de trabalhos (`JobIntake`/`IdempotencyStore`) que ignora mensagens retidas e não repete uma chave de idempotência; um contrato `ScenarioOutcome` mais `compare_runs()`, uma verificação partilhada de «foi mesmo corrigido» que devolve `apparent-success` (não `regression-fixed`) quando uma falha deixou de se reproduzir mas a impressão digital de base nunca se moveu; um contrato `Operation` mais `validate_status_transition()`, o ciclo de vida partilhado de objetivo/trabalho/operação (`received`/`authorized`/`queued`/`sent`/`confirmed`/`terminated`/`rejected`, nunca um único saco colapsado de «executado»); um `result` opcional em `Operation` mais `concludes_success()`, evidência real (`run_id`/`origin`/`observers_enabled`/`outcome`) que se recusa a concluir sucesso a partir de um resultado obsoleto/repetido ou de uma execução com a observação desativada; um contrato autónomo `Capability` mais `is_capability_usable()`, em que o facto de um alvo sequer *declarar* suporte para um tipo de operação (`kind`) se modela como dado distinto de esse suporte ter sido *verificado recentemente de facto* (`last_checked_at_utc`/`checked_configuration`/`max_age_seconds`), de modo que uma capacidade declarada mas nunca verificada, ou já obsoleta, nunca é tratada em silêncio como utilizável; e um `hydra-umc-sdk-mock-server` (`mock_server.py`) que serve um exemplo de carga válida por contrato conhecido em HTTP simples, para que uma interface ou adaptador se desenvolva contra ele antes de existir qualquer hardware real de CM5/robô/MCU. Todos os 10 contratos têm pelo menos uma fixture válida e uma inválida, verificadas pela matriz de compatibilidade acima.

## 🔒 Segurança e proteção

| Ameaça | Defesa | Onde |
|---|---|---|
| Um comando de ponte fora do seu contrato | Um trabalho leva no máximo 32 parâmetros, nomes de 64 caracteres, valores de 1024 e identificadores de 128; usa-se o estado da máquina que a ponte observa, não o que o requerente afirma | `bridge_contract.py` |
| O mesmo comando executado duas vezes, ou uma mensagem retida repetida | A admissão de trabalhos ignora mensagens retidas e nunca executa duas vezes uma chave de idempotência | `job_intake.py` |
| Uma paragem à espera atrás de um comando longo | Os comandos normais correm um de cada vez numa faixa e os verbos de paragem numa segunda faixa | `bridge_transport.py` |
| Credenciais do broker num ficheiro de configuração, ou broker não verificado | Utilizador e palavra-passe vêm do ambiente ou de um ficheiro, o TLS pode verificar o broker contra uma CA, e um certificado de cliente com a sua chave ativa o TLS mútuo | `mqtt_connection.py` |
| Um esquema alterado sem que o validador o acompanhe | Uma matriz de compatibilidade verifica cada esquema publicado contra a lista de contratos do validador e julga cada fixture pelo que o nome do ficheiro afirma | `tools/verify_contract_matrix.py` |

**O que nunca faz:** servir de função de segurança certificada. A porta de trabalhos é uma implementação de software partilhada pelas pontes, não uma certificação de segurança.

## 🔌 Interfaces

| Tópico ou rota | O que leva |
|---|---|
| `contracts/json-schema/v1/` | dez contratos JSON Schema v1: capacidade, descritor de dispositivo, envelope de evento, relatório de saúde, operação, manifesto de projeto, estado de segurança, resultado de cenário, descoberta de servidor, manifesto de atualização |
| `contracts/openapi/v1/server.openapi.json` | a primeira fatia OpenAPI v1 do HYDRA-UMC-SERVER: descoberta, início de sessão, definições e comandos (um subconjunto do `docs/openapi.json` do próprio servidor) |
| `contracts/ports.yaml` | o registo de porta, caminho de saúde e unidade systemd de cada serviço, gerado por `tools/sync_ports.py` |
| `hydra/bridges/<name>/cmd/#` | onde uma ponte escuta; responde em `.../<verbo>/result` |
| `hydra-umc-contract-validate`, `hydra-umc-sdk-mock-server` | o validador na linha de comandos (código de saída 2 em caso de falha) e um servidor simulado em `127.0.0.1:8790` que serve um exemplo válido por contrato |

## ⚙️ Configuração

| Variável | Predefinição | O que define |
|---|---|---|
| `HYDRA_MQTT_USERNAME`, `HYDRA_MQTT_PASSWORD` | sem credencial | a credencial do broker; a palavra-passe só junto com o utilizador |
| `HYDRA_MQTT_PASSWORD_FILE` | - | a palavra-passe lida de um ficheiro (um segredo do Docker ou systemd); ignorada se a variável acima estiver definida |
| `HYDRA_MQTT_TLS`, `HYDRA_MQTT_TLS_CA` | sem TLS | `HYDRA_MQTT_TLS=1` verifica o broker com as CA do sistema; `HYDRA_MQTT_TLS_CA` indica o ficheiro da CA que assinou o seu certificado |
| `HYDRA_MQTT_TLS_CERT`, `HYDRA_MQTT_TLS_KEY` | - | o certificado de cliente e a chave para um broker que exige TLS mútuo; são precisos os dois e ativam o TLS |
| `--host`, `--port` | `127.0.0.1`, `8790` | onde escuta o servidor simulado |
| `HYDRA_UMC_SDK_ROOT` | a pasta ao lado | onde os testes dos outros repositórios encontram este |

## 🚀 Início rápido

Requer Python 3.11 ou superior. Os clientes Go, TypeScript e Rust também são compilados e testados se a sua cadeia de ferramentas estiver instalada.

```bash
PYTHONPATH=clients/python/src python -m unittest discover -s clients/python/tests  # the Python client tests
python tools/verify_contract_matrix.py                                             # every schema against the validator and every fixture
PYTHONPATH=clients/python/src python -m hydra_umc_sdk.validation --help            # the contract validator on the command line
./build-test.sh                                                                    # the non-mutating build check (build-test.bat on Windows)
```

## 🧪 Testes

492 testes automáticos correm com `python -m unittest discover -s clients/python/tests`. Os outros clientes têm as suas próprias suites: 28 testes em Go (`go test ./...`), 105 em TypeScript (`npm test`) e 31 em Rust (`cargo test`), executados por `tools/extra_build_steps.py` se a cadeia de ferramentas estiver instalada. Nenhum precisa de hardware.

A CI executa `HYDRA_UMC_CI=1 python tools/ci_validate.py`, que verifica o manifesto, os documentos, os oito README e as imagens.

## 🏗️ Compilação e publicação

Use a verificação de compilação que não altera versões antes de uma compilação de lançamento:

| Ação | Windows | Linux / macOS |
|---|---|---|
| Verificação de compilação (sem alterar versão nem CHANGELOG) | `build-test.bat` | `./build-test.sh` |
| Executar / desenvolvimento (quando existir) | `run*.bat` ou `dev*.bat` | `./run*.sh` ou `./dev*.sh` |

`build-test.bat` e `build-test.sh` compilam ou validam a pilha do projeto sem incrementar `hydra-umc.project.json` nem modificar `CHANGELOG.md`. Podem criar a saída normal do compilador. Os scripts `build*.bat`, `build*.sh`, `run*` e `dev*` existentes mantêm o seu comportamento próprio do projeto, versionado ou de execução; use-os quando esse comportamento for necessário.

## 🩺 Resolução de problemas

| Vê | Porque | Faça |
|---|---|---|
| `hydra-umc-contract-validate: missing required field: ...` | A carga viola o contrato; o comando termina com código de saída 2 | Compare o ficheiro com o exemplo que o servidor simulado serve para esse contrato |
| `verify_contract_matrix.py` falha | Um esquema foi adicionado ou alterado e a lista de contratos do validador ou uma fixture não foi atualizada | Adicione a entrada do validador e uma fixture válida e outra inválida |
| `go test ./...` é ignorado | A verificação de compilação só corre os clientes Go, TypeScript e Rust se `go`, `npm` e `cargo` estiverem no PATH | Instale a cadeia de ferramentas; a verificação imprime que cliente foi ignorado |

## 📂 Estrutura do repositório

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of HYDRA-UMC-SDK" width="100%">
</p>

<details>
<summary>Versão em texto da árvore</summary>

```text
HYDRA-UMC-SDK/
├── contracts/                 fontes JSON Schema v1, a fatia OpenAPI e o registo de portas
├── clients/                   os clientes de referência em Python, Go, TypeScript e Rust
├── conformance/               fixtures válidas e inválidas de cada contrato
├── docs/                      guias de contratos, API e desenvolvimento
├── examples/                  exemplos Python executáveis
├── tools/                     matriz de contratos, porta OpenAPI, sincronização de ferramentas, verificação de compilação
├── .github/                   fluxo de CI e modelos de problemas
├── images/                    faixa e imagens do README
├── CHANGELOG.md               o que mudou em cada versão
├── build-test.sh              verificação de compilação sem alterações
├── build.sh                   compila e verifica; nunca muda a versão
├── bump_manifest_version.py   sincroniza a versão do manifesto
├── bump_version.py            subida de versão explícita
├── hydra-umc.project.json     manifesto: versão, maturidade, família
├── run.sh                     arranca o programa
└── test.sh                    executa os testes
```

</details>

`tools/`: `verify_contract_matrix.py` (matriz de compatibilidade esquema/validador), `verify_openapi.py` (porta estrutural de OpenAPI sem dependências) e o motor `build-test` que não altera nada. `sync_repo_tools.py` mantém idênticas as ferramentas partilhadas de todos os repositórios, `pin_sdk.py` fixa os consumidores do SDK a uma etiqueta de versão e `canonical/` guarda as cópias únicas que são replicadas (entre elas o comando `hydra_project_tool.py`, que valida, testa e só sobe a versão quando lhe é pedido). `sync_ports.py` gera e verifica `contracts/ports.yaml`, o registo da porta, do caminho de saúde e da unidade systemd de cada serviço; a redação partilhada de segredos (`canonical/redaction.py`, com os casos em `contracts/redaction/vectors.json`) é copiada para os projetos que enviam texto para fora.

## 🗺️ Roteiro e limites conhecidos

**Limites conhecidos hoje**

* O Protobuf ainda não está publicado, e a fatia OpenAPI cobre só descoberta, início de sessão, definições e comandos.
* As rotas do servidor não estão versionadas hoje; `/api/v1` é o objetivo de desenho descrito em `docs/API_DESIGN.md`.
* Nada disto correu em hardware real, e a porta de trabalhos é uma função de software, não uma função de segurança certificada.

**A seguir:** publicar o Protobuf onde uma integração precisar e alargar a fatia OpenAPI ao resto das rotas do servidor.

## 🌍 Idiomas

Este README e os documentos do repositório existem em oito idiomas: inglês, espanhol, alemão, francês, italiano, japonês, chinês e português (Portugal). São escritos em conjunto e a CI verifica que os oito ficheiros têm as mesmas secções e as mesmas ligações. Este repositório não tem ecrã nem catálogo de mensagens próprios, por isso não há textos de interface para traduzir.

## 🔗 Projetos relacionados

Este projeto faz parte do ecossistema de robótica HYDRA-UMC do mesmo autor (JuanenRac / Electro Hobby 3D). Vale a pena conhecê-los, porque um pedido pode ser, na verdade, sobre um destes e não sobre este repositório.

**Projeto-mãe**
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — camada de produto reproduzível do Raspberry Pi OS para o CM5: agente só de leitura, configuração/perfis validados, aprovisionamento Wi-Fi de primeiro contacto; um agente de dispositivo que consome os contratos de dispositivo, saúde, segurança e atualização deste SDK.
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — registo declarativo de manifestos de adaptador e validador para conectores de máquinas externas; estende a ideia de contrato do SDK a máquinas externas sem substituir os projetos de gateway industrial.

**Diretamente relacionados**
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — o verdadeiro backend sem interface (REST/WebSocket) com que falam todos os clientes de controlo — um produtor e consumidor de API autenticada governado pelos contratos deste SDK.
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — ferramenta administrativa de desktop que descobre, clona e atualiza todos os repositórios deste ecossistema — publica metadados de versão e compatibilidade que os clientes deste SDK, cientes dos contratos, consomem.
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — ferramenta de desktop para Windows/Linux que constrói uma imagem do CM5 pronta a gravar com as versões mais recentes do ecossistema, com configuração de primeiro arranque de Wi-Fi/utilizador/SSH ao estilo do Raspberry Pi Imager.
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — coordenador de incidentes de manutenção: um papel de borda de poucos privilégios recolhe um inventário/estado higienizado, um papel de plano de controlo mostra-o só de leitura e pede a um fornecedor de IA que sugira um diagnóstico; nunca aplica um patch nem implanta nada.
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — anfitrião de desenvolvimento reproduzível (Raspberry Pi 5 / CM5) que guarda o código-fonte do ecossistema e executa tarefas limitadas de compilação/teste numa fila durável; um papel de desenvolvimento dedicado, explicitamente não um CM5 operacional.
- **[HYDRA-UMC-DOCS](https://github.com/JuanenRac/HYDRA-UMC-DOCS)** — o centro de documentação e ferramentas do ecossistema: arquitetura, interfaces, base de segurança, matriz de capacidades e um catálogo de projetos gerado a partir de cada manifesto.
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — o desenho da placa-mãe do braço robótico: anfitrião CM5 + STM32H745 de dois núcleos, pensado para orquestrar até 8 braços de ferramenta por CAN-OTA/SPI-OTA (firmware numa fase inicial; ainda sem placa montada).
- **[URTC](https://github.com/JuanenRac/URTC)** — firmware da placa física Universal Robot Tool Controller, mais de 25 perfis de ferramenta por barramento CAN — uma plataforma independente de controlador de ferramenta ligada através dos adaptadores de integração versionados deste SDK.
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — coordenador com um transporte ROS 2 baseado em rclpy importado sob demanda (ainda não executado contra uma instalação ROS 2) — usa a porta comum BridgeJob deste SDK para a observação, a inspeção e o trabalho de célula cancelável em ROS 2.
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — coordenador seguro de fluxo de placa de alto nível para pick-and-place com OpenPnP — usa os trabalhos correlacionados e idempotentes deste SDK para entregas de PCB rastreáveis.
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — fronteira de coordenação segura para impressoras 3D Moonraker/Klipper, com comandos de trabalho reais protegidos por portas — usa a porta deste SDK em torno da prontidão nativa da impressora; não expõe o controlo do aquecedor nem do movimento.
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — coordenador de células CNC de alto nível com acesso ao estado GRBL e aos bytes de controlo (testado apenas contra um emulador) — usa a porta deste SDK para coordenar apenas junto de uma CNC inativa e protegida.
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — coordenador de células laser que lê 3 sinais GPIO (chave, caixa e interlock) (testado apenas contra um chip simulado; não pode armar nem disparar um laser) — usa a porta deste SDK para os auxiliares, preservando a autoridade de segurança do laser.
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — fronteira de coordenação para frotas AGV/AMR através de um publicador MQTT VDA 5050 (testado apenas contra uma frota emulada) — também valida os seus comandos contra esta mesma porta partilhada de trabalho e segurança.
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — fronteira de coordenação para droides com patas/humanoides, com um emissor de comandos para o Boston Dynamics Spot (testado apenas contra um emulador) — também valida os seus comandos contra esta mesma porta partilhada de trabalho e segurança.
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — fronteira de coordenação para UAV com câmara, com um emissor de comandos MAVLink (testado apenas contra um emulador) — também valida os seus comandos contra esta mesma porta partilhada de trabalho e segurança.

**Também fazem parte do ecossistema**

*Backend central e clientes*
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — painel web de controlo com visualização 3D em tempo real de vários robôs.
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — centro de comando de enxame para desktop (PySide6) para vários servidores ao mesmo tempo, empacotado como executável independente.
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — aplicação Android nativa de controlo, com início de sessão biométrico e um companheiro Wear OS emparelhado.
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — aplicação de controlo para iOS/iPadOS (Flutter) com sincronização WebSocket em tempo real.
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — interface tátil nativa para o ecrã tátil DSI de 7" integrado, executada no próprio CM5.
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — criador/editor gráfico de URDF para desktop que envia os modelos concluídos para o catálogo do STUDIO.
- **[HYDRA-UMC-EDITOR-STL](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-STL)** — editor de modelos STL para desktop que transforma/substitui/remove/adiciona peças reais no mesmo catálogo de modelos que o HYDRA-UMC-EDITOR-URDF também edita.

*Plataforma de ferramentas URTC*
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — ferramenta gráfica de gravação para desktop das placas URTC, por CAN-OTA e também SWD/JTAG de chip completo.
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — ferramenta de diagnóstico CAN em tempo real para desktop das placas URTC, com um painel por perfil de ferramenta.
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — alternativa no navegador ao URTC-TESTER através da Web Serial API, sem instalação local.
- **[URTC-GATEWAY](https://github.com/JuanenRac/URTC-GATEWAY)** — gateway à frente do barramento CAN do URTC: lista de identificadores permitidos, limite de taxa e chave de sessão; software testado num computador, ainda não num barramento real.

*Nó de IA de visão (Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — centro de integração do pipeline de visão Hailo-8, com uma verificação real de prontidão de hardware por fase.
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — registo real de modelos compilados com verificação segura de carga por arquitetura Hailo e soma de verificação.
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — pipeline GStreamer real e gerador de configuração MediaMTX com uma fronteira de integração HailoRT real.
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — lei de correção de servovisão baseada em posição com autorização condicionada ao estado da zona; ainda sem estimativa de pose por câmara.
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — lógica v0 de violação de zonas, atualidade da calibração e pedido de E-STOP que lê as posições dos objetos de um ficheiro; nenhum detetor a alimenta e ainda não há E-STOP físico ligado.

*Nó de IA cognitiva (Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — centro de integração do pipeline cognitivo do Hailo-10 (orquestração de LLM/VLA/voz).
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — codificação/descodificação real de tokens de ação e geração de trajetórias para um modelo Visão-Linguagem-Ação.
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — front-end de voz real (VAD + analisador de intenções) com um relé para o relógio limitado e protegido por confirmação.
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — decomposição real de tarefas baseada em regras e recuperação semântica de erros sobre os códigos de erro do MCU.
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — pesquisa real de documentos TF-IDF só com a biblioteca padrão sobre a documentação Markdown deste ecossistema.
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — técnico de manutenção de IA local, protegido por políticas, para o próprio ecossistema: observa, diagnostica e propõe correções; os dois níveis de maior risco não estão implementados de propósito.

*Orquestração e enxame*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — centro de integração com um contrato real de relatório de saúde gRPC/Protobuf e uma máquina de estados de missões.
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — fila real de trabalhos por prioridade com deduplicação, sobre uma API HTTP real.
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — vigilante real de saúde da frota por gRPC com repetição/recuo e deteção de identidade incoerente.
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — planeador real de trajetórias 3D baseado em RRT com validação real de colisões com obstáculos e espaço de trabalho.
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — sincronização real de estado CRDT LWW-Element-Map, testada por propriedades para a convergência de várias células.

*Gémeo digital e simulação*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — centro de integração do motor de gémeo digital, com um contrato real de sincronização de compatibilidade de versões.
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — encaminhador hardware-in-the-loop com um interlock de software de colisão entre a simulação e o hardware real (testado sem hardware real).
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — cinemática direta real e validação de limites de juntas sobre um subconjunto real de URDF.
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — gerador procedural real de cenas 2D com exportação de anotações YOLO/COCO.

*Dados e análise*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — armazém real de séries temporais sobre sqlite3 com uma API HTTP real de ingestão/consulta.
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — detetor real de anomalias por FFT e linha de base estatística, com monitorização de deriva.
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — cálculo real de OEE/disponibilidade sobre o histórico do DATALAKE, com exportação CSV reprodutível.
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — pipeline real de ingestão CAN/WebSocket para o DATALAKE, com deduplicação por sequência.

*Gateway industrial*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — centro de integração que retransmite para protocolos industriais, com uma camada real de lista de comandos permitidos e contrapressão.
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — espaço de endereços OPC-UA real, verificado com uma sessão de cliente real do protocolo binário.
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — broker MQTT real com autenticação opcional por cliente e ACL de tópicos.
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — endpoints XML MTConnect `/probe` e `/current` reais com saída em modo degradado.

*Ferramentas complementares e operações do ecossistema*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — painéis de Resumos Inteligentes e Realce de Anomalias sobre o DATALAKE/ANOMALY-DETECTOR, com um recurso estatístico honesto.
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — CLI da frota com um contrato de códigos de saída real e estável, um cliente vivo genuíno da API do HYDRA-UMC-SERVER.
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — aplicação companheira WearOS com padrões de alerta tátil e um relé de voz para o telemóvel emparelhado (ainda não executada num relógio físico).
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — firmware de um rack de montagem de placas com descodificação real do ID da ferramenta e lógica de pré-aquecimento Smart Idle.
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — firmware mais um companheiro de visão em Python real para uma cabeça de ferramenta de inspeção térmica/RGB.

## 📚 Documentação

Onde ler mais:

* [Base de segurança do ecossistema](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)
* [Modelo de ameaças do ecossistema](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)
* [Registo de alterações deste repositório](CHANGELOG.md)
* [Licença deste repositório](LICENSE.md)

## 🤝 Contribuir e comunidade

* Antes de um pull request execute `HYDRA_UMC_CI=1 py -3 tools/ci_validate.py` (ou `HYDRA_UMC_CI=1 python3 tools/ci_validate.py`): tem de imprimir `CI_VALIDATION=PASS`. Não execute `build.sh` nem `build.bat` para esta verificação; compilar não é verificar.
* Os oito README são escritos a partir de uma única fonte em HYDRA-UMC-DOCS; não os edite à mão. Altere a fonte e escreva-os de novo com `tools/make_readmes.py`.
* Não afirme num README o que não foi executado: diga «simulado» ou «não testado em hardware» quando for a verdade.
* Consulte [CONTRIBUTING.md](CONTRIBUTING.md), o [código de conduta](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md) e [SUPPORT.md](SUPPORT.md).

## 👤 AUTOR

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 LICENÇA

GPL-3.0-or-later - [LICENSE](LICENSE).

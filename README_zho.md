<!-- =============================================================================
HYDRA-UMC-SDK - Shared contracts and integration toolkit
Copyright (C) JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-SDK banner" width="100%">
</p>

# 🧰 HYDRA-UMC-SDK

<p align="center"><a href="README.md">🇺🇸 English</a> | <a href="README_spa.md">🇪🇸 Español</a> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | 🇨🇳 <b>简体中文</b> | <a href="README_jpn.md">🇯🇵 日本語</a> | <a href="README_por.md">🇵🇹 Português</a></p>

### 🧰 HYDRA-UMC 的共享契约、参考客户端和集成工具

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Contracts-JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="Contracts">
  <img src="https://img.shields.io/badge/Reference%20clients-Python%20%7C%20Go%20%7C%20TypeScript%20%7C%20Rust-blueviolet.svg" alt="Reference%20clients">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="Integration">
  <img src="https://img.shields.io/badge/Tests-617%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.4.1-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-established-2EA44F.svg" alt="Maturity">
</p>

---

> **诚实检查——今天真正可运行的部分：** 十个 JSON Schema v1 契约（各带一个有效和一个无效夹具）、Python 验证器、HYDRA-UMC-SERVER 的第一部分 OpenAPI v1、执行相同架构的 Go、TypeScript 和 Rust 客户端、桥接辅助代码和兼容性矩阵都是真实的，并已在计算机上测试（617 个 Python 测试，外加其他三个客户端的测试集）。Protobuf 尚未发布，作业门是共用的软件功能而不是经过认证的安全功能，这里的内容从未在真实硬件上运行。

---

> **安全与安防现状:**本生态系统不是经认证的安全系统。目前尚无硬件 E-STOP 通路,没有由固件强制执行的限位或联锁,也没有经过验证的运动指令;固件映像使用 CRC-32 和 Ed25519 签名校验,发布构建会拒绝已公开的开发密钥(中继之后的工具头和扩展板仍运行 URTC 的引导程序,它们使用共享密钥的 HMAC-SHA256 而不是签名);TLS 与双向 TLS 均为可选项,默认关闭;自制电路板尚未组装或测试。在依赖此处任何说法来保障人身安全之前,请先阅读[安全基线](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)和[威胁模型](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)。

---

## 📋 速览

| | |
|---|---|
| 版本 | `0.4.1` |
| 成熟度 | 成熟 |
| 测试 | 617 (`python -m unittest discover -s clients/python/tests`) |
| 技术栈 | Python / TypeScript / Go / Rust / JSON Schema |
| 真实硬件 | 尚未：此版本没有在真实硬件上运行的记录 |

**跳转：** [概述](#-概述) · [架构](#-架构) · [功能](#-功能) · [安全与防护](#-安全与防护) · [接口](#-接口) · [配置](#-配置) · [快速开始](#-快速开始) · [测试](#-测试) · [故障排除](#-故障排除) · [仓库结构](#-仓库结构) · [相关项目](#-相关项目)

## 🚦 项目状态

每一行是本仓库的一个部分，灯号表示它今天做到了哪一步。内容依据仓库能够展示的证据（测试、构建、运行），而不是计划。

🟢 已完成并验证 · 🟡 可用，有已知限制 · 🟠 部分完成或尚未验证 · 🔴 未完成或不可用

| 领域 | 状态 | 在这里的含义 |
|---|---|---|
| 软件 | 🟢 | 就其用途而言已完整且稳定；上面的诚实性检查列出了已知限制 |
| 测试 | 🟢 | 617 项自动测试，每次变更都会运行 |
| 真实硬件 | 🔴 | 尚未：此版本没有在真实硬件上运行的记录 |
| 文档 | 🟢 | 八种语言的 README，每次变更都会与清单核对 |

## 🎯 概述

HYDRA-UMC-SDK 定义了 HYDRA-UMC 服务、客户端、CM5 适配器和 URTC
集成共享的稳定语言。它拥有规范性合约、无依赖的 Python 参考验证器、
一致性 fixture 和集成指南。它不会取代 Raspberry Pi OS、Hailo、ROS 2、
MQTT、OPC-UA 或 MTConnect 各自的官方 API。

## 🧩 在 HYDRA-UMC 中的角色

**HYDRA-UMC-SDK** 是生态系统的共同语言：JSON Schema v1 契约、服务器的第一部分 OpenAPI、Python、Go、TypeScript 和 Rust 参考客户端、所有桥接和连接器中枢都用的桥接辅助代码，以及让每个仓库的工具保持一致的工具。它不运行自己的服务，也不替代任何官方 API。

## 🏛️ 架构

<p align="center">
  <img src="images/architecture.svg" alt="HYDRA-UMC-SDK architecture" width="100%">
</p>

## ✨ 功能

### 状态

JSON Schema v1 合约、有效/无效 fixture、Python 验证客户端、
并实施主机端测试,以及针对 HYDRA-UMC-SERVER 自身 HTTP 接口的真实首个
OpenAPI v1 切片(`contracts/openapi/v1/server.openapi.json` - 参见
[docs/CONTRACTS.md](docs/CONTRACTS.md#openapi-v1))。Protobuf 的发布是后续的兼容性里程碑;Go、TypeScript 和 Rust 客户端已经存在。

一个真实、自动化的兼容性矩阵（`tools/verify_contract_matrix.py`）会将每个已发布的架构与 Python 验证器自身的合约列表进行交叉核对，并发现并修复了一个真实的缺口：`project-manifest.schema.json`（本生态系统中每个仓库都会发布的 `hydra-umc.project.json` 合约）此前完全没有验证器条目。现在它证明，每个一致性 fixture 都会按照其自身文件名所声明的方式被判定，此外还涵盖了未知合约和不兼容架构版本这两种情况。

自下方"第一个里程碑"之后又新增了若干合约(现共 15 个):面向外部机器的公开桥接合约 `BridgeJob`/`GateDecision`(见 [docs/BRIDGE_CONTRACT.md](docs/BRIDGE_CONTRACT.md)),由 `HYDRA-UMC-BRIDGE-ROS2`/`-OPENPNP`/`-PRINTER3D`/`-CNC`/`-LASER`/`-AMR`/`-DROIDS`/`-UAV` 共享,并拥有自己真实的 JSON 线上格式(`job_to_dict()`/`job_from_dict()`/`decision_to_dict()`)，以及由桥接器自己观测到的机器状态（闸门使用它而不是请求方声称的状态），还有一个作业接收器（`JobIntake`/`IdempotencyStore`），它忽略保留消息，并且绝不会执行同一幂等键两次;一个 `ScenarioOutcome` 合约加上 `compare_runs()`,即共享的"是否真的修复了"检查——当某个失败不再复现、但基线指纹从未改变时,返回 `apparent-success` 而非 `regression-fixed`;一个 `Operation` 合约加上 `validate_status_transition()`,即共享的目标/任务/操作生命周期——`received`/`authorized`/`queued`/`sent`/`confirmed`/`terminated`/`rejected`,绝不归入单一的"已执行"筐里;`Operation` 上新增可选的 `result` 字段加上 `concludes_success()`——真实证据(`run_id`/`origin`/`observers_enabled`/`outcome`)拒绝从过期/重放的结果或观测被禁用的运行中得出成功结论;一个独立的 `Capability` 合约加上 `is_capability_usable()`——某个目标是否*声明*支持某个操作 `kind`,被建模为与该支持是否*最近被真实验证过*(`last_checked_at_utc`/`checked_configuration`/`max_age_seconds`)不同的数据,从而已声明但从未验证或已过期的能力绝不会被默默当作可用;以及一个 `hydra-umc-sdk-mock-server`(`mock_server.py`),通过普通 HTTP 为每个已知合约提供一份有效的示例负载,便于在真实的 CM5/机器人/MCU 硬件就绪之前开发 UI 或适配器。全部 10 个合约都至少各有一个有效和一个无效的一致性 fixture,已通过上述兼容性矩阵验证。

## 🔒 安全与防护

| 威胁 | 防御 | 位置 |
|---|---|---|
| 超出契约的桥接命令 | 一个作业最多 32 个参数，名称 64 个字符，值 1024 个字符，标识符 128 个字符；使用桥接自己观察到的机器状态，而不是请求方声称的状态 | `bridge_contract.py` |
| 同一命令执行两次，或重放保留消息 | 作业接收会忽略保留消息，同一幂等键绝不执行两次 | `job_intake.py` |
| 停止命令排在长命令之后等待 | 普通命令在一条通道上逐个执行，停止动词在第二条通道上执行 | `bridge_transport.py` |
| 配置文件中保存代理凭据，或未验证的代理 | 用户名和密码来自环境变量或文件，TLS 可用 CA 验证代理，客户端证书和密钥会启用双向 TLS | `mqtt_connection.py` |
| 架构变了而验证器没有跟上 | 兼容性矩阵把每个已发布架构与验证器的契约列表比对，并按文件名所声明的结果判定每个夹具 | `tools/verify_contract_matrix.py` |

**它绝不做的事：** 充当经过认证的安全功能。作业门是各桥接共用的软件实现，不是安全认证。

## 🔌 接口

| 主题或路由 | 内容 |
|---|---|
| `contracts/json-schema/v1/` | 十个 JSON Schema v1 契约：能力、设备描述符、事件信封、健康报告、操作、项目清单、安全状态、场景结果、服务器发现、更新清单 |
| `contracts/openapi/v1/server.openapi.json` | HYDRA-UMC-SERVER 的第一部分 OpenAPI v1：发现、登录、设置和命令（服务器自身 `docs/openapi.json` 的子集） |
| `contracts/ports.yaml` | 每个服务的端口、健康路径和 systemd 单元登记表，由 `tools/sync_ports.py` 生成 |
| `hydra/bridges/<name>/cmd/#` | 桥接监听的位置；应答发到 `.../<动词>/result` |
| `hydra-umc-contract-validate`, `hydra-umc-sdk-mock-server` | 命令行验证器（失败时退出码为 2）和在 `127.0.0.1:8790` 上为每个契约提供一个有效示例的模拟服务器 |

## ⚙️ 配置

| 变量 | 默认值 | 设置内容 |
|---|---|---|
| `HYDRA_MQTT_USERNAME`, `HYDRA_MQTT_PASSWORD` | 无凭据 | 代理凭据；密码只能与用户名一起使用 |
| `HYDRA_MQTT_PASSWORD_FILE` | - | 从文件读取的密码（Docker 或 systemd 机密）；如果设置了上一个变量则忽略 |
| `HYDRA_MQTT_TLS`, `HYDRA_MQTT_TLS_CA` | 无 TLS | `HYDRA_MQTT_TLS=1` 用系统 CA 验证代理；`HYDRA_MQTT_TLS_CA` 指定签发其证书的 CA 文件 |
| `HYDRA_MQTT_TLS_CERT`, `HYDRA_MQTT_TLS_KEY` | - | 用于要求双向 TLS 的代理的客户端证书和密钥；两者都需要，并会启用 TLS |
| `--host`, `--port` | `127.0.0.1`, `8790` | 模拟服务器的监听位置 |
| `HYDRA_UMC_SDK_ROOT` | 同级文件夹 | 其他仓库的测试在哪里找到本仓库 |

## 🚀 快速开始

需要 Python 3.11 或更高版本。如果安装了相应工具链，Go、TypeScript 和 Rust 客户端也会被构建和测试。

```bash
PYTHONPATH=clients/python/src python -m unittest discover -s clients/python/tests  # the Python client tests
python tools/verify_contract_matrix.py                                             # every schema against the validator and every fixture
PYTHONPATH=clients/python/src python -m hydra_umc_sdk.validation --help            # the contract validator on the command line
./build-test.sh                                                                    # the non-mutating build check (build-test.bat on Windows)
```

## 🧪 测试

运行 `python -m unittest discover -s clients/python/tests` 会执行 617 个自动测试。 其他客户端有各自的测试集：Go 28 个（`go test ./...`）、TypeScript 105 个（`npm test`）、Rust 31 个（`cargo test`），安装了工具链时由 `tools/extra_build_steps.py` 运行。都不需要硬件。

CI 运行 `HYDRA_UMC_CI=1 python tools/ci_validate.py`，检查清单、文档、八个 README 和图片。

## 🏗️ 构建与发布

请在发布构建前使用不改动版本的构建检查：

| 操作 | Windows | Linux / macOS |
|---|---|---|
| 构建检查（不修改版本或 CHANGELOG） | `build-test.bat` | `./build-test.sh` |
| 运行 / 开发（如提供） | `run*.bat` 或 `dev*.bat` | `./run*.sh` 或 `./dev*.sh` |

`build-test.bat` 和 `build-test.sh` 会编译或验证项目技术栈，但不会递增 `hydra-umc.project.json`，也不会修改 `CHANGELOG.md`。它们仅可能生成正常的编译器输出。现有的 `build*.bat`、`build*.sh`、`run*` 和 `dev*` 脚本保留各自的版本化或运行时行为；需要该行为时请使用它们。

## 🩺 故障排除

| 你看到 | 原因 | 处理 |
|---|---|---|
| `hydra-umc-contract-validate: missing required field: ...` | 载荷违反契约；命令以退出码 2 结束 | 把文件与模拟服务器为该契约提供的示例对比 |
| `verify_contract_matrix.py` 失败 | 新增或修改了架构，但验证器的契约列表或夹具没有更新 | 添加验证器条目以及一个有效和一个无效夹具 |
| `go test ./...` 被跳过 | 只有 `go`、`npm` 和 `cargo` 在 PATH 中时，构建检查才会运行 Go、TypeScript 和 Rust 客户端 | 安装工具链；检查会打印被跳过的客户端 |

## 📂 仓库结构

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of HYDRA-UMC-SDK" width="100%">
</p>

<details>
<summary>目录树的文本版本</summary>

```text
HYDRA-UMC-SDK/
├── contracts/                 JSON Schema v1 源文件、OpenAPI 部分和端口登记表
├── clients/                   Python、Go、TypeScript 和 Rust 参考客户端
├── conformance/               每个契约的有效和无效夹具
├── docs/                      契约、API 和开发指南
├── examples/                  可运行的 Python 示例
├── tools/                     契约矩阵、OpenAPI 闸门、工具同步、构建检查
├── .github/                   CI 工作流和 Issue 模板
├── images/                    横幅和 README 的图片
├── CHANGELOG.md               每个版本的变更
├── build-test.sh              不修改内容的构建检查
├── build.sh                   构建并检查；从不改变版本
├── bump_manifest_version.py   同步清单版本
├── bump_version.py            显式提升版本
├── hydra-umc.project.json     清单：版本、成熟度、系列
├── run.sh                     启动程序
└── test.sh                    运行测试
```

</details>

`tools/`: `verify_contract_matrix.py`(架构/验证器兼容性矩阵)、`verify_openapi.py`(无依赖的 OpenAPI 结构校验)以及不做修改的 `build-test` 引擎。`sync_repo_tools.py` 使所有仓库的共享工具保持一致，`pin_sdk.py` 将 SDK 的使用方固定到某个发布标签，`canonical/` 保存被分发的唯一副本（包括 `hydra_project_tool.py` 命令：它负责校验、测试，只有在明确要求时才提升版本号）。 `sync_ports.py` 生成并检查 `contracts/ports.yaml`,即每个服务的端口、健康路径和 systemd 单元的登记表;共享的机密信息脱敏(`canonical/redaction.py`,用例在 `contracts/redaction/vectors.json`)会复制到向外发送文本的项目中。

## 🗺️ 路线图与已知限制

**目前已知的限制**

* Protobuf 尚未发布，OpenAPI 部分只覆盖发现、登录、设置和命令。
* 服务器的路由目前没有版本化；`/api/v1` 是 `docs/API_DESIGN.md` 中描述的设计目标。
* 这里的内容从未在真实硬件上运行，作业门是软件功能而不是经过认证的安全功能。

**下一步：** 在集成需要的地方发布 Protobuf，并把 OpenAPI 部分扩展到服务器的其余路由。

## 🌍 语言

本 README 和仓库文档提供八种语言：英语、西班牙语、德语、法语、意大利语、日语、中文和葡萄牙语（葡萄牙）。它们同时编写，并由 CI 检查八个文件拥有相同的章节和相同的链接。 本仓库没有自己的界面或消息目录，因此没有需要翻译的界面文字。

## 🔗 相关项目

本项目是同一作者(JuanenRac / Electro Hobby 3D)打造的 HYDRA-UMC 机器人生态系统的一部分。值得了解,因为某个请求实际上可能是关于这些项目之一,而非本仓库本身。

**父项目**
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — 面向 CM5 的可复现 Raspberry Pi OS 产品层——只读代理、经过验证的配置/配置文件、WiFi 首次配网;消费本 SDK 自身设备、健康、安全与更新契约的设备代理。
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — 面向外部机器连接器的声明式适配器清单注册与校验工具；把 SDK 自身的契约理念扩展到外部机器，而不取代工业网关类项目。

**直接相关**
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — 每个控制客户端真正通信的真实无头后端(REST/WebSocket) —— 受本 SDK 自身契约约束的经认证 API 生产者与消费者。
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — 发现、克隆并更新本生态系统中每个仓库的管理类桌面工具 —— 发布由本 SDK 自身理解契约的客户端所消费的版本与兼容性元数据。
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** —— 构建即刻可烧录、预装生态系统最新版本的 CM5 镜像的 Windows/Linux 桌面工具,具备类似 Raspberry Pi Imager 风格的首次启动 Wi-Fi/用户/SSH 配置。
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — 维护事件协调器：一个低权限的边缘角色采集经过脱敏的库存/健康快照，一个控制面角色以只读方式渲染它，并请求某个 AI 提供方给出诊断建议——从不应用补丁，也从不部署任何内容。
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — 可复现的开发主机（Raspberry Pi 5 / CM5），保存整个生态系统的源代码，并在持久队列下运行有界的构建/测试任务；这是专用的开发角色，明确区别于运行中的 CM5。
- **[HYDRA-UMC-DOCS](https://github.com/JuanenRac/HYDRA-UMC-DOCS)** — 生态的文档与工具中心：架构、接口、安全基线、能力矩阵，以及由每个清单生成的项目目录。
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — 机器人手臂主板设计——CM5 主机 + 双核 STM32H745,目标是通过 CAN-OTA/SPI-OTA 协调最多 8 条工具臂(固件处于早期阶段,尚无已组装的电路板)。
- **[URTC](https://github.com/JuanenRac/URTC)** — 面向实体 Universal Robot Tool Controller 板卡的固件，通过 CAN 总线支持 25 种以上工具配置 —— 通过本 SDK 自身版本化的集成适配器连接的独立工具控制器平台。
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — 带有惰性导入 rclpy ROS 2 传输层的协调器(尚未在 ROS 2 环境中运行) —— 使用本 SDK 自身通用的 BridgeJob 门限进行 ROS 2 观测、检查与可取消的单元作业。
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — 面向 OpenPnP 贴片机板级流程的安全高层协调器 —— 使用本 SDK 自身具备关联性与幂等性的作业实现可追溯的 PCB 交接。
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — 面向 Moonraker/Klipper 3D 打印机的安全协调边界，具备真实的受控作业指令 —— 围绕原生打印机就绪状态使用本 SDK 自身的门限;不暴露加热器或运动控制。
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — 具备 GRBL 状态/控制字节访问能力的高层 CNC 单元协调器(仅针对模拟器测试) —— 仅在配合处于空闲且受保护状态的 CNC 时,使用本 SDK 自身的门限进行协调。
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — 读取 3 路钥匙/外壳/联锁 GPIO 信号的激光单元协调器(仅针对模拟芯片测试;无法使激光器上膛或发射) —— 在保留激光安全权限的同时,针对辅助功能使用本 SDK 自身的门限。
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — 通过 VDA 5050 MQTT 发布者为 AGV/AMR 车队提供的协调边界(仅针对仿真车队测试) —— 同样针对这一共享的作业与安全门限校验自身指令。
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — 面向足式/人形机器人的协调边界,带有 Boston Dynamics Spot 指令发送器(仅针对模拟器测试) —— 同样针对这一共享的作业与安全门限校验自身指令。
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — 面向搭载摄像头的无人机的协调边界,带有 MAVLink 指令发送器(仅针对模拟器测试) —— 同样针对这一共享的作业与安全门限校验自身指令。

**生态系统中的其他项目**

*核心后端与客户端*
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — 具有实时多机器人 3D 可视化的网页控制面板。
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — 面向多台服务器的桌面(PySide6)集群指挥中心，打包为独立可执行文件。
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — 具有生物识别登录和配对 Wear OS 伴侣应用的原生 Android 控制应用。
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — 具有实时 WebSocket 同步的 iOS/iPadOS 控制应用(Flutter)。
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — 面向机载 7 英寸 DSI 触摸屏的原生触控界面，直接嵌入 CM5 本体。
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — 将完成的模型推送到 STUDIO 自身目录的桌面版图形化 URDF 创建/编辑工具。
- **[HYDRA-UMC-EDITOR-STL](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-STL)** — 桌面 STL 模型编辑器，在 HYDRA-UMC-EDITOR-URDF 编辑的同一模型目录中变换/替换/移除/添加真实部件。

*URTC 工具平台*
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — 面向 URTC 板卡的桌面图形烧录工具，支持 CAN-OTA 以及全芯片 SWD/JTAG。
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — 面向 URTC 板卡的桌面实时 CAN 总线诊断工具，每种工具配置对应一个面板。
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — 通过 Web Serial API 实现的浏览器版 URTC-TESTER 替代方案，无需本地安装。
- **[URTC-GATEWAY](https://github.com/JuanenRac/URTC-GATEWAY)** — URTC CAN 总线前的网关：允许的标识符列表、速率限制和会话密钥；软件已在计算机上测试，尚未在真实总线上测试。

*视觉 AI 节点(Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — 面向 Hailo-8 视觉流水线的集成中枢，具备逐阶段的真实硬件就绪检测。
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — 具备 Hailo 架构/校验和安全加载验证的真实编译模型注册表。
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — 具备真实 HailoRT 集成边界的真实 GStreamer 流水线 + MediaMTX 配置生成器。
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — 以区域状态为授权条件的 Position-Based Visual Servoing 修正律;尚无摄像头位姿估计。
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — 从文件读取物体位置的 v0 区域入侵、校准新鲜度与 E-STOP 请求逻辑;没有检测器为其供数,也尚未连接任何物理 E-STOP。

*认知 AI 节点(Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — 面向 Hailo-10 认知流水线(LLM/VLA/语音编排)的集成中枢。
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — 面向 Vision-Language-Action 模型的真实动作 token 编解码与轨迹生成。
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — 具备受限、需确认的 Watch 中继的真实语音前端(VAD + 意图解析)。
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — 基于真实规则的任务分解，以及针对 MCU 错误码的语义化错误恢复。
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — 面向本生态系统自身 Markdown 文档的真实纯标准库 TF-IDF 文档检索。
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — 面向生态系统自身的本地、按策略门控的 AI 维护技师——观察、诊断并提出修复建议;两个最高风险等级目前特意尚未实现。

*编排与集群*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — 具备真实 gRPC/Protobuf 健康报告契约与任务状态机的集成中枢。
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — 基于真实 HTTP API 的真实优先级任务队列，支持去重。
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — 具备重试/退避与身份不匹配检测的真实基于 gRPC 的车队健康看门狗。
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — 具备真实障碍物/工作空间碰撞校验的真实基于 RRT 的三维路径规划器。
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — 经过多单元收敛属性测试的真实 CRDT LWW-Element-Map 状态同步。

*数字孪生与仿真*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — 面向数字孪生引擎的集成中枢，具备真实的版本兼容性同步契约。
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — 在仿真与真实硬件之间带有软件碰撞联锁的硬件在环路由器(未在真实硬件上测试)。
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — 面向真实 URDF 子集的真实正向运动学与关节限位校验。
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — 具备 YOLO/COCO 标注导出功能的真实程序化 2D 场景生成器。

*数据与分析*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — 具备真实数据摄入/查询 HTTP API 的真实 sqlite3 时序数据存储。
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — 具备漂移监测能力的真实 FFT + 统计基线异常检测器。
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — 基于 DATALAKE 历史数据的真实 OEE/可用率计算，支持可复现的 CSV 导出。
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — 面向 DATALAKE 的真实 CAN/WebSocket 数据摄入管道，支持序列去重。

*工业网关*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — 中继至工业协议的集成中枢，具备真实的指令白名单/背压控制层。
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — 经真实二进制协议客户端会话验证的真实 OPC-UA 地址空间。
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — 具备可选按客户端认证与主题 ACL 的真实 MQTT 代理。
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — 具备降级模式输出的真实 MTConnect `/probe` 与 `/current` XML 端点。

*辅助工具与生态系统运维*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — 基于 DATALAKE/ANOMALY-DETECTOR 的智能摘要与异常高亮面板，具备诚实的统计回退机制。
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — 具备真实、稳定退出码契约的车队 CLI，是 HYDRA-UMC-SERVER 自身 API 的真实在线客户端。
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — 带有触觉提醒模式与配对手机语音中继的 WearOS 伴侣应用(尚未在实体手表上运行)。
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — 面向板卡安装机架的固件，具备真实的工具 ID 解码与 Smart Idle 预热逻辑。
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — 面向热成像/RGB 检测工具头的固件及真实 Python 视觉伴侣程序。

## 📚 文档

更多阅读：

* [生态系统的安全基线](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)
* [生态系统的威胁模型](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)
* [本仓库的更新日志](CHANGELOG.md)
* [本仓库的许可证](LICENSE.md)

## 🤝 参与贡献与社区

* 提交 pull request 之前，请运行 `HYDRA_UMC_CI=1 py -3 tools/ci_validate.py`（或 `HYDRA_UMC_CI=1 python3 tools/ci_validate.py`）：它必须输出 `CI_VALIDATION=PASS`。此检查不要运行 `build.sh` 或 `build.bat`；构建不是检查。
* 八个 README 由 HYDRA-UMC-DOCS 中的同一个源生成；请勿手工编辑。修改源文件，再用 `tools/make_readmes.py` 重新生成。
* 不要在 README 中声称尚未运行过的内容：属实时请写“仅模拟”或“尚未在硬件上试过”。
* 请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)、[行为准则](CODE_OF_CONDUCT.md)、[SECURITY.md](SECURITY.md) 和 [SUPPORT.md](SUPPORT.md)。

## 👤 作者

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 许可证

GPL-3.0-or-later - [LICENSE](LICENSE).

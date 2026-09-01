<!--
=================================================================================
HYDRA-UMC-SDK - 公共合约和集成工具包概述
版权所有 (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
CC BY-SA 4.0 - 参见 LICENSE.md
=================================================================================
-->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-SDK 横幅" width="100%">
</p>

<p align="center">
  <a href="README.md">🇺🇸 English</a> |
  <a href="README_spa.md">🇪🇸 西班牙语</a> |
  <a href="README_fra.md">🇫🇷法语</a> |
  <a href="README_ita.md">🇮🇹意大利语</a> |
  <a href="README_deu.md">🇩🇪德语</a> |
  <a href="README_zho.md">🇨🇳简体中文</a> |
  <a href="README_jpn.md">🇯🇵日本语</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0-blue.svg" alt="许可证：GPL 3.0">
  <img src="https://img.shields.io/badge/Contracts-Protobuf%20%7C%20JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="合约：Protobuf | JSON 架构 | OpenAPI">
  <img src="https://img.shields.io/badge/Reference%20client-Python-blueviolet.svg" alt="参考客户端：Python">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="集成：CM5 | URTC">
</p>

# HYDRA-UMC-SDK

## 🧩 HYDRA-UMC 的共享合约和集成工具包

HYDRA-UMC-SDK 定义了 HYDRA-UMC 服务、客户端、CM5 适配器和 URTC
集成共享的稳定语言。它拥有规范性合约、无依赖的 Python 参考验证器、
一致性装置和集成指南。它不会取代 Raspberry Pi OS、Hailo、ROS 2、
MQTT、OPC-UA 或 MTConnect 各自的官方 API。

## 🚧 状态

JSON Schema v1 合约、有效/无效装置、Python 验证客户端、
并实施主机端测试。 Protobuf/OpenAPI 发布和客户端
对于更多语言是后续的兼容性里程碑。

一个真实、自动化的兼容性矩阵（`tools/verify_contract_matrix.py`）会将每个已发布的架构与 Python 验证器自身的合约列表进行交叉核对，并发现并修复了一个真实的缺口：`project-manifest.schema.json`（本生态系统中每个仓库都会发布的 `hydra-umc.project.json` 合约）此前完全没有验证器条目。现在它证明，每个一致性装置都会按照其自身文件名所声明的方式被判定，此外还涵盖了未知合约和不兼容架构版本这两种情况。

## 🎯 第一个里程碑

1. 发布 `DeviceDescriptor`、`HealthReport`、`SafetyState` 和
   `UpdateManifest` JSON 模式 v1。
2. 使用 Python 参考客户端验证有效和无效的装置。
3. 在 CI 中加入生产者/消费者兼容性矩阵。
4. 在集成需要时发布 Protobuf/OpenAPI 表示。
5. 从稳定合约中添加 TypeScript、Go 和 Rust 客户端。

## 📂 存储库布局

<p align="center">
  <img src="images/REPOSITORY_LAYOUT.svg" alt="HYDRA-UMC-SDK 存储库布局的可视化地图" width="100%">
</p>

|路径|目的|
| ---| ---|
| `contracts/` |规范性 JSON Schema v1 源文件；其余表示形式遵循稳定的合约。 |
| `clients/` |无依赖的 Python 参考验证器和未来的其他语言客户端。 |
| `conformance/` |兼容性测试使用的有效和无效 v1 装置。 |
| `docs/` |合约、API、安全和开发规范文档。 |
| `examples/` |可运行的 Python 验证示例。 |

在定义新消息之前，请阅读[合约指南](docs/CONTRACTS.md)。

## 🛠️ 构建与运行

请在发布构建前使用不改动版本的构建检查：

| 操作 | Windows | Linux / macOS |
|---|---|---|
| 构建检查（不修改版本或 CHANGELOG） | `build-test.bat` | `./build-test.sh` |
| 运行 / 开发（如提供） | `run*.bat` 或 `dev*.bat` | `./run*.sh` 或 `./dev*.sh` |

`build-test.bat` 和 `build-test.sh` 会编译或验证项目技术栈，但不会递增 `hydra-umc.project.json`，也不会修改 `CHANGELOG.md`。它们仅可能生成正常的编译器输出。现有的 `build*.bat`、`build*.sh`、`run*` 和 `dev*` 脚本保留各自的版本化或运行时行为；需要该行为时请使用它们。

## 🔗 相关项目

> 规范的公共生态系统关系图。

|项目|与 HYDRA-UMC-SDK 的关系 |
| ---| ---|
| [HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS) |设备代理消费者的设备、健康、安全和更新合同。 |
| [HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER) |经过身份验证的 API 生产者和消费者受 SDK 合约管理。 |
| [HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER) |发布合同感知客户端使用的版本和兼容性元数据。 |
| [HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC) |通过有界 CM5 和 MCU 适配器合约公开的硬件/固件平台。 |
| [URTC](https://github.com/JuanenRac/URTC) |通过版本化集成适配器连接的独立工具控制器平台。 |
| [HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2) | 使用通用 BridgeJob 门控处理 ROS 2 观测、检查和可取消单元任务。 |
| [HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP) | 使用关联且幂等的任务实现可追溯 PCB 交接。 |
| [HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D) | 使用围绕原生打印机就绪状态的门控，不开放加热或运动控制。 |
| [HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC) | 仅在 CNC 空闲且受到保护时使用门控进行协调。 |
| [HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER) | 使用门控协调辅助任务，同时保留激光安全权限。 |

**生态系统的其余部分：** 探索 [JuanenRac 生态系统仪表板](https://juanenrac.github.io/JuanenRac/) 中的七个公共层。

## 👤 作者
**JuanenRac** (Electro Hobby 3D)
📧 electrohobby3d@gmail.com
📺 [youtube.com/@electrohobby3d](https://youtube.com/@electrohobby3d)

## 📜 许可证

代码为 GPL-3.0 或更高版本；文档是 CC BY-SA 4.0。请参阅 [LICENSE](LICENSE)。

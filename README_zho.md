<!--
=================================================================================
HYDRA-UMC-SDK - 公共合约和集成工具包概述
版权所有 (C) 2026 JuanenRac (Electro Hobby 3D) < electrohobby3d@gmail.com>
CC BY-SA 4.0 - 参见 LICENSE.md
=================================================================================
-->

<p对齐=“中心”>
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-SDK 横幅" width="100%">
</p>

<p对齐=“中心”>
  <a href="README.md">???? English</a> |
  <a href="README_spa.md">🇪🇸 西班牙语</a> |
  <a href="README_fra.md">🇫🇷法语</a> |
  <a href="README_ita.md">🇮🇹意大利语</a> |
  <a href="README_deu.md">🇩🇪德语</a> |
  <a href="README_zho.md">🇨🇳简体中文</a> |
  <a href="README_jpn.md">🇯🇵日本语</a>
</p>

<p对齐=“中心”>
  <img src="https://img.shields.io/badge/License-GPL%203.0-blue.svg" alt="许可证：GPL 3.0">
  <img src="https://img.shields.io/badge/Contracts-Protobuf%20%7C%20JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="合约：Protobuf | JSON 架构 | OpenAPI">
  <img src="https://img.shields.io/badge/Reference%20client-Python-blueviolet.svg" alt="参考客户端：Python">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="集成：CM5 | URTC">
</p>

# HYDRA-UMC-SDK

## 🧩 HYDRA-UMC 的共享合约和集成工具包

HYDRA-UMC-SDK定义了HYDRA-UMC服务共享的稳定语言，
客户端、CM5 适配器和 URTC 集成。它拥有规范的合同、
无依赖的 Python 参考验证器、一致性装置和
整合指导。它不
替换 Raspberry Pi OS、Hailo、ROS 2、MQTT、OPC-UA 或的官方 API
MT连接。

## 🚧 状态

JSON Schema v1 合约、有效/无效装置、Python 验证客户端、
并实施主机端测试。 Protobuf/OpenAPI 发布和客户端
对于更多语言是后续的兼容性里程碑。

## 🎯 第一个里程碑

1. 发布 `DeviceDescriptor`、`HealthReport`、`SafetyState` 和
   `UpdateManifest` JSON 模式 v1。
2. 使用 Python 参考客户端验证有效和无效的装置。
3.在CI中添加生产者/消费者兼容性矩阵。
4. 在集成需要时发布 Protobuf/OpenAPI 表示。
5. 从稳定合约中添加 TypeScript、Go 和 Rust 客户端。

## 📂 存储库布局

<p对齐=“中心”>
  <img src="images/REPOSITORY_LAYOUT.svg" alt="HYDRA-UMC-SDK 存储库布局的可视化地图" width="100%">
</p>

|路径|目的|
| ---| ---|
| `合同/` |规范的 JSON Schema v1 源；进一步的交涉遵循稳定的合同。 |
| `客户/` |无依赖的 Python 参考验证器和未来的语言客户端。 |
| `一致性/` |兼容性测试使用的有效和无效的 v1 装置。 |
| `文档/` |合同、API、安全和开发规范。 |
| `示例/` |可运行的 Python 验证示例。 |

在定义新消息之前，请阅读[合约指南](docs/CONTRACTS.md)。

## 🔗 相关项目

> 规范的公共生态系统关系图。

|项目|与 HYDRA-UMC-SDK 的关系 |
| ---| ---|
| [HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS) |设备代理消费者的设备、健康、安全和更新合同。 |
| [HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER) |经过身份验证的 API 生产者和消费者受 SDK 合约管理。 |
| [HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER) |发布合同感知客户端使用的版本和兼容性元数据。 |
| [HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC) |通过有界 CM5 和 MCU 适配器合约公开的硬件/固件平台。 |
| [URTC](https://github.com/JuanenRac/URTC) |通过版本化集成适配器连接的独立工具控制器平台。 |

**生态系统的其余部分：** 探索 [JuanenRac 生态系统仪表板](https://juanenrac.github.io/JuanenRac/) 中的七个公共层。

## 📜 许可证

代码为 GPL-3.0 或更高版本；文档是 CC BY-SA 4.0。请参阅[许可证]（许可证）。
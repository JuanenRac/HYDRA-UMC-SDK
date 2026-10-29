<!-- =============================================================================
HYDRA-UMC-SDK - Shared contracts and integration toolkit
Copyright (C) JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
GPL-3.0-or-later - see LICENSE
============================================================================= -->

<p align="center">
  <img src="images/HYDRA_UMC_BANNER.svg" alt="HYDRA-UMC-SDK banner" width="100%">
</p>

# 🧰 HYDRA-UMC-SDK

<p align="center"><a href="README.md">🇺🇸 English</a> | <a href="README_spa.md">🇪🇸 Español</a> | <a href="README_fra.md">🇫🇷 Français</a> | <a href="README_ita.md">🇮🇹 Italiano</a> | <a href="README_deu.md">🇩🇪 Deutsch</a> | <a href="README_zho.md">🇨🇳 简体中文</a> | 🇯🇵 <b>日本語</b> | <a href="README_por.md">🇵🇹 Português</a></p>

### 🧰 HYDRA-UMC の共有契約、リファレンスクライアント、統合ツール

<p align="center">
  <img src="https://img.shields.io/badge/License-GPL%203.0--or--later-blue.svg" alt="GPL 3.0 or later">
  <img src="https://img.shields.io/badge/Contracts-JSON%20Schema%20%7C%20OpenAPI-orange.svg" alt="Contracts">
  <img src="https://img.shields.io/badge/Reference%20clients-Python%20%7C%20Go%20%7C%20TypeScript%20%7C%20Rust-blueviolet.svg" alt="Reference%20clients">
  <img src="https://img.shields.io/badge/Integration-CM5%20%7C%20URTC-red.svg" alt="Integration">
  <img src="https://img.shields.io/badge/Tests-463%20passing-2ea44f.svg" alt="Tests">
  <img src="https://img.shields.io/badge/Version-0.3.8-0f6cbd.svg" alt="Version">
  <img src="https://img.shields.io/badge/Maturity-established-2EA44F.svg" alt="Maturity">
</p>

---

> **誠実性チェック - 今日実際に動くもの:** JSON Schema v1 の 10 件の契約（それぞれ有効・無効のフィクスチャ付き）、Python の検証器、HYDRA-UMC-SERVER の最初の OpenAPI v1 部分、同じスキーマを強制する Go・TypeScript・Rust のクライアント、ブリッジ用ヘルパー、互換性マトリクスは実在し、コンピューター上でテスト済みです（Python のテスト 463 件と、他の 3 つのクライアントのスイート）。Protobuf はまだ公開されておらず、ジョブゲートは共有のソフトウェア機能であって認証済みの安全機能ではなく、ここにあるものは実機では動かしていません。

---

> **安全性とセキュリティの現状:** このエコシステムは認証された安全システムではありません。ハードウェアの E-STOP 経路、ファームウェアが強制する制限やインターロック、検証済みの動作コマンドはまだありません。ファームウェアイメージは CRC32 と共有鍵の HMAC-SHA256 で検査しており、非対称署名ではありません。TLS と相互 TLS は任意で、既定では無効です。独自基板はまだ実装も試験もされていません。ここに書かれた内容を人の安全のために頼る前に、[セキュリティベースライン](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)と[脅威モデル](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)をお読みください。

---

## 📋 ひと目で

| | |
|---|---|
| バージョン | `0.3.8` |
| 成熟度 | 確立 |
| テスト | 463 (`python -m unittest discover -s clients/python/tests`) |
| 技術 | Python / TypeScript / Go / Rust / JSON Schema |
| 実機での確認 | まだです：このバージョンについて実機での動作記録はありません |

**移動：** [概要](#-概要) · [アーキテクチャ](#-アーキテクチャ) · [機能](#-機能) · [セキュリティと安全](#-セキュリティと安全) · [インターフェース](#-インターフェース) · [設定](#-設定) · [クイックスタート](#-クイックスタート) · [テスト](#-テスト) · [トラブルシューティング](#-トラブルシューティング) · [リポジトリの構成](#-リポジトリの構成) · [関連プロジェクト](#-関連プロジェクト)

## 🚦 プロジェクトの状況

各行はこのリポジトリの一部分で、信号は今日どこまで進んでいるかを示します。計画ではなく、リポジトリが示せるもの（テスト、ビルド、実行）に基づいて書かれています。

🟢 完了・検証済み · 🟡 動作する（既知の制限あり） · 🟠 一部のみ、または未検証 · 🔴 未実装または動作しない

| 領域 | 状態 | ここでの意味 |
|---|---|---|
| ソフトウェア | 🟢 | 目的に対して完成していて安定しています。既知の制限は上の正直さの確認に書かれています |
| テスト | 🟢 | 自動テスト 463 件。変更のたびに実行されます |
| 実機 | 🔴 | まだです：このバージョンについて実機での動作記録はありません |
| ドキュメント | 🟢 | 8 言語の README。変更のたびにマニフェストと照合されます |

## 🎯 概要

HYDRA-UMC-SDK は、HYDRA-UMC サービス、クライアント、CM5 アダプター、および
URTC 統合によって共有される安定した言語を定義します。規範的な契約、
依存関係のない Python 参照バリデータ、適合フィクスチャ、
統合ガイダンスを備えています。Raspberry Pi OS、Hailo、ROS 2、MQTT、OPC-UA、
MTConnect の公式 API を置き換えるものではありません。

## 🧩 HYDRA-UMC での役割

**HYDRA-UMC-SDK** はエコシステム共通の言語です。JSON Schema v1 の契約、サーバーの最初の OpenAPI 部分、Python・Go・TypeScript・Rust のリファレンスクライアント、すべてのブリッジとコネクターハブが使うブリッジ用ヘルパー、そして各リポジトリのツールを同一に保つツールを提供します。独自のサービスは動かさず、公式 API の代わりにもなりません。

## 🏛️ アーキテクチャ

<p align="center">
  <img src="images/architecture.svg" alt="HYDRA-UMC-SDK architecture" width="100%">
</p>

## ✨ 機能

### ステータス

JSON スキーマ v1 コントラクト、有効/無効なフィクスチャ、Python 検証クライアント、
ホスト側のテスト、そして HYDRA-UMC-SERVER 自身の HTTP サーフェスに対する実際の
最初の OpenAPI v1 スライス（`contracts/openapi/v1/server.openapi.json` -
[docs/CONTRACTS.md](docs/CONTRACTS.md#openapi-v1) 参照）が実装されています。
Protobuf の公開はその後の互換性マイルストーンです。Go、TypeScript、Rust のクライアントはすでにあります。

実際に動作する自動互換性マトリクス（`tools/verify_contract_matrix.py`）は、公開されているすべてのスキーマを Python バリデータ自身のコントラクト一覧と突き合わせて検証します。これにより、`project-manifest.schema.json`（このエコシステムの各リポジトリが公開する `hydra-umc.project.json` のコントラクト）にバリデータのエントリが一つも存在しないという実際のギャップを発見し、修正しました。現在では、各適合フィクスチャがそのファイル名どおりに判定されること、さらに未知のコントラクトおよび非互換なスキーマバージョンのケースについても正しく判定されることを証明しています。

下記の最初のマイルストーン以降、さらにコントラクトが追加されました(現在10件)。外部マシン連携のための公開コントラクト `BridgeJob`/`GateDecision`(詳細は [docs/BRIDGE_CONTRACT.md](docs/BRIDGE_CONTRACT.md))は `HYDRA-UMC-BRIDGE-ROS2`/`-OPENPNP`/`-PRINTER3D`/`-CNC`/`-LASER`/`-AMR`/`-DROIDS`/`-UAV` で共有され、独自の実データJSONワイヤー形式(`job_to_dict()`/`job_from_dict()`/`decision_to_dict()`)を持ちます。加えて、リクエスト側が主張する状態の代わりにゲートが使う、ブリッジ自身が観測した機器の状態と、保持メッセージを無視し同じ冪等キーを二度実行しないジョブ受付（`JobIntake`/`IdempotencyStore`）があります。`ScenarioOutcome` コントラクトと `compare_runs()` は、共有の「本当に直ったか」チェックで、障害が再現しなくなってもベースのフィンガープリントが変わっていなければ `apparent-success`(`regression-fixed` ではなく)を返します。`Operation` コントラクトと `validate_status_transition()` は、共有の目標/ジョブ/操作ライフサイクル - `received`/`authorized`/`queued`/`sent`/`confirmed`/`terminated`/`rejected` を表し、単一の「実行済み」の器にまとめることは決してありません。`Operation` のオプション `result` と `concludes_success()` は、実際の証拠(`run_id`/`origin`/`observers_enabled`/`outcome`)により、古い/再送された結果や観測が無効化された実行から成功を結論づけることを拒否します。独立した `Capability` コントラクトと `is_capability_usable()` は、あるターゲットが操作 `kind` のサポートを*宣言している*かどうかを、その裏付けが*最近実際に検証された*かどうか(`last_checked_at_utc`/`checked_configuration`/`max_age_seconds`)とは別のデータとしてモデル化し、宣言されただけで一度も検証されていない、または古くなった能力が黙って利用可能と扱われることを防ぎます。また `hydra-umc-sdk-mock-server`(`mock_server.py`)は、実際のCM5・ロボット・MCUハードウェアが無くてもUIやアダプタを開発できるよう、既知の各コントラクトについて有効なサンプルペイロードを単純なHTTP経由で提供します。10個すべてのコントラクトが、上記の互換性マトリクスで検証済みの有効・無効な適合フィクスチャを少なくとも1つずつ持っています。

## 🔒 セキュリティと安全

| 脅威 | 防御 | 場所 |
|---|---|---|
| 契約から外れたブリッジコマンド | ジョブのパラメーターは最大 32 個、名前は 64 文字、値は 1024 文字、識別子は 128 文字まで。要求側が主張する状態ではなく、ブリッジが観測した機械状態を使います | `bridge_contract.py` |
| 同じコマンドの二重実行、または保持メッセージの再生 | ジョブ受付は保持メッセージを無視し、同じ冪等キーを二度実行しません | `job_intake.py` |
| 長いコマンドの後ろで待たされる停止 | 通常のコマンドは 1 本のレーンで順に、停止の動詞は 2 本目のレーンで実行されます | `bridge_transport.py` |
| 設定ファイルにブローカーの認証情報がある、またはブローカーが未検証 | ユーザーとパスワードは環境変数かファイルから取り、TLS は CA でブローカーを検証でき、クライアント証明書と鍵で相互 TLS になります | `mqtt_connection.py` |
| スキーマだけが変わり検証器が追従していない | 互換性マトリクスが、公開された各スキーマを検証器の契約一覧と照合し、各フィクスチャをファイル名の主張どおりに判定します | `tools/verify_contract_matrix.py` |

**絶対にしないこと：** 認証済みの安全機能として働くこと。ジョブゲートはブリッジが共有するソフトウェア実装であり、安全認証ではありません。

## 🔌 インターフェース

| トピックまたはルート | 内容 |
|---|---|
| `contracts/json-schema/v1/` | JSON Schema v1 の契約 10 件：能力、デバイス記述子、イベントエンベロープ、ヘルスレポート、オペレーション、プロジェクトマニフェスト、安全状態、シナリオ結果、サーバー探索、更新マニフェスト |
| `contracts/openapi/v1/server.openapi.json` | HYDRA-UMC-SERVER の最初の OpenAPI v1 部分：探索、サインイン、設定、コマンド（サーバー自身の `docs/openapi.json` の一部） |
| `contracts/ports.yaml` | 各サービスのポート、ヘルスパス、systemd ユニットの一覧。`tools/sync_ports.py` が生成 |
| `hydra/bridges/<name>/cmd/#` | ブリッジが待ち受ける場所。応答は `.../<動詞>/result` |
| `hydra-umc-contract-validate`, `hydra-umc-sdk-mock-server` | コマンドラインの検証器（失敗時の終了コードは 2）と、契約ごとに有効な例を返す `127.0.0.1:8790` のモックサーバー |

## ⚙️ 設定

| 変数 | 既定値 | 設定する内容 |
|---|---|---|
| `HYDRA_MQTT_USERNAME`, `HYDRA_MQTT_PASSWORD` | 認証情報なし | ブローカーの認証情報。パスワードはユーザー名と併せてのみ |
| `HYDRA_MQTT_PASSWORD_FILE` | - | ファイルから読むパスワード（Docker や systemd のシークレット）。上の変数があれば無視されます |
| `HYDRA_MQTT_TLS`, `HYDRA_MQTT_TLS_CA` | TLS なし | `HYDRA_MQTT_TLS=1` はシステムの CA でブローカーを検証し、`HYDRA_MQTT_TLS_CA` は証明書に署名した CA のファイルを指します |
| `HYDRA_MQTT_TLS_CERT`, `HYDRA_MQTT_TLS_KEY` | - | 相互 TLS を要求するブローカー用のクライアント証明書と鍵。両方が必要で、TLS が有効になります |
| `--host`, `--port` | `127.0.0.1`, `8790` | モックサーバーの待ち受け先 |
| `HYDRA_UMC_SDK_ROOT` | 隣のフォルダー | 他のリポジトリのテストがこのリポジトリを見つける場所 |

## 🚀 クイックスタート

Python 3.11 以上が必要です。Go・TypeScript・Rust のクライアントも、ツールチェーンがあればビルドとテストを行います。

```bash
PYTHONPATH=clients/python/src python -m unittest discover -s clients/python/tests  # the Python client tests
python tools/verify_contract_matrix.py                                             # every schema against the validator and every fixture
PYTHONPATH=clients/python/src python -m hydra_umc_sdk.validation --help            # the contract validator on the command line
./build-test.sh                                                                    # the non-mutating build check (build-test.bat on Windows)
```

## 🧪 テスト

`python -m unittest discover -s clients/python/tests` で自動テスト 463 件を実行します。 他のクライアントには独自のスイートがあります。Go は 26 件（`go test ./...`）、TypeScript は 104 件（`npm test`）、Rust は 28 件（`cargo test`）で、ツールチェーンがあれば `tools/extra_build_steps.py` が実行します。ハードウェアは不要です。

CI は `HYDRA_UMC_CI=1 python tools/ci_validate.py` を実行し、マニフェスト、文書、8 つの README、図を検査します。

## 🏗️ ビルドとリリース

リリースビルドの前に、バージョンを変更しないビルドチェックを使用してください。

| 操作 | Windows | Linux / macOS |
|---|---|---|
| ビルドチェック（バージョンと CHANGELOG を変更しない） | `build-test.bat` | `./build-test.sh` |
| 実行 / 開発（提供されている場合） | `run*.bat` または `dev*.bat` | `./run*.sh` または `./dev*.sh` |

`build-test.bat` と `build-test.sh` は、`hydra-umc.project.json` をインクリメントせず、`CHANGELOG.md` も変更せずにプロジェクトのスタックをコンパイルまたは検証します。通常のコンパイラ出力だけが作成される場合があります。既存の `build*.bat`、`build*.sh`、`run*`、`dev*` は、各プロジェクト固有のバージョン化または実行時の動作を維持します。その動作が必要な場合はそれらを使用してください。

## 🩺 トラブルシューティング

| 表示 | 原因 | 対処 |
|---|---|---|
| `hydra-umc-contract-validate: missing required field: ...` | ペイロードが契約に違反しています。コマンドは終了コード 2 で終わります | そのファイルを、モックサーバーがその契約用に返す例と比べる |
| `verify_contract_matrix.py` が失敗する | スキーマが追加・変更されたが、検証器の契約一覧かフィクスチャが更新されていない | 検証器のエントリーと、有効・無効のフィクスチャを 1 つずつ追加 |
| `go test ./...` がスキップされる | ビルド確認は `go`・`npm`・`cargo` が PATH にあるときだけ Go・TypeScript・Rust のクライアントを実行します | ツールチェーンを入れる。どのクライアントがスキップされたかは出力に出ます |

## 📂 リポジトリの構成

<p align="center">
  <img src="images/repository-structure.svg" alt="Repository structure of HYDRA-UMC-SDK" width="100%">
</p>

<details>
<summary>ツリーのテキスト版</summary>

```text
HYDRA-UMC-SDK/
├── contracts/                 JSON Schema v1 のソース、OpenAPI 部分、ポート一覧
├── clients/                   Python・Go・TypeScript・Rust のリファレンスクライアント
├── conformance/               各契約の有効・無効のフィクスチャ
├── docs/                      契約・API・開発のガイド
├── examples/                  実行できる Python の例
├── tools/                     契約マトリクス、OpenAPI ゲート、ツール同期、ビルド確認
├── .github/                   CI ワークフローと Issue テンプレート
├── images/                    バナーと README の図
├── CHANGELOG.md               各バージョンの変更点
├── build-test.sh              変更を伴わないビルド確認
├── build.sh                   ビルドと検査。バージョンは変更しない
├── bump_manifest_version.py   マニフェストのバージョンを同期
├── bump_version.py            明示的なバージョン更新
├── hydra-umc.project.json     マニフェスト：バージョン、成熟度、ファミリー
├── run.sh                     プログラムを起動
└── test.sh                    テストを実行
```

</details>

`tools/`: `verify_contract_matrix.py`(スキーマ/バリデータ互換性マトリクス)、`verify_openapi.py`(依存関係のない OpenAPI 構造検証)、そして変更を加えない `build-test` エンジン。`sync_repo_tools.py` は全リポジトリの共有ツールを同一に保ち、`pin_sdk.py` は SDK の利用側をリリースタグに固定し、`canonical/` は複製元となる唯一のコピー（検証・テストを行い、求められたときだけバージョンを上げる `hydra_project_tool.py` コマンドを含む）を保持します。 `sync_ports.py` は各サービスのポート、ヘルスパス、systemd ユニットの登録簿 `contracts/ports.yaml` を生成・検査します。共通の秘密情報マスキング(`canonical/redaction.py`、ケースは `contracts/redaction/vectors.json`)は、テキストを外部に送るプロジェクトに同梱されます。

## 🗺️ ロードマップと既知の制限

**現時点の既知の制限**

* Protobuf はまだ公開されておらず、OpenAPI 部分が扱うのは探索・サインイン・設定・コマンドだけです。
* サーバーのルートは現在バージョン管理されておらず、`/api/v1` は `docs/API_DESIGN.md` に書かれた設計上の目標です。
* ここにあるものは実機では動かしておらず、ジョブゲートはソフトウェア機能であって認証済みの安全機能ではありません。

**次：** 統合が必要とする箇所で Protobuf を公開し、OpenAPI 部分をサーバーの残りのルートへ広げます。

## 🌍 言語

この README とリポジトリの文書は、英語・スペイン語・ドイツ語・フランス語・イタリア語・日本語・中国語・ポルトガル語（ポルトガル）の 8 言語で提供されています。8 つのファイルは同時に書かれ、同じ節と同じリンクを持つことを CI が確認します。 このリポジトリには独自の画面もメッセージカタログもないため、翻訳すべきインターフェース文字列はありません。

## 🔗 関連プロジェクト

本プロジェクトは、同じ作者(JuanenRac / Electro Hobby 3D)による HYDRA-UMC ロボティクスエコシステムの一部です。リクエストが実はこの中のどれかについてのものである可能性があるため、知っておく価値があります。

**親プロジェクト**
- **[HYDRA-UMC-OS](https://github.com/JuanenRac/HYDRA-UMC-OS)** — CM5 向けの再現可能な Raspberry Pi OS プロダクト層——読み取り専用エージェント、検証済み設定/プロファイル、WiFi 初回接続プロビジョニング。本 SDK 自身のデバイス・ヘルス・セーフティ・アップデート契約を消費するデバイスエージェント。
- **[HYDRA-UMC-CONNECTOR-HUB](https://github.com/JuanenRac/HYDRA-UMC-CONNECTOR-HUB)** — 外部マシン用コネクタのための宣言的アダプターマニフェストのレジストリとバリデーター。SDK 自身の契約という発想を外部マシンにまで拡張し、産業用ゲートウェイ系のプロジェクトを置き換えることはありません。

**直接関連**
- **[HYDRA-UMC-SERVER](https://github.com/JuanenRac/HYDRA-UMC-SERVER)** — すべての制御クライアントが実際に通信する、本物のヘッドレスバックエンド(REST/WebSocket) ——本 SDK 自身の契約に統治される、認証済みの API プロデューサー兼コンシューマー。
- **[HYDRA-UMC-UPDATER](https://github.com/JuanenRac/HYDRA-UMC-UPDATER)** — このエコシステム内のすべてのリポジトリを検出・クローン・更新する、管理用デスクトップツール ——本 SDK 自身の契約を理解するクライアントが消費する、バージョンおよび互換性メタデータを公開する。
- **[HYDRA-UMC-OS-REBUILDER](https://github.com/JuanenRac/HYDRA-UMC-OS-REBUILDER)** — エコシステムの最新バージョンをプリロードした、書き込み可能なCM5イメージを構築するWindows/Linuxデスクトップツール。Raspberry Pi Imager方式の初回起動Wi-Fi/ユーザー/SSH設定を備える。
- **[HYDRA-UMC-OPS-AGENT](https://github.com/JuanenRac/HYDRA-UMC-OPS-AGENT)** — 保守インシデントコーディネーター: 低権限のエッジ役割がサニタイズされたインベントリ/ヘルスのスナップショットを収集し、コントロールプレーン役割がそれを読み取り専用でレンダリングして AI プロバイダーに診断の提案を依頼します - パッチを適用することも、何かをデプロイすることも決してありません。
- **[HYDRA-UMC-DEV-SERVER](https://github.com/JuanenRac/HYDRA-UMC-DEV-SERVER)** — 再現可能な開発ホスト（Raspberry Pi 5 / CM5）。エコシステムのソースコードを保管し、永続キューのもとで境界の明確なビルド/テストタスクを実行する。運用中の CM5 とは明確に異なる、開発専用の役割。
- **[HYDRA-UMC-DOCS](https://github.com/JuanenRac/HYDRA-UMC-DOCS)** — エコシステムのドキュメントとツールの拠点：アーキテクチャ、インターフェース、セキュリティ基準、能力マトリクス、各マニフェストから生成されるプロジェクトカタログ。
- **[HYDRA-UMC](https://github.com/JuanenRac/HYDRA-UMC)** — ロボットアームのマザーボードの設計——CM5 ホスト + デュアルコア STM32H745、CAN-OTA/SPI-OTA 経由で最大 8 本のツールアームを統括することを目指す(ファームウェアは初期段階で、実装済みの基板はまだない)。
- **[URTC](https://github.com/JuanenRac/URTC)** — 物理的な Universal Robot Tool Controller 基板向けファームウェア、CAN バス経由の 25 以上のツールプロファイル ——本 SDK 自身のバージョン管理された統合アダプターを通じて接続される、独立したツールコントローラープラットフォーム。
- **[HYDRA-UMC-BRIDGE-ROS2](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-ROS2)** — 遅延インポートの rclpy ROS 2 トランスポートを持つコーディネーター(ROS 2 環境ではまだ実行していない) ——ROS 2 の観測・検査・キャンセル可能なセル作業のために、本 SDK 自身の共通 BridgeJob ゲートを使用する。
- **[HYDRA-UMC-BRIDGE-OPENPNP](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-OPENPNP)** — OpenPnP ピックアンドプレースの基板フローを安全に統括する高レベルコーディネーター ——追跡可能な基板の引き渡しのために、本 SDK 自身の相関付けられた冪等ジョブを使用する。
- **[HYDRA-UMC-BRIDGE-PRINTER3D](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-PRINTER3D)** — 実際にゲート制御されたジョブコマンドを持つ、Moonraker/Klipper 3D プリンター向けの安全な調整境界 ——ネイティブなプリンター準備状態を取り巻く本 SDK 自身のゲートを使用する。ヒーターや動作制御は公開しない。
- **[HYDRA-UMC-BRIDGE-CNC](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-CNC)** — GRBL ステータス/制御バイトへのアクセスを持つ、CNC セルの高レベルコーディネーター(エミュレーターに対してのみテスト済み) ——アイドル状態で保護された CNC の傍らでのみ調整するために、本 SDK 自身のゲートを使用する。
- **[HYDRA-UMC-BRIDGE-LASER](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-LASER)** — キー/筐体/インターロックの GPIO 信号 3 系統を読み取るレーザーセルのコーディネーター(模擬チップに対してのみテスト済み。レーザーの武装や発射はできない) ——レーザーの安全権限を保持しながら、補助機能のために本 SDK 自身のゲートを使用する。
- **[HYDRA-UMC-BRIDGE-AMR](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-AMR)** — VDA 5050 MQTT パブリッシャーによる AGV/AMR フリートの調整境界(エミュレートしたフリートに対してのみテスト済み) ——同じ共有ジョブ・安全ゲートに対して、自身のコマンドも検証する。
- **[HYDRA-UMC-BRIDGE-DROIDS](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-DROIDS)** — Boston Dynamics Spot コマンド送信機能を持つ、脚型/ヒューマノイドドロイドの調整境界(エミュレーターに対してのみテスト済み) ——同じ共有ジョブ・安全ゲートに対して、自身のコマンドも検証する。
- **[HYDRA-UMC-BRIDGE-UAV](https://github.com/JuanenRac/HYDRA-UMC-BRIDGE-UAV)** — MAVLink コマンド送信機能を持つ、カメラ搭載 UAV の調整境界(エミュレーターに対してのみテスト済み) ——同じ共有ジョブ・安全ゲートに対して、自身のコマンドも検証する。

**エコシステムの他のプロジェクト**

*コアバックエンド&クライアント*
- **[HYDRA-UMC-STUDIO](https://github.com/JuanenRac/HYDRA-UMC-STUDIO)** — リアルタイムのマルチロボット 3D 可視化を備えたウェブ制御ダッシュボード。
- **[HYDRA-UMC-SUITE](https://github.com/JuanenRac/HYDRA-UMC-SUITE)** — 複数のサーバーを同時に扱えるデスクトップ(PySide6)スウォームコマンドセンター、スタンドアロン実行ファイルとしてパッケージ化。
- **[HYDRA-UMC-ANDROID-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-ANDROID-CONTROL)** — 生体認証ログインとペアリングされた Wear OS コンパニオンを備えたネイティブ Android 制御アプリ。
- **[HYDRA-UMC-IOS-CONTROL](https://github.com/JuanenRac/HYDRA-UMC-IOS-CONTROL)** — リアルタイム WebSocket 同期を備えた iOS/iPadOS 制御アプリ(Flutter)。
- **[HYDRA-UMC-DSI](https://github.com/JuanenRac/HYDRA-UMC-DSI)** — 本体搭載の 7 インチ DSI タッチスクリーン向けネイティブタッチ UI、CM5 自体に組み込み。
- **[HYDRA-UMC-EDITOR-URDF](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-URDF)** — 完成したモデルを STUDIO 自身のカタログへ送信するデスクトップ用グラフィカル URDF 作成/編集ツール。
- **[HYDRA-UMC-EDITOR-STL](https://github.com/JuanenRac/HYDRA-UMC-EDITOR-STL)** — HYDRA-UMC-EDITOR-URDF も編集する同じモデルカタログ内で、実在するパーツを変換/置換/削除/追加するデスクトップ STL モデルエディタ。

*URTC ツールプラットフォーム*
- **[URTC-FLASHER](https://github.com/JuanenRac/URTC-FLASHER)** — URTC 基板用のデスクトップ GUI 書き込みツール、CAN-OTA およびフルチップ SWD/JTAG。
- **[URTC-TESTER](https://github.com/JuanenRac/URTC-TESTER)** — URTC 基板向けのデスクトップ CAN バスライブ診断ツール、ツールプロファイルごとに 1 パネル。
- **[URTC-WEB-STUDIO](https://github.com/JuanenRac/URTC-WEB-STUDIO)** — Web Serial API を使ったブラウザベースの URTC-TESTER の代替、ローカルインストール不要。
- **[URTC-GATEWAY](https://github.com/JuanenRac/URTC-GATEWAY)** — URTC の CAN バスの前に置くゲートウェイ：許可する識別子のリスト、レート制限、セッション鍵。コンピューター上でテスト済みで、実際のバスではまだ試していません。

*ビジョン AI ノード(Hailo-8)*
- **[HYDRA-UMC-VISION-NODE](https://github.com/JuanenRac/HYDRA-UMC-VISION-NODE)** — Hailo-8 ビジョンパイプラインの統合ハブ、段階ごとの実際のハードウェア準備状況チェック付き。
- **[HYDRA-UMC-DETECTION-HEF](https://github.com/JuanenRac/HYDRA-UMC-DETECTION-HEF)** — Hailo アーキテクチャ/チェックサムによる安全読み込み検証を備えた、実際のコンパイル済みモデルレジストリ。
- **[HYDRA-UMC-VISION-STREAMER](https://github.com/JuanenRac/HYDRA-UMC-VISION-STREAMER)** — 実際の HailoRT 統合境界を持つ、実際の GStreamer パイプライン + MediaMTX 設定生成器。
- **[HYDRA-UMC-VISUAL-SERVOING-API](https://github.com/JuanenRac/HYDRA-UMC-VISUAL-SERVOING-API)** — ゾーン状態を条件に承認する Position-Based Visual Servoing 補正則。カメラによる姿勢推定はまだない。
- **[HYDRA-UMC-SAFETY-ZONES](https://github.com/JuanenRac/HYDRA-UMC-SAFETY-ZONES)** — ファイルから物体位置を受け取る、ゾーン侵入・キャリブレーション鮮度・E-STOP 要求の v0 ロジック。検出器は接続されておらず、物理 E-STOP もまだ配線されていない。

*コグニティブ AI ノード(Hailo-10)*
- **[HYDRA-UMC-COGNITIVE-NODE](https://github.com/JuanenRac/HYDRA-UMC-COGNITIVE-NODE)** — Hailo-10 コグニティブパイプライン(LLM/VLA/音声オーケストレーション)の統合ハブ。
- **[HYDRA-UMC-VLA-ENGINE](https://github.com/JuanenRac/HYDRA-UMC-VLA-ENGINE)** — Vision-Language-Action モデル向けの、実際のアクショントークンのエンコード/デコードと軌道生成。
- **[HYDRA-UMC-VOICE-UI](https://github.com/JuanenRac/HYDRA-UMC-VOICE-UI)** — 確認ゲート付きの限定的な Watch リレーを備えた、実際の音声フロントエンド(VAD + 意図解析)。
- **[HYDRA-UMC-SEMANTIC-PLANNER](https://github.com/JuanenRac/HYDRA-UMC-SEMANTIC-PLANNER)** — MCU エラーコードに対する、実際のルールベースのタスク分解と意味的エラー復旧。
- **[HYDRA-UMC-DOCS-QA](https://github.com/JuanenRac/HYDRA-UMC-DOCS-QA)** — このエコシステム自身の Markdown ドキュメントに対する、標準ライブラリのみの実際の TF-IDF 文書検索。
- **[HYDRA-UMC-LOCAL-TECHNICIAN](https://github.com/JuanenRac/HYDRA-UMC-LOCAL-TECHNICIAN)** — エコシステム自身のための、ローカルでポリシーゲート付きのAIメンテナンス技術者 — 観察、診断し、修正を提案する;最上位の2つのリスクレベルは意図的にまだ実装されていない。

*オーケストレーション&スウォーム*
- **[HYDRA-UMC-ORCHESTRATOR](https://github.com/JuanenRac/HYDRA-UMC-ORCHESTRATOR)** — 実際の gRPC/Protobuf ヘルスレポート契約とミッションステートマシンを持つ統合ハブ。
- **[HYDRA-UMC-JOB-DISPATCHER](https://github.com/JuanenRac/HYDRA-UMC-JOB-DISPATCHER)** — 実際の HTTP API 上に構築された、優先度ベースの実際のジョブキュー(重複排除付き)。
- **[HYDRA-UMC-NODE-HEALING](https://github.com/JuanenRac/HYDRA-UMC-NODE-HEALING)** — リトライ/バックオフとアイデンティティ不一致検出を備えた、実際の gRPC ベースのフリートヘルスウォッチドッグ。
- **[HYDRA-UMC-PATH-PLANNER-3D](https://github.com/JuanenRac/HYDRA-UMC-PATH-PLANNER-3D)** — 実際の障害物/ワークスペース衝突検証を備えた、実際の RRT ベースの 3D 経路プランナー。
- **[HYDRA-UMC-SWARM-SYNC](https://github.com/JuanenRac/HYDRA-UMC-SWARM-SYNC)** — 複数セルの収束についてプロパティテストされた、実際の CRDT LWW-Element-Map 状態同期。

*デジタルツイン&シミュレーション*
- **[HYDRA-UMC-TWIN](https://github.com/JuanenRac/HYDRA-UMC-TWIN)** — 実際のバージョン互換性同期契約を持つ、デジタルツインエンジンの統合ハブ。
- **[HYDRA-UMC-HIL-BRIDGE](https://github.com/JuanenRac/HYDRA-UMC-HIL-BRIDGE)** — シミュレーションと実機の間にソフトウェアの衝突インターロックを備えたハードウェア・イン・ザ・ループのルーター(実機なしでテスト済み)。
- **[HYDRA-UMC-PHYSICS-REPLICA](https://github.com/JuanenRac/HYDRA-UMC-PHYSICS-REPLICA)** — 実際の URDF サブセットに対する、実際の順運動学と関節限界検証。
- **[HYDRA-UMC-SYNTHETIC-DATA-GEN](https://github.com/JuanenRac/HYDRA-UMC-SYNTHETIC-DATA-GEN)** — YOLO/COCO アノテーションのエクスポート機能を持つ、実際のプロシージャル 2D シーンジェネレーター。

*データ&分析*
- **[HYDRA-UMC-DATALAKE](https://github.com/JuanenRac/HYDRA-UMC-DATALAKE)** — 実際の取り込み/クエリ HTTP API を備えた、実際の sqlite3 ベースの時系列ストア。
- **[HYDRA-UMC-ANOMALY-DETECTOR](https://github.com/JuanenRac/HYDRA-UMC-ANOMALY-DETECTOR)** — ドリフト監視を備えた、実際の FFT + 統計ベースラインによる異常検知器。
- **[HYDRA-UMC-PRODUCTION-REPORTS](https://github.com/JuanenRac/HYDRA-UMC-PRODUCTION-REPORTS)** — DATALAKE の履歴に対する実際の OEE/稼働率計算、再現可能な CSV エクスポート付き。
- **[HYDRA-UMC-TELEMETRY-COLLECTOR](https://github.com/JuanenRac/HYDRA-UMC-TELEMETRY-COLLECTOR)** — シーケンス重複排除機能を備えた、DATALAKE への実際の CAN/WebSocket 取り込みパイプライン。

*産業用ゲートウェイ*
- **[HYDRA-UMC-GATEWAY-INDUSTRIAL](https://github.com/JuanenRac/HYDRA-UMC-GATEWAY-INDUSTRIAL)** — 実際のコマンド許可リスト/バックプレッシャー層を持つ、産業用プロトコルへ中継する統合ハブ。
- **[HYDRA-UMC-OPCUA-SERVER](https://github.com/JuanenRac/HYDRA-UMC-OPCUA-SERVER)** — 実際のバイナリプロトコルクライアントセッションで検証された、実際の OPC-UA アドレス空間。
- **[HYDRA-UMC-MQTT-BROKER](https://github.com/JuanenRac/HYDRA-UMC-MQTT-BROKER)** — クライアント単位のオプション認証とトピック ACL を備えた、実際の MQTT ブローカー。
- **[HYDRA-UMC-MTCONNECT-ADAPTER](https://github.com/JuanenRac/HYDRA-UMC-MTCONNECT-ADAPTER)** — 縮退モード出力を備えた、実際の MTConnect `/probe` および `/current` XML エンドポイント。

*補完ツール&エコシステム運用*
- **[HYDRA-UMC-DASHBOARD-AI](https://github.com/JuanenRac/HYDRA-UMC-DASHBOARD-AI)** — 誠実な統計フォールバックを備えた、DATALAKE/ANOMALY-DETECTOR 上のスマートサマリーと異常ハイライトパネル。
- **[HYDRA-UMC-TOOL-CLI](https://github.com/JuanenRac/HYDRA-UMC-TOOL-CLI)** — 実際の安定した終了コード契約を持つフリート CLI、HYDRA-UMC-SERVER 自身の API の本物のライブクライアント。
- **[HYDRA-UMC-WATCH](https://github.com/JuanenRac/HYDRA-UMC-WATCH)** — 触覚アラートのパターンとペアリング済みスマートフォンへの音声リレーを備えた WearOS コンパニオンアプリ(物理的なウォッチではまだ実行していない)。
- **[URTC-SMART-RACK](https://github.com/JuanenRac/URTC-SMART-RACK)** — 実際の工具 ID デコードと Smart Idle 予熱ロジックを備えた、基板搭載ラック用ファームウェア。
- **[URTC-VISION-TOOL](https://github.com/JuanenRac/URTC-VISION-TOOL)** — サーマル/RGB 検査ツールヘッド向けの、ファームウェアと実際の Python ビジョンコンパニオン。

## 📚 ドキュメント

さらに読むには：

* [エコシステムのセキュリティ基準](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/SECURITY_BASELINE.md)
* [エコシステムの脅威モデル](https://github.com/JuanenRac/HYDRA-UMC-DOCS/blob/main/docs/THREAT_MODEL.md)
* [このリポジトリの変更履歴](CHANGELOG.md)
* [このリポジトリのライセンス](LICENSE.md)

## 🤝 コントリビュートとコミュニティ

* プルリクエストの前に `HYDRA_UMC_CI=1 py -3 tools/ci_validate.py`（または `HYDRA_UMC_CI=1 python3 tools/ci_validate.py`）を実行してください。`CI_VALIDATION=PASS` と表示される必要があります。この確認に `build.sh` や `build.bat` は使わないでください。ビルドは検査ではありません。
* 8 つの README は HYDRA-UMC-DOCS の 1 つのソースから書かれます。手で編集しないでください。ソースを変更し、`tools/make_readmes.py` で書き直します。
* 実行していないことを README に書かないでください。事実であれば「シミュレーションのみ」「実機では未確認」と書きます。
* [CONTRIBUTING.md](CONTRIBUTING.md)、[行動規範](CODE_OF_CONDUCT.md)、[SECURITY.md](SECURITY.md)、[SUPPORT.md](SUPPORT.md) を参照してください。

## 👤 作者

**JuanenRac (Electro Hobby 3D)** · electrohobby3d@gmail.com

## 📜 ライセンス

GPL-3.0-or-later - [LICENSE](LICENSE).

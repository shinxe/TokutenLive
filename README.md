# TokutenLive - クラスマッチ運営支援ツール

A useful management tool/Calculator for all of the classmatch organizers in Japanese H.S
<br><br>Collaborated with GEMINI

## ✨ Features

- **リアルタイム更新**: 試合のスコアを入力すると、リーグ順位やトーナメント表が即座に更新されます。
- **自動トーナメント生成**: 各予選リーグの結果に基づき、決勝トーナメントの組み合わせを自動で生成します。
- **多様な競技に対応**: 複数の競技を同時に管理でき、競技特性に応じた異なるトーナメント形式に対応しています。
    - **球技（サッカー、バレーボールなど）**: 4チームによる決勝トーナメント
    - **ラケット競技（バドミントン、卓球）**: 8チームによる決勝トーナメント
- **順位の自動計算**: リーグ戦の勝敗や直接対決の結果を考慮して、複雑な順位を自動で計算します。
- **総合ランキング**: 全競技の成績をポイント化し、クラスごとの総合順位を算出します。
- **管理者用パネル**: 試合結果の入力、チーム管理、トーナメント生成などをWeb上の画面から直感的に操作できます。

## 🛠️ 技術スタック

- **バックエンド**: Python 3, FastAPI, SQLAlchemy
- **フロントエンド**: Vue.js 3, Vite, Axios
- **データベース**: SQLite

## 📂 プロジェクト構造

```
.
├── api/         # FastAPIバックエンドのソースコード
├── frontend/    # Vue.jsフロントエンドのソースコード
├── scripts/     # データベース初期化などの各種スクリプト
└── class_match.db # SQLiteデータベースファイル
```

## 🚀 セットアップと実行方法

このアプリケーションをローカル環境で実行するための手順です。

### 1. 前提条件

- [Python 3.8+](https://www.python.org/)
- [Node.js 16+](https://nodejs.org/) (npmを含む)

### 2. インストール

まず、プロジェクトをクローンします。

```bash
git clone <repository-url>
cd TokutenLive
```

#### バックエンドのセットアップ

```bash
# 1. Python仮想環境を作成
python -m venv venv

# 2. 仮想環境を有効化
# Windowsの場合
venv\Scripts\activate
# macOS/Linuxの場合
source venv/bin/activate

# 3. 必要なライブラリをインストール
pip install -r requirements.txt
```

#### フロントエンドのセットアップ

```bash
# 1. frontendディレクトリに移動
cd frontend

# 2. 必要なライブラリをインストール
npm install

# 3. 環境変数ファイルを作成
# .env.production をコピーして .env ファイルを作成します
cp .env.production .env
```

`.env` ファイルの中身を確認し、`VITE_API_BASE_URL` がバックエンドのURL（デフォルトでは `http://127.0.0.1:8000`）を指していることを確認してください。

### 3. データベースの初期化

アプリケーションで利用するデータベースと初期データを準備します。プロジェクトのルートディレクトリで以下のコマンドを実行してください。

```bash
# 1. データベースとテーブルを作成
python api/models.py

# 2. 参加クラスの初期データを登録
python populate_league.py
```

### 4. アプリケーションの実行

#### バックエンドサーバーの起動

```bash
# プロジェクトのルートディレクトリで実行
uvicorn api.main:app --reload
```

サーバーは `http://localhost:8000` で起動します。

#### フロントエンドサーバーの起動

```bash
# frontendディレクトリで実行
npm run dev
```

開発サーバーが起動し、 `http://localhost:5173` でアプリケーションにアクセスできます。

## 🔒 管理者アクセス

試合結果の入力など、管理者権限が必要な操作を行うにはログインが必要です。

- **アクセス**: アプリケーション右上の「管理者用」メニュー
- If you wanna change the pw, edit `main.py` and change ADMIN_PASSWORD
# Agno Blog - Getting Started Guide

このガイドでは、Agno Blogアプリケーションの起動と基本的な使用方法について説明します。

## 🚀 クイックスタート

### 1. 前提条件の確認

以下がインストールされていることを確認してください：

- **Python 3.11+**
- **Docker & Docker Compose**（推奨）
- **Git**

### 2. APIキーの準備

以下のAPIキーを取得してください：

- **OpenAI API Key**: [OpenAI Platform](https://platform.openai.com/api-keys)
- **Anthropic API Key**: [Anthropic Console](https://console.anthropic.com/)
- **Cohere API Key**: [Cohere Dashboard](https://dashboard.cohere.ai/api-keys)（オプション）

### 3. プロジェクトのセットアップ

```bash
# 1. リポジトリをクローン（または既存のプロジェクトに移動）
cd agno-blog

# 2. 環境変数ファイルを作成
cp .env.example .env

# 3. .envファイルを編集してAPIキーを設定
# テキストエディタで.envファイルを開き、以下の値を設定：
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 4. アプリケーションの起動

#### 方法A: Docker Compose（推奨）

```bash
# 全サービスを起動
make quick-start

# または手動で
docker-compose up -d
```

#### 方法B: Python直接実行

```bash
# 依存関係をインストール
make install

# または手動で
pip install -r src/requirements.txt

# アプリケーションを起動
make dev

# または手動で
cd src && python main.py
```

### 5. アプリケーションにアクセス

ブラウザで以下のURLにアクセス：

- **メインアプリケーション**: http://localhost:8000
- **ヘルスチェック**: http://localhost:8000/health
- **API仕様書**: http://localhost:8000/docs

## 📖 基本的な使用方法

### ブログ記事の生成

1. **ホーム画面**（http://localhost:8000）にアクセス
2. **URL入力欄**に記事の元となるWebページのURLを入力
3. **テンプレート**を選択（デフォルト、技術チュートリアル、ニュース記事）
4. **「ブログ記事を生成」**ボタンをクリック
5. **生成された記事**を確認
6. 必要に応じて**フィードバック**を送信

### 記事の管理

1. **記事一覧**（http://localhost:8000/posts）にアクセス
2. **検索・フィルター**機能を使用して記事を絞り込み
3. **詳細表示**で記事の全文を確認
4. **コピー機能**で記事をクリップボードにコピー

### テンプレートの管理

1. **テンプレート管理**（http://localhost:8000/templates）にアクセス
2. **テンプレート一覧**で利用可能なテンプレートを確認
3. **詳細表示**でテンプレートの構造を確認
4. **フィードバック**機能でテンプレートの改善提案

## 🛠 開発者向け情報

### プロジェクト構造

```
agno-blog/
├── src/                    # メインアプリケーション
│   ├── main.py            # エントリーポイント
│   ├── agents/            # AIエージェント
│   ├── tools/             # ツール・ユーティリティ
│   ├── models/            # データモデル
│   └── workflows/         # ワークフロー定義
├── templates/             # HTMLテンプレート
├── docker-compose.yml     # Docker設定
├── Dockerfile            # Dockerイメージ定義
├── Makefile              # 開発用コマンド
└── README.md             # プロジェクト概要
```

### 利用可能なコマンド

```bash
# 開発
make install        # 依存関係インストール
make dev           # 開発サーバー起動
make test          # テスト実行
make lint          # コード品質チェック
make format        # コードフォーマット

# Docker
make build         # Dockerイメージビルド
make run           # Docker Composeで起動
make stop          # コンテナ停止
make logs          # ログ表示
make shell         # コンテナシェルアクセス

# 本番環境
make deploy        # 本番デプロイ
make backup        # データベースバックアップ
make restore       # データベース復元

# ユーティリティ
make clean         # 一時ファイル削除
make health        # アプリケーション状態確認
make status        # サービス状態確認
```

### API仕様

主要なAPIエンドポイント：

- `POST /api/generate-post`: ブログ記事生成
- `GET /api/posts`: 記事一覧取得
- `GET /api/posts/{post_id}`: 記事詳細取得
- `POST /api/update-template`: テンプレート更新
- `GET /api/templates`: テンプレート一覧取得

詳細なAPI仕様は http://localhost:8000/docs で確認できます。

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. APIキーエラー

**エラー**: "API key not found" または認証エラー

**解決方法**:
```bash
# .envファイルの確認
cat .env

# APIキーが正しく設定されているか確認
# 必要に応じて.envファイルを編集
```

#### 2. ポートが使用中

**エラー**: "Port 8000 is already in use"

**解決方法**:
```bash
# ポートを使用しているプロセスを確認
lsof -i :8000

# または別のポートを使用
export PORT=8001
make dev
```

#### 3. Docker関連の問題

**エラー**: Docker関連のエラー

**解決方法**:
```bash
# Dockerサービスの状態確認
docker --version
docker-compose --version

# コンテナの再起動
make stop
make run

# ログの確認
make logs
```

#### 4. 依存関係の問題

**エラー**: モジュールが見つからない

**解決方法**:
```bash
# 依存関係の再インストール
make clean
make install

# または
pip install --upgrade -r src/requirements.txt
```

### ログの確認

```bash
# アプリケーションログ
make logs

# 特定のサービスのログ
docker-compose logs agno-blog

# リアルタイムログ監視
docker-compose logs -f agno-blog
```

### デバッグモード

開発時はデバッグモードを有効にできます：

```bash
# .envファイルで設定
DEBUG=true

# または環境変数として設定
export DEBUG=true
make dev
```

## 📚 参考資料

- **Agno Framework**: https://docs.agno.com
- **FastAPI**: https://fastapi.tiangolo.com
- **Docker Compose**: https://docs.docker.com/compose/

## 🆘 サポート

問題が解決しない場合は、以下をお試しください：

1. **基本テストの実行**:
   ```bash
   python3 test_basic.py
   ```

2. **システム状態の確認**:
   ```bash
   make health
   make status
   ```

3. **ログの詳細確認**:
   ```bash
   make logs
   ```

4. **クリーンな再起動**:
   ```bash
   make clean-all
   make quick-start
   ```

---

**Happy Blogging with Agno! 🚀**
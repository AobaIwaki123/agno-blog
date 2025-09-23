# Agno Blog Application

AIを活用したブログ記事の自動生成・管理システムです。[Agnoフレームワーク](https://docs.agno.com)を使用して、URLから高品質なブログ記事を自動生成し、ユーザーフィードバックに基づいてテンプレートを継続的に改善します。

## 🚀 機能

### 1. ブログ記事の自動生成
- **URL入力**: WebページのURLを入力するだけで記事を生成
- **コンテンツ抽出**: 高度なWebスクレイピングでメインコンテンツを抽出
- **AI生成**: Claude Sonnet 4.0とGPT-4oを使用した高品質な記事生成
- **テンプレート選択**: 用途に応じた複数のテンプレートから選択可能

### 2. テンプレート管理
- **フィードバック処理**: ユーザーの意見を基にテンプレートを自動改善
- **バージョン管理**: テンプレートの変更履歴を追跡
- **カスタムテンプレート**: 独自のテンプレートを作成・編集
- **使用統計**: テンプレートの利用状況と評価を可視化

### 3. ブログ記事管理
- **記事一覧**: 生成された全記事の閲覧・管理
- **検索・フィルター**: タイトル、テンプレート、日付での絞り込み
- **詳細表示**: 記事の詳細情報とメタデータの確認
- **エクスポート**: 記事のコピー・エクスポート機能

## 🛠 技術スタック

### フレームワーク・ライブラリ
- **[Agno](https://docs.agno.com)**: マルチエージェントシステムフレームワーク
- **FastAPI**: 高性能WebAPIフレームワーク
- **SQLAlchemy**: データベースORM
- **Pydantic**: データバリデーション

### AIモデル
- **Claude 3.5 Sonnet**: コンテンツ分析・テンプレート管理
- **GPT-4o**: ブログ記事生成・SEO最適化
- **Cohere**: ベクトル検索・知識ベース

### データベース・ストレージ
- **SQLite**: 開発環境用軽量データベース
- **PostgreSQL**: 本番環境用データベース
- **LanceDB**: ベクトルデータベース（知識ベース）
- **Redis**: キャッシュ・セッション管理

### インフラ・デプロイ
- **Docker**: コンテナ化
- **Docker Compose**: マルチコンテナ管理
- **Nginx**: リバースプロキシ・ロードバランサー

## 📦 インストール

### 前提条件
- Python 3.11以上
- Docker & Docker Compose（推奨）
- 以下のAPIキー:
  - [OpenAI API Key](https://platform.openai.com/api-keys)
  - [Anthropic API Key](https://console.anthropic.com/)
  - [Cohere API Key](https://dashboard.cohere.ai/api-keys)（オプション）

### クイックスタート

1. **リポジトリをクローン**
   ```bash
   git clone <repository-url>
   cd agno-blog
   ```

2. **環境変数を設定**
   ```bash
   cp .env.example .env
   # .envファイルを編集してAPIキーを設定
   ```

3. **Dockerで起動（推奨）**
   ```bash
   make quick-start
   ```

4. **ブラウザでアクセス**
   ```
   http://localhost:8000
   ```

### 開発環境セットアップ

```bash
# 依存関係をインストール
make install

# 開発サーバーを起動
make dev
```

## 🔧 使用方法

### 1. ブログ記事の生成

1. **ホーム画面**でURLを入力
2. **テンプレート**を選択（デフォルト、技術チュートリアル、ニュース記事）
3. **「ブログ記事を生成」**をクリック
4. **生成された記事**を確認・編集
5. **フィードバック**を送信してテンプレートを改善

### 2. 記事の管理

- **記事一覧**ページで全記事を閲覧
- **検索・フィルター**機能で記事を絞り込み
- **詳細表示**で記事の全文とメタデータを確認
- **コピー機能**で記事をクリップボードにコピー

### 3. テンプレートの管理

- **テンプレート管理**ページでテンプレート一覧を表示
- **詳細表示**でテンプレートの構造と統計を確認
- **フィードバック**機能でテンプレートの改善提案
- **新規作成**で独自のテンプレートを作成

## 📊 アーキテクチャ

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web UI        │    │   FastAPI        │    │   AI Agents     │
│   (HTML/JS)     │◄──►│   (REST API)     │◄──►│   (Agno)        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                                ▼                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Database      │    │   Vector DB      │    │   External APIs │
│   (PostgreSQL)  │    │   (LanceDB)      │    │   (OpenAI, etc) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### エージェント構成

1. **URL Processor Agent**: Webページからコンテンツを抽出・分析
2. **Content Generator Agent**: 抽出されたコンテンツからブログ記事を生成
3. **Template Manager Agent**: ユーザーフィードバックを分析してテンプレートを改善

## 🚀 デプロイ

### Docker Compose（推奨）

```bash
# 本番環境用デプロイ
make deploy-prod

# モニタリング付きデプロイ
make deploy-monitoring
```

### 環境別設定

- **開発環境**: SQLite + デバッグモード
- **本番環境**: PostgreSQL + Redis + Nginx
- **モニタリング**: Prometheus + Grafana

## 🔍 API仕様

### 主要エンドポイント

- `POST /api/generate-post`: ブログ記事生成
- `GET /api/posts`: 記事一覧取得
- `GET /api/posts/{post_id}`: 記事詳細取得
- `POST /api/update-template`: テンプレート更新
- `GET /api/templates`: テンプレート一覧取得
- `GET /health`: ヘルスチェック

### リクエスト例

```bash
# ブログ記事生成
curl -X POST "http://localhost:8000/api/generate-post" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "template_id": "default"
  }'
```

## 🧪 テスト

```bash
# 全テスト実行
make test

# コード品質チェック
make lint

# コードフォーマット
make format
```

## 📈 モニタリング

### ヘルスチェック

```bash
# アプリケーション状態確認
make health

# サービス状態確認
make status

# ログ確認
make logs
```

### メトリクス（オプション）

- **Prometheus**: メトリクス収集
- **Grafana**: データ可視化
- **アクセス**: http://localhost:3000 (admin/admin)

## 🛡 セキュリティ

- **入力検証**: Pydanticによる厳密なデータバリデーション
- **レート制限**: Nginxによる API制限
- **HTTPS対応**: SSL/TLS証明書設定
- **セキュリティヘッダー**: XSS、CSRF保護

## 🔧 カスタマイズ

### 新しいテンプレートの作成

```python
# テンプレート例
template_content = """
# {title}

## 概要
{overview}

## 詳細
{details}

## まとめ
{conclusion}
"""
```

### 新しいツールの追加

```python
from agno.tools import Tool

def custom_tool(input_data: str) -> dict:
    # カスタムロジック
    return {"result": "processed"}
```

## 🤝 コントリビューション

1. フォークを作成
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🆘 サポート

- **ドキュメント**: [Agno公式ドキュメント](https://docs.agno.com)
- **Issue**: [GitHub Issues](https://github.com/your-repo/issues)
- **ディスカッション**: [GitHub Discussions](https://github.com/your-repo/discussions)

## 📝 更新履歴

### v1.0.0 (2024-12-XX)
- 初回リリース
- URL処理エージェント実装
- コンテンツ生成エージェント実装
- テンプレート管理エージェント実装
- Web UI実装
- Docker対応

---

**Powered by [Agno Framework](https://docs.agno.com) 🤖**
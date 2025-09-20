# Agno Blog - AI-Powered Blog Generation

Agno Agentを使用したAI駆動のブログ生成・管理システムです。

## 機能

### 1. ブログ記事の自動生成
- URLを送信すると、AIエージェントが関連情報を収集
- 構造化されたブログ記事を自動生成
- 複数のテンプレートに対応（一般記事、技術記事、ニュース記事）

### 2. テンプレート管理
- ユーザーフィードバックに基づくテンプレート改善
- 複数バージョンのテンプレート管理
- カテゴリ別テンプレート対応

### 3. 記事の改善機能
- 生成された記事に対するフィードバック機能
- AIによる記事の自動改善
- 継続的な品質向上

## 技術スタック

- **フレームワーク**: Agno Agent, FastAPI
- **AI モデル**: Claude Sonnet 4.0, OpenAI GPT
- **データベース**: SQLite (開発), PostgreSQL (本番)
- **フロントエンド**: HTML, CSS, JavaScript
- **デプロイ**: Docker, Docker Compose

## セットアップ

### 1. 環境準備

```bash
# リポジトリをクローン
git clone <repository-url>
cd agno-blog

# 仮想環境を作成
conda create -n agno python=3.12
conda activate agno

# 依存関係をインストール
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
# .envファイルを作成
cp .env.example .env

# 必要なAPIキーを設定
export ANTHROPIC_API_KEY=your_anthropic_api_key
export OPENAI_API_KEY=your_openai_api_key
export CO_API_KEY=your_cohere_api_key
export OS_SECURITY_KEY=your_security_key
```

### 3. アプリケーションの起動

```bash
# 開発サーバーを起動
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# またはDockerを使用
docker-compose up --build
```

### 4. アクセス

ブラウザで `http://localhost:8000` にアクセス

## 使用方法

### ブログ記事の生成

1. メインページでURLを入力
2. テンプレートを選択（一般記事、技術記事、ニュース記事）
3. 必要に応じてカスタム指示を追加
4. 「ブログ記事を生成」ボタンをクリック

### 記事の改善

1. 生成された記事の「記事を改善」ボタンをクリック
2. 改善点を入力
3. AIが記事を自動改善

### テンプレートの更新

1. 「テンプレート管理」セクションでフィードバックを入力
2. 「テンプレートを更新」ボタンをクリック
3. 今後の記事生成に反映

## API エンドポイント

### ブログ記事生成
```http
POST /api/generate-post
Content-Type: application/json

{
  "url": "https://example.com/article",
  "template_id": "general",
  "custom_instructions": "技術的な内容を分かりやすく説明してください"
}
```

### 記事一覧取得
```http
GET /api/blog-posts
```

### 記事改善
```http
POST /api/improve-post/{post_id}
Content-Type: application/json

{
  "feedback": "もっと具体的な例を追加してください"
}
```

### テンプレート更新
```http
POST /api/update-template
Content-Type: application/json

{
  "template_id": "default",
  "feedback": "導入部分をもっと魅力的にしてください"
}
```

## デプロイ

### Docker Compose を使用

```bash
# 本番環境で起動
docker-compose --profile production up -d

# ログを確認
docker-compose logs -f agno-blog
```

### Cloud Run へのデプロイ

```bash
# Google Cloud SDKをインストール
gcloud auth login
gcloud config set project your-project-id

# イメージをビルド・プッシュ
gcloud builds submit --tag gcr.io/your-project-id/agno-blog

# Cloud Runにデプロイ
gcloud run deploy agno-blog \
  --image gcr.io/your-project-id/agno-blog \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated
```

## アーキテクチャ

### エージェント構成

1. **URL Processor Agent**: URLからコンテンツを抽出・分析
2. **Content Generator Agent**: ブログ記事を生成・改善
3. **Template Manager Agent**: テンプレートの管理・更新

### データフロー

```
URL入力 → URL処理 → コンテンツ分析 → ブログ記事生成 → 表示
                ↓
        テンプレート管理 ← ユーザーフィードバック
```

## 開発

### プロジェクト構造

```
agno-blog/
├── src/
│   ├── agents/          # AIエージェント
│   ├── models/          # データモデル
│   ├── tools/           # ツール類
│   ├── workflows/       # ワークフロー
│   └── main.py          # メインアプリケーション
├── static/              # 静的ファイル
├── templates/           # HTMLテンプレート
├── requirements.txt     # Python依存関係
├── Dockerfile          # Docker設定
├── docker-compose.yml  # Docker Compose設定
└── README.md           # このファイル
```

### テスト

```bash
# ユニットテストを実行
python -m pytest tests/

# カバレッジレポートを生成
python -m pytest --cov=src tests/
```

## ライセンス

MIT License

## 貢献

プルリクエストやイシューの報告を歓迎します。

## サポート

問題が発生した場合は、GitHubのIssuesページで報告してください。
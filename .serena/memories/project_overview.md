# Agno Blog Project Overview

## Project Purpose
Agno Agentを使用したブログ自動作成・投稿・閲覧システムの構築プロジェクトです。

## Tech Stack
- **Framework**: Agno (Python multi-agent framework)
- **Language**: Python 3.12
- **Database**: SQLite (開発環境)
- **Web Framework**: FastAPI
- **AI Models**: 
  - Claude Sonnet 4.0 (Anthropic)
  - OpenAI GPT models
- **Tools**: MCP (Model Context Protocol)
- **Containerization**: Docker
- **Environment Management**: Conda

## Project Structure
```
agno-blog/
├── agno-agent/           # 既存のAgno Agent実装
│   ├── src/
│   │   ├── agno_agent.py      # メインのAgno Agent
│   │   └── hackernews_agent.py # HackerNews用エージェント
│   ├── requirements.txt
│   ├── Dockerfile
│   └── Makefile
├── src/                  # 新しいブログシステム
│   ├── models/           # データモデル
│   ├── agents/           # ブログ用エージェント
│   ├── tools/            # カスタムツール
│   └── workflows/        # ワークフロー
├── compose.yml           # Docker Compose設定
└── README.md
```

## Key Features (Planned)
1. URL処理エージェント - URLからコンテンツを抽出
2. コンテンツ生成エージェント - ブログ記事を自動生成
3. テンプレート管理エージェント - テンプレートの編集と更新
4. ブログ閲覧機能 - 静的サイトでの記事表示
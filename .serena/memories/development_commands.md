# Development Commands

## Environment Setup
```bash
# Conda環境の作成とアクティベート
conda create -n agno python=3.12
conda activate agno

# 依存関係のインストール
pip install -r agno-agent/requirements.txt
```

## Running the Application

### Agno Agent (既存)
```bash
# HackerNewsエージェントのクイックスタート
make quick-start
# または
python agno-agent/src/hackernews_agent.py

# Agno Agentの起動
make agno-agent
# または
fastapi dev agno-agent/src/agno_agent.py
```

### Docker Compose
```bash
# コンテナの起動
docker-compose up

# バックグラウンドで起動
docker-compose up -d
```

## Development Workflow
```bash
# プロジェクトルートに移動
cd /Users/iwakiaoiyou/agno-blog

# 新しいブログシステムの開発
# src/ ディレクトリ内で作業
```

## System Commands (Darwin/macOS)
```bash
# ファイル検索
find . -name "*.py" -type f
grep -r "pattern" .

# ディレクトリ一覧
ls -la
ls -la src/

# Git操作
git status
git add .
git commit -m "message"
git push
```
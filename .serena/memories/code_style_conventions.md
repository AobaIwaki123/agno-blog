# Code Style and Conventions

## Python Style
- **Python Version**: 3.12
- **Type Hints**: 必須（Pydanticモデル使用）
- **Docstrings**: Google style推奨
- **Naming**: 
  - クラス: PascalCase (e.g., `BlogPost`)
  - 関数/変数: snake_case (e.g., `blog_post`)
  - 定数: UPPER_CASE (e.g., `DEFAULT_TEMPLATE`)

## Agno Framework Conventions
- **Agent定義**: 明確な名前と役割を設定
- **Tools**: 独立したツールクラスとして実装
- **Models**: Pydantic BaseModelを使用
- **Database**: SQLite（開発）、PostgreSQL（本番）

## Project Structure Conventions
```
src/
├── models/          # Pydanticデータモデル
├── agents/          # Agno Agent実装
├── tools/           # カスタムツール
├── workflows/       # ワークフロー定義
└── main.py         # エントリーポイント
```

## Import Style
```python
# 標準ライブラリ
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

# サードパーティ
from agno.agent import Agent
from agno.models.anthropic import Claude
from pydantic import BaseModel

# ローカル
from .models.blog_post import BlogPost
from .tools.web_scraper import WebScraperTool
```

## Error Handling
- 適切な例外処理を実装
- ログ出力でデバッグ情報を提供
- ユーザーフレンドリーなエラーメッセージ
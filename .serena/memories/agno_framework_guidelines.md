# Agno Framework Guidelines

## Agent Design Principles
- **Single Responsibility**: 各エージェントは明確な役割を持つ
- **Tool Integration**: 適切なツールを選択してエージェントに追加
- **Memory Management**: ユーザーメモリと履歴を活用
- **Error Handling**: 堅牢なエラーハンドリングを実装

## Agent Configuration
```python
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.db.sqlite import SqliteDb

agent = Agent(
    name="Descriptive Name",
    model=Claude(id="claude-sonnet-4-0"),
    tools=[custom_tools],
    db=SqliteDb(db_file="blog.db"),
    add_history_to_context=True,
    markdown=True,
)
```

## Tool Development
- **Async Support**: 非同期処理をサポート
- **Error Handling**: 適切なエラーレスポンス
- **Type Hints**: 明確な型定義
- **Documentation**: ツールの目的と使用方法を明記

## Database Integration
- **SQLite**: 開発環境での使用
- **PostgreSQL**: 本番環境での使用
- **Schema Design**: 適切なテーブル設計
- **Migration**: データベーススキーマの管理

## Workflow Design
- **Step Definition**: 明確なステップ定義
- **Error Recovery**: エラー時の回復処理
- **Parallel Processing**: 可能な限り並列処理
- **State Management**: 適切な状態管理
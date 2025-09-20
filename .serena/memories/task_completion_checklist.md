# Task Completion Checklist

## Before Starting Development
- [ ] プロジェクト構造の確認
- [ ] 必要な依存関係のインストール
- [ ] 環境変数の設定（API keys等）

## During Development
- [ ] 型ヒントの追加
- [ ] エラーハンドリングの実装
- [ ] ログ出力の追加
- [ ] ドキュメント文字列の記述

## After Code Changes
- [ ] 構文エラーのチェック
- [ ] インポートエラーの確認
- [ ] 基本的な動作テスト
- [ ] コードの可読性確認

## Testing Commands
```bash
# Python構文チェック
python -m py_compile src/*.py

# インポートテスト
python -c "import src.models.blog_post"

# アプリケーション起動テスト
fastapi dev src/main.py
```

## Code Quality
- [ ] 一貫した命名規則
- [ ] 適切なコメント
- [ ] 不要なコードの削除
- [ ] ファイル構造の整理

## Documentation
- [ ] README.mdの更新
- [ ] コード内コメントの追加
- [ ] API仕様の記録
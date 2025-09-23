#!/usr/bin/env python3
"""
シンプルなAgent起動テストスクリプト

基本的な機能をクイックテストするためのスクリプト
"""

import os
import sys
from pathlib import Path

# srcディレクトリをパスに追加
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def quick_test():
    """クイックテスト実行"""
    print("⚡ Agent起動 クイックテスト")
    print("=" * 40)
    
    # 1. 環境変数の基本チェック
    print("\n🔑 API Keys:")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if anthropic_key:
        print(f"✅ Anthropic: {len(anthropic_key)} 文字")
    else:
        print("❌ Anthropic: 未設定")
    
    if openai_key:
        print(f"✅ OpenAI: {len(openai_key)} 文字")
    else:
        print("❌ OpenAI: 未設定")
    
    # API キーが1つもない場合は終了
    if not anthropic_key and not openai_key:
        print("\n❌ API キーが設定されていません")
        print("環境変数を設定してから再実行してください:")
        print("export ANTHROPIC_API_KEY='your_key'")
        print("export OPENAI_API_KEY='your_key'")
        return False
    
    # 2. 基本インポートテスト
    print("\n📦 Imports:")
    try:
        import agno
        print("✅ agno: OK")
    except ImportError as e:
        print(f"❌ agno: {e}")
        return False
    
    try:
        from config import Config
        print("✅ config: OK")
    except ImportError as e:
        print(f"❌ config: {e}")
        return False
    
    # 3. Agent作成テスト
    print("\n🤖 Agents:")
    try:
        from agents.factory import create_agents
        agents = create_agents()
        print(f"✅ {len(agents)} Agents created")
        for i, agent in enumerate(agents, 1):
            print(f"  {i}. {agent.name}")
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False
    
    # 4. FastAPIアプリテスト
    print("\n🌐 FastAPI:")
    try:
        from main import create_app
        app = create_app()
        print("✅ App created successfully")
        
        # AgentOS マウントの確認
        agno_routes = [route for route in app.routes if "/agno" in str(route)]
        if agno_routes:
            print("✅ Agent UI mounted at /agno")
        else:
            print("⚠️  Agent UI not mounted")
        
    except Exception as e:
        print(f"❌ FastAPI app failed: {e}")
        return False
    
    print("\n🎉 All basic tests passed!")
    print("\n🚀 Start the application:")
    print("cd src && python main.py")
    
    return True

def load_env_from_file():
    """env.exampleからのサンプル環境変数読み込み"""
    env_file = Path("env.example")
    if not env_file.exists():
        return
    
    print("📄 env.exampleから環境変数のヒントを読み込み中...")
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line or '=' not in line:
                    continue
                
                key, value = line.split('=', 1)
                if key.endswith('_API_KEY') and not os.getenv(key):
                    print(f"💡 {key} が未設定です")
    except Exception as e:
        print(f"⚠️  env.example読み込みエラー: {e}")

def main():
    """メイン関数"""
    # 環境変数のヒント表示
    load_env_from_file()
    
    # クイックテスト実行
    success = quick_test()
    
    if not success:
        print("\n🔧 トラブルシューティング:")
        print("1. 依存関係をインストール: pip install -r src/requirements.txt")
        print("2. API キーを設定: export ANTHROPIC_API_KEY='your_key'")
        print("3. 詳細チェック: python check_agent_startup.py")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

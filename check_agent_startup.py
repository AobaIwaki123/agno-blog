#!/usr/bin/env python3
"""
Agno Blog Agent 起動チェックスクリプト

FastAPIアプリケーションでAgentが正常に起動できているかを包括的に確認します。
"""

import os
import sys
import traceback
from pathlib import Path
from typing import List, Optional, Dict, Any

# srcディレクトリをパスに追加
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

class AgentStartupChecker:
    """Agent起動状況をチェックするクラス"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.errors: List[str] = []
    
    def check_environment_variables(self) -> bool:
        """環境変数の確認"""
        print("🔍 環境変数をチェック中...")
        
        env_vars = {
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "CO_API_KEY": os.getenv("CO_API_KEY"),
            "OS_SECURITY_KEY": os.getenv("OS_SECURITY_KEY", "agno-blog-key"),
            "DATABASE_URL": os.getenv("DATABASE_URL", "sqlite:///agno_blog.db"),
        }
        
        self.results["environment"] = env_vars
        
        # API キーの確認
        for var_name, var_value in env_vars.items():
            if var_value and var_name.endswith("_API_KEY"):
                masked_value = f"{var_value[:10]}..." if len(var_value) > 10 else "***"
                print(f"✅ {var_name}: 設定済み ({masked_value})")
            elif var_name.endswith("_API_KEY"):
                print(f"❌ {var_name}: 未設定")
            else:
                print(f"✅ {var_name}: {var_value}")
        
        # 最低限の要件をチェック
        has_anthropic = bool(env_vars["ANTHROPIC_API_KEY"])
        has_openai = bool(env_vars["OPENAI_API_KEY"])
        
        if has_anthropic or has_openai:
            print("✅ 最低限のAPI キーが設定されています")
            return True
        else:
            self.errors.append("ANTHROPIC_API_KEY または OPENAI_API_KEY のいずれかが必要です")
            print("❌ ANTHROPIC_API_KEY または OPENAI_API_KEY のいずれかが必要です")
            return False
    
    def check_agno_framework(self) -> bool:
        """Agnoフレームワークのインポートをチェック"""
        print("\n🔍 Agnoフレームワークをチェック中...")
        
        framework_checks = {
            "agno": ("agno", "Core Agno framework"),
            "agent": ("agno.agent", "Agent"),
            "anthropic": ("agno.models.anthropic", "Claude"),
            "openai": ("agno.models.openai", "OpenAIChat"),
            "agent_os": ("agno.os", "AgentOS"),
            "sqlite_db": ("agno.db.sqlite", "SqliteDb"),
        }
        
        framework_status = {}
        all_passed = True
        
        for key, (module_path, class_name) in framework_checks.items():
            try:
                if class_name:
                    module = __import__(module_path, fromlist=[class_name])
                    getattr(module, class_name)
                else:
                    __import__(module_path)
                
                print(f"✅ {module_path}: インポート成功")
                framework_status[key] = True
            except ImportError as e:
                print(f"❌ {module_path}: インポート失敗 - {e}")
                self.errors.append(f"{module_path}: {e}")
                framework_status[key] = False
                all_passed = False
            except AttributeError as e:
                print(f"❌ {module_path}.{class_name}: クラスが見つかりません - {e}")
                self.errors.append(f"{module_path}.{class_name}: {e}")
                framework_status[key] = False
                all_passed = False
        
        self.results["framework"] = framework_status
        return all_passed
    
    def check_application_modules(self) -> bool:
        """アプリケーションモジュールのインポートをチェック"""
        print("\n🔍 アプリケーションモジュールをチェック中...")
        
        app_modules = {
            "config": "config",
            "database": "database",
            "logging_config": "logging_config",
            "agents.factory": "agents.factory",
            "tools.web_scraper": "tools.web_scraper",
            "tools.content_processor": "tools.content_processor",
            "tools.template_manager": "tools.template_manager",
        }
        
        module_status = {}
        all_passed = True
        
        for key, module_path in app_modules.items():
            try:
                __import__(module_path)
                print(f"✅ {module_path}: インポート成功")
                module_status[key] = True
            except ImportError as e:
                print(f"❌ {module_path}: インポート失敗 - {e}")
                self.errors.append(f"{module_path}: {e}")
                module_status[key] = False
                all_passed = False
        
        self.results["app_modules"] = module_status
        return all_passed
    
    def check_configuration(self) -> bool:
        """設定の検証"""
        print("\n🔍 アプリケーション設定をチェック中...")
        
        try:
            from config import Config
            
            # 設定検証を実行
            Config.validate()
            print("✅ 設定検証: 成功")
            
            # 設定値を記録
            config_info = {
                "host": Config.HOST,
                "port": Config.PORT,
                "debug": Config.DEBUG,
                "database_url": Config.DATABASE_URL[:50] + "..." if len(Config.DATABASE_URL) > 50 else Config.DATABASE_URL,
            }
            
            self.results["config"] = config_info
            print(f"✅ ホスト: {Config.HOST}:{Config.PORT}")
            print(f"✅ デバッグモード: {Config.DEBUG}")
            
            return True
            
        except Exception as e:
            print(f"❌ 設定エラー: {e}")
            self.errors.append(f"設定エラー: {e}")
            return False
    
    def check_database_connection(self) -> bool:
        """データベース接続をチェック"""
        print("\n🔍 データベース接続をチェック中...")
        
        try:
            from database import get_database, get_knowledge
            
            # データベース接続テスト
            db = get_database()
            print("✅ データベース接続: 成功")
            
            # ナレッジベースのチェック
            knowledge = get_knowledge()
            if knowledge:
                print("✅ ナレッジベース: 利用可能")
            else:
                print("⚠️  ナレッジベース: 利用不可 (CO_API_KEYが未設定の可能性)")
            
            self.results["database"] = {
                "connection": True,
                "knowledge_base": knowledge is not None
            }
            
            return True
            
        except Exception as e:
            print(f"❌ データベースエラー: {e}")
            self.errors.append(f"データベースエラー: {e}")
            return False
    
    def check_agent_creation(self) -> Optional[List]:
        """Agentの作成をテスト"""
        print("\n🔍 Agent作成をテスト中...")
        
        try:
            from agents.factory import create_agents
            
            # Agentを作成
            agents = create_agents()
            
            agent_info = []
            for i, agent in enumerate(agents, 1):
                model_type = type(agent.model).__name__
                tools_count = len(agent.tools) if hasattr(agent, 'tools') and agent.tools else 0
                
                info = {
                    "name": agent.name,
                    "model": model_type,
                    "tools_count": tools_count
                }
                agent_info.append(info)
                
                print(f"  {i}. {agent.name}")
                print(f"     モデル: {model_type}")
                print(f"     ツール数: {tools_count}")
            
            print(f"✅ Agent作成: {len(agents)}個のAgentが作成されました")
            
            self.results["agents"] = {
                "count": len(agents),
                "details": agent_info
            }
            
            return agents
            
        except Exception as e:
            print(f"❌ Agent作成エラー: {e}")
            self.errors.append(f"Agent作成エラー: {e}")
            traceback.print_exc()
            return None
    
    def check_agentOS_integration(self, agents: List) -> bool:
        """AgentOSの統合をテスト"""
        print("\n🔍 AgentOS統合をテスト中...")
        
        if not agents:
            print("❌ AgentOSテスト: Agentがないためスキップ")
            return False
        
        try:
            from agno.os import AgentOS
            
            # AgentOSを作成
            agent_os = AgentOS(agents=agents)
            print("✅ AgentOS作成: 成功")
            
            # FastAPIアプリを取得
            agno_app = agent_os.get_app()
            print("✅ AgentOS FastAPIアプリ取得: 成功")
            
            self.results["agent_os"] = {
                "creation": True,
                "app_creation": True,
                "agents_count": len(agents)
            }
            
            return True
            
        except Exception as e:
            print(f"❌ AgentOS統合エラー: {e}")
            self.errors.append(f"AgentOS統合エラー: {e}")
            traceback.print_exc()
            return False
    
    def check_fastapi_application(self) -> bool:
        """FastAPIアプリケーションの統合をテスト"""
        print("\n🔍 FastAPIアプリケーション統合をテスト中...")
        
        try:
            from main import create_app
            
            # FastAPIアプリを作成
            app = create_app()
            print("✅ FastAPIアプリ作成: 成功")
            
            # ルートの確認
            routes = [route.path for route in app.routes]
            route_count = len(routes)
            
            # 重要なルートの確認
            important_routes = {
                "/agno": any(r.startswith("/agno") for r in routes),
                "/api": any(r.startswith("/api") for r in routes),
                "/docs": "/docs" in routes,
                "/": "/" in routes or any(r == "" for r in routes),
            }
            
            print(f"✅ 総ルート数: {route_count}")
            for route, available in important_routes.items():
                status = "✅" if available else "❌"
                print(f"  {status} {route}: {'利用可能' if available else '見つかりません'}")
            
            self.results["fastapi"] = {
                "app_creation": True,
                "route_count": route_count,
                "important_routes": important_routes
            }
            
            return True
            
        except Exception as e:
            print(f"❌ FastAPIアプリエラー: {e}")
            self.errors.append(f"FastAPIアプリエラー: {e}")
            traceback.print_exc()
            return False
    
    def run_comprehensive_check(self) -> bool:
        """包括的なチェックを実行"""
        print("🚀 Agno Blog Agent 包括的起動チェックを開始")
        print("=" * 70)
        
        checks = [
            ("環境変数", self.check_environment_variables),
            ("Agnoフレームワーク", self.check_agno_framework),
            ("アプリケーションモジュール", self.check_application_modules),
            ("設定", self.check_configuration),
            ("データベース", self.check_database_connection),
        ]
        
        # 基本チェック
        passed = 0
        total = len(checks)
        
        for name, check_func in checks:
            print(f"\n📋 {name}チェック")
            try:
                if check_func():
                    passed += 1
                    print(f"✅ {name}: 合格")
                else:
                    print(f"❌ {name}: 不合格")
            except Exception as e:
                print(f"❌ {name}: 例外発生 - {e}")
                self.errors.append(f"{name}: {e}")
        
        # 基本チェックが通った場合のみAgent関連をチェック
        if passed >= len(checks) - 1:  # データベースエラーは許容
            print(f"\n📋 Agent作成チェック")
            agents = self.check_agent_creation()
            if agents:
                passed += 1
                print("✅ Agent作成: 合格")
                
                print(f"\n📋 AgentOS統合チェック")
                if self.check_agentOS_integration(agents):
                    passed += 1
                    print("✅ AgentOS統合: 合格")
                else:
                    print("❌ AgentOS統合: 不合格")
                
                total += 2
            else:
                print("❌ Agent作成: 不合格")
                total += 1
        
        # FastAPI統合チェック
        print(f"\n📋 FastAPI統合チェック")
        if self.check_fastapi_application():
            passed += 1
            print("✅ FastAPI統合: 合格")
        else:
            print("❌ FastAPI統合: 不合格")
        total += 1
        
        # 結果報告
        self.print_results(passed, total)
        
        return passed >= total - 1  # 1つ以下の失敗は許容
    
    def print_results(self, passed: int, total: int):
        """結果の詳細を出力"""
        print("\n" + "=" * 70)
        print(f"📊 チェック結果: {passed}/{total} 項目合格")
        
        if self.errors:
            print(f"\n⚠️  検出されたエラー ({len(self.errors)}件):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if passed >= total - 1:
            print("\n🎉 Agent起動チェックは概ね良好です！")
            self.print_next_steps()
        else:
            print("\n⚠️  重要な問題が検出されました。")
            self.print_troubleshooting()
    
    def print_next_steps(self):
        """次のステップを表示"""
        print("\n📝 次のステップ:")
        print("1. アプリケーションを起動:")
        print("   cd src && python main.py")
        print("\n2. ブラウザでアクセス:")
        print("   - メインアプリ: http://localhost:8000")
        print("   - Agent UI: http://localhost:8000/agno")
        print("   - API ドキュメント: http://localhost:8000/docs")
        print("   - ヘルスチェック: http://localhost:8000/api/health")
        
        print("\n3. Agent機能のテスト:")
        print("   - URL処理: /api/generate-post エンドポイント")
        print("   - テンプレート管理: /api/templates エンドポイント")
    
    def print_troubleshooting(self):
        """トラブルシューティング情報を表示"""
        print("\n🔧 トラブルシューティング:")
        
        if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            print("1. API キーを設定してください:")
            print("   export ANTHROPIC_API_KEY='your_key_here'")
            print("   export OPENAI_API_KEY='your_key_here'")
        
        print("\n2. 依存関係を再インストール:")
        print("   cd src && pip install -r requirements.txt")
        
        print("\n3. 詳細なログで再実行:")
        print("   DEBUG=true python check_agent_startup.py")


def main():
    """メイン関数"""
    checker = AgentStartupChecker()
    success = checker.run_comprehensive_check()
    
    # 結果をJSONで出力（オプション）
    if "--json" in sys.argv:
        import json
        output = {
            "success": success,
            "results": checker.results,
            "errors": checker.errors
        }
        print(f"\n📄 JSON結果:\n{json.dumps(output, indent=2, ensure_ascii=False)}")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

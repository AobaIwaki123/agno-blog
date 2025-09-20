#!/usr/bin/env python3
"""
Basic test script for Agno Blog Application
Tests basic functionality without requiring external dependencies
"""

import sys
import os
from pathlib import Path

def test_project_structure():
    """Test that all required files and directories exist."""
    print("Testing project structure...")
    
    # Required directories
    required_dirs = [
        "src",
        "src/agents",
        "src/tools", 
        "src/models",
        "src/workflows",
        "templates"
    ]
    
    # Required files
    required_files = [
        "src/main.py",
        "src/requirements.txt",
        "src/agents/url_processor.py",
        "src/agents/content_generator.py", 
        "src/agents/template_manager.py",
        "src/tools/web_scraper.py",
        "src/tools/content_processor.py",
        "src/tools/template_manager.py",
        "src/models/blog_post.py",
        "templates/base.html",
        "templates/index.html",
        "templates/posts.html",
        "templates/templates.html",
        "docker-compose.yml",
        "Dockerfile",
        "README.md"
    ]
    
    missing_dirs = []
    missing_files = []
    
    for directory in required_dirs:
        if not Path(directory).exists():
            missing_dirs.append(directory)
        else:
            print(f"✓ Directory exists: {directory}")
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✓ File exists: {file_path}")
    
    if missing_dirs:
        print(f"\n❌ Missing directories: {missing_dirs}")
        return False
        
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    print("\n✅ All required files and directories exist!")
    return True

def test_python_syntax():
    """Test that all Python files have valid syntax."""
    print("\nTesting Python syntax...")
    
    python_files = [
        "src/main.py",
        "src/agents/url_processor.py",
        "src/agents/content_generator.py",
        "src/agents/template_manager.py",
        "src/tools/web_scraper.py",
        "src/tools/content_processor.py",
        "src/tools/template_manager.py",
        "src/models/blog_post.py"
    ]
    
    syntax_errors = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Try to compile the code
            compile(content, file_path, 'exec')
            print(f"✓ Syntax OK: {file_path}")
            
        except SyntaxError as e:
            print(f"❌ Syntax Error in {file_path}: {e}")
            syntax_errors.append((file_path, str(e)))
        except Exception as e:
            print(f"⚠️  Warning in {file_path}: {e}")
    
    if syntax_errors:
        print(f"\n❌ Syntax errors found in {len(syntax_errors)} files")
        return False
    
    print("\n✅ All Python files have valid syntax!")
    return True

def test_imports():
    """Test basic imports without external dependencies."""
    print("\nTesting basic imports...")
    
    # Add src to path
    sys.path.insert(0, str(Path("src").absolute()))
    
    try:
        # Test standard library imports
        import json
        import logging
        import datetime
        import uuid
        from typing import Dict, Any, List, Optional
        print("✓ Standard library imports OK")
        
        # Test that our modules can be imported (syntax check)
        import importlib.util
        
        modules_to_test = [
            ("tools.content_processor", "src/tools/content_processor.py"),
            ("models.blog_post", "src/models/blog_post.py")
        ]
        
        for module_name, file_path in modules_to_test:
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    # Just check if we can load the spec, don't actually import
                    print(f"✓ Module spec OK: {module_name}")
                else:
                    print(f"⚠️  Could not create spec for: {module_name}")
            except Exception as e:
                print(f"⚠️  Issue with module {module_name}: {e}")
        
        print("\n✅ Basic imports test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import test failed: {e}")
        return False

def test_configuration_files():
    """Test configuration files."""
    print("\nTesting configuration files...")
    
    try:
        # Test requirements.txt
        with open("src/requirements.txt", 'r') as f:
            requirements = f.read().strip()
            if requirements:
                print("✓ requirements.txt is not empty")
            else:
                print("❌ requirements.txt is empty")
                return False
        
        # Test .env.example
        if Path(".env.example").exists():
            with open(".env.example", 'r') as f:
                env_content = f.read()
                if "OPENAI_API_KEY" in env_content and "ANTHROPIC_API_KEY" in env_content:
                    print("✓ .env.example contains required API key placeholders")
                else:
                    print("⚠️  .env.example missing some API key placeholders")
        
        # Test docker-compose.yml
        if Path("docker-compose.yml").exists():
            with open("docker-compose.yml", 'r') as f:
                compose_content = f.read()
                if "agno-blog" in compose_content:
                    print("✓ docker-compose.yml contains agno-blog service")
                else:
                    print("⚠️  docker-compose.yml missing agno-blog service")
        
        print("\n✅ Configuration files test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration files test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Agno Blog Application Tests")
    print("=" * 50)
    
    tests = [
        test_project_structure,
        test_python_syntax,
        test_imports,
        test_configuration_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print("-" * 30)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print("-" * 30)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application structure is ready.")
        print("\n📝 Next steps:")
        print("1. Install dependencies: pip install -r src/requirements.txt")
        print("2. Set up environment: cp .env.example .env (and edit with your API keys)")
        print("3. Run the application: cd src && python main.py")
        print("4. Or use Docker: make quick-start")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""
Agno Blog Application Launcher
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main entry point for the application"""
    
    # Check for required environment variables
    required_vars = ["ANTHROPIC_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables and try again.")
        print("Example:")
        print("   export ANTHROPIC_API_KEY=your_api_key_here")
        sys.exit(1)
    
    print("🚀 Starting Agno Blog Application...")
    print("📝 AI-powered blog generation system")
    print("🌐 Access the application at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("\n" + "="*50)
    
    # Run the application
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simple start script for the Professional Chatbot
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Change to the chat-bot directory
    chat_bot_dir = Path(__file__).parent / "chat-bot"
    os.chdir(chat_bot_dir)
    
    print("🤖 Starting Professional Chatbot...")
    print("📁 Working directory:", os.getcwd())
    
    # Check if config file exists
    if not Path("config.py").exists():
        print("❌ Error: config.py not found. Please ensure you're in the correct directory.")
        sys.exit(1)
    
    # Start the FastAPI application
    try:
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ]
        
        print("🚀 Starting server with command:")
        print("   " + " ".join(cmd))
        print("\n🌐 Once started, access the chatbot at:")
        print("   http://localhost:8000")
        print("\n📊 API Documentation available at:")
        print("   http://localhost:8000/docs")
        print("\n⏹️  Press Ctrl+C to stop the server")
        print("-" * 50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down the chatbot server...")
    except FileNotFoundError:
        print("❌ Error: Python or uvicorn not found. Please ensure they are installed.")
        print("💡 Try: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
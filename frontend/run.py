#!/usr/bin/env python3
"""
Simple runner script for the JustWork Streamlit frontend.
Run this script to start the Streamlit app.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the Streamlit application"""
    
    # Change to the frontend directory
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)
    
    print("🚀 Starting JustWork Streamlit Frontend...")
    print("📂 Frontend directory:", frontend_dir)
    print("🌐 App will be available at: http://localhost:8501")
    print("⚠️  Make sure the backend is running at: http://localhost:8000")
    print("=" * 60)
    
    try:
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "false",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Streamlit app...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

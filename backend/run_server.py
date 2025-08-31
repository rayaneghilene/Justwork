#!/usr/bin/env python3
"""
FastAPI Server Runner for JustWork Resume Analysis API

This script runs the FastAPI application server.

Usage:
    python run_server.py
    
Or from the backend directory:
    python -m backend.run_server
    
The server will be available at: http://localhost:8000
API documentation will be available at: http://localhost:8000/docs
"""

import uvicorn
from backend.app import app

def run_development_server():
    """Run the development server with auto-reload"""
    print("🚀 Starting JustWork Resume Analysis API server...")
    print("📊 Server will be available at: http://localhost:8000")
    print("📚 API documentation available at: http://localhost:8000/docs")
    print("📋 Alternative docs available at: http://localhost:8000/redoc")
    print("⏹️  Press CTRL+C to stop the server\n")
    
    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

def run_production_server():
    """Run the production server"""
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=8000,
        log_level="warning"
    )

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--production":
        run_production_server()
    else:
        run_development_server()

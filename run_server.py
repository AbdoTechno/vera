#!/usr/bin/env python
"""
VERA Clinical Intelligence Platform - Local API Server Runner
Usage:
    python run_server.py
    or:
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
"""

import uvicorn
import os
import sys

if __name__ == "__main__":
    print("=" * 65)
    print("  🏥 VERA Clinical Intelligence Platform - FastAPI Server")
    print("  🚀 Starting server on: http://localhost:8000")
    print("  📖 Interactive Swagger Docs: http://localhost:8000/docs")
    print("  🩺 Health Check: http://localhost:8000/api/v1/health")
    print("=" * 65)
    
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENV", "development").lower() == "development"
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload
    )

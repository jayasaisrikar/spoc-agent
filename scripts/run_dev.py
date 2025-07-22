#!/usr/bin/env python3
"""
Run the AI Code Architecture Agent in development mode
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import config
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting AI Code Architecture Agent in development mode...")
    uvicorn.run(
        "src.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="debug"
    )

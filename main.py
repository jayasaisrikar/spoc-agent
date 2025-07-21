#!/usr/bin/env python3
"""
Main entry point for the AI Code Architecture Agent
"""
import config  # This sets up the Python path
import uvicorn

def main():
    """Main entry point for the application"""
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()

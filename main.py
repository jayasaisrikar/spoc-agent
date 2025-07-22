#!/usr/bin/env python3
"""
Main entry point for the AI Code Architecture Agent with Agentic Capabilities
"""
import config  # This sets up the Python path
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application"""
    logger.info("🚀 Starting AI Code Architecture Agent with Agentic Capabilities")
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()

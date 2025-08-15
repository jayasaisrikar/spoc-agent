#!/usr/bin/env python3
"""
Main entry point for the AI Code Architecture Agent with Agentic Capabilities
"""
import config  # This sets up the Python path
import uvicorn
import logging
import sys
import os

# Import safe logging utilities
from src.utils.safe_logging import setup_windows_encoding, get_safe_logger, safe_log_message

# Configure logging with UTF-8 encoding for Windows
def setup_logging():
    """Setup logging with proper Unicode support for Windows"""
    # Force UTF-8 encoding for stdout/stderr on Windows
    if sys.platform.startswith('win'):
        # Set environment variable to force UTF-8 output
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Configure logging with UTF-8 encoding
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Ensure the handler uses UTF-8 encoding
        for handler in logging.root.handlers:
            if hasattr(handler.stream, 'reconfigure'):
                handler.stream.reconfigure(encoding='utf-8')
    else:
        # Standard logging configuration for non-Windows systems
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

# Initialize logging
setup_logging()

# Also try the Windows encoding setup
setup_windows_encoding()

logger = get_safe_logger(__name__)

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

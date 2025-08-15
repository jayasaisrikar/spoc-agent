"""
Utility module for safe Unicode logging on Windows systems
"""
import sys
import logging


def safe_log_message(message: str) -> str:
    """
    Convert Unicode characters to ASCII equivalents for Windows console compatibility
    
    Args:
        message: The original log message that may contain Unicode characters
        
    Returns:
        A safe version of the message with Unicode characters replaced
    """
    if sys.platform.startswith('win'):
        # Replace common Unicode characters with ASCII equivalents
        replacements = {
            '🚀': '[ROCKET]',
            '🤖': '[ROBOT]', 
            '✅': '[SUCCESS]',
            '⚠️': '[WARNING]',
            '❌': '[ERROR]',
            '🔍': '[SEARCH]',
            '📊': '[CHART]',
            '🎯': '[TARGET]',
            '💡': '[IDEA]',
            '🔧': '[TOOL]',
            '📝': '[NOTE]',
            '🌟': '[STAR]',
            '🔥': '[FIRE]',
            '⭐': '[STAR]',
            '🎉': '[CELEBRATION]',
            '📈': '[TRENDING_UP]',
            '📉': '[TRENDING_DOWN]',
            '🚨': '[ALERT]',
            '🎨': '[ART]',
            '🛠️': '[HAMMER_WRENCH]',
            '⚡': '[ZAP]',
            '🔄': '[ARROWS_COUNTERCLOCKWISE]',
            '👍': '[THUMBS_UP]',
            '👎': '[THUMBS_DOWN]',
            '🔐': '[LOCK]',
            '🔓': '[UNLOCK]'
        }
        
        for unicode_char, ascii_replacement in replacements.items():
            message = message.replace(unicode_char, ascii_replacement)
    
    return message


def get_safe_logger(name: str):
    """
    Get a logger that automatically handles Unicode characters safely
    
    Args:
        name: The logger name
        
    Returns:
        A logger instance with safe Unicode handling
    """
    logger = logging.getLogger(name)
    
    # Create a wrapper class that automatically applies safe_log_message
    class SafeLogger:
        def __init__(self, logger):
            self._logger = logger
            
        def debug(self, message, *args, **kwargs):
            self._logger.debug(safe_log_message(str(message)), *args, **kwargs)
            
        def info(self, message, *args, **kwargs):
            self._logger.info(safe_log_message(str(message)), *args, **kwargs)
            
        def warning(self, message, *args, **kwargs):
            self._logger.warning(safe_log_message(str(message)), *args, **kwargs)
            
        def error(self, message, *args, **kwargs):
            self._logger.error(safe_log_message(str(message)), *args, **kwargs)
            
        def critical(self, message, *args, **kwargs):
            self._logger.critical(safe_log_message(str(message)), *args, **kwargs)
            
        def exception(self, message, *args, **kwargs):
            self._logger.exception(safe_log_message(str(message)), *args, **kwargs)
    
    return SafeLogger(logger)


def setup_windows_encoding():
    """
    Setup proper encoding for Windows console to handle Unicode characters
    This should be called early in the application startup
    """
    if sys.platform.startswith('win'):
        import os
        
        # Set environment variables for UTF-8 support
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONUTF8'] = '1'
        
        # Try to set console code page to UTF-8
        try:
            import subprocess
            subprocess.run(['chcp', '65001'], capture_output=True, shell=True)
        except Exception:
            pass  # Ignore if chcp fails
            
        # Configure logging with UTF-8 encoding
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Try to reconfigure stream encoding
        try:
            for handler in logging.root.handlers:
                if hasattr(handler, 'stream') and hasattr(handler.stream, 'reconfigure'):
                    handler.stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass  # Ignore if reconfiguration fails

"""
Debug logging utility for Janitor Bot.
Writes debug messages to a timestamped log file.
"""

import os
from datetime import datetime
import threading

class DebugLogger:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DebugLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.log_dir = "logs"
            self.ensure_log_directory()
            self.log_file = self.create_log_file()
    
    def ensure_log_directory(self):
        """Create logs directory if it doesn't exist."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def create_log_file(self):
        """Create a new log file with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"janitor_debug_{timestamp}.txt"
        log_path = os.path.join(self.log_dir, log_filename)
        
        # Write initial header
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"=== Broom Bot Debug Log ===\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*50}\n\n")
        
        return log_path
    
    def log(self, message, module="GENERAL", level="DEBUG"):
        """Write a debug message to the log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        formatted_message = f"[{timestamp}] [{level}] [{module}] {message}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(formatted_message)
        except Exception as e:
            # Fallback to console if file write fails
            print(f"LOG ERROR: {e}")
            print(formatted_message.strip())
    
    def get_log_path(self):
        """Return the current log file path."""
        return self.log_file

# Global logger instance
_logger = DebugLogger()

def debug_log(message, module="GENERAL", level="DEBUG"):
    """Convenience function for logging debug messages."""
    _logger.log(message, module, level)

def get_current_log_file():
    """Get the path to the current log file."""
    return _logger.get_log_path()
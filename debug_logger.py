import logging
import os
import sys
from datetime import datetime

class DebugLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DebugLogger, cls).__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Create timestamp for log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"logs/puddle_debug_{timestamp}.log"
        
        # Configure logging
        self.logger = logging.getLogger('PuddleDebug')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(log_filename, mode='w')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"=== PUDDLE DEBUG LOG STARTED ===")
        self.logger.info(f"Log file: {log_filename}")
    
    def log_function_entry(self, function_name, module_name="", **kwargs):
        """Log when entering a function"""
        args_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()]) if kwargs else ""
        self.logger.debug(f"ENTERING: {module_name}.{function_name}({args_str})")
    
    def log_function_exit(self, function_name, module_name="", return_value=None):
        """Log when exiting a function"""
        if return_value is not None:
            self.logger.debug(f"EXITING: {module_name}.{function_name} -> {return_value}")
        else:
            self.logger.debug(f"EXITING: {module_name}.{function_name}")
    
    def log_info(self, message, module_name=""):
        """Log info message"""
        self.logger.info(f"[{module_name}] {message}")
    
    def log_warning(self, message, module_name=""):
        """Log warning message"""
        self.logger.warning(f"[{module_name}] {message}")
    
    def log_error(self, message, module_name="", exc_info=None):
        """Log error message"""
        self.logger.error(f"[{module_name}] {message}", exc_info=exc_info)
    
    def log_debug(self, message, module_name=""):
        """Log debug message"""
        self.logger.debug(f"[{module_name}] {message}")

# Global logger instance
debug_logger = DebugLogger()

def log_function(func):
    """Decorator to automatically log function entry/exit"""
    def wrapper(*args, **kwargs):
        module_name = func.__module__.split('.')[-1] if func.__module__ else ""
        debug_logger.log_function_entry(func.__name__, module_name, **kwargs)
        try:
            result = func(*args, **kwargs)
            debug_logger.log_function_exit(func.__name__, module_name, result)
            return result
        except Exception as e:
            debug_logger.log_error(f"Exception in {func.__name__}: {str(e)}", module_name, exc_info=True)
            raise
    return wrapper 
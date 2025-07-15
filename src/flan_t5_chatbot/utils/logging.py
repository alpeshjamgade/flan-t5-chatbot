"""
Logging utilities for FLAN-T5 ChatBot with colored output
"""

import logging
import sys
import os
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
        'BOLD': '\033[1m',        # Bold
        'DIM': '\033[2m',         # Dim
    }
    
    def __init__(self, fmt=None, datefmt=None, use_colors=True):
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors and self._supports_color()
    
    def _supports_color(self) -> bool:
        """Check if terminal supports colors"""
        return (
            hasattr(sys.stdout, "isatty") and 
            sys.stdout.isatty() and 
            os.environ.get("TERM") != "dumb"
        )
    
    def format(self, record):
        if self.use_colors:
            # Add color to the log level
            levelname = record.levelname
            if levelname in self.COLORS:
                colored_levelname = f"{self.COLORS[levelname]}{self.COLORS['BOLD']}{levelname}{self.COLORS['RESET']}"
                record.levelname = colored_levelname
            
            # Color the logger name
            if hasattr(record, 'name'):
                record.name = f"{self.COLORS['DIM']}{record.name}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging(level: str = "INFO", debug: bool = False, no_color: bool = False) -> logging.Logger:
    """Setup logging configuration with colors"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Set level
    if debug:
        level = "DEBUG"
    
    log_level = getattr(logging, level.upper())
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_formatter = ColoredFormatter(
        '%(levelname)s %(name)s: %(message)s',
        use_colors=not no_color
    )
    
    # File handler (no colors for file)
    file_handler = logging.FileHandler(log_dir / 'chatbot.log')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler (with colors if supported)
    if debug:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # Get main logger
    logger = logging.getLogger('flan_t5_chatbot')
    logger.info(f"Logging initialized at level: {level}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module"""
    # Remove the package prefix for cleaner names
    clean_name = name.replace('flan_t5_chatbot.', '')
    return logging.getLogger(f'flan_t5_chatbot.{clean_name}')

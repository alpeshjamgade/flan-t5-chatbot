"""
Helper utility functions
"""

import re
import platform
from typing import Any


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def validate_input(text: str, max_length: int = 1000) -> bool:
    """Validate user input"""
    if not text or not text.strip():
        return False
    
    if len(text) > max_length:
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = "untitled"
    
    return filename


def get_system_info() -> dict:
    """Get system information"""
    try:
        import psutil
        
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "cpu_count": psutil.cpu_count()
        }
    except ImportError:
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }


class ProgressBar:
    """Simple progress bar for terminal"""
    
    def __init__(self, total: int, width: int = 50):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, progress: int):
        """Update progress bar"""
        self.current = progress
        percent = (self.current / self.total) * 100
        filled = int(self.width * self.current // self.total)
        bar = '█' * filled + '-' * (self.width - filled)
        
        print(f'\r|{bar}| {percent:.1f}% Complete', end='', flush=True)
        
        if self.current >= self.total:
            print()  # New line when complete

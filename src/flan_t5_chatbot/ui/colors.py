"""
ANSI color codes for terminal output
"""

import os
import sys


class Colors:
    """ANSI color codes for terminal output"""
    
    # Check if colors should be enabled
    @staticmethod
    def _should_use_colors():
        """Determine if colors should be used"""
        # Force colors if FORCE_COLOR is set
        if os.environ.get('FORCE_COLOR', '').lower() in ('1', 'true', 'yes'):
            return True
        
        # Disable colors if NO_COLOR is set
        if os.environ.get('NO_COLOR', ''):
            return False
        
        # Check for common color-supporting environments
        if os.environ.get('COLORTERM'):
            return True
        
        # Check for specific terminals that support colors
        term = os.environ.get('TERM', '').lower()
        if any(t in term for t in ['color', 'xterm', 'screen', 'tmux', 'ansi']):
            return True
        
        # Check for IDEs that support colors
        if any(var in os.environ for var in ['PYCHARM_HOSTED', 'VSCODE_PID', 'TERM_PROGRAM']):
            return True
        
        # Check if stdout is a TTY (traditional check)
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            return True
        
        # Default to True for most cases (be more permissive)
        return True
    
    # Initialize colors based on detection
    _colors_enabled = _should_use_colors()
    
    if _colors_enabled:
        RESET = '\033[0m'
        BOLD = '\033[1m'
        DIM = '\033[2m'
        
        # Foreground colors
        BLACK = '\033[30m'
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        MAGENTA = '\033[35m'
        CYAN = '\033[36m'
        WHITE = '\033[37m'
        
        # Bright colors
        BRIGHT_RED = '\033[91m'
        BRIGHT_GREEN = '\033[92m'
        BRIGHT_YELLOW = '\033[93m'
        BRIGHT_BLUE = '\033[94m'
        BRIGHT_MAGENTA = '\033[95m'
        BRIGHT_CYAN = '\033[96m'
        BRIGHT_WHITE = '\033[97m'
        
        # Background colors
        BG_BLACK = '\033[40m'
        BG_RED = '\033[41m'
        BG_GREEN = '\033[42m'
        BG_YELLOW = '\033[43m'
        BG_BLUE = '\033[44m'
        BG_MAGENTA = '\033[45m'
        BG_CYAN = '\033[46m'
        BG_WHITE = '\033[47m'
    else:
        # No colors - all empty strings
        RESET = BOLD = DIM = ''
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ''
        BRIGHT_RED = BRIGHT_GREEN = BRIGHT_YELLOW = BRIGHT_BLUE = ''
        BRIGHT_MAGENTA = BRIGHT_CYAN = BRIGHT_WHITE = ''
        BG_BLACK = BG_RED = BG_GREEN = BG_YELLOW = BG_BLUE = ''
        BG_MAGENTA = BG_CYAN = BG_WHITE = ''
    
    @classmethod
    def disable_colors(cls):
        """Disable all colors by setting them to empty strings"""
        cls._colors_enabled = False
        cls.RESET = cls.BOLD = cls.DIM = ''
        cls.BLACK = cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = ''
        cls.MAGENTA = cls.CYAN = cls.WHITE = ''
        cls.BRIGHT_RED = cls.BRIGHT_GREEN = cls.BRIGHT_YELLOW = ''
        cls.BRIGHT_BLUE = cls.BRIGHT_MAGENTA = cls.BRIGHT_CYAN = cls.BRIGHT_WHITE = ''
        cls.BG_BLACK = cls.BG_RED = cls.BG_GREEN = cls.BG_YELLOW = ''
        cls.BG_BLUE = cls.BG_MAGENTA = cls.BG_CYAN = cls.BG_WHITE = ''
    
    @classmethod
    def enable_colors(cls):
        """Force enable all colors"""
        cls._colors_enabled = True
        cls.RESET = '\033[0m'
        cls.BOLD = '\033[1m'
        cls.DIM = '\033[2m'
        cls.BLACK = '\033[30m'
        cls.RED = '\033[31m'
        cls.GREEN = '\033[32m'
        cls.YELLOW = '\033[33m'
        cls.BLUE = '\033[34m'
        cls.MAGENTA = '\033[35m'
        cls.CYAN = '\033[36m'
        cls.WHITE = '\033[37m'
        cls.BRIGHT_RED = '\033[91m'
        cls.BRIGHT_GREEN = '\033[92m'
        cls.BRIGHT_YELLOW = '\033[93m'
        cls.BRIGHT_BLUE = '\033[94m'
        cls.BRIGHT_MAGENTA = '\033[95m'
        cls.BRIGHT_CYAN = '\033[96m'
        cls.BRIGHT_WHITE = '\033[97m'
        cls.BG_BLACK = '\033[40m'
        cls.BG_RED = '\033[41m'
        cls.BG_GREEN = '\033[42m'
        cls.BG_YELLOW = '\033[43m'
        cls.BG_BLUE = '\033[44m'
        cls.BG_MAGENTA = '\033[45m'
        cls.BG_CYAN = '\033[46m'
        cls.BG_WHITE = '\033[47m'
    
    @classmethod
    def status(cls):
        """Print color status for debugging"""
        print(f"Colors enabled: {cls._colors_enabled}")
        print(f"FORCE_COLOR: {os.environ.get('FORCE_COLOR', 'Not set')}")
        print(f"NO_COLOR: {os.environ.get('NO_COLOR', 'Not set')}")
        print(f"COLORTERM: {os.environ.get('COLORTERM', 'Not set')}")
        print(f"TERM: {os.environ.get('TERM', 'Not set')}")
        print(f"stdout.isatty(): {hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()}")
        
        # Test colors
        if cls._colors_enabled:
            print(f"{cls.RED}RED{cls.RESET} {cls.GREEN}GREEN{cls.RESET} {cls.BLUE}BLUE{cls.RESET}")
        else:
            print("Colors are disabled")

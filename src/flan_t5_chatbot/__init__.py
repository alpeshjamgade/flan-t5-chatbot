"""
FLAN-T5 ChatBot - A sophisticated shell-based chat interface
"""

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "1.0.0"

__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "A sophisticated shell-based chat interface using Google's FLAN-T5-Large model"

from .core.chat_engine import ChatEngine
from .core.conversation_manager import ConversationManager
from .ui.manager import UIManager
from .config.settings import Config

__all__ = [
    "ChatEngine",
    "ConversationManager", 
    "UIManager",
    "Config",
    "__version__",
]

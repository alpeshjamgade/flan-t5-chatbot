"""
Data models for FLAN-T5 ChatBot
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Message:
    """Represents a single message in a conversation"""
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    metadata: Dict = None


@dataclass
class Conversation:
    """Represents a complete conversation"""
    id: str
    title: str
    messages: List[Message]
    created_at: str
    updated_at: str
    metadata: Dict = None

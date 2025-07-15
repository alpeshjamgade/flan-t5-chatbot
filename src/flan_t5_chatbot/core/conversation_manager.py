"""
Conversation Manager - Handle conversation history and context with Redis support
"""

import json
import uuid
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from .models import Message, Conversation
from ..utils.logging import get_logger
from ..data.redis_store import RedisConversationStore
from ..data.file_store import FileConversationStore


class ConversationManager:
    """Manages conversations and message history with Redis support"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.conversations: Dict[str, Conversation] = {}
        
        # Initialize storage backend
        self.storage = None
        if config.use_redis:
            try:
                self.storage = RedisConversationStore(config)
                self.logger.info("Using Redis for conversation storage")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Redis storage: {e}")
                self.logger.info("Falling back to file storage")
                self.storage = FileConversationStore(config)
        else:
            self.storage = FileConversationStore(config)
            self.logger.info("Using file storage for conversations")
    
    def create_conversation(self, title: str = None) -> str:
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        if not title:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        conversation = Conversation(
            id=conversation_id,
            title=title,
            messages=[],
            created_at=timestamp,
            updated_at=timestamp
        )
        
        self.conversations[conversation_id] = conversation
        
        # Save to storage
        self.storage.save_conversation(conversation)
        
        self.logger.info(f"Created new conversation: {conversation_id}")
        return conversation_id
    
    def add_message(self, conversation_id: str, role: str, content: str, metadata: Dict = None) -> str:
        """Add a message to a conversation"""
        if conversation_id not in self.conversations:
            # Try to load from storage
            conversation = self.storage.load_conversation(conversation_id)
            if conversation:
                self.conversations[conversation_id] = conversation
            else:
                raise ValueError(f"Conversation {conversation_id} not found")
        
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        message = Message(
            id=message_id,
            role=role,
            content=content,
            timestamp=timestamp,
            metadata=metadata or {}
        )
        
        self.conversations[conversation_id].messages.append(message)
        self.conversations[conversation_id].updated_at = timestamp
        
        # Save to storage
        self.storage.save_conversation(self.conversations[conversation_id])
        
        self.logger.debug(f"Added {role} message to conversation {conversation_id}")
        return message_id
    
    def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        """Get all messages from a conversation"""
        if conversation_id not in self.conversations:
            # Try to load from storage
            conversation = self.storage.load_conversation(conversation_id)
            if conversation:
                self.conversations[conversation_id] = conversation
            else:
                return []
        
        return self.conversations[conversation_id].messages
    
    def get_conversation_context(self, conversation_id: str, max_messages: int = None) -> List[Dict]:
        """Get conversation context for AI model"""
        if max_messages is None:
            max_messages = self.config.conversation.max_context_messages
            
        messages = self.get_conversation_messages(conversation_id)
        
        # Get recent messages for context
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
        
        # Convert to simple dict format
        context = []
        for msg in recent_messages:
            context.append({
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            })
        
        return context
    
    def save_conversation(self, conversation_id: str, filename: str = None) -> bool:
        """Save a conversation (legacy method for compatibility)"""
        if conversation_id not in self.conversations:
            return False
        
        return self.storage.save_conversation(self.conversations[conversation_id])
    
    def load_conversation(self, conversation_id: str) -> bool:
        """Load a conversation from storage"""
        conversation = self.storage.load_conversation(conversation_id)
        if conversation:
            self.conversations[conversation.id] = conversation
            self.logger.info(f"Loaded conversation: {conversation_id}")
            return True
        return False
    
    def list_conversations(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List all conversations"""
        return self.storage.list_conversations(limit, offset)
    
    def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        """Search conversations"""
        return self.storage.search_conversations(query, limit)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        # Remove from memory
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
        
        # Remove from storage
        success = self.storage.delete_conversation(conversation_id)
        
        if success:
            self.logger.info(f"Deleted conversation: {conversation_id}")
        
        return success
    
    def get_conversation_summary(self, conversation_id: str) -> str:
        """Get a summary of the conversation"""
        if conversation_id not in self.conversations:
            conversation = self.storage.load_conversation(conversation_id)
            if conversation:
                self.conversations[conversation_id] = conversation
            else:
                return "Conversation not found"
        
        conv = self.conversations[conversation_id]
        message_count = len(conv.messages)
        
        if message_count == 0:
            return f"Empty conversation created at {conv.created_at}"
        
        last_message_time = conv.messages[-1].timestamp if conv.messages else conv.created_at
        
        return f"{conv.title} - {message_count} messages, last activity: {last_message_time}"
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        return self.storage.get_conversation_stats()
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """Clean up old conversations"""
        return self.storage.cleanup_old_conversations(days)

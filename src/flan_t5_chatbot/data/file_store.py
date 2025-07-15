"""
File-based conversation storage (fallback when Redis is not available)
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import asdict
from pathlib import Path

from ..core.models import Message, Conversation
from ..utils.logging import get_logger


class FileConversationStore:
    """File-based conversation storage"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.data_dir = Path(config.conversation.save_directory)
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the conversations directory exists"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger.debug(f"Conversations directory: {self.data_dir}")
    
    def save_conversation(self, conversation: Conversation) -> bool:
        """Save conversation to file"""
        try:
            filename = f"conversation_{conversation.id}.json"
            filepath = self.data_dir / filename
            
            # Convert to serializable format
            data = {
                "conversation": asdict(conversation),
                "export_timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved conversation {conversation.id} to file")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving conversation to file: {e}")
            return False
    
    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Load conversation from file"""
        try:
            filename = f"conversation_{conversation_id}.json"
            filepath = self.data_dir / filename
            
            if not filepath.exists():
                self.logger.warning(f"Conversation file not found: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            conversation_data = data["conversation"]
            
            # Reconstruct messages
            messages = []
            for msg_data in conversation_data["messages"]:
                message = Message(**msg_data)
                messages.append(message)
            
            # Reconstruct conversation
            conversation = Conversation(
                id=conversation_data["id"],
                title=conversation_data["title"],
                messages=messages,
                created_at=conversation_data["created_at"],
                updated_at=conversation_data["updated_at"],
                metadata=conversation_data.get("metadata")
            )
            
            self.logger.debug(f"Loaded conversation {conversation_id} from file")
            return conversation
            
        except Exception as e:
            self.logger.error(f"Error loading conversation from file: {e}")
            return None
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation file"""
        try:
            filename = f"conversation_{conversation_id}.json"
            filepath = self.data_dir / filename
            
            if filepath.exists():
                filepath.unlink()
                self.logger.info(f"Deleted conversation file {filepath}")
                return True
            else:
                self.logger.warning(f"Conversation file not found: {filepath}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting conversation file: {e}")
            return False
    
    def list_conversations(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List conversations from files"""
        try:
            conversations = []
            
            # Get all conversation files
            pattern = "conversation_*.json"
            files = list(self.data_dir.glob(pattern))
            
            for filepath in files:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    conv_data = data["conversation"]
                    conversations.append({
                        "id": conv_data["id"],
                        "title": conv_data["title"],
                        "message_count": len(conv_data["messages"]),
                        "created_at": conv_data["created_at"],
                        "updated_at": conv_data["updated_at"]
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Error reading conversation file {filepath}: {e}")
                    continue
            
            # Sort by updated_at (most recent first)
            conversations.sort(key=lambda x: x["updated_at"], reverse=True)
            
            # Apply pagination
            return conversations[offset:offset + limit]
            
        except Exception as e:
            self.logger.error(f"Error listing conversations from files: {e}")
            return []
    
    def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        """Search conversations in files"""
        try:
            query_lower = query.lower()
            matching_conversations = []
            
            # Get all conversation files
            pattern = "conversation_*.json"
            files = list(self.data_dir.glob(pattern))
            
            for filepath in files:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    conv_data = data["conversation"]
                    
                    # Search in title
                    title_match = query_lower in conv_data["title"].lower()
                    
                    # Search in message content
                    content_match = False
                    for message in conv_data["messages"]:
                        if query_lower in message["content"].lower():
                            content_match = True
                            break
                    
                    if title_match or content_match:
                        matching_conversations.append({
                            "id": conv_data["id"],
                            "title": conv_data["title"],
                            "message_count": len(conv_data["messages"]),
                            "created_at": conv_data["created_at"],
                            "updated_at": conv_data["updated_at"]
                        })
                    
                except Exception as e:
                    self.logger.warning(f"Error searching conversation file {filepath}: {e}")
                    continue
            
            # Sort by updated_at and limit results
            matching_conversations.sort(key=lambda x: x["updated_at"], reverse=True)
            return matching_conversations[:limit]
            
        except Exception as e:
            self.logger.error(f"Error searching conversations in files: {e}")
            return []
    
    def get_conversation_stats(self) -> Dict:
        """Get statistics about stored conversations"""
        try:
            pattern = "conversation_*.json"
            files = list(self.data_dir.glob(pattern))
            
            total_size = sum(f.stat().st_size for f in files)
            
            return {
                "total_conversations": len(files),
                "storage_size_bytes": total_size,
                "storage_size_mb": round(total_size / (1024 * 1024), 2),
                "storage_directory": str(self.data_dir)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting conversation stats: {e}")
            return {}
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """Clean up conversations older than specified days"""
        try:
            cutoff_timestamp = datetime.now().timestamp() - (days * 24 * 60 * 60)
            pattern = "conversation_*.json"
            files = list(self.data_dir.glob(pattern))
            
            deleted_count = 0
            for filepath in files:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    conv_data = data["conversation"]
                    updated_at = conv_data["updated_at"]
                    
                    conv_timestamp = datetime.fromisoformat(updated_at).timestamp()
                    if conv_timestamp < cutoff_timestamp:
                        filepath.unlink()
                        deleted_count += 1
                        
                except Exception as e:
                    self.logger.warning(f"Error processing file {filepath}: {e}")
                    continue
            
            self.logger.info(f"Cleaned up {deleted_count} old conversation files")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old conversations: {e}")
            return 0

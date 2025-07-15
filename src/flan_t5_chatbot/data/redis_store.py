"""
Redis-based conversation storage with search capabilities
"""

import json
import uuid
import redis
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import asdict
import hashlib

from ..core.models import Message, Conversation
from ..utils.logging import get_logger


class RedisConversationStore:
    """Redis-based conversation storage with search capabilities"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            redis_config = self.config.redis
            self.redis_client = redis.Redis(
                host=redis_config.host,
                port=redis_config.port,
                db=redis_config.db,
                password=redis_config.password,
                decode_responses=redis_config.decode_responses,
                socket_timeout=redis_config.socket_timeout,
                socket_connect_timeout=redis_config.socket_connect_timeout,
                retry_on_timeout=redis_config.retry_on_timeout,
                health_check_interval=redis_config.health_check_interval
            )
            
            # Test connection
            self.redis_client.ping()
            self.logger.info("Connected to Redis successfully")
            
            # Initialize search index if it doesn't exist
            self._initialize_search_index()
            
        except redis.ConnectionError as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            raise
        except Exception as e:
            self.logger.error(f"Redis initialization error: {e}")
            self.redis_client = None
            raise
    
    def _initialize_search_index(self):
        """Initialize Redis search index for conversations"""
        try:
            # Check if RediSearch is available
            info = self.redis_client.execute_command("MODULE", "LIST")
            has_search = any("search" in str(module).lower() for module in info)
            
            if has_search:
                # Create search index for conversations
                try:
                    self.redis_client.execute_command(
                        "FT.CREATE", "conversations_idx",
                        "ON", "HASH",
                        "PREFIX", "1", "conversation:",
                        "SCHEMA",
                        "title", "TEXT", "WEIGHT", "2.0",
                        "content", "TEXT", "WEIGHT", "1.0",
                        "created_at", "NUMERIC", "SORTABLE",
                        "updated_at", "NUMERIC", "SORTABLE",
                        "message_count", "NUMERIC", "SORTABLE"
                    )
                    self.logger.info("Created Redis search index for conversations")
                except redis.ResponseError as e:
                    if "Index already exists" not in str(e):
                        self.logger.warning(f"Could not create search index: {e}")
            else:
                self.logger.warning("RediSearch module not available - search functionality will be limited")
                
        except Exception as e:
            self.logger.warning(f"Could not initialize search index: {e}")
    
    def is_connected(self) -> bool:
        """Check if Redis connection is active"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def save_conversation(self, conversation: Conversation) -> bool:
        """Save conversation to Redis"""
        if not self.is_connected():
            self.logger.error("Redis not connected")
            return False
        
        try:
            conversation_key = f"conversation:{conversation.id}"
            
            # Prepare conversation data
            conversation_data = asdict(conversation)
            
            # Create searchable content from messages
            content_parts = []
            for message in conversation.messages:
                content_parts.append(f"{message.role}: {message.content}")
            searchable_content = " ".join(content_parts)
            
            # Store main conversation data
            self.redis_client.hset(conversation_key, mapping={
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
                "message_count": len(conversation.messages),
                "content": searchable_content[:5000],  # Limit content for search
                "data": json.dumps(conversation_data)
            })
            
            # Store individual messages for detailed retrieval
            for i, message in enumerate(conversation.messages):
                message_key = f"message:{conversation.id}:{i}"
                self.redis_client.hset(message_key, mapping={
                    "conversation_id": conversation.id,
                    "message_index": i,
                    "id": message.id,
                    "role": message.role,
                    "content": message.content,
                    "timestamp": message.timestamp,
                    "metadata": json.dumps(message.metadata or {})
                })
            
            # Add to conversation list
            self.redis_client.sadd("conversations", conversation.id)
            
            # Set expiration (optional - 30 days)
            self.redis_client.expire(conversation_key, 30 * 24 * 60 * 60)
            
            self.logger.debug(f"Saved conversation {conversation.id} to Redis")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving conversation to Redis: {e}")
            return False
    
    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Load conversation from Redis"""
        if not self.is_connected():
            self.logger.error("Redis not connected")
            return None
        
        try:
            conversation_key = f"conversation:{conversation_id}"
            
            # Check if conversation exists
            if not self.redis_client.exists(conversation_key):
                self.logger.warning(f"Conversation {conversation_id} not found in Redis")
                return None
            
            # Get conversation data
            conversation_data = self.redis_client.hget(conversation_key, "data")
            if not conversation_data:
                return None
            
            # Parse conversation data
            data = json.loads(conversation_data)
            
            # Reconstruct messages
            messages = []
            for msg_data in data["messages"]:
                message = Message(**msg_data)
                messages.append(message)
            
            # Reconstruct conversation
            conversation = Conversation(
                id=data["id"],
                title=data["title"],
                messages=messages,
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                metadata=data.get("metadata")
            )
            
            self.logger.debug(f"Loaded conversation {conversation_id} from Redis")
            return conversation
            
        except Exception as e:
            self.logger.error(f"Error loading conversation from Redis: {e}")
            return None
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation from Redis"""
        if not self.is_connected():
            self.logger.error("Redis not connected")
            return False
        
        try:
            conversation_key = f"conversation:{conversation_id}"
            
            # Get message count to delete individual messages
            message_count = self.redis_client.hget(conversation_key, "message_count")
            if message_count:
                message_count = int(message_count)
                # Delete individual messages
                for i in range(message_count):
                    message_key = f"message:{conversation_id}:{i}"
                    self.redis_client.delete(message_key)
            
            # Delete main conversation
            self.redis_client.delete(conversation_key)
            
            # Remove from conversation list
            self.redis_client.srem("conversations", conversation_id)
            
            self.logger.info(f"Deleted conversation {conversation_id} from Redis")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting conversation from Redis: {e}")
            return False
    
    def list_conversations(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List conversations with pagination"""
        if not self.is_connected():
            self.logger.error("Redis not connected")
            return []
        
        try:
            # Get all conversation IDs
            conversation_ids = list(self.redis_client.smembers("conversations"))
            
            conversations = []
            for conv_id in conversation_ids[offset:offset + limit]:
                conversation_key = f"conversation:{conv_id}"
                conv_info = self.redis_client.hmget(
                    conversation_key,
                    "id", "title", "created_at", "updated_at", "message_count"
                )
                
                if all(conv_info):
                    conversations.append({
                        "id": conv_info[0],
                        "title": conv_info[1],
                        "created_at": conv_info[2],
                        "updated_at": conv_info[3],
                        "message_count": int(conv_info[4]) if conv_info[4] else 0
                    })
            
            # Sort by updated_at (most recent first)
            conversations.sort(key=lambda x: x["updated_at"], reverse=True)
            
            return conversations
            
        except Exception as e:
            self.logger.error(f"Error listing conversations from Redis: {e}")
            return []
    
    def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        """Search conversations using Redis search"""
        if not self.is_connected():
            self.logger.error("Redis not connected")
            return []
        
        try:
            # Try using RediSearch if available
            try:
                search_query = f"@title:({query}) | @content:({query})"
                results = self.redis_client.execute_command(
                    "FT.SEARCH", "conversations_idx", search_query,
                    "LIMIT", "0", str(limit),
                    "SORTBY", "updated_at", "DESC"
                )
                
                conversations = []
                # Parse search results (skip count at index 0)
                for i in range(1, len(results), 2):
                    if i + 1 < len(results):
                        conv_key = results[i]
                        conv_data = results[i + 1]
                        
                        # Convert list to dict
                        data_dict = {}
                        for j in range(0, len(conv_data), 2):
                            if j + 1 < len(conv_data):
                                data_dict[conv_data[j]] = conv_data[j + 1]
                        
                        conversations.append({
                            "id": data_dict.get("id", ""),
                            "title": data_dict.get("title", ""),
                            "created_at": data_dict.get("created_at", ""),
                            "updated_at": data_dict.get("updated_at", ""),
                            "message_count": int(data_dict.get("message_count", 0))
                        })
                
                return conversations
                
            except redis.ResponseError:
                # Fallback to manual search if RediSearch not available
                return self._manual_search(query, limit)
                
        except Exception as e:
            self.logger.error(f"Error searching conversations in Redis: {e}")
            return []
    
    def _manual_search(self, query: str, limit: int) -> List[Dict]:
        """Manual search fallback when RediSearch is not available"""
        try:
            query_lower = query.lower()
            conversation_ids = list(self.redis_client.smembers("conversations"))
            
            matching_conversations = []
            for conv_id in conversation_ids:
                conversation_key = f"conversation:{conv_id}"
                conv_data = self.redis_client.hmget(
                    conversation_key,
                    "id", "title", "content", "created_at", "updated_at", "message_count"
                )
                
                if all(conv_data[:2]):  # At least id and title exist
                    title = conv_data[1].lower()
                    content = (conv_data[2] or "").lower()
                    
                    if query_lower in title or query_lower in content:
                        matching_conversations.append({
                            "id": conv_data[0],
                            "title": conv_data[1],
                            "created_at": conv_data[3] or "",
                            "updated_at": conv_data[4] or "",
                            "message_count": int(conv_data[5]) if conv_data[5] else 0
                        })
            
            # Sort by updated_at and limit results
            matching_conversations.sort(key=lambda x: x["updated_at"], reverse=True)
            return matching_conversations[:limit]
            
        except Exception as e:
            self.logger.error(f"Error in manual search: {e}")
            return []
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get statistics about stored conversations"""
        if not self.is_connected():
            return {}
        
        try:
            total_conversations = self.redis_client.scard("conversations")
            
            # Get memory usage info
            memory_info = self.redis_client.info("memory")
            
            return {
                "total_conversations": total_conversations,
                "redis_memory_used": memory_info.get("used_memory_human", "Unknown"),
                "redis_connected_clients": self.redis_client.info("clients").get("connected_clients", 0),
                "redis_version": self.redis_client.info("server").get("redis_version", "Unknown")
            }
            
        except Exception as e:
            self.logger.error(f"Error getting conversation stats: {e}")
            return {}
    
    def cleanup_old_conversations(self, days: int = 30) -> int:
        """Clean up conversations older than specified days"""
        if not self.is_connected():
            return 0
        
        try:
            cutoff_timestamp = datetime.now().timestamp() - (days * 24 * 60 * 60)
            conversation_ids = list(self.redis_client.smembers("conversations"))
            
            deleted_count = 0
            for conv_id in conversation_ids:
                conversation_key = f"conversation:{conv_id}"
                updated_at = self.redis_client.hget(conversation_key, "updated_at")
                
                if updated_at:
                    try:
                        conv_timestamp = datetime.fromisoformat(updated_at).timestamp()
                        if conv_timestamp < cutoff_timestamp:
                            if self.delete_conversation(conv_id):
                                deleted_count += 1
                    except ValueError:
                        # Skip conversations with invalid timestamps
                        continue
            
            self.logger.info(f"Cleaned up {deleted_count} old conversations")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old conversations: {e}")
            return 0

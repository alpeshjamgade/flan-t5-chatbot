"""
Configuration management for FLAN-T5 ChatBot
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from ..utils.logging import get_logger


@dataclass
class ModelConfig:
    """Model configuration"""
    name: str = "google/flan-t5-large"
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.2
    do_sample: bool = True


@dataclass
class UIConfig:
    """UI configuration"""
    show_timestamps: bool = True
    word_wrap: bool = True
    colors_enabled: bool = True
    typing_indicator: bool = True


@dataclass
class ConversationConfig:
    """Conversation configuration"""
    max_context_messages: int = 10
    auto_save: bool = False
    save_directory: str = "conversations"


@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    decode_responses: bool = True
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    health_check_interval: int = 30


class Config:
    """Main configuration class"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.logger = get_logger(__name__)
        
        # Initialize with defaults
        self.model = ModelConfig()
        self.ui = UIConfig()
        self.conversation = ConversationConfig()
        self.redis = RedisConfig()
        self.log_level = "INFO"
        self.use_redis = True
        
        # Load configuration if file exists
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Update model config
                if 'model' in config_data:
                    for key, value in config_data['model'].items():
                        if hasattr(self.model, key):
                            setattr(self.model, key, value)
                
                # Update UI config
                if 'ui' in config_data:
                    for key, value in config_data['ui'].items():
                        if hasattr(self.ui, key):
                            setattr(self.ui, key, value)
                
                # Update conversation config
                if 'conversation' in config_data:
                    for key, value in config_data['conversation'].items():
                        if hasattr(self.conversation, key):
                            setattr(self.conversation, key, value)
                
                # Update Redis config
                if 'redis' in config_data:
                    for key, value in config_data['redis'].items():
                        if hasattr(self.redis, key):
                            setattr(self.redis, key, value)
                
                # Update other settings
                if 'log_level' in config_data:
                    self.log_level = config_data['log_level']
                
                if 'use_redis' in config_data:
                    self.use_redis = config_data['use_redis']
                
                self.logger.info(f"Loaded configuration from {self.config_path}")
                    
            except Exception as e:
                self.logger.warning(f"Could not load config file: {e}")
                self.logger.info("Using default configuration")
        else:
            self.logger.info("Config file not found, using defaults")
            self.save_config()  # Create default config file
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config_data = {
                'model': asdict(self.model),
                'ui': asdict(self.ui),
                'conversation': asdict(self.conversation),
                'redis': asdict(self.redis),
                'log_level': self.log_level,
                'use_redis': self.use_redis
            }
            
            # Ensure parent directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info(f"Saved configuration to {self.config_path}")
                
        except Exception as e:
            self.logger.warning(f"Could not save config file: {e}")
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration as dictionary"""
        return {
            'model': asdict(self.model),
            'ui': asdict(self.ui),
            'conversation': asdict(self.conversation),
            'redis': asdict(self.redis),
            'log_level': self.log_level,
            'use_redis': self.use_redis
        }
    
    def update_config(self, **kwargs):
        """Update configuration values"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                if isinstance(getattr(self, key), (ModelConfig, UIConfig, ConversationConfig, RedisConfig)):
                    # Update nested config
                    config_obj = getattr(self, key)
                    for nested_key, nested_value in value.items():
                        if hasattr(config_obj, nested_key):
                            setattr(config_obj, nested_key, nested_value)
                else:
                    setattr(self, key, value)
        
        self.save_config()

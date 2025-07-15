"""
Main application class for FLAN-T5 ChatBot
"""

import signal
import sys
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

import torch

from .core.chat_engine import ChatEngine
from .core.conversation_manager import ConversationManager
from .ui.manager import UIManager
from .config.settings import Config
from .utils.logging import get_logger


@dataclass
class AppState:
    """Application state management"""
    current_conversation_id: Optional[str] = None
    is_running: bool = True
    debug_mode: bool = False
    model_loaded: bool = False


class FlanT5ChatBot:
    """Main application class"""

    def __init__(self, config_path: str = "config.json", debug_mode: bool = False, no_color: bool = False):
        self.config = Config(config_path)
        self.state = AppState(debug_mode=debug_mode)
        self.logger = get_logger(__name__)

        # Initialize components
        self.ui = UIManager(self.config, no_color=no_color)
        self.conversation_manager = ConversationManager(self.config)
        self.chat_engine = None

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)

    def _handle_interrupt(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        self.ui.print_info("\n\nGracefully shutting down...")
        self.state.is_running = False
        if self.chat_engine:
            self.chat_engine.cleanup()
        sys.exit(0)

    def initialize(self) -> bool:
        """Initialize the chat engine and load model"""
        self.ui.print_header()
        self.ui.print_info("Initializing FLAN-T5-Large model...")

        try:
            self.chat_engine = ChatEngine(self.config)
            self.ui.show_loading("Loading model", self.chat_engine.load_model)
            self.state.model_loaded = True
            self.ui.print_success("Model loaded successfully!")
            self.logger.info("Model initialized successfully")

            # Show storage info
            storage_stats = self.conversation_manager.get_storage_stats()
            if storage_stats:
                if 'redis_version' in storage_stats:
                    self.ui.print_info(f"Using Redis storage (v{storage_stats['redis_version']})")
                else:
                    self.ui.print_info("Using file storage")

            # Show device and system info
            device_info = self.chat_engine.device
            if device_info.type == "mps":
                self.ui.print_success("Using Metal Performance Shaders (Apple Silicon acceleration)")
            elif device_info.type == "cuda":
                gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "Unknown"
                self.ui.print_success(f"Using CUDA GPU: {gpu_name}")
            else:
                self.ui.print_info("Using CPU (no GPU acceleration)")

            return True

        except Exception as e:
            self.ui.print_error(f"Failed to initialize model: {str(e)}")
            self.logger.error(f"Model initialization failed: {str(e)}")
            return False

    def run(self):
        """Main application loop"""
        if not self.initialize():
            return

        self.ui.print_welcome_message()
        self.ui.print_help()

        # Start new conversation
        conversation_id = self.conversation_manager.create_conversation()
        self.state.current_conversation_id = conversation_id
        self.logger.info(f"Started new conversation: {conversation_id}")

        while self.state.is_running:
            try:
                user_input = self.ui.get_user_input()

                if not user_input.strip():
                    continue

                # Handle special commands
                if self._handle_command(user_input):
                    continue

                # Process chat message
                self._process_chat_message(user_input)

            except KeyboardInterrupt:
                self._handle_interrupt(None, None)
            except Exception as e:
                self.ui.print_error(f"An error occurred: {str(e)}")
                self.logger.error(f"Runtime error: {str(e)}")
                if self.state.debug_mode:
                    import traceback
                    traceback.print_exc()

    def _handle_command(self, user_input: str) -> bool:
        """Handle special commands"""
        command = user_input.strip().lower()

        command_handlers = {
            ('/help', '/h'): self.ui.print_help,
            ('/clear', '/c'): self.ui.clear_screen,
            ('/new', '/n'): self._start_new_conversation,
            ('/history', '/hist'): self._show_conversation_history,
            ('/save', '/s'): self._save_conversation,
            ('/load', '/l'): self._load_conversation,
            ('/list',): self._list_conversations,
            ('/search',): self._search_conversations,
            ('/stats',): self._show_stats,
            ('/cleanup',): self._cleanup_conversations,
            ('/debug',): self._toggle_debug,
            ('/quit', '/q', '/exit'): self._quit_application,
            ('/colors',): self.ui.show_color_status,
            ('/sysinfo',): self._show_system_info,
        }

        for commands, handler in command_handlers.items():
            if command in commands:
                if command in ('/quit', '/q', '/exit'):
                    handler()
                else:
                    handler()
                return True

        # Handle commands with parameters
        if command.startswith('/search '):
            query = user_input[8:].strip()
            self._search_conversations(query)
            return True

        return False

    def _process_chat_message(self, user_input: str):
        """Process a chat message"""
        if not self.state.current_conversation_id:
            self.ui.print_error("No active conversation")
            return

        # Add user message to conversation
        self.conversation_manager.add_message(
            self.state.current_conversation_id,
            "user",
            user_input
        )

        # Show typing indicator
        self.ui.show_typing_indicator()

        try:
            # Get conversation context
            context = self.conversation_manager.get_conversation_context(
                self.state.current_conversation_id
            )

            # Generate response
            response = self.chat_engine.generate_response(user_input, context)

            # Stop typing indicator
            self.ui.stop_typing_indicator()

            # Display response
            self.ui.print_assistant_response(response)

            # Add assistant response to conversation
            self.conversation_manager.add_message(
                self.state.current_conversation_id,
                "assistant",
                response
            )

            self.logger.debug(f"Processed message exchange in conversation {self.state.current_conversation_id}")

        except Exception as e:
            self.ui.stop_typing_indicator()
            self.ui.print_error(f"Failed to generate response: {str(e)}")
            self.logger.error(f"Response generation failed: {str(e)}")

    def _start_new_conversation(self):
        """Start a new conversation"""
        conversation_id = self.conversation_manager.create_conversation()
        self.state.current_conversation_id = conversation_id
        self.ui.print_success("Started new conversation")
        self.logger.info(f"Started new conversation: {conversation_id}")

    def _show_conversation_history(self):
        """Show conversation history"""
        if not self.state.current_conversation_id:
            self.ui.print_error("No active conversation")
            return

        messages = self.conversation_manager.get_conversation_messages(
            self.state.current_conversation_id
        )
        self.ui.display_conversation_history(messages)

    def _save_conversation(self):
        """Save current conversation"""
        if not self.state.current_conversation_id:
            self.ui.print_error("No active conversation to save")
            return

        if self.conversation_manager.save_conversation(self.state.current_conversation_id):
            self.ui.print_success("Conversation saved successfully")
            self.logger.info("Conversation saved")
        else:
            self.ui.print_error("Failed to save conversation")

    def _load_conversation(self):
        """Load a conversation"""
        conversations = self.conversation_manager.list_conversations(limit=10)
        if not conversations:
            self.ui.print_info("No saved conversations found")
            return

        self.ui.print_info("Recent conversations:")
        for i, conv in enumerate(conversations, 1):
            self.ui.print_info(f"{i}. {conv['title']} ({conv['message_count']} messages)")

        try:
            choice = input("Enter conversation number to load (or press Enter to cancel): ").strip()
            if choice and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(conversations):
                    conv_id = conversations[idx]['id']
                    if self.conversation_manager.load_conversation(conv_id):
                        self.state.current_conversation_id = conv_id
                        self.ui.print_success(f"Loaded conversation: {conversations[idx]['title']}")
                    else:
                        self.ui.print_error("Failed to load conversation")
                else:
                    self.ui.print_error("Invalid conversation number")
        except ValueError:
            self.ui.print_error("Invalid input")

    def _list_conversations(self):
        """List all conversations"""
        conversations = self.conversation_manager.list_conversations(limit=20)
        if not conversations:
            self.ui.print_info("No conversations found")
            return

        self.ui.print_info(f"Found {len(conversations)} conversations:")
        for conv in conversations:
            updated = datetime.fromisoformat(conv['updated_at']).strftime("%Y-%m-%d %H:%M")
            self.ui.print_info(f"• {conv['title']} ({conv['message_count']} messages, updated: {updated})")

    def _search_conversations(self, query: str = None):
        """Search conversations"""
        if not query:
            query = input("Enter search query: ").strip()

        if not query:
            self.ui.print_error("Search query cannot be empty")
            return

        results = self.conversation_manager.search_conversations(query, limit=10)
        if not results:
            self.ui.print_info(f"No conversations found matching '{query}'")
            return

        self.ui.print_info(f"Found {len(results)} conversations matching '{query}':")
        for result in results:
            updated = datetime.fromisoformat(result['updated_at']).strftime("%Y-%m-%d %H:%M")
            self.ui.print_info(f"• {result['title']} ({result['message_count']} messages, updated: {updated})")

    def _show_stats(self):
        """Show storage statistics"""
        stats = self.conversation_manager.get_storage_stats()
        if not stats:
            self.ui.print_error("Could not retrieve statistics")
            return

        self.ui.print_info("Storage Statistics:")
        for key, value in stats.items():
            formatted_key = key.replace('_', ' ').title()
            self.ui.print_info(f"• {formatted_key}: {value}")

    def _cleanup_conversations(self):
        """Clean up old conversations"""
        if self.ui.confirm_action("Delete conversations older than 30 days?"):
            deleted_count = self.conversation_manager.cleanup_old_conversations(30)
            self.ui.print_success(f"Cleaned up {deleted_count} old conversations")

    def _toggle_debug(self):
        """Toggle debug mode"""
        self.state.debug_mode = not self.state.debug_mode
        self.ui.print_info(f"Debug mode: {'ON' if self.state.debug_mode else 'OFF'}")

    def _quit_application(self):
        """Quit the application"""
        self.state.is_running = False

    def _show_system_info(self):
        """Show system information"""
        import platform

        self.ui.print_info("System Information:")
        self.ui.print_info(f"• Platform: {platform.system()} {platform.release()}")
        self.ui.print_info(f"• Architecture: {platform.machine()}")
        self.ui.print_info(f"• Python: {platform.python_version()}")

        if self.chat_engine:
            device = self.chat_engine.device
            self.ui.print_info(f"• AI Device: {device}")

            if device.type == "cuda":
                import torch
                if torch.cuda.is_available():
                    self.ui.print_info(f"• GPU: {torch.cuda.get_device_name(0)}")
                    self.ui.print_info(f"• CUDA Version: {torch.version.cuda}")
            elif device.type == "mps":
                self.ui.print_info("• Metal Performance Shaders: Available")

        # Storage info
        storage_stats = self.conversation_manager.get_storage_stats()
        if 'redis_version' in storage_stats:
            self.ui.print_info(f"• Redis: v{storage_stats['redis_version']}")
        else:
            self.ui.print_info("• Storage: File-based")

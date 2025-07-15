"""
UI Manager - Handle all user interface interactions
"""

import os
import sys
import time
import threading
from typing import List
import shutil
from datetime import datetime

from .colors import Colors
from ..utils.logging import get_logger
from .. import __version__


class UIManager:
    """Manages all user interface interactions"""
    
    def __init__(self, config, no_color: bool = False):
        self.config = config
        self.logger = get_logger(__name__)
        self.terminal_width = self._get_terminal_width()
        self.typing_active = False
        self.typing_thread = None
        
        # Handle color settings
        if no_color:
            Colors.disable_colors()
        else:
            # Force enable colors if not already enabled
            if not Colors._colors_enabled:
                Colors.enable_colors()
        
        # Debug: Print color status
        print(f"🎨 UI Manager - Colors enabled: {Colors._colors_enabled}")
        if Colors._colors_enabled:
            print(f"{Colors.GREEN}✅ Colors should be working{Colors.RESET}")
        else:
            print("❌ Colors are disabled")
    
    def _get_terminal_width(self) -> int:
        """Get terminal width"""
        try:
            return shutil.get_terminal_size().columns
        except:
            return 80
    
    def _supports_color(self) -> bool:
        """Check if terminal supports colors"""
        return Colors._colors_enabled
    
    def print_header(self):
        """Print application header"""
        header = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            FLAN-T5 ChatBot v{__version__:<8}                        ║
║                     Intelligent Shell-Based Assistant                       ║
║                        Powered by Google FLAN-T5-Large                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(f"{Colors.BRIGHT_CYAN}{header}{Colors.RESET}")
    
    def print_welcome_message(self):
        """Print welcome message"""
        welcome = f"""
{Colors.BRIGHT_GREEN}Welcome to FLAN-T5 ChatBot!{Colors.RESET}

This is an intelligent conversational AI powered by Google's FLAN-T5-Large model.
I'm here to help you with questions, tasks, and engaging conversations.

{Colors.YELLOW}Features:{Colors.RESET}
• Intelligent conversation with context awareness
• Conversation history and management with Redis search
• Save, load, and search conversations
• Multiple conversation threads
• Smart response generation

{Colors.CYAN}Type your message and press Enter to start chatting!{Colors.RESET}
Type {Colors.BOLD}/help{Colors.RESET} for available commands.
        """
        print(welcome)
    
    def print_help(self):
        """Print help information"""
        help_text = f"""
{Colors.BRIGHT_YELLOW}Available Commands:{Colors.RESET}

{Colors.BOLD}Chat Commands:{Colors.RESET}
  {Colors.GREEN}/help, /h{Colors.RESET}      - Show this help message
  {Colors.GREEN}/clear, /c{Colors.RESET}     - Clear the screen
  {Colors.GREEN}/new, /n{Colors.RESET}       - Start a new conversation
  {Colors.GREEN}/quit, /q, /exit{Colors.RESET} - Exit the application

{Colors.BOLD}Conversation Management:{Colors.RESET}
  {Colors.GREEN}/history, /hist{Colors.RESET} - Show current conversation history
  {Colors.GREEN}/save, /s{Colors.RESET}       - Save current conversation
  {Colors.GREEN}/load, /l{Colors.RESET}       - Load a saved conversation
  {Colors.GREEN}/list{Colors.RESET}           - List all conversations
  {Colors.GREEN}/search [query]{Colors.RESET} - Search conversations
  {Colors.GREEN}/stats{Colors.RESET}          - Show storage statistics
  {Colors.GREEN}/cleanup{Colors.RESET}        - Clean up old conversations

{Colors.BOLD}System:{Colors.RESET}
  {Colors.GREEN}/debug{Colors.RESET}          - Toggle debug mode
  {Colors.GREEN}/colors{Colors.RESET}         - Show color status
  {Colors.GREEN}/sysinfo{Colors.RESET}        - Show system information

{Colors.DIM}Simply type your message to chat with the AI assistant.{Colors.RESET}
{Colors.DIM}Example: /search "machine learning" to find related conversations{Colors.RESET}
        """
        print(help_text)
    
    def get_user_input(self) -> str:
        """Get user input with a nice prompt"""
        try:
            prompt = f"{Colors.BRIGHT_BLUE}You:{Colors.RESET} "
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return "/quit"
    
    def print_assistant_response(self, response: str):
        """Print assistant response with formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n{Colors.BRIGHT_GREEN}Assistant{Colors.RESET} {Colors.DIM}({timestamp}):{Colors.RESET}")
        
        # Word wrap the response
        wrapped_response = self._wrap_text(response, self.terminal_width - 4)
        
        for line in wrapped_response.split('\n'):
            print(f"  {line}")
        
        print()  # Add spacing
    
    def print_info(self, message: str):
        """Print info message"""
        print(f"{Colors.CYAN}ℹ {message}{Colors.RESET}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{Colors.BRIGHT_GREEN}✓ {message}{Colors.RESET}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"{Colors.BRIGHT_RED}✗ {message}{Colors.RESET}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{Colors.BRIGHT_YELLOW}⚠ {message}{Colors.RESET}")
    
    def show_loading(self, message: str, task_func):
        """Show loading animation while executing a task"""
        loading_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        loading_active = True
        
        def loading_animation():
            i = 0
            while loading_active:
                char = loading_chars[i % len(loading_chars)]
                print(f"\r{Colors.CYAN}{char} {message}...{Colors.RESET}", end='', flush=True)
                time.sleep(0.1)
                i += 1
        
        # Start loading animation
        loading_thread = threading.Thread(target=loading_animation)
        loading_thread.daemon = True
        loading_thread.start()
        
        try:
            # Execute the task
            result = task_func()
            loading_active = False
            loading_thread.join(timeout=0.5)
            print(f"\r{' ' * (len(message) + 10)}\r", end='')  # Clear loading line
            return result
        except Exception as e:
            loading_active = False
            loading_thread.join(timeout=0.5)
            print(f"\r{' ' * (len(message) + 10)}\r", end='')  # Clear loading line
            raise e
    
    def show_typing_indicator(self):
        """Show typing indicator"""
        if self.typing_active:
            return
        
        self.typing_active = True
        
        def typing_animation():
            dots = 0
            while self.typing_active:
                dot_str = '.' * (dots % 4)
                print(f"\r{Colors.DIM}Assistant is typing{dot_str}{' ' * (3 - len(dot_str))}{Colors.RESET}", end='', flush=True)
                time.sleep(0.5)
                dots += 1
        
        self.typing_thread = threading.Thread(target=typing_animation)
        self.typing_thread.daemon = True
        self.typing_thread.start()
    
    def stop_typing_indicator(self):
        """Stop typing indicator"""
        if self.typing_active:
            self.typing_active = False
            if self.typing_thread:
                self.typing_thread.join(timeout=1)
            print(f"\r{' ' * 30}\r", end='')  # Clear typing line
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_header()
    
    def display_conversation_history(self, messages: List):
        """Display conversation history"""
        if not messages:
            self.print_info("No messages in current conversation")
            return
        
        print(f"\n{Colors.BRIGHT_YELLOW}Conversation History:{Colors.RESET}")
        print("=" * 50)
        
        for i, msg in enumerate(messages, 1):
            timestamp = datetime.fromisoformat(msg.timestamp).strftime("%H:%M:%S")
            role_color = Colors.BRIGHT_BLUE if msg.role == "user" else Colors.BRIGHT_GREEN
            role_name = "You" if msg.role == "user" else "Assistant"
            
            print(f"\n{Colors.BOLD}{i}.{Colors.RESET} {role_color}{role_name}{Colors.RESET} {Colors.DIM}({timestamp}):{Colors.RESET}")
            
            # Word wrap the content
            wrapped_content = self._wrap_text(msg.content, self.terminal_width - 4)
            for line in wrapped_content.split('\n'):
                print(f"   {line}")
        
        print("\n" + "=" * 50)
    
    def _wrap_text(self, text: str, width: int) -> str:
        """Wrap text to specified width"""
        if len(text) <= width:
            return text
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def confirm_action(self, message: str) -> bool:
        """Ask for user confirmation"""
        response = input(f"{Colors.YELLOW}{message} (y/N): {Colors.RESET}").strip().lower()
        return response in ['y', 'yes']
    
    def show_color_status(self):
        """Show color status for debugging"""
        Colors.status()

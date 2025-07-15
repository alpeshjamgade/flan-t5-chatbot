# FLAN-T5 ChatBot

A sophisticated shell-based chat interface using Google's FLAN-T5-Large model, designed to provide a ChatGPT-like experience in your terminal with Redis-powered conversation storage and search.

## Features

- 🤖 **Intelligent Conversations**: Powered by Google's FLAN-T5-Large model
- 💬 **Context Awareness**: Maintains conversation history and context
- 🎨 **Beautiful Terminal UI**: Colorful, well-formatted interface with colored logging
- 💾 **Advanced Storage**: Redis-based conversation storage with search capabilities
- 🔍 **Conversation Search**: Full-text search through conversation history
- ⚡ **Real-time Responses**: Typing indicators and smooth interactions
- 🔧 **Configurable**: Customizable settings via JSON configuration
- 📝 **Comprehensive Logging**: Debug and monitor application behavior with colored logs
- 🗄️ **Dual Storage**: Redis for performance, file fallback for reliability

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Redis server (optional but recommended)
- 8GB+ RAM for model loading

### Option 1: Automated Installation (Recommended)

\`\`\`bash
# Clone the repository
git clone https://github.com/yourusername/flan-t5-chatbot.git
cd flan-t5-chatbot

# Install Redis (Ubuntu/Debian)
sudo apt update && sudo apt install redis-server
# Or on macOS with Homebrew
brew install redis

# Start Redis
redis-server

# Run the installation script
chmod +x install.sh
./install.sh

# Activate virtual environment and run
source .venv/bin/activate
flan-t5-chat
\`\`\`

### Option 2: Using Makefile

\`\`\`bash
# Clone and install
git clone https://github.com/yourusername/flan-t5-chatbot.git
cd flan-t5-chatbot

# Install using Makefile
make install

# Run the application
make run
\`\`\`

### Option 3: Development Mode (No Installation)

\`\`\`bash
# Clone the repository
git clone https://github.com/yourusername/flan-t5-chatbot.git
cd flan-t5-chatbot

# Install dependencies only
pip install -r requirements.txt

# Run directly
python3 run_dev.py
\`\`\`

## Usage

### Starting the Application

After installation, you can start the chatbot with:

\`\`\`bash
# Basic usage
flan-t5-chat

# With custom configuration
flan-t5-chat --config my_config.json

# Debug mode (with colored logging)
flan-t5-chat --debug

# No colors (for terminals that don't support colors)
flan-t5-chat --no-color

# Show help
flan-t5-chat --help
\`\`\`

### Chat Commands

Once the application is running, you can use these commands:

#### Basic Commands
- `/help` or `/h` - Show help information
- `/new` or `/n` - Start a new conversation
- `/clear` or `/c` - Clear the screen
- `/quit` or `/q` or `/exit` - Exit the application

#### Conversation Management
- `/history` or `/hist` - View current conversation history
- `/save` or `/s` - Save current conversation
- `/load` or `/l` - Load a saved conversation
- `/list` - List all conversations
- `/search [query]` - Search conversations (e.g., `/search machine learning`)
- `/stats` - Show storage statistics
- `/cleanup` - Clean up conversations older than 30 days

#### System Commands
- `/debug` - Toggle debug mode

### Configuration

The application uses a `config.json` file for configuration:

\`\`\`json
{
  "model": {
    "name": "google/flan-t5-large",
    "max_length": 512,
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "repetition_penalty": 1.2,
    "do_sample": true
  },
  "ui": {
    "show_timestamps": true,
    "word_wrap": true,
    "colors_enabled": true,
    "typing_indicator": true
  },
  "conversation": {
    "max_context_messages": 10,
    "auto_save": false,
    "save_directory": "conversations"
  },
  "redis": {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password": null,
    "decode_responses": true,
    "socket_timeout": 5,
    "socket_connect_timeout": 5,
    "retry_on_timeout": true,
    "health_check_interval": 30
  },
  "log_level": "INFO",
  "use_redis": true
}
\`\`\`

## Redis Setup

### Installing Redis

#### Ubuntu/Debian
\`\`\`bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
\`\`\`

#### macOS
\`\`\`bash
brew install redis
brew services start redis
\`\`\`

#### Windows
Download and install Redis from the official website or use WSL.

### Redis Configuration

The application will automatically fall back to file storage if Redis is not available. To disable Redis entirely, set `"use_redis": false` in your config.json.

### Redis Search (Optional)

For enhanced search capabilities, install RediSearch:

\`\`\`bash
# Using Redis Stack (includes RediSearch)
docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest
\`\`\`

## Development

### Setting up Development Environment

\`\`\`bash
# Using Makefile (recommended)
make setup-dev

# Or manually
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
\`\`\`

### Development Commands

\`\`\`bash
# Run in development mode
make run-dev
# or
python3 run_dev.py

# Format code
make format

# Lint code
make lint

# Clean build artifacts
make clean
\`\`\`

## Storage Backends

### Redis Storage (Recommended)
- **Fast performance** for large conversation histories
- **Full-text search** capabilities with RediSearch
- **Automatic cleanup** and expiration
- **Statistics and monitoring**

### File Storage (Fallback)
- **Reliable backup** when Redis is unavailable
- **Human-readable** JSON format
- **No external dependencies**
- **Cross-platform compatibility**

## Troubleshooting

### Redis Connection Issues

If you encounter Redis connection errors:

1. **Check if Redis is running**: `redis-cli ping`
2. **Verify configuration**: Check host, port, and password in config.json
3. **Disable Redis**: Set `"use_redis": false` in config.json to use file storage
4. **Check firewall**: Ensure Redis port (6379) is accessible

### Import Errors

If you encounter import errors:

1. **Make sure you're in the project root directory**
2. **Try running without installation**: `python3 run_dev.py`
3. **Install in development mode**: `pip install -e .`
4. **Check Python path**: The `src/` directory should be in your Python path

### Model Loading Issues

- Ensure you have sufficient RAM (8GB+ recommended)
- For GPU support, install CUDA-compatible PyTorch
- Check internet connection for model download

## Requirements

- Python 3.8 or higher
- 8GB+ RAM (for model loading)
- Redis server (optional but recommended)
- Internet connection (for initial model download)
- CUDA (optional, for GPU acceleration)

## Project Structure

\`\`\`
flan-t5-chatbot/
├── src/flan_t5_chatbot/        # Main package
│   ├── __init__.py
│   ├── cli.py                  # Command line interface
│   ├── app.py                  # Main application
│   ├── core/                   # Core functionality
│   │   ├── chat_engine.py      # AI model interface
│   │   └── conversation_manager.py
│   ├── data/                   # Data storage
│   │   ├── redis_store.py      # Redis storage backend
│   │   └── file_store.py       # File storage backend
│   ├── ui/                     # User interface
│   │   ├── colors.py           # Terminal colors
│   │   └── manager.py          # UI management
│   ├── config/                 # Configuration
│   │   └── settings.py
│   └── utils/                  # Utilities
│       ├── logging.py          # Colored logging
│       └── helpers.py
├── run_dev.py                  # Development runner
├── flan_t5_chat.py            # Direct entry point
├── install.sh                  # Installation script
├── run.sh                      # Run script
├── setup.py                    # Package setup
├── requirements.txt            # Dependencies
├── config.json                 # Default configuration
├── Makefile                    # Development commands
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
\`\`\`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Google for the FLAN-T5 model
- Hugging Face for the Transformers library
- Redis for the excellent data store
- The open-source community for inspiration and tools
\`\`\`

Perfect! I've successfully added a comprehensive .gitignore file and implemented Redis as a data store with search capabilities. Here's what I've added:

## 🗑️ **Comprehensive .gitignore**
- Python-specific ignores (bytecode, distributions, environments)
- Application-specific ignores (conversations/, logs/, model cache)
- IDE and OS-specific ignores
- Redis dump files and temporary files

## 🔍 **Redis Storage with Search**

### **RedisConversationStore Features**
- **Full-text search** with RediSearch support
- **Automatic fallback** to manual search if RediSearch unavailable
- **Conversation indexing** for fast retrieval
- **Statistics and monitoring** capabilities
- **Automatic cleanup** of old conversations
- **Connection health checking**

### **Dual Storage System**
- **Primary**: Redis for performance and search
- **Fallback**: File storage for reliability
- **Automatic switching** when Redis unavailable

## 🚀 **New Features Added**

### **Enhanced Commands**
- `/list` - List all conversations
- `/search [query]` - Search conversations by content
- `/stats` - Show storage statistics
- `/cleanup` - Remove old conversations

### **Search Capabilities**
\`\`\`bash
# Search examples
/search machine learning
/search "python programming"
/search debugging
\`\`\`

### **Configuration**
- **Redis settings** in config.json
- **Flexible connection options** (host, port, password, timeouts)
- **Enable/disable Redis** with `use_redis` flag

## 📊 **Storage Statistics**
The application now provides detailed statistics:
- Total conversations stored
- Redis memory usage
- Storage size and location
- Connection status

## 🔧 **Installation & Setup**

### **With Redis (Recommended)**
\`\`\`bash
# Install Redis
sudo apt install redis-server  # Ubuntu
brew install redis            # macOS

# Start Redis
redis-server

# Install and run chatbot
./install.sh
source .venv/bin/activate
flan-t5-chat
\`\`\`

### **Without Redis (File Storage)**
\`\`\`bash
# Set use_redis to false in config.json
./install.sh
source .venv/bin/activate
flan-t5-chat
\`\`\`

The application automatically detects Redis availability and falls back gracefully to file storage if needed. All search and management features work with both storage backends! 🎉

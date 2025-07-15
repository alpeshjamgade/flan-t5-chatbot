#!/bin/bash

# FLAN-T5 ChatBot Installation Script

set -e

echo "🤖 Installing FLAN-T5 ChatBot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install PyTorch first (CPU version for compatibility)
echo "🔥 Installing PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
echo "📥 Installing other dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "📦 Installing FLAN-T5 ChatBot..."
pip install -e .

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p conversations logs

# Test installation
echo "🧪 Testing installation..."
python3 -c "import flan_t5_chatbot; print('✅ Package installed successfully')" || {
    echo "❌ Package installation test failed"
    exit 1
}

echo "✅ Installation complete!"
echo ""
echo "🚀 To run the chatbot:"
echo "   Method 1 (Recommended - after installation):"
echo "     source .venv/bin/activate"
echo "     flan-t5-chat"
echo ""
echo "   Method 2 (Development - without installation):"
echo "     source .venv/bin/activate"
echo "     python3 run_dev.py"
echo ""
echo "   Method 3 (Direct):"
echo "     source .venv/bin/activate"
echo "     python3 flan_t5_chat.py"
echo ""
echo "📖 For help: flan-t5-chat --help"
echo "🐛 For debug mode: flan-t5-chat --debug"
echo ""
echo "⚠️  Note: First run will download the FLAN-T5-Large model (~3GB)"
echo "    Make sure you have a stable internet connection and sufficient disk space."

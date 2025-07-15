#!/bin/bash

# Quick Setup Script for FLAN-T5 ChatBot
# This script sets up the environment and installs dependencies quickly

set -e

echo "🚀 Quick Setup for FLAN-T5 ChatBot"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Make sure you're in the project root directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install PyTorch (CPU version for compatibility)
echo "🔥 Installing PyTorch (this may take a few minutes)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
echo "📥 Installing other dependencies..."
pip install transformers>=4.30.0 tokenizers>=0.13.0 accelerate>=0.20.0 psutil>=5.9.0 numpy>=1.24.0 redis>=4.5.0 pydantic>=2.0.0

# Install package in development mode
echo "📦 Installing package..."
pip install -e .

# Create directories
mkdir -p conversations logs

# Test installation
echo "🧪 Testing installation..."
python3 -c "import torch; print('✅ PyTorch installed:', torch.__version__)"
python3 -c "import transformers; print('✅ Transformers installed:', transformers.__version__)"
python3 -c "import flan_t5_chatbot; print('✅ Package installed successfully')"

echo ""
echo "✅ Quick setup complete!"
echo ""
echo "🚀 To run the chatbot:"
echo "   source .venv/bin/activate"
echo "   python3 run_dev.py"
echo ""
echo "Or use the Makefile:"
echo "   make run-dev"

#!/bin/bash

# FLAN-T5 ChatBot Runner Script

set -e

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if PyTorch is installed
if ! python3 -c "import torch" &> /dev/null; then
    echo "❌ PyTorch not installed. Please run ./install.sh first."
    exit 1
fi

# Check if package is installed
if ! python3 -c "import flan_t5_chatbot" &> /dev/null; then
    echo "❌ FLAN-T5 ChatBot not installed. Please run ./install.sh first."
    echo "🔄 Alternatively, you can run: source .venv/bin/activate && python3 run_dev.py"
    exit 1
fi

# Run the chatbot
echo "🤖 Starting FLAN-T5 ChatBot..."
flan-t5-chat "$@"

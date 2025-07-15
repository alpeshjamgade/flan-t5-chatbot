#!/bin/bash

# Dependency Fix Script
# Run this if you're having import issues

echo "🔧 Fixing dependencies..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Upgrade pip
pip install --upgrade pip

# Install PyTorch specifically
echo "🔥 Installing/Updating PyTorch..."
pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install/update other dependencies
echo "📥 Installing/Updating other dependencies..."
pip install --upgrade transformers tokenizers accelerate psutil numpy redis pydantic

# Reinstall package
echo "📦 Reinstalling package..."
pip install -e . --force-reinstall

echo "✅ Dependencies fixed!"
echo ""
echo "🧪 Testing installation..."
python3 -c "import torch; print('✅ PyTorch:', torch.__version__)"
python3 -c "import transformers; print('✅ Transformers:', transformers.__version__)"
python3 -c "import flan_t5_chatbot; print('✅ Package working!')"

echo ""
echo "🚀 Now try running:"
echo "   python3 run_dev.py"

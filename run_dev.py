#!/usr/bin/env python3
"""
Development runner for FLAN-T5 ChatBot
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} found")
    except ImportError:
        missing_deps.append("torch")
    
    try:
        import transformers
        print(f"✅ Transformers {transformers.__version__} found")
    except ImportError:
        missing_deps.append("transformers")
    
    try:
        import redis
        print(f"✅ Redis {redis.__version__} found")
    except ImportError:
        missing_deps.append("redis")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("\n🔧 To fix this, run one of the following:")
        print("   Option 1: ./install.sh")
        print("   Option 2: make setup-env")
        print("   Option 3: pip install -r requirements.txt")
        print("\n💡 If you're using a virtual environment, make sure it's activated:")
        print("   source .venv/bin/activate")
        return False
    
    return True

def main():
    """Main function"""
    print("🔍 Checking dependencies...")
    
    if not check_dependencies():
        sys.exit(1)
    
    # Add the src directory to Python path
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    sys.path.insert(0, str(src_dir))
    
    # Change to project root directory
    os.chdir(project_root)
    
    try:
        print("🚀 Starting FLAN-T5 ChatBot in development mode...")
        from flan_t5_chatbot.cli import main
        main()
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure you're running from the project root directory")
        print("2. Install the package with: pip install -e .")
        print("3. Or run the full installation: ./install.sh")
        print("4. Check if virtual environment is activated: source .venv/bin/activate")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🐛 If this error persists, try running with --debug flag")
        sys.exit(1)

if __name__ == "__main__":
    main()

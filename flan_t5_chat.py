#!/usr/bin/env python3
"""
Direct entry point for FLAN-T5 ChatBot
This script can be run directly without installation
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Now import and run
from flan_t5_chatbot.cli import main

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Command Line Interface for FLAN-T5 ChatBot
"""

import argparse
import sys
import os
from pathlib import Path

from .app import FlanT5ChatBot
from .config.settings import Config
from .utils.logging import setup_logging
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        prog="flan-t5-chatbot",
        description="A sophisticated shell-based chat interface using Google's FLAN-T5-Large model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  flan-t5-chat                    # Start with default settings
  flan-t5-chat --config my.json  # Use custom config
  flan-t5-chat --debug           # Enable debug mode
  flan-t5-chat --version         # Show version
        """
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration file (default: config.json)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        help="Directory for storing conversations and logs"
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    return parser


def main():
    """Main entry point for the CLI"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Setup logging
        logger = setup_logging(
            level=args.log_level,
            debug=args.debug,
            no_color=args.no_color
        )
        
        # Create data directory if specified
        if args.data_dir:
            Path(args.data_dir).mkdir(parents=True, exist_ok=True)
            os.chdir(args.data_dir)
        
        # Initialize and run chatbot
        chatbot = FlanT5ChatBot(
            config_path=args.config,
            debug_mode=args.debug,
            no_color=args.no_color
        )
        
        chatbot.run()
        
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

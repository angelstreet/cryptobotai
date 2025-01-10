# main.py
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
import os
import argparse
from src.crew import CryptoAgency

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='AI Crypto Trading System',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('-d','--debug', action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--virtual', action='store_true',
                       help='Use virtual portfolio for practice (default: live)')
    parser.add_argument('command', nargs='?', default='welcome',
                       choices=['welcome', 'show_portfolio', 'help', 'exit'],
                       help='Command to execute')

    return parser.parse_args()

def main():
    """Main entry point"""
    crew = CryptoAgency(config=parse_arguments())
    crew.kickoff()

if __name__ == "__main__":
    main()
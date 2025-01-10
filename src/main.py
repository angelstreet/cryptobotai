# main.py
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import argparse
from src.crew import CryptoAgency

COMMANDS = {
    'show_portfolio': 'Show portfolio overview',
    'trade': 'Execute live trade',
    'backtest': 'Run backtest simulation',
    'virtual': 'Run virtual trade in sandbox',
    'help': 'Show this help message',
    'exit': 'Exit the program'
}

OPTIONS = {
    '-h, --help': 'Show this help message',
    '-d, --debug': 'Enable debug mode',
    '--virtual': 'Use virtual portfolio for practice (default: live)'
} 

def show_help_and_exit():
    """Display help message and exit"""
    # Build help message from config
    message = ["=== AI Crypto Agency ==="] 
    message.append("\nAvailable commands:")
    for cmd, desc in COMMANDS.items():
        message.append(f"• {cmd:<10} - {desc}")
    
    message.append("\nOptions:")
    for opt, desc in OPTIONS.items():
        message.append(f"  {opt:<12} {desc}")
    
    print('\n'.join(message))
    sys.exit(0)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description=argparse.SUPPRESS,
        usage=argparse.SUPPRESS
    )
    
    parser.add_argument('-d', '--debug', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('command', 
                       nargs='?',  # Make command optional
                       default='welcome',  # Default to welcome
                       choices=['welcome', 'show_portfolio', 'trade', 'backtest', 'virtual', 'help'],
                       help=argparse.SUPPRESS)

    args = parser.parse_args()
    
    # Show help if explicitly requested
    if args.command == 'help':
        show_help_and_exit()
        
    return args

def main():
    """Main entry point"""
    crew = CryptoAgency(config=parse_arguments())
    crew.kickoff()

if __name__ == "__main__":
    main()
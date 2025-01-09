import sys
from pathlib import Path
from dataclasses import dataclass
from crewai import LLM

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
import os
import argparse
from src.crew import CryptoAgency

@dataclass
class Config:
    debug: bool = False
    llm: LLM = None  # Will be set by CryptoAgency

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='AI Crypto Trading Agency',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Only keep debug flag
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    return parser.parse_args()

def main():
    """Main"""
    # Parse arguments
    args = parse_arguments()
    
    # Create minimal config object
    config = Config(debug=args.debug)
    
    # Initialize and run Trading Crew
    result = CryptoAgency.kickoff(config)
    print(result)

if __name__ == "__main__":
    main() 
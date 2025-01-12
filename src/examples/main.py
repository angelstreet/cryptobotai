
import argparse
import sys
from pathlib import Path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
from src.crew import CryptoCrew

def main():
    parser = argparse.ArgumentParser(description="Gradio UI for Browser Agent")
    parser.add_argument('-d', '--debug', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('command', 
                       nargs='?', 
                       default='welcome',   
                       choices=['welcome', 'show_portfolio', 'trade', 'backtest', 'virtual', 'help'],
                       help=argparse.SUPPRESS)
    args = parser.parse_args()    
    crew = CryptoCrew(config=args)
    crew.kickoff()

if __name__ == "__main__":
    main()
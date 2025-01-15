
import argparse
import sys
from pathlib import Path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
from src.agency import CryptoAgency

def main():
    parser = argparse.ArgumentParser(description="AI Crypto Agency")
    parser.add_argument('-d', '--debug', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-c', '--display_currency', type=str, default='usd', help='Display currency')
    config = parser.parse_args()    
    agency = CryptoAgency(config)
    agency.start()

if __name__ == "__main__":
    main()
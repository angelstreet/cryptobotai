import argparse
from datetime import datetime
from dotenv import load_dotenv
import os
from lib.crews.ai_agency import AIAgency
from lib.utils.api import get_ai_client, get_ai_credentials
from lib.utils.display import print_header
from lib.config.config import Config
from crewai import Crew, Task

def main():
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Portfolio Overview')
    parser.add_argument('--exchange', type=str, default='binance', help='Exchange name')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    # Initialize config and agency
    config = Config('default')
    agency = AIAgency(config)
    
    # Set debug mode if requested
    agency.set_debug(args.debug)
    
    # Create portfolio overview task
    portfolio_task = Task(
        description="Display current portfolio overview",
        agent=agency.crew_agents['portfolio_manager'],
        context={
            'exchange': args.exchange,
            'timestamp': datetime.now()
        }
    )
    
    # Create and run crew with single task
    crew = Crew(
        agents=[agency.crew_agents['portfolio_manager']],
        tasks=[portfolio_task],
        verbose=args.debug
    )
    
    print_header("Portfolio Overview")
    
    try:
        result = crew.kickoff()
        if 'error' in result:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Error executing portfolio overview: {str(e)}")

if __name__ == "__main__":
    main() 
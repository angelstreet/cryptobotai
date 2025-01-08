import argparse
from datetime import datetime
from dotenv import load_dotenv
import os
from lib.crews.ai_agency import AIAgency
from lib.utils.api import get_ai_client, get_ai_credentials
from lib.utils.display import print_header, print_api_config
from lib.config.config import Config
from crewai import Crew, Task

def main():
    # Load environment variables first
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Crypto Trading Bot')
    parser.add_argument('--symbol', type=str, default='BTC/USDT', help='Trading pair symbol')
    parser.add_argument('--exchange', type=str, default='binance', help='Exchange name (default: binance)')
    parser.add_argument('--strategy', type=str, default='default', help='Trading strategy')
    parser.add_argument('--portfolio', type=str, default='portfolio.json', help='Portfolio file path')
    parser.add_argument('--ai-provider', type=str, default='LOCAL', 
                       choices=['LOCAL', 'OPENAI', 'CLAUDE', 'OPENROUTER'])
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--mock', action='store_true', help='Use mock data')
    parser.add_argument('--refresh', action='store_true', help='Refresh market data only')
    parser.add_argument('--backtest', action='store_true', help='Run in backtest mode')
    parser.add_argument('--portfolio-overview', action='store_true', help='Show portfolio overview')
    parser.add_argument('--start-date', type=str, help='Start date (DD/MM/YYYY)')
    parser.add_argument('--end-date', type=str, help='End date (DD/MM/YYYY)')
    parser.add_argument('--timeframe', type=str, default='1h', help='Timeframe (1m,5m,1h,1d)')
    parser.add_argument('--initial-balance', type=float, default=10000, help='Initial balance')
    args = parser.parse_args()

    # Set AI provider in environment
    os.environ['AI_PROVIDER'] = args.ai_provider

    # Initialize config and agency
    config = Config(args.strategy)        
    agency = AIAgency(config)
    
    # Configure agency
    agency.portfolio_manager.set_portfolio_file(args.portfolio)
    agency.portfolio_manager.set_exchange(args.exchange)
    agency.set_debug(args.debug)
    agency.set_mock(args.mock)
    
    print_header(args.symbol)
    print_api_config(config, get_ai_client(get_ai_credentials()), args.debug)

    # Create context for tasks
    context = {
        'exchange': args.exchange,
        'symbol': args.symbol,
        'timestamp': datetime.now(),
        'timeframe': args.timeframe,
        'start_date': args.start_date,
        'end_date': args.end_date,
        'initial_balance': args.initial_balance,
        'show_reasoning': args.debug
    }

    # Select tasks based on command arguments
    tasks = []
    agents = []

    if args.portfolio_overview:
        tasks.append(Task(
            description="Display current portfolio overview",
            agent=agency.crew_agents['portfolio_manager'],
            context=context
        ))
        agents.append(agency.crew_agents['portfolio_manager'])

    elif args.backtest:
        tasks.extend([
            Task(
                description="Fetch historical market data for backtesting",
                agent=agency.crew_agents['data_analyst'],
                context=context
            ),
            Task(
                description="Develop trading strategy for backtesting",
                agent=agency.crew_agents['portfolio_manager'],
                context=context,
                depends_on=["Fetch historical market data for backtesting"]
            ),
            Task(
                description="Execute backtest simulation",
                agent=agency.crew_agents['backtester'],
                context=context,
                depends_on=["Develop trading strategy for backtesting"]
            )
        ])
        agents.extend([
            agency.crew_agents['data_analyst'],
            agency.crew_agents['portfolio_manager'],
            agency.crew_agents['backtester']
        ])

    else:
        # Regular trading workflow
        tasks.extend([
            Task(
                description="Analyze current market conditions",
                agent=agency.crew_agents['data_analyst'],
                context=context
            ),
            Task(
                description="Develop trading strategy",
                agent=agency.crew_agents['portfolio_manager'],
                context=context,
                depends_on=["Analyze current market conditions"]
            ),
            Task(
                description="Execute trading decisions",
                agent=agency.crew_agents['trader'],
                context=context,
                depends_on=["Develop trading strategy"]
            ),
            Task(
                description="Evaluate trading performance",
                agent=agency.crew_agents['portfolio_manager'],
                context=context,
                depends_on=["Execute trading decisions"]
            )
        ])
        agents.extend([
            agency.crew_agents['data_analyst'],
            agency.crew_agents['portfolio_manager'],
            agency.crew_agents['trader']
        ])

    # Create and execute crew
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=args.debug
    )

    try:
        result = crew.kickoff()
        if 'error' in result:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Error executing workflow: {str(e)}")

if __name__ == "__main__":
    main() 
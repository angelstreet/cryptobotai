import argparse
from datetime import datetime
from dotenv import load_dotenv
import os
from lib.agents import TraderAgent, DataAnalystAgent, RiskManagerAgent
from lib.utils.api import get_ai_client, get_ai_credentials
from lib.utils.display import print_header, print_api_config
from lib.config.config import Config

def main():
    # Load environment variables first
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Crypto Trading Bot')
    parser.add_argument('--symbol', type=str, default='BTC/USDT', help='Trading pair symbol')
    parser.add_argument('--exchange', type=str, default='binance', help='Exchange name (default: binance)')
    parser.add_argument('--strategy', type=str, default='default', help='Trading strategy (default/aggressive/conservative)')
    parser.add_argument('--portfolio', type=str, default='portfolio.json', 
                       help='Path to portfolio file (default: portfolio.json)')
    parser.add_argument('--ai-provider', type=str, default='LOCAL', 
                       choices=['LOCAL', 'OPENAI', 'CLAUDE', 'OPENROUTER'],
                       help='AI provider (default: LOCAL)')
    parser.add_argument('--init-position', type=float, default=0.0, 
                       help='Initial position size (default: 0.0)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    # Set AI provider in environment
    os.environ['AI_PROVIDER'] = args.ai_provider

    # Initialize AI client and config
    creds = get_ai_credentials()
    client = get_ai_client(creds)
    config = Config(args.strategy)        
    
    # Initialize agents with config
    data_analyst = DataAnalystAgent(config)
    trader = TraderAgent(config)
    risk_manager = RiskManagerAgent(config)
    
    # Set portfolio file
    risk_manager.set_portfolio_file(args.portfolio)
    
    # Get current position from portfolio
    position = risk_manager.get_position(args.exchange, args.symbol)
    current_position = position.amount if position else args.init_position
    entry_price = position.entry_price if position else 0.0
    
    # Set debug mode for all agents
    for agent in [data_analyst, trader, risk_manager]:
        agent.set_debug(args.debug)
    
    print_header(args.symbol)
    print_api_config(config, client, args.debug)
    # 1. Fetch and analyze market data
    market_data = data_analyst.fetch_market_data(args.exchange, args.symbol)
        
    # 2. Generate trading decision with position info
    trade_suggestion = trader.generate_trading_decision(
        market_data, 
        current_position=current_position,
        entry_price=entry_price
    )
    
    # 3. Evaluate trade against risk parameters
    final_decision = risk_manager.evaluate_trade(trade_suggestion, market_data)
    
    # 4. Execute or simulate trade if approved
    if final_decision['action'] != 'HOLD':
        risk_manager.update_position(
            exchange=market_data['exchange'],
            symbol=market_data['symbol'],
            action=final_decision['action'],
            amount=final_decision['amount'],
            price=market_data['price']
        )
        
        # Show updated portfolio
        risk_manager.print_portfolio()

if __name__ == "__main__":
    main() 
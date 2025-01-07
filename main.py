import asyncio
import argparse
from datetime import datetime
from dotenv import load_dotenv
import os
from lib.agents.agent import TradingAgent
from lib.utils.api import get_ai_client, get_ai_credentials
from lib.utils.display import print_header

async def main():
    # Load environment variables first
    load_dotenv()
    
    parser = argparse.ArgumentParser(description='Crypto Trading Bot')
    parser.add_argument('--symbol', type=str, default='BTC/USDT', help='Trading pair symbol')
    parser.add_argument('--strategy', type=str, default='default', help='Trading strategy (default/aggressive/conservative)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--show-reasoning', action='store_true', help='Show AI reasoning')
    args = parser.parse_args()

    # Initialize AI client
    creds = get_ai_credentials()
    client = get_ai_client(creds)
    
    # Initialize trading agent
    agent = TradingAgent(client, args.strategy)
    agent.set_debug(args.debug)
    agent.set_show_reasoning(args.show_reasoning)
    
    print_header(args.symbol)
    
    # Fetch initial market data
    df = await agent.fetch_market_data('binance', args.symbol)
    if df.empty:
        print("Failed to fetch market data")
        return
        
    # Get latest market data
    latest = df.iloc[-1]
    market_data = {
        "price": latest['close'],
        "volume": latest['volume'],
        "change_24h": ((latest['close'] - df.iloc[-24]['close']) / df.iloc[-24]['close']) * 100 if len(df) >= 24 else 0,
        "high_low_range": ((latest['high'] - latest['low']) / latest['low']) * 100,
        "candle_number": len(df)
    }
    
    # Generate trading decision
    decision = agent.generate_trading_decision(market_data)

if __name__ == "__main__":
    asyncio.run(main()) 
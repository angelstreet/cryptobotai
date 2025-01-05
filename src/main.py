import argparse
from decimal import Decimal
from dotenv import load_dotenv
import os
import asyncio
from openai import OpenAI
from data.market_data import MarketDataFetcher
from agents.trading_agent import TradingAgent

async def run_trading_bot(args):
    # Load environment variables
    load_dotenv()
    
    # Initialize OpenAI client for OpenRouter
    openai_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={
            "HTTP-Referer": os.getenv("APP_URL", "http://localhost:3000"),
            "X-Title": os.getenv("APP_NAME", "Crypto AI Trading Bot")
        }
    )
    
    # Initialize market data fetcher
    market_fetcher = MarketDataFetcher(args.exchange)
    
    # Initialize trading agent with OpenAI client
    trading_agent = TradingAgent(openai_client=openai_client)
    
    # Fetch market data
    market_data = await market_fetcher.fetch_ohlcv(args.symbol, args.timeframe)
    if market_data.empty:
        print("Error: Could not fetch market data")
        return
        
    # Generate trading decision
    decision = trading_agent.generate_trading_decision({
        "price": market_data['close'].iloc[-1],
        "volume": market_data['volume'].iloc[-1],
        "change_24h": (market_data['close'].iloc[-1] - market_data['close'].iloc[-2]) / market_data['close'].iloc[-2] * 100
    })
    
    # Print results
    print(f"\nTrading Analysis for {args.symbol}:")
    print(f"Action: {decision['action']}")
    print(f"Position Size: {decision['amount']:.2f}")
    print(f"Confidence: {decision['confidence']}%")
    if args.show_reasoning:
        print(f"\nReasoning:\n{decision['reasoning']}")

def main():
    parser = argparse.ArgumentParser(description='Crypto AI Trading Bot')
    parser.add_argument('--symbol', type=str, required=True, help='Trading pair (e.g., BTC/USDT)')
    parser.add_argument('--exchange', type=str, default='binance', help='Exchange to use')
    parser.add_argument('--show-reasoning', action='store_true', help='Show agent reasoning')
    parser.add_argument('--timeframe', type=str, default='1h', help='Trading timeframe')
    
    args = parser.parse_args()
    
    # Run the async function
    asyncio.run(run_trading_bot(args))

if __name__ == "__main__":
    main() 
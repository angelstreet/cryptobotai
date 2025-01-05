import argparse
from decimal import Decimal
from dotenv import load_dotenv
import os
import asyncio
import ccxt
import pandas as pd
from openai import OpenAI
from agent import TradingAgent
from backtester import Backtester

async def fetch_market_data(exchange: str, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
    try:
        exchange_instance = getattr(ccxt, exchange)()
        ohlcv = exchange_instance.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return pd.DataFrame()

async def run_trading_bot(args):
    if args.backtest:
        await run_backtest(args)
        return
    
    load_dotenv()
    
    openai_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={
            "HTTP-Referer": os.getenv("APP_URL", "http://localhost:3000"),
            "X-Title": os.getenv("APP_NAME", "Crypto AI Trading Bot")
        }
    )
    
    trading_agent = TradingAgent(openai_client=openai_client)
    
    market_data = await fetch_market_data(args.exchange, args.symbol, args.timeframe)
    if market_data.empty:
        print("Error: Could not fetch market data")
        return
        
    decision = trading_agent.generate_trading_decision({
        "price": market_data['close'].iloc[-1],
        "volume": market_data['volume'].iloc[-1],
        "change_24h": (market_data['close'].iloc[-1] - market_data['close'].iloc[-2]) / market_data['close'].iloc[-2] * 100
    })
    
    print(f"\nTrading Analysis for {args.symbol}:")
    print(f"Action: {decision['action']}")
    print(f"Position Size: {decision['amount']:.2f}")
    print(f"Confidence: {decision['confidence']}%")
    if args.show_reasoning:
        print(f"\nReasoning:\n{decision['reasoning']}")

async def run_backtest(args):
    load_dotenv()
    
    openai_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={
            "HTTP-Referer": os.getenv("APP_URL", "http://localhost:3000"),
            "X-Title": os.getenv("APP_NAME", "Crypto AI Trading Bot")
        }
    )
    
    trading_agent = TradingAgent(openai_client=openai_client)
    backtester = Backtester(initial_balance=Decimal(args.initial_balance))
    
    # Fetch historical data
    market_data = await fetch_market_data(args.exchange, args.symbol, args.timeframe, limit=args.backtest_days * 24)
    if market_data.empty:
        print("Error: Could not fetch market data")
        return
    
    # Run backtest
    results = await backtester.run(trading_agent, market_data)
    backtester.print_results(results)

def main():
    parser = argparse.ArgumentParser(description='Crypto AI Trading Bot')
    parser.add_argument('--symbol', type=str, required=True, help='Trading pair (e.g., BTC/USDT)')
    parser.add_argument('--exchange', type=str, default='binance', help='Exchange to use')
    parser.add_argument('--show-reasoning', action='store_true', help='Show agent reasoning')
    parser.add_argument('--timeframe', type=str, default='1h', help='Trading timeframe')
    parser.add_argument('--backtest', action='store_true', help='Run in backtest mode')
    parser.add_argument('--backtest-days', type=int, default=30, help='Number of days to backtest')
    parser.add_argument('--initial-balance', type=float, default=10000, help='Initial balance for backtest')
    
    asyncio.run(run_trading_bot(parser.parse_args()))

if __name__ == "__main__":
    main() 
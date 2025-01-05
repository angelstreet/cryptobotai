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
from datetime import datetime, timedelta

async def fetch_market_data(
    exchange: str, 
    symbol: str, 
    timeframe: str = '1h',
    start_date: datetime = None,
    end_date: datetime = None
) -> pd.DataFrame:
    try:
        exchange_instance = getattr(ccxt, exchange)()
        
        # Convert dates to timestamps if provided
        since = int(start_date.timestamp() * 1000) if start_date else None
        until = int(end_date.timestamp() * 1000) if end_date else None
        
        # Fetch OHLCV data
        ohlcv = []
        if since:
            while True:
                data = exchange_instance.fetch_ohlcv(
                    symbol, 
                    timeframe, 
                    since=since,
                    limit=1000  # Most exchanges limit to 1000 candles per request
                )
                ohlcv.extend(data)
                
                if not data or (until and data[-1][0] >= until):
                    break
                    
                since = data[-1][0] + 1  # Next candle timestamp
                
        else:
            ohlcv = exchange_instance.fetch_ohlcv(symbol, timeframe, limit=1000)
        
        # Convert to DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Filter by date range if provided
        if start_date:
            df = df[df['timestamp'] >= start_date]
        if end_date:
            df = df[df['timestamp'] <= end_date]
            
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
    
    # Parse dates if provided
    start_date = None
    end_date = None
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%d/%m/%Y')
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%d/%m/%Y')
    elif args.backtest_days:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.backtest_days)
    
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
    
    # Fetch historical data with date range
    market_data = await fetch_market_data(
        args.exchange, 
        args.symbol, 
        args.timeframe,
        start_date=start_date,
        end_date=end_date
    )
    
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
    parser.add_argument('--backtest-days', type=int, help='Number of days to backtest')
    parser.add_argument('--start-date', type=str, help='Start date for backtest (DD/MM/YYYY)')
    parser.add_argument('--end-date', type=str, help='End date for backtest (DD/MM/YYYY)')
    parser.add_argument('--initial-balance', type=float, default=10000, help='Initial balance for backtest')
    
    asyncio.run(run_trading_bot(parser.parse_args()))

if __name__ == "__main__":
    main() 
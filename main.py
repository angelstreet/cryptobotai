import argparse
from decimal import Decimal
from dotenv import load_dotenv
import os
import asyncio
import ccxt
import pandas as pd
from openai import OpenAI
from lib.agent import TradingAgent
from lib.backtester import Backtester
from lib.visualization import TradingVisualizer
from datetime import datetime, timedelta
from lib.display import console, print_trading_analysis

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
    
    # Configure AI client based on provider
    provider = os.getenv("AI_PROVIDER", "openrouter").lower()
    base_headers = {
        "HTTP-Referer": os.getenv("APP_URL", "http://localhost:3000"),
        "X-Title": os.getenv("APP_NAME", "Crypto AI Trading Bot")
    }
    
    # Add provider-specific headers
    if provider == "openrouter":
        headers = base_headers
    else:
        headers = {}  # Default empty headers for other providers
    
    openai_client = OpenAI(
        base_url=os.getenv("AI_API_URL"),
        api_key=os.getenv("AI_API_KEY"),
        default_headers=headers
    )
    
    trading_agent = TradingAgent(openai_client=openai_client, config_name=args.agent_config)
    
    market_data = await fetch_market_data(args.exchange, args.symbol, args.timeframe)
    if market_data.empty:
        print("Error: Could not fetch market data")
        return
        
    # Calculate market metrics
    last_24h_data = market_data.iloc[-24:] if len(market_data) >= 24 else market_data
    price_24h_ago = market_data['close'].iloc[-25] if len(market_data) >= 25 else market_data['close'].iloc[0]
    current_price = market_data['close'].iloc[-1]
    
    # Calculate changes
    price_change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
    
    # Calculate ranges
    high_24h = last_24h_data['high'].max()
    low_24h = last_24h_data['low'].min()
    high_low_range = ((high_24h - low_24h) / low_24h) * 100
    
    # Calculate recent changes
    price_changes = []
    for i in range(1, min(25, len(market_data))):
        change = (market_data['close'].iloc[-i] - market_data['close'].iloc[-i-1]) / market_data['close'].iloc[-i-1] * 100
        price_changes.append(change)
    
    decision = trading_agent.generate_trading_decision({
        "price": float(current_price),
        "volume": float(market_data['volume'].iloc[-1]),
        "change_24h": float(price_change_24h),
        "high_low_range": float(high_low_range),
        "high_24h": float(high_24h),
        "low_24h": float(low_24h),
        "historical_changes": price_changes
    })
    
    # Create market data dict for analysis
    market_metrics = {
        "price": float(current_price),
        "volume": float(market_data['volume'].iloc[-1]),
        "change_24h": float(price_change_24h),
        "high_low_range": float(high_low_range),
        "high_24h": float(high_24h),
        "low_24h": float(low_24h),
        "historical_changes": price_changes
    }
    
    print_trading_analysis(
        args.symbol,
        market_metrics,
        decision,
        trading_agent,
        args.show_reasoning
    )

    # Create visualization if requested
    if args.advanced:
        # Create a mock trade for visualization
        mock_trade = {
            'timestamp': market_data['timestamp'].iloc[-1],
            'action': decision['action'],
            'price': current_price,
            'amount': decision['amount'],
            'fee': 0.0,
            'balance': 0.0,
            'position': 0.0,
            'reasoning': decision['reasoning']
        }
        
        visualizer = TradingVisualizer(market_data, [mock_trade])
        visualizer.plot_chart()

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
        base_url=os.getenv("AI_API_URL"),
        api_key=os.getenv("AI_API_KEY"),
        default_headers={
            "HTTP-Referer": os.getenv("APP_URL", "http://localhost:3000"),
            "X-Title": os.getenv("APP_NAME", "Crypto AI Trading Bot")
        }
    )
    
    trading_agent = TradingAgent(openai_client=openai_client, config_name=args.agent_config)
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
    
    # Set symbol name in DataFrame
    market_data.name = args.symbol
    
    # Run backtest
    results = await backtester.run(trading_agent, market_data, args.show_reasoning)
    if results['trades']:
        backtester.print_results(results)
    else:
        console.print("\nNo trades executed during backtest period", style="info")

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
    parser.add_argument('--agent-config', type=str, default='default',
                       choices=['default', 'conservative', 'aggressive'],
                       help='Trading agent configuration to use')
    parser.add_argument('--advanced', action='store_true', help='Show advanced visualization')
    
    asyncio.run(run_trading_bot(parser.parse_args()))

if __name__ == "__main__":
    main() 
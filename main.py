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
from visualization import TradingVisualizer
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
    
    trading_agent = TradingAgent(openai_client=openai_client, config_name=args.agent_config)
    
    # Fetch more historical data for context in live trading
    market_data = await fetch_market_data(
        args.exchange, 
        args.symbol, 
        args.timeframe,
        start_date=datetime.now() - timedelta(days=7)  # Last 7 days of data
    )
    
    if market_data.empty:
        print("Error: Could not fetch market data")
        return
    
    # Get latest market data
    current_price = market_data['close'].iloc[-1]
    current_volume = market_data['volume'].iloc[-1]
    price_change = (current_price - market_data['close'].iloc[-2]) / market_data['close'].iloc[-2] * 100
    
    decision = trading_agent.generate_trading_decision({
        "price": current_price,
        "volume": current_volume,
        "change_24h": price_change
    })
    
    # Print analysis
    print(f"\nTrading Analysis for {args.symbol}:")
    print(f"Action: {decision['action']}")
    print(f"Position Size: {decision['amount']:.2f}")
    print(f"Confidence: {decision['confidence']}%")
    if args.show_reasoning:
        print(f"\nReasoning:\n{decision['reasoning']}")
    
    # Create visualization if requested
    if args.advanced:
        # Create a mock trade for visualization
        mock_trade = {
            'timestamp': market_data['timestamp'].iloc[-1],
            'action': decision['action'],
            'price': float(current_price),
            'amount': float(decision['amount']),
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
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
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
    
    # Run backtest
    results = await backtester.run(trading_agent, market_data)
    backtester.print_results(results, show_advanced=args.advanced)

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
    parser.add_argument('--advanced', action='store_true', help='Show advanced visualization')
    parser.add_argument('--agent-config', type=str, default='default', 
                       choices=['default', 'conservative', 'aggressive'],
                       help='Trading agent configuration to use')
    parser.add_argument('--show-config', action='store_true',
                       help='Show detailed configuration information and exit')
    
    args = parser.parse_args()
    
    if args.show_config:
        print("""
Trading Bot Configuration Guide:

Available Agent Profiles:
  - default: Balanced trading approach
    • Min confidence: 60%
    • Min price change: 1%
    • Stop loss: 2%, Take profit: 3%
    • Risk per trade: 2%
    • Kelly factor: 0.5 (half-Kelly)

  - conservative: Risk-averse strategy
    • Min confidence: 80%
    • Min price change: 2%
    • Stop loss: 1%, Take profit: 2%
    • Risk per trade: 1%
    • Kelly factor: 0.25 (quarter-Kelly)

  - aggressive: High-risk strategy
    • Min confidence: 40%
    • Min price change: 0.5%
    • Stop loss: 5%, Take profit: 10%
    • Risk per trade: 5%
    • Kelly factor: 1.0 (full-Kelly)

Configuration Parameters:
  model: AI model used for analysis
  temperature: Controls randomness (0.5-0.9)
  max_tokens: Maximum response length
  trading_params:
    • min_confidence: Required confidence for trades
    • max_position_size: Maximum trade size (0-1)
    • min_price_change: Required price movement
    • stop_loss: Stop loss percentage
    • take_profit:
        • Array of profit targets:
            - level: Price target percentage
            - size: Position fraction to close at target

position_sizing:
    • max_position_size: Maximum allocation per trade
    • risk_per_trade: Maximum risk per trade (% of portfolio)
    • kelly_factor: Fraction of Kelly Criterion to use
    • units: Specify if values are in percent or USD
       - position_size: "percent" (0.0-1.0) or "usd" (dollar amount)
       - risk: "percent" (0.0-1.0) or "usd" (dollar amount)

price_change_threshold:
    • base: Default minimum price change required
    • volatility_multiplier: Adjusts threshold based on market volatility
    • min_threshold: Minimum allowed threshold
    • max_threshold: Maximum allowed threshold

stop_loss:
    • initial: Initial stop-loss percentage
    • trailing: Distance to maintain from highest price
    • activation_threshold: Profit % needed to activate trailing

time_exit:
    • max_holding_period: Maximum time to hold a trade ("12h", "24h", "7d", etc., or null for unlimited)
    • force_close_at: Daily times to close positions
    • weekend_exit: Whether to exit before weekends

Example Usage:
  python main.py --symbol BTC/USDT --agent-config conservative
  python main.py --symbol ETH/USDT --agent-config aggressive --advanced
""")
        return
    
    asyncio.run(run_trading_bot(args))

if __name__ == "__main__":
    main() 
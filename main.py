import argparse
from decimal import Decimal
from dotenv import load_dotenv
import os
import asyncio
import ccxt
import pandas as pd
from openai import OpenAI
from anthropic import Anthropic
from lib.agent import TradingAgent
from lib.backtester import Backtester
from lib.display import console, print_trading_analysis, print_header, print_chart
from datetime import datetime, timedelta
import signal
import requests  # For local LLM API calls

def parse_args():
    parser = argparse.ArgumentParser(description='Crypto AI Trading Bot')
    parser.add_argument('--symbol', type=str, required=True, help='Trading pair (e.g., BTC/USDT)')
    parser.add_argument('--exchange', type=str, default='binance', help='Exchange to use')
    parser.add_argument('--show-reasoning', action='store_true', help='Show agent reasoning')
    parser.add_argument('--debug', action='store_true', help='Show debug information')
    parser.add_argument('--timeframe', type=str, default='1h', help='Trading timeframe')
    parser.add_argument('--backtest', action='store_true', help='Run in backtest mode')
    parser.add_argument('--backtest-days', type=int, help='Number of days to backtest')
    parser.add_argument('--start-date', type=str, help='Start date for backtest (DD/MM/YYYY)')
    parser.add_argument('--end-date', type=str, help='End date for backtest (DD/MM/YYYY)')
    parser.add_argument('--initial-balance', type=float, default=10000, help='Initial balance for backtest')
    parser.add_argument('--agent-config', type=str, default='default',
                       choices=['default', 'conservative', 'aggressive', 'buytest'],
                       help='Trading agent configuration to use')
    parser.add_argument('--advanced', action='store_true', help='Show advanced visualization')
    return parser.parse_args()

def get_ai_credentials():
    provider = os.getenv("AI_PROVIDER", "OPENAI").upper()
    
    # Get provider-specific settings
    credentials = {
        "api_key": os.getenv(f"{provider}_API_KEY"),
        "base_url": os.getenv(f"{provider}_API_URL"),
        "model": os.getenv(f"{provider}_MODEL"),
        "temperature": float(os.getenv(f"{provider}_TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv(f"{provider}_MAX_TOKENS", "200")),
        "headers": {}
    }
    
    # Handle OpenRouter specific configuration
    if provider == "OPENROUTER":
        credentials["model"] = os.getenv("AI_MODEL")
        credentials["headers"].update({
            "HTTP-Referer": os.getenv("APP_URL", "http://localhost:3000"),
            "X-Title": os.getenv("APP_NAME", "Crypto AI Trading Bot")
        })
    
    if provider == "OPENAI":
        credentials["model"] = os.getenv("OPENAI_MODEL")
    
    return credentials

def get_ai_client(creds):
    """Get the appropriate AI client based on provider"""
    provider = os.getenv("AI_PROVIDER", "OPENAI").upper()
    
    if provider == "LOCAL":
        # Return a wrapper for Ollama API
        class OllamaLLM:
            def __init__(self, base_url):
                self.base_url = base_url
                
            def chat_completions_create(self, **kwargs):
                # Convert OpenAI format to Ollama format
                messages = kwargs.get('messages', [])
                prompt = "\n".join([m["content"] for m in messages])
                
                # Ollama parameters
                # https://github.com/ollama/ollama/blob/main/docs/api.md#parameters
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": kwargs.get('model', 'llama2'),
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": 100,  # Similar to max_tokens
                            "top_p": 0.9,       # Alternative to temperature
                            "stop": ["</response>", "Action:"]  # Stop sequences
                        }
                    }
                )
                
                # Convert Ollama response to OpenAI format
                result = response.json()
                return {
                    "choices": [{
                        "message": {
                            "content": result.get('response', '')
                        }
                    }]
                }
        
        return OllamaLLM(creds["base_url"])
    elif provider == "CLAUDE":
        return Anthropic(api_key=creds["api_key"])
    else:
        return OpenAI(
            api_key=creds["api_key"],
            base_url=creds["base_url"],
            default_headers=creds["headers"],
            timeout=30.0
        )

async def run_trading_bot(args):
    try:
        load_dotenv()
        print_header(args.symbol)
        
        # Get credentials and appropriate client
        creds = get_ai_credentials()
        ai_client = get_ai_client(creds)
        
        trading_agent = TradingAgent(ai_client=ai_client, config_name=args.agent_config)
        trading_agent.set_debug(args.debug)
        trading_agent.set_show_reasoning(args.show_reasoning)
        
        if args.backtest:
            backtester = Backtester(initial_balance=Decimal(args.initial_balance))
            await backtester.run_backtest(args, trading_agent)
            return
            
        market_data = await trading_agent.fetch_market_data(args.exchange, args.symbol, args.timeframe)
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
        
    except KeyboardInterrupt:
        console.print("\nGracefully shutting down...", style="info")
    except Exception as e:
        console.print(f"\nError: {str(e)}", style="error")
    finally:
        console.print("\nExiting...", style="info")

def main():
    asyncio.run(run_trading_bot(parse_args()))

if __name__ == "__main__":
    main() 
import ccxt
import pandas as pd
from typing import Dict

class MarketDataFetcher:
    def __init__(self, exchange: str = 'binance'):
        self.exchange = getattr(ccxt, exchange)()
        
    async def fetch_ohlcv(self, 
                         symbol: str, 
                         timeframe: str = '1h', 
                         limit: int = 100) -> pd.DataFrame:
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return pd.DataFrame() 
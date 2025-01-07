from datetime import datetime
from typing import Dict, Any
import ccxt
import pandas as pd
import numpy as np
from lib.utils.display import (
    print_market_config, 
    print_loading_start, 
    print_loading_complete,
    print_trading_error
)
from lib.agents.agent import Agent

class DataAnalystAgent(Agent):
    def __init__(self, config):
        super().__init__(config)
        self.historical_data = []  # Store recent price data
        self.symbol = None
        self.debug = False

    def set_debug(self, debug: bool):
        self.debug = debug

    def _calculate_volatility(self, price_changes: list) -> float:
        """Calculate volatility using standard deviation of recent price changes"""
        if len(price_changes) < 2:
            return 1.0
        return float(np.std(price_changes) / np.mean(np.abs(price_changes)))

    def _calculate_24h_change(self, df: pd.DataFrame) -> float:
        """Calculate 24h price change percentage"""
        if len(df) < 2:
            return 0.0
        return float((df['close'].iloc[-1] - df['close'].iloc[-24 if len(df) > 24 else 0]) / 
                    df['close'].iloc[-24 if len(df) > 24 else 0] * 100)

    def _calculate_high_low_range(self, candle: pd.Series) -> float:
        """Calculate high-low range percentage"""
        return float((candle['high'] - candle['low']) / candle['low'] * 100)

    def fetch_market_data(self, exchange: str, symbol: str) -> Dict[str, float]:
        """Fetch and analyze market data"""
        try:
            # Print loading message
            print_loading_start(exchange)
            
            # Get market data
            data = self._fetch_ohlcv(exchange, symbol)
            
            # Calculate metrics
            last_price = data['close'].iloc[-1]
            volume_24h = data['volume'].iloc[-1]
            change_24h = ((last_price - data['open'].iloc[-1]) / data['open'].iloc[-1]) * 100
            high_low_range = ((data['high'].iloc[-1] - data['low'].iloc[-1]) / data['low'].iloc[-1]) * 100
            
            market_data = {
                'price': last_price,
                'volume': volume_24h,
                'change_24h': change_24h,
                'high_low_range': high_low_range,
                'exchange': exchange,  # Add exchange
                'symbol': symbol      # Add symbol
            }
            
            # Print loading complete
            print_loading_complete()
            
            return market_data
            
        except Exception as e:
            print_trading_error(str(e))
            return {
                'price': 0.0,
                'volume': 0.0,
                'change_24h': 0.0,
                'high_low_range': 0.0,
                'exchange': exchange,  # Add exchange
                'symbol': symbol      # Add symbol
            } 
from typing import Dict, Any
from datetime import datetime
from src.config.models.action import Action

def get_mock_market_data(exchange: str = 'binance', symbol: str = 'BTC/USDT') -> Dict[str, Any]:
    """Return mock market data based on real historical data"""
    return {
        'price': 65000.0,
        'volume': 1250.75,
        'change_24h': 0.3,
        'high_low_range': 2.1,
        'exchange': exchange,
        'symbol': symbol,
        'reasoning': """Given the current price and volume data, it appears that there is no recent trading activity or trend. 
        However, if we look at the Trading Parameters, the Base Threshold of 0.3% and Required Change of 0.3% suggest a potential 
        for price movement in the near future. With a stop loss of 2.0% and take profit targets set at +2.0% and +5.0%, the 
        risk-reward ratio seems favorable."""
    }

def get_mock_trade_suggestion(action: str = 'BUY', amount: float = 0.1) -> Dict[str, Any]:
    """Return mock trade suggestion based on real historical decision"""
    return {
        'action': action,
        'amount': amount,
        'confidence': 65.0,
        'reasoning': """The minimum confidence level is set at 60%, which we have met based on these parameters. 
        Therefore, a cautious buy order with the specified amount would be appropriate, but keep in mind that there 
        are no guarantees in trading. Always monitor your positions closely and be prepared to adjust as necessary."""
    }

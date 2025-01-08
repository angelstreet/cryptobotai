from typing import Dict, Any
from .base import Task
from lib.agents import TraderAgent

class TradingDecision(Task):
    def __init__(self, trader: TraderAgent):
        super().__init__("trading_decision")
        self.trader = trader
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading decision based on market data"""
        market_data = context.get('market_data', {})
        return self.trader.generate_trading_decision(
            market_data,
            current_position=context.get('current_position', 0.0),
            entry_price=context.get('entry_price', 0.0)
        ) 
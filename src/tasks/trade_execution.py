from typing import Dict, Any
from .base import Task

class TradeExecution(Task):
    def __init__(self, trader):
        super().__init__("trade_execution")
        self.trader = trader
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trading decisions"""
        strategy = context.get('strategy', {})
        market_data = context.get('market_analysis', {}).get('live_data', {})
        
        # Generate and execute trading decision
        decision = self.trader.generate_trading_decision(
            market_data,
            strategy=strategy
        )
        
        # Monitor order execution
        execution_result = self.trader.monitor_orders(decision)
        
        return {
            'decision': decision,
            'execution': execution_result
        } 
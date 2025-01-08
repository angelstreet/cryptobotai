from typing import Dict, Any
from .base import Task

class BacktestExecution(Task):
    def __init__(self, backtester):
        super().__init__("backtest_execution")
        self.backtester = backtester
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute backtest with strategy"""
        strategy = context.get('strategy', {})
        market_data = context.get('market_analysis', {}).get('historical_data', {})
        
        # Run backtest
        backtest_results = self.backtester.run_backtest({
            'strategy': strategy,
            'market_data': market_data,
            'parameters': context.get('parameters', {}),
            'symbol': context.get('symbol'),
            'exchange': context.get('exchange')
        })
        
        # Analyze results
        analysis = self.backtester.analyze_results(backtest_results)
        
        return {
            'backtest_results': backtest_results,
            'analysis': analysis
        } 
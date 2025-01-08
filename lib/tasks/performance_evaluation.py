from typing import Dict, Any
from .base import Task

class PerformanceEvaluation(Task):
    def __init__(self, portfolio_manager):
        super().__init__("performance_evaluation")
        self.portfolio_manager = portfolio_manager
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate trading performance"""
        execution_result = context.get('trade_execution', {})
        
        # Update portfolio with execution results
        if execution_result.get('decision', {}).get('action') != 'HOLD':
            self.portfolio_manager.update_position(
                context['symbol'],
                execution_result['decision']['action'],
                execution_result['decision']['amount'],
                execution_result['execution']['price']
            )
        
        # Get updated portfolio status
        portfolio_status = self.portfolio_manager.get_position(context['symbol'])
        
        return {
            'portfolio_status': portfolio_status,
            'performance_metrics': {
                'position_value': portfolio_status.get('value_eur', 0) if portfolio_status else 0,
                'realized_pnl': portfolio_status.get('realized_pnl', 0) if portfolio_status else 0,
                'unrealized_pnl': portfolio_status.get('unrealized_pnl', 0) if portfolio_status else 0
            }
        } 
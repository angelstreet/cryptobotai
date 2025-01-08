from typing import Dict, Any
from .base import Task
from lib.agents import PortfolioManagerAgent

class PortfolioManagement(Task):
    def __init__(self, portfolio_manager: PortfolioManagerAgent):
        super().__init__("portfolio_management")
        self.portfolio_manager = portfolio_manager
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update portfolio based on trade decision"""
        trade_decision = context.get('trade_decision', {})
        market_data = context.get('market_data', {})
        
        if trade_decision.get('action') != 'HOLD':
            self.portfolio_manager.update_position(
                symbol=market_data['symbol'],
                action=trade_decision['action'],
                amount=trade_decision['amount'],
                price=market_data['price']
            )
            
        return self.portfolio_manager.portfolio.dict() 
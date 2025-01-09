from typing import Dict, Any
from .base import Task

class PortfolioOverview(Task):
    def __init__(self, portfolio_manager):
        super().__init__("portfolio_overview")
        self.portfolio_manager = portfolio_manager
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Display portfolio overview"""
        try:
            # Get current portfolio status
            portfolio_status = self.portfolio_manager.portfolio.dict()
            
            # Get current market data for portfolio positions
            for symbol in portfolio_status['positions']:
                market_data = self.portfolio_manager.data_analyst.fetch_market_data(
                    context.get('exchange', 'binance'),
                    symbol
                )
                self.portfolio_manager.update_market_data(market_data)
            
            # Print portfolio overview
            self.portfolio_manager.print_portfolio()
            
            # Return portfolio data
            return {
                'portfolio': portfolio_status,
                'timestamp': context.get('timestamp'),
                'exchange': context.get('exchange')
            }
            
        except Exception as e:
            if self.portfolio_manager.debug:
                print(f"Error in portfolio overview: {str(e)}")
            return {'error': str(e)} 
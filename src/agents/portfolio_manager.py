# src/agents/portfolio_manager.py
from typing import Dict, Any, Optional, List
from crewai import Agent, Task
from pydantic import Field, ConfigDict
from src.config.models.portfolio import Portfolio, PortfolioType

class PortfolioManagerAgent(Agent):
    """Agent responsible for portfolio management"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    portfolio: Dict[str, float] = Field(default_factory=lambda: {
        'BTC': 0.5,   # 0.5 Bitcoin
        'ETH': 5.0,   # 5 Ethereum
        'USDT': 1000  # 1000 Tether
    })
    market_prices: Dict[str, float] = Field(default_factory=lambda: {
        'BTC': 50000,  # Bitcoin price
        'ETH': 3000,   # Ethereum price
        'USDT': 1      # Tether price
    })
    
    def __init__(self, config=None):
        """Initialize portfolio manager"""
        super().__init__(
            name="Portfolio Manager",
            role="Crypto Portfolio Tracker",
            goal="Provide comprehensive portfolio overview and asset tracking",
            backstory="An expert in managing and analyzing cryptocurrency portfolios",
            tools=[],
            llm=None,
            verbose=False
        )

    def execute_task(self, task: Task, context: Optional[str] = None, tools: Optional[List] = None) -> Dict[str, Any]:
        """
        Execute tasks for the portfolio manager
        
        Args:
            task (Task): The task to execute
            context (Optional[str]): Additional context for the task
            tools (Optional[List]): List of available tools
        
        Returns:
            Dict[str, Any]: Task execution result
        """
        if "portfolio" in task.description.lower():
            return self.show_portfolio()
        
        return {"error": "Unknown task"}

    def show_portfolio(self) -> Dict[str, Any]:
        """
        Generate a detailed portfolio overview
        
        Returns:
            Dict[str, Any]: Comprehensive portfolio details
        """
        # Calculate total value and individual asset values
        portfolio_details = {
            'total_value': 0,
            'assets': []
        }
        
        for asset, amount in self.portfolio.items():
            current_price = self.market_prices.get(asset, 0)
            asset_value = amount * current_price
            
            portfolio_details['total_value'] += asset_value
            portfolio_details['assets'].append({
                'symbol': asset,
                'amount': amount,
                'price_per_unit': current_price,
                'total_value': asset_value
            })
        
        # Print portfolio details
        print("\n=== Portfolio Overview ===")
        print(f"Total Portfolio Value: ${portfolio_details['total_value']:,.2f}")
        print("\nAsset Breakdown:")
        for asset in portfolio_details['assets']:
            print(f"{asset['symbol']}: {asset['amount']} @ ${asset['price_per_unit']:,.2f} = ${asset['total_value']:,.2f}")
        
        return portfolio_details

    def update_market_prices(self, new_prices: Dict[str, float]):
        """
        Update market prices for assets
        
        Args:
            new_prices (Dict[str, float]): New market prices for assets
        """
        self.market_prices.update(new_prices)
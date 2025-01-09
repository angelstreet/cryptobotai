from typing import Dict, Any, Optional
from .agent import Agent
from config.models.portfolio import Portfolio
from pydantic import Field, ConfigDict
import json

class PortfolioManagerAgent(Agent):
    """Agent responsible for portfolio management"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    portfolio: Portfolio = Field(default_factory=lambda: Portfolio(exchange='binance'))
    portfolio_file: str = Field(default='portfolio.json')
    
    def set_portfolio_file(self, file_path: str) -> None:
        """Set and load portfolio from file"""
        self.portfolio_file = file_path
        self._load_portfolio()
        
    def _load_portfolio(self) -> None:
        """Load portfolio from file"""
        try:
            with open(self.portfolio_file, 'r') as f:
                data = json.load(f)
                self.portfolio = Portfolio(**data)
        except FileNotFoundError:
            if self.debug:
                print(f"Portfolio file {self.portfolio_file} not found, using empty portfolio")
        except Exception as e:
            if self.debug:
                print(f"Error loading portfolio: {str(e)}")
    
    def get_portfolio_overview(self) -> Dict[str, Any]:
        """Get current portfolio overview"""
        return {
            'positions': self.portfolio.positions,
            'estimated_prices': self.portfolio.estimated_prices,
            'display_currency': self.portfolio.display_currency
        }
        
    def analyze_risk(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze portfolio risk based on market data"""
        return {
            'risk_level': 'medium',  # Placeholder
            'recommendations': [],
            'current_exposure': sum(
                pos.value_eur for pos in self.portfolio.positions.values()
            )
        } 
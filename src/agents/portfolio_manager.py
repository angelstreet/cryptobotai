# src/agents/portfolio_manager.py
from typing import Dict, Any, Optional, List
from crewai import Agent, Task
from crewai.tools import BaseTool
from pydantic import Field, ConfigDict
import json
from datetime import datetime
import uuid
from enum import Enum

class PortfolioType(str, Enum):
    LIVE = "live"
    VIRTUAL = "virtual"

class Portfolio:
    """Represents a crypto portfolio"""
    def __init__(self, exchange: str = 'binance', portfolio_type: PortfolioType = PortfolioType.VIRTUAL):
        self.exchange = exchange
        self.portfolio_type = portfolio_type
        self.positions: Dict[str, float] = {}
        self.transactions: List[Dict[str, Any]] = []
        self.estimated_prices: Dict[str, float] = {}
        self.display_currency: str = 'USD'
        self.last_updated: Optional[datetime] = None
        self.initial_balance: float = 0.0
        self.cash_balance: float = 0.0

class GetPortfolioOverviewTool(BaseTool):
    name: str = "get_portfolio_overview"
    description: str = "Get current portfolio overview"
    manager: Any = Field(description="Portfolio manager reference")

    def __init__(self, portfolio_manager: 'PortfolioManagerAgent') -> None:
        super().__init__(manager=portfolio_manager)

    def _run(self) -> str:
        """Get overview of the current portfolio"""
        portfolio = self.manager.portfolio
        total_value = sum(
            qty * portfolio.estimated_prices.get(sym, 0)
            for sym, qty in portfolio.positions.items()
        )
        
        overview = [
            f"\n=== {portfolio.portfolio_type.value.upper()} PORTFOLIO OVERVIEW ===",
            f"Exchange: {portfolio.exchange}",
            f"Last Updated: {portfolio.last_updated or 'Never'}"
        ]
        
        # Add positions if any exist
        if portfolio.positions:
            overview.append("\nPositions:")
            for symbol, qty in portfolio.positions.items():
                price = portfolio.estimated_prices.get(symbol, 0)
                value = qty * price
                overview.append(f"  {symbol}: {qty:.8f} @ {price:.2f} = {value:.2f} {portfolio.display_currency}")
        else:
            overview.append("\nNo positions")

        # Add cash balance for virtual portfolio
        if portfolio.portfolio_type == PortfolioType.VIRTUAL:
            overview.extend([
                f"\nCash Balance: {portfolio.cash_balance:.2f} {portfolio.display_currency}",
                f"Initial Balance: {portfolio.initial_balance:.2f} {portfolio.display_currency}",
                f"Total Value (Positions + Cash): {total_value + portfolio.cash_balance:.2f} {portfolio.display_currency}",
                f"P/L: {(total_value + portfolio.cash_balance - portfolio.initial_balance):.2f} {portfolio.display_currency}"
            ])
        else:
            overview.append(f"\nTotal Value: {total_value:.2f} {portfolio.display_currency}")
            
        return "\n".join(overview)

class PortfolioManagerAgent(Agent):
    """Agent responsible for portfolio management"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    portfolio: Portfolio = Field(default_factory=lambda: Portfolio())
    portfolio_type: PortfolioType = Field(default=PortfolioType.VIRTUAL)
    debug: bool = Field(default=False, description="Debug mode flag")
    
    def __init__(self, config):
        """Initialize portfolio manager"""
        is_virtual = getattr(config, 'virtual', False)
        portfolio_type = PortfolioType.VIRTUAL if is_virtual else PortfolioType.LIVE
        portfolio = Portfolio(portfolio_type=portfolio_type)
        
        # Create the agent with all fields set properly
        super().__init__(
            name="Portfolio Manager",
            role="Portfolio Management Specialist",
            goal="Manage crypto portfolio",
            backstory="Expert in managing and tracking crypto portfolios",
            tools=[GetPortfolioOverviewTool(self)],
            llm=None,  # No LLM needed for this agent
            verbose=getattr(config, 'debug', False),
            portfolio=portfolio,
            portfolio_type=portfolio_type,
            debug=getattr(config, 'debug', False)
        )
        self._load_portfolio()
    
    @property
    def portfolio_file(self) -> str:
        """Get the current portfolio file path based on type"""
        return f"{self.portfolio_type.value}_portfolio.json"
        
    def _load_portfolio(self) -> None:
        """Load portfolio from file based on current type"""
        try:
            with open(self.portfolio_file, 'r') as f:
                data = json.load(f)
                self.portfolio = Portfolio(**data)
        except FileNotFoundError:
            if self.debug:
                print(f"{self.portfolio_type.value} portfolio file not found, using empty portfolio")
            self.portfolio = Portfolio(portfolio_type=self.portfolio_type)
            self._save_portfolio()
        except Exception as e:
            if self.debug:
                print(f"Error loading portfolio: {str(e)}")
                
    def _save_portfolio(self) -> None:
        """Save current portfolio to file"""
        try:
            with open(self.portfolio_file, 'w') as f:
                json.dump(self.portfolio.__dict__, f, indent=2)
        except Exception as e:
            if self.debug:
                print(f"Error saving portfolio: {str(e)}")

    def execute_task(self, task: Task, context: Optional[str] = None, tools: Optional[List[BaseTool]] = None) -> str:
        """Execute portfolio management tasks without using LLM"""
        task_description = task.description.lower()
        
        if "overview" in task_description or "show" in task_description:
            return GetPortfolioOverviewTool(self)._run()
            
        return f"Task not supported: {task.description}"
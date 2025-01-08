from typing import Dict, Any
from datetime import datetime
from lib.agents.agent import Agent
from lib.utils.mock_data import get_mock_market_data
from rich.console import Console

console = Console()

class DataAnalystAgent(Agent):
    def __init__(self, config):
        super().__init__(config)
        self.debug = False
        self.mock = False
        self.watched_symbols = set()
        self.estimated_prices = {}
        self.currency_rates = {
            'EUR/USD': 1.08,
            'USD/EUR': 0.926
        }
        self.last_refresh = None

    def fetch_market_data(self, exchange: str, symbol: str) -> Dict[str, Any]:
        """Fetch market data including currency rates"""
        self.watched_symbols.add(symbol)
        
        if self.mock:
            market_data = get_mock_market_data(exchange, symbol)
        else:
            market_data = self._fetch_real_market_data(exchange, symbol)
        
        # Store price
        self.estimated_prices[symbol] = market_data['price']
        self.last_refresh = datetime.now()
        
        # Add our stored rates
        market_data['currency_rates'] = self.currency_rates
        return market_data

    def refresh_market_data(self) -> None:
        """Refresh all prices and rates"""
        # Update currency rates
        if not self.mock:
            self.currency_rates = self._fetch_real_currency_rates()
        
        # Update prices for all watched symbols
        for symbol in self.watched_symbols:
            if self.mock:
                price = get_mock_market_data('', symbol)['price']
            else:
                price = self._fetch_real_market_data('', symbol)['price']
            self.estimated_prices[symbol] = price
            
        self.last_refresh = datetime.now()
        
        if self.debug:
            console.print("[green]Market data refreshed successfully[/]")

    def get_estimated_price(self, symbol: str) -> float:
        """Get latest price for symbol"""
        return self.estimated_prices.get(symbol, 0.0)

    def get_currency_rate(self, from_currency: str, to_currency: str) -> float:
        """Get currency conversion rate"""
        if from_currency == to_currency:
            return 1.0
        rate_key = f"{from_currency}/{to_currency}"
        return self.currency_rates.get(rate_key, 1.0)

    def _fetch_real_currency_rates(self) -> Dict[str, float]:
        """Fetch real currency rates from API"""
        # TODO: Implement real currency rate fetching
        return self.currency_rates 
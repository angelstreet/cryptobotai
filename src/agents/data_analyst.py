from typing import Dict, Any, Set
from .agent import Agent

class DataAnalystAgent(Agent):
    def __init__(self, config):
        super().__init__(config)
        self._watched_symbols: Set[str] = set()
        self._estimated_prices: Dict[str, float] = {}
        self._currency_rates: Dict[str, float] = {
            'EUR/USD': 1.08,
            'USD/EUR': 0.926
        }

    @property
    def watched_symbols(self) -> Set[str]:
        return self._watched_symbols

    @property
    def estimated_prices(self) -> Dict[str, float]:
        return self._estimated_prices

    @property
    def currency_rates(self) -> Dict[str, float]:
        return self._currency_rates

    def fetch_market_data(self, exchange: str, symbol: str) -> Dict[str, Any]:
        """Fetch market data including currency rates"""
        self._watched_symbols.add(symbol)
        
        if self.mock:
            return get_mock_market_data(exchange, symbol)
            
        # Regular market data fetching...
        market_data = self._fetch_real_market_data(exchange, symbol)
        market_data['currency_rates'] = self._currency_rates
        return market_data

    def get_currency_rate(self, from_currency: str, to_currency: str) -> float:
        """Get currency conversion rate"""
        if from_currency == to_currency:
            return 1.0
        rate_key = f"{from_currency}/{to_currency}"
        return self._currency_rates.get(rate_key, 1.0) 
from typing import Dict, Any, Set
import requests
from .agent import Agent
from forex_python.converter import CurrencyRates
from enum import Enum

class Exchange(Enum):
    BINANCE = "binance"
    COINBASE = "coinbase"

class DataAnalystAgent(Agent):
    def __init__(self, config):
        super().__init__(config)
        self._watched_symbols: Set[str] = set()
        self._estimated_prices: Dict[str, float] = {}
        self._currency_rates: Dict[str, float] = {}
        
    @property
    def watched_symbols(self) -> Set[str]:
        return self._watched_symbols

    @property
    def estimated_prices(self) -> Dict[str, float]:
        return self._estimated_prices

    @property
    def currency_rates(self) -> Dict[str, float]:
        return self._currency_rates

    def _fetch_currency_rates(self) -> Dict[str, Any]:
        """Fetch currency rates"""
        c = CurrencyRates()
        # Get the EUR/USD exchange rate
        eur_usd_rate = c.get_rate('EUR', 'USD')
        print(f"EUR/USD: {eur_usd_rate}")

        # Get the USD/EUR exchange rate
        usd_eur_rate = c.get_rate('USD', 'EUR')
        print(f"USD/EUR: {usd_eur_rate}")
        
        self._currency_rates: Dict[str, float] = {
            'EUR/USD': eur_usd_rate,
            'USD/EUR': usd_eur_rate
        }

    def _get_binance_price(self, symbol: str) -> Dict[str, Any]:
        """Fetch price data from Binance"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return {
                'price': float(data['price']),
                'exchange': Exchange.BINANCE.value,
                'symbol': symbol
            }
        except Exception as e:
            print(f"Error fetching Binance price: {e}")
            return None

    def _get_coinbase_price(self, crypto_id: str, currency: str) -> Dict[str, Any]:
        """Fetch price data from Coinbase"""
        try:
            url = f"https://api.coinbase.com/v2/prices/{crypto_id}-{currency}/spot"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return {
                'price': float(data['data']['amount']),
                'exchange': Exchange.COINBASE.value,
                'symbol': f"{crypto_id}-{currency}"
            }
        except Exception as e:
            print(f"Error fetching Coinbase price: {e}")
            return None

    def fetch_market_data(self, exchange: str, symbol: str, mock: bool = False) -> Dict[str, Any]:
        """Fetch market data including currency rates"""
        self._watched_symbols.add(symbol)
        self._fetch_currency_rates()

        if mock:
            return self._fetch_mock_market_data(exchange, symbol)
        elif exchange == "binance":
            # Fetch from Binance
            market_data = self._fetch_real_market_data(exchange, "BTCUSDT")
        elif exchange == "coinbase":
            # Fetch from Coinbase
            market_data = self._fetch_real_market_data(exchange, "BTC-USD")
        else:
            raise ValueError(f"Unsupported exchange: {exchange}")
        market_data['currency_rates'] = self._currency_rates
        return market_data

    def _fetch_real_market_data(self, exchange: str, symbol: str) -> Dict[str, Any]:
        """Fetch real market data from specified exchange"""
        exchange_lower = exchange.lower()
        
        if exchange_lower == Exchange.BINANCE.value:
            # For Binance, we expect symbols like 'BTCUSDT'
            data = self._get_binance_price(symbol)
        elif exchange_lower == Exchange.COINBASE.value:
            # For Coinbase, we need to split the symbol (e.g., 'BTC-USD' -> 'BTC', 'USD')
            crypto_id, currency = symbol.split('-')
            data = self._get_coinbase_price(crypto_id, currency)
        else:
            raise ValueError(f"Unsupported exchange: {exchange}")

        if data is None:
            raise Exception(f"Failed to fetch data from {exchange} for {symbol}")

        return data

    def _fetch_mock_market_data(self, exchange: str = 'binance', symbol: str = 'BTCUSDT') -> Dict[str, Any]:
        """Return mock market data based on real historical data"""
        return {
            'price': 65000.0,
            'volume': 1250.75,
            'change_24h': 0.3,
            'high_low_range': 2.1,
            'exchange': exchange,
            'symbol': symbol,
            'reasoning': """Given the current price and volume data, it appears that there is no recent trading activity or trend. 
            However, if we look at the Trading Parameters, the Base Threshold of 0.3% and Required Change of 0.3% suggest a potential 
            for price movement in the near future. With a stop loss of 2.0% and take profit targets set at +2.0% and +5.0%, the 
            risk-reward ratio seems favorable."""
        }

    def get_currency_rate(self, from_currency: str, to_currency: str) -> float:
        """Get currency conversion rate"""
        if from_currency == to_currency:
            return 1.0
        rate_key = f"{from_currency}/{to_currency}"
        return self._currency_rates.get(rate_key, 1.0)
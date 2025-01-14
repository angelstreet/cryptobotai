from typing import Dict, Any, Set, Optional
import requests
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from .agent import Agent
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

class CoinGeckoIds(Enum):
    BTC = "bitcoin"
    ETH = "ethereum"
    SOL = "solana"
    XRP = "xrp"
    DOGE = "dogecoin"

class Exchange(Enum):
    COINGECKO = "coingecko"

class TimeFrame(Enum):
    WEEK = "7d"
    MONTH = "30d"
    YEAR = "365d"
    YTD = "ytd"

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

    def _get_coingecko_price(self, crypto_id: str, currency: str = "usd") -> Dict[str, Any]:
        """Fetch current price data from CoinGecko"""
        try:
            url = f"{COINGECKO_BASE_URL}/simple/price"
            params = {
                "ids": crypto_id,
                "vs_currencies": currency,
                "include_24hr_change": "true",  
                "include_24hr_vol": "true",     
                "include_last_updated_at": "true"  
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Get the currency data safely with defaults
            currency_data = data.get(crypto_id, {})
            price = float(currency_data.get(currency, 0))
            market_cap = float(currency_data.get(f"{currency}_market_cap", 0))
            volume_24h = float(currency_data.get(f"{currency}_24h_vol", 0))
            change_24h = float(currency_data.get(f"{currency}_24h_change", 0))
            last_updated_at = currency_data.get("last_updated_at", None)
            
            # Convert last_updated_at timestamp to a readable format
            if last_updated_at:
                last_updated_at = datetime.fromtimestamp(last_updated_at).strftime('%Y-%m-%d %H:%M:%S')
            else:
                last_updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(currency_data)  # Debugging: Print the raw currency data
            
            return {
                'price': price,
                'market_cap': market_cap,
                'volume_24h': volume_24h,
                'change_24h': change_24h,
                'last_updated': last_updated_at,
                'exchange': Exchange.COINGECKO.value,
                'symbol': f"{crypto_id}/{currency}"
            }
        except Exception as e:
            print(f"Error fetching CoinGecko price: {e}")
            return None

    def get_historical_data(self, crypto_id: str, timeframe: TimeFrame, currency: str = "usd") -> Dict[str, Any]:
        """
        Fetch historical price data from CoinGecko
        
        Args:
            crypto_id: The cryptocurrency ID (e.g., 'bitcoin')
            timeframe: TimeFrame enum value (7d, 30d, 365d, ytd)
            currency: The currency to get prices in (e.g., 'usd', 'eur')
            
        Returns:
            Dictionary containing historical price data with formatted dates
        """
        try:
            end_date = datetime.now()
            
            if timeframe == TimeFrame.YTD:
                start_date = datetime(end_date.year, 1, 1)
            else:
                days = int(timeframe.value.replace('d', ''))
                start_date = end_date - timedelta(days=days)
            
            url = f"{COINGECKO_BASE_URL}/coins/{crypto_id}/market_chart/range"
            params = {
                "vs_currency": currency.lower(),
                "from": int(start_date.timestamp()),
                "to": int(end_date.timestamp())
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Format the timestamp data
            formatted_data = {
                'prices': [
                    {
                        'date': datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d'),
                        'time': datetime.fromtimestamp(ts / 1000).strftime('%H:%M:%S'),
                        'value': value
                    }
                    for ts, value in data['prices']
                ],
                'market_caps': [
                    {
                        'date': datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d'),
                        'value': value
                    }
                    for ts, value in data['market_caps']
                ],
                'total_volumes': [
                    {
                        'date': datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d'),
                        'value': value
                    }
                    for ts, value in data['total_volumes']
                ],
                'metadata': {
                    'timeframe': timeframe.value,
                    'symbol': f"{crypto_id}/{currency.lower()}",
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'currency': currency.lower()
                }
            }
            
            return formatted_data
            
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None

    def _get_coingecko_market_data(self, crypto_id: str, currency: str = "usd") -> Dict[str, Any]:
        """Fetch detailed market data from CoinGecko"""
        try:
            url = f"{COINGECKO_BASE_URL}/coins/{crypto_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "false"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            market_data = data.get('market_data', {})
            
            return {
                'price': float(market_data.get('current_price', {}).get(currency, 0)),
                'market_cap': float(market_data.get('market_cap', {}).get(currency, 0)),
                'total_volume': float(market_data.get('total_volume', {}).get(currency, 0)),
                'high_24h': float(market_data.get('high_24h', {}).get(currency, 0)),
                'low_24h': float(market_data.get('low_24h', {}).get(currency, 0)),
                'price_change_24h': float(market_data.get('price_change_24h', 0)),
                'price_change_percentage_24h': float(market_data.get('price_change_percentage_24h', 0)),
                'market_cap_change_24h': float(market_data.get('market_cap_change_24h', 0)),
                'market_cap_change_percentage_24h': float(market_data.get('market_cap_change_percentage_24h', 0)),
                'circulating_supply': float(market_data.get('circulating_supply', 0)),
                'total_supply': float(market_data.get('total_supply', 0)),
                'max_supply': float(market_data.get('max_supply', 0)),
                'last_updated': market_data.get('last_updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'exchange': Exchange.COINGECKO.value,
                'symbol': f"{crypto_id}/{currency}"
            }
        except Exception as e:
            print(f"Error fetching CoinGecko market data: {e}")
            return None

    def fetch_market_data(self, crypto_id: str, currency: str = "usd", 
                         timeframe: Optional[TimeFrame] = None) -> Dict[str, Any]:
        """
        Fetch market data including current price and optional historical data
        
        Args:
            crypto_id: The cryptocurrency ID (e.g., 'bitcoin')
            currency: The currency to get prices in (e.g., 'usd', 'eur')
            timeframe: Optional TimeFrame enum value for historical data
        """
        self._watched_symbols.add(f"{crypto_id}/{currency.lower()}")
        
        # Get detailed market data
        market_data = self._get_coingecko_market_data(crypto_id, currency.lower())
        if not market_data:
            return None
            
        # If timeframe is specified, add historical data
        if timeframe:
            historical_data = self.get_historical_data(crypto_id, timeframe, currency.lower())
            if historical_data:
                market_data['historical'] = historical_data
        
        # Add metadata
        market_data['metadata'] = {
            'currency': currency.lower(),
            'crypto_id': crypto_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return market_data

    def _fetch_currency_rates(self) -> Dict[str, Any]:
        """Fetch currency rates from CoinGecko"""
        try:
            url = f"{COINGECKO_BASE_URL}/exchange_rates"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            eur_usd_rate = data['rates']['usd']['value'] / data['rates']['eur']['value']
            usd_eur_rate = 1 / eur_usd_rate
            
            self._currency_rates = {
                'EUR/USD': eur_usd_rate,
                'USD/EUR': usd_eur_rate
            }
            
            return self._currency_rates
            
        except Exception as e:
            print(f"Error fetching currency rates: {e}")
            return {
                'EUR/USD': 1.08,
                'USD/EUR': 0.926
            }
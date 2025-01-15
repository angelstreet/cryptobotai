from typing import Dict, Any, List
import requests
import plotext as plt
from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta
from enum import Enum
from .agent import Agent
from src.utils.display import print_friendly_table

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
BTC = "bitcoin"
ETH = "ethereum"
SOL = "solana"
XRP = "xrp"
DOGE = "dogecoin"

class Exchange(Enum):
    COINGECKO = "coingecko"

class TimeFrame(Enum):
    DAY = "1d"
    WEEK = "7d"
    MONTH = "30d"
    YEAR = "365d"
    YTD = "ytd"

class DataAnalystAgent(Agent):
    def __init__(self, config):
        super().__init__(config)

def coingecko_get_price(crypto_ids: List[str], currency: str = "usd") -> Dict[str, Any]:
    """Fetch current price data from CoinGecko for a list of cryptocurrency IDs."""
    try:
        url = f"{COINGECKO_BASE_URL}/simple/price"
        params = {
            "ids": ",".join(crypto_ids),  # Convert list to comma-separated string
            "vs_currencies": currency,
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true",
            "include_last_updated_at": "true"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = {}
        for crypto_id in crypto_ids:
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
            
            results[crypto_id] = {
                'price': price,  
                'change_24h': change_24h,
                'volume_24h': volume_24h,
                'market_cap': market_cap,
                'last_updated': last_updated_at,
                'exchange': Exchange.COINGECKO.value,
                'symbol': f"{crypto_id}/{currency}",
            }

        #print_friendly_table(data, "CoinGecko Simple Price")  # Debugging: Print the raw API response
        return results
    except Exception as e:
        print(f"Error fetching CoinGecko price: {e}")
        return None

def coingecko_get_historical_data(crypto_id: str, currency: str = "usd", timeframe: TimeFrame = TimeFrame.DAY) -> Dict[str, Any]:
    """
    Fetch historical price data from CoinGecko.

    Args:
        crypto_id: The cryptocurrency ID (e.g., 'bitcoin').
        currency: The currency to get prices in (e.g., 'usd', 'eur').
        timeframe: TimeFrame enum value (7d, 30d, 365d, ytd).

    Returns:
        Dictionary containing historical price data with formatted dates.
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
        
        formatted_data = {
            'prices': [
                {
                    'timestamp': ts,
                    'date': datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d'),
                    'time': datetime.fromtimestamp(ts / 1000).strftime('%H:%M:%S'),
                    'value': value
                }
                for ts, value in data.get('prices', [])
            ],
            'market_caps': [
                {
                    'timestamp': ts,
                    'date': datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d'),
                    'value': value
                }
                for ts, value in data.get('market_caps', [])
            ],
            'total_volumes': [
                {
                    'timestamp': ts,
                    'date': datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d'),
                    'value': value
                }
                for ts, value in data.get('total_volumes', [])
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
    except requests.exceptions.RequestException as e:
        print(f"Error fetching historical data: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def print_coingecko_historical_table(crypto_id: str,currency: str ,timeframe: TimeFrame, data: Dict[str, Any]):
    """
    Print trading chart using rich library.

    Args:
        data: Dictionary containing historical price data.
        symbol: The trading symbol (e.g., 'BTC/USD').
    """
    if not data:
        print("No data to display.")
        return

    console = Console()
    table = Table(title=f"{crypto_id}/{currency} Market Data")
    table.add_column("Time", justify="left", style="cyan")
    table.add_column("Price", justify="right")
    table.add_column("Change", justify="right")
    table.add_column("Volume", justify="right")
    table.add_column("Market Cap", justify="right")
    prices = data.get('prices', [])
    volumes = data.get('total_volumes', [])
    market_caps = data.get('market_caps', [])
    for i in range(1, len(prices)):
        prev_price = prices[i - 1]['value']
        current_price = prices[i]['value']
        time = prices[i]['time']
        price = f"${current_price:,.2f}"
        change = f"{((current_price - prev_price) / prev_price * 100):+.2f}%"
        volume = f"${volumes[i]['value']}"
        market_cap = f"${market_caps[i]['value']}"
        change_style = "red" if "-" in change else "green"
        table.add_row(time, price, change, volume, market_cap, style=change_style)
    console.print(table)

def plot_plotext_chart(crypto_id: str,currency: str , data: Dict[str, Any]):
    """
    Plot price over time using plotext (terminal-based plot).
    """
    if not data:
        print("No data to plot.")
        return

    # Extract timestamps and prices
    timestamps = [price['timestamp'] / 1000 for price in data['prices']]
    prices = [price['value'] for price in data['prices']]
    dates = [datetime.fromtimestamp(ts).strftime('%d/%m/%Y') for ts in timestamps]
    plt.clear_figure()

    # Calculate y-axis limits with some padding
    min_price = min(prices)
    max_price = max(prices)
    price_range = max_price - min_price
    y_min = min_price - (price_range * 0.1)  # Add 10% padding below
    y_max = max_price + (price_range * 0.1)  # Add 10% padding above

    # Plot with explicit y-axis limits
    plt.plot(dates, prices, label=f"{crypto_id}", marker="dot")
    plt.ylim(y_min, y_max)  # Set y-axis limits
    plt.title(f"{crypto_id}/{currency} ({data['metadata']['timeframe']})")
    plt.xlabel("Date")
    plt.ylabel(f"({currency.upper()})") 
    plt.grid(True)
    plt.theme("dark")  
    plt.show()

def coingecko_get_currency_rates() -> Dict[str, Any]:
    """Fetch currency rates from CoinGecko"""
    try:
        url = f"{COINGECKO_BASE_URL}/exchange_rates"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        eur_usd_rate = data['rates']['usd']['value'] / data['rates']['eur']['value']
        usd_eur_rate = 1 / eur_usd_rate
        
        _currency_rates = {
            'EUR/USD': eur_usd_rate,
            'USD/EUR': usd_eur_rate
        }
        
        return _currency_rates
        
    except Exception as e:
        print(f"Error fetching currency rates: {e}")
        return {
            'EUR/USD': 1.08,
            'USD/EUR': 0.926
        }
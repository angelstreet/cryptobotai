import requests

def get_exchange_rates():
    try:
        # Using exchangerate-api.com's free endpoint
        url = "https://api.exchangerate-api.com/v4/latest/EUR"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        eur_usd_rate = data['rates']['USD']
        usd_eur_rate = 1 / eur_usd_rate  # Calculate inverse rate
        
        print(f"EUR/USD: {eur_usd_rate:.4f}")
        print(f"USD/EUR: {usd_eur_rate:.4f}")
        
        return {
            'EUR/USD': round(eur_usd_rate, 4),
            'USD/EUR': round(usd_eur_rate, 4)
        }
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error processing exchange rate data: {e}")
        return None

# Example usage
rates = get_exchange_rates()
if rates:
    print("\nExchange Rates Dictionary:")
    print(rates)
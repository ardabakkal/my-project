import requests
from datetime import datetime

class ExchangeRateService:
    BASE_URL = "https://api.exchangeratesapi.io/v1/latest"
    
    def __init__(self, api_key):
        self.api_key = api_key

    def get_rates(self, base_currency="USD"):
        try:
            params = {
                'access_key': self.api_key,
                'base': base_currency
            }
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('success', True):
                raise ValueError(f"API Error: {data.get('error', {}).get('info', 'Unknown error')}")
                
            return {
                "rates": data['rates'],
                "last_updated": datetime.fromtimestamp(data['timestamp'])
            }
        except Exception as e:
            print(f"API Error: {str(e)}")
            return None
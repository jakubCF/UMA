import requests
import logging
import base64
from requests.exceptions import RequestException, Timeout
from apps.djangocore.utils import get_app_setting

logger = logging.getLogger(__name__)

class UpgatesAPIClient:
    def __init__(self):
        # Fetch Upgates API settings from Django settings
        self.base_url = get_app_setting('UPGATES_API_BASE_URL')
        self.api_key = get_app_setting('UPGATES_API_KEY')
        self.api_login = get_app_setting('UPGATES_API_LOGIN') 

        if not self.base_url or not self.api_key:
            raise ValueError("Upgates API configuration missing in settings.")

        # Create Basic Auth header
        credentials = f"{self.api_login}:{self.api_key}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Basic {encoded_credentials}'
        }

    def _make_request(self, method, endpoint, params=None, json_data=None, timeout=30):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method, url, headers=self.headers, params=params, json=json_data, timeout=timeout
            )
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json() # Assume JSON for most API endpoints

        except Timeout:
            logger.error(f"Upgates API request to {url} timed out.")
            raise
        except RequestException as e:
            logger.error(f"Error making request to Upgates API: {e} - Response: {getattr(e.response, 'text', 'N/A')}")
            raise

    def get_orders(self, **kwargs):
        # Fetch orders from Upgates API
        return self._make_request('GET', '/orders', params=kwargs)



    # Add other methods for specific Upgates API endpoints as needed
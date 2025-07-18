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
            if response.status_code == 204:
                return {} # Return an empty dict for No Content success
            return response.json() # Assume JSON for most API endpoints

        except Timeout:
            logger.error(f"Upgates API request to {url} timed out. (Method: {method}).")
            raise
        except RequestException as e:
            # Log more details including the request payload if possible
            request_payload = json_data or params
            logger.error(
                f"Error making request to Upgates API (Method: {method}, URL: {url}): {e} - "
                f"Request Payload: {request_payload} - "
                f"Response Status: {getattr(e.response, 'status_code', 'N/A')} - "
                f"Response Body: {getattr(e.response, 'text', 'N/A')}"
            )
            raise

    def get_orders(self, **kwargs):
        # Fetch orders from Upgates API
        return self._make_request('GET', '/orders', params=kwargs)

    def get_products_simple(self, **kwargs):
        # Fetch products from Upgates API
        return self._make_request('GET', '/products/simple', params=kwargs)

    def put_product_data(self, data: dict):
        logger.info(f"Sending PUT request to '/products' with data: {data}")
        return self._make_request('PUT', '/products', json_data=data)

    # Add other methods for specific Upgates API endpoints as needed
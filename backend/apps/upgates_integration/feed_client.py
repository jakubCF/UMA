import requests
import xml.etree.ElementTree as ET
import logging
from apps.djangocore.utils import get_app_setting
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger(__name__)

class UpgatesFeedClient:
    def __init__(self):
        self.product_full_feed_url = get_app_setting("UPGATES_PRODUCTS_FULL_XML_URL") # This URL points directly to the XML feed
        self.availability_feed_url = get_app_setting("UPGATES_PRODUCTS_AVAIBILITY_XML_URL") # This URL points to the availability XML feed
        if not self.product_full_feed_url and not self.availability_feed_url:
            raise ValueError("UPGATES_PRODUCTS_FULL_XML_URL or UPGATES_PRODUCTS_AVAIBILITY_XML_URL must be configured in settings.")

    def _fetch_xml_feed(self, url):
        """Helper to fetch and parse an XML feed from a given URL."""
        try:
            response = requests.get(url, timeout=180)
            response.raise_for_status()
            logger.info(f"Successfully fetched XML feed from {url}")
            return ET.fromstring(response.content)
        except Timeout:
            logger.error(f"XML feed download timed out from {url}.")
            raise
        except RequestException as e:
            logger.error(f"Error fetching XML feed from {url}: {e} - Response: {getattr(e.response, 'text', 'N/A')}")
            raise
        except ET.ParseError as e:
            logger.error(f"Error parsing XML feed from {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching/parsing XML feed from {url}: {e}")
            raise

    def get_full_products_xml_feed(self):
        """Fetches the full product XML feed."""
        return self._fetch_xml_feed(self.product_full_feed_url)

    def get_partial_products_xml_feed(self):
        """Fetches the partial product XML feed."""
        if not self.availability_feed_url:
            logger.warning("Partial product feed URL is not configured. Skipping partial feed sync.")
            return None # Or raise an error
        return self._fetch_xml_feed(self.availability_feed_url)
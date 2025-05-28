import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)

class UpgatesProductXMLParser:
    def __init__(self, xml_root):
        if not isinstance(xml_root, ET.Element):
            raise ValueError("xml_root must be an ElementTree Element object.")
        self.xml_root = xml_root

    def _get_text(self, element, tag, default=None):
        """Helper to safely get text from a sub-element."""
        node = element.find(tag)
        if node is not None and node.text is not None:
            return node.text.strip()
        return default

    def _get_bool(self, element, tag, default=False):
        """Helper to safely get boolean from a sub-element (0/1 or true/false)."""
        text = self._get_text(element, tag)
        if text is not None:
            return text.lower() in ['1', 'true', 'yes']
        return default

    def _get_decimal(self, element, tag, default=None):
        """Helper to safely get decimal from a sub-element."""
        text = self._get_text(element, tag)
        if text:
            try:
                return float(text) # Convert to float, DecimalField will handle it
            except ValueError:
                logger.warning(f"Could not convert '{text}' to decimal for tag '{tag}'.")
        return default

    def _parse_prices(self, price_element):
        """Parses price information from a <PRICE> element."""
        prices = {}
        if price_element is None:
            return prices

        # Assuming 'cz' language for now, adjust if you need other languages
        cz_price_node = price_element.find('PRICE[@language="cz"]')
        if cz_price_node is None:
            return prices

        # Extracting from PRICELISTS/PRICELIST
        pricelist_node = cz_price_node.find('PRICELISTS/PRICELIST')
        if pricelist_node:
            prices['price_original'] = self._get_decimal(pricelist_node, 'PRICE_ORIGINAL')
            prices['price_sale'] = self._get_decimal(pricelist_node, 'PRICE_SALE')
            prices['price_with_vat'] = self._get_decimal(pricelist_node, 'PRICE_WITH_VAT')
            prices['price_without_vat'] = self._get_decimal(pricelist_node, 'PRICE_WITHOUT_VAT')

        # Extracting from direct price fields
        prices['price_purchase'] = self._get_decimal(cz_price_node, 'PRICE_PURCHASE')
        prices['currency'] = self._get_text(cz_price_node, 'CURRENCY')
        
        return prices

    def _parse_parameters(self, parameters_element):
        """Parses parameters from a <PARAMETERS> element into a dictionary."""
        params_dict = {}
        if parameters_element is None:
            return params_dict
        for param_node in parameters_element.findall('PARAMETER'):
            name = self._get_text(param_node, 'NAME[@language="cz"]') # Assuming CZ language
            value = self._get_text(param_node, 'VALUE[@language="cz"]') # Assuming CZ language
            if name and value:
                params_dict[name] = value
        return params_dict

    def _get_nested_text(self, element, path, default=None):
        """Safely navigate through nested XML elements and get text."""
        if element is None:
            return default
        
        try:
            # Direct xpath find for the entire path
            found = element.find(path)
            if found is not None and found.text is not None:
                return found.text.strip()
        except Exception:
            logger.warning(f"Failed to find element with path: {path}")
        
        return default

    def _get_main_image_url(self, element):
        """Get the URL of the main image (MAIN_YN="1")"""
        images = element.find('IMAGES')
        if images is not None:
            for image in images.findall('IMAGE'):
                if self._get_text(image, 'MAIN_YN') == '1':
                    return self._get_text(image, 'URL')
        return None

    def parse_product(self, product_node):
        """Parses a single <PRODUCT> XML element."""
        product_data = {
            'code': self._get_text(product_node, 'CODE'),
            'product_id': self._get_text(product_node, 'PRODUCT_ID'),
            'title': self._get_nested_text(product_node, './/DESCRIPTION[@language="cz"]/TITLE'),
            'manufacturer': self._get_text(product_node, 'MANUFACTURER'),
            'ean': self._get_text(product_node, 'EAN'),
            'supplier_code': self._get_text(product_node, 'SUPPLIER_CODE'),
            'availability': self._get_text(product_node, 'AVAILABILITY'),
            'stock': self._get_text(product_node, 'STOCK', '0'),
            'stock_position': self._get_text(product_node, 'STOCK_POSITION'),
            'weight': self._get_decimal(product_node, 'WEIGHT', 0),
            'unit': self._get_text(product_node, 'UNIT'),
            'image_url': self._get_main_image_url(product_node),
        }

        # Convert product_id and stock to integers safely
        try:
            if product_data['product_id']:
                product_data['product_id'] = int(product_data['product_id'])
            if product_data['stock']:
                product_data['stock'] = int(product_data['stock'])
        except (ValueError, TypeError):
            product_data['product_id'] = None
            product_data['stock'] = 0

        return product_data

    def parse_variant(self, variant_node):
        """Parses a single <VARIANT> XML element."""
        variant_data = {
            'code': self._get_text(variant_node, 'CODE'),
            'variant_id': self._get_text(variant_node, 'VARIANT_ID'),
            'supplier_code': self._get_text(variant_node, 'SUPPLIER_CODE'),
            'ean': self._get_text(variant_node, 'EAN'),
            'availability': self._get_text(variant_node, 'AVAILABILITY'),
            'stock': self._get_text(variant_node, 'STOCK', '0'),
            'stock_position': self._get_text(variant_node, 'STOCK_POSITION'),
            'weight': self._get_decimal(variant_node, 'WEIGHT', 0),
            'image_url': self._get_text(variant_node, 'IMAGE_URL'),
            'prices': self._parse_prices(variant_node.find('PRICES')),
            'parameters': self._parse_parameters(variant_node.find('PARAMETERS')),
        }

        # Convert variant_id and stock to integers safely
        try:
            if variant_data['variant_id']:
                variant_data['variant_id'] = int(variant_data['variant_id'])
            if variant_data['stock']:
                variant_data['stock'] = int(variant_data['stock'])
        except (ValueError, TypeError):
            variant_data['variant_id'] = None
            variant_data['stock'] = 0

        return variant_data

    def get_all_products_data(self):
        """Iterates through all products and their variants in the XML."""
        products_data = []
        for product_node in self.xml_root.findall('PRODUCT'):
            product_info = self.parse_product(product_node)
            
            # Parse variants for this product
            product_info['variants'] = []
            variants_node = product_node.find('VARIANTS')
            if variants_node is not None:
                for variant_node in variants_node.findall('VARIANT'):
                    variant_info = self.parse_variant(variant_node)
                    product_info['variants'].append(variant_info)
            
            products_data.append(product_info)
        return products_data
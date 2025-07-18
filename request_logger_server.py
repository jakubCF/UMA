import http.server
import socketserver
import json
import logging
import os
from email.parser import Parser

# Configure logging for the server itself
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PORT = 8001 # Choose a port that doesn't conflict with your Django server (usually 8000)

class RequestLoggerHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def parse_content_type(self, content_type):
        """Parse content type header into main type and parameters"""
        if not content_type:
            return '', {}
        
        # Split content type and parameters
        parts = content_type.split(';')
        content_type = parts[0].strip()
        
        # Parse parameters
        params = {}
        for param in parts[1:]:
            if '=' in param:
                key, value = param.split('=', 1)
                params[key.strip()] = value.strip().strip('"\'')
                
        return content_type, params

    def do_POST(self):
        logger.info(f"\n--- POST Request ---")
        logger.info(f"Path: {self.path}")
        logger.info(f"Headers:\n{self.headers}")
        self._set_headers()
        response_data = {'message': 'POST request received', 'path': self.path}
        self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def do_PUT(self):
        logger.info(f"\n--- PUT Request ---")
        logger.info(f"Path: {self.path}")
        logger.info(f"Headers:\n{self.headers}")

        # Get content length from headers
        content_length = int(self.headers.get('Content-Length', 0))
        
        # Read request body data
        request_body = self.rfile.read(content_length)

        logger.info(f"Body: {request_body.decode('utf-8')}")
        # if request data contains code 'P00018', return dummy orders response

        if b'"P00018-10"' in request_body:
            dummy_response = {
                "products": [
                    {
                        "code": "P00018",
                        "product_id": 180,
                        "updated_yn": True,
                        "messages": [
                            {
                            "object": None,
                            "property": None,
                            "message": "",
                            "level": "info"
                            }
                        ],
                        "variants": [
                            {
                                "code": "P00018-10",
                                "variant_id": 1303,
                                "updated_yn": True,
                                "messages": [
                                    {
                                    "object": None,
                                    "property": None,
                                    "message": "",
                                    "level": "info"
                                    }
                                ],
                            }
                        ],
                    }
                ]
            }
            self._set_headers()
            self.wfile.write(json.dumps(dummy_response).encode('utf-8'))
        else:
            # Default response for other endpoints
            self._set_headers()
            response_data = {'message': 'PUT request received', 'path': self.path}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

    def do_GET(self):
        logger.info(f"\n--- GET Request ---")
        logger.info(f"Path: {self.path}")
        logger.info(f"Headers:\n{self.headers}")

        if self.path == '/export-full.xml':
            try:
                # Get the directory of the current script
                current_dir = os.path.dirname(os.path.abspath(__file__))
                xml_path = os.path.join(current_dir, 'export-full.xml')
                
                with open(xml_path, 'rb') as f:
                    self._set_headers(200, 'application/xml')
                    self.wfile.write(f.read())
                return
            except FileNotFoundError:
                self._set_headers(404, 'application/json')
                self.wfile.write(json.dumps({'error': 'XML file not found'}).encode('utf-8'))
                return
            except Exception as e:
                self._set_headers(500, 'application/json')
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
                return
        
        elif self.path == '/export-partial.xml':
            try:
                # Get the directory of the current script
                current_dir = os.path.dirname(os.path.abspath(__file__))
                xml_path = os.path.join(current_dir, 'export-partial.xml')
                
                with open(xml_path, 'rb') as f:
                    self._set_headers(200, 'application/xml')
                    self.wfile.write(f.read())
                return
            except FileNotFoundError:
                self._set_headers(404, 'application/json')
                self.wfile.write(json.dumps({'error': 'XML file not found'}).encode('utf-8'))
                return
            except Exception as e:
                self._set_headers(500, 'application/json')
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
                return

        # Handle /orders endpoint directly
        elif '/orders' in self.path:
            self._set_headers(200, 'application/json')
            dummy_orders_response = {
                "current_page": 1,
                "current_page_items": 1,
                "number_of_pages": 1,
                "number_of_items": 1,
                "orders": [
                    {
                        "order_number": "O2205022",
                        "order_id": 8093,
                        "case_number": None,
                        "external_order_number": None,
                        "uuid": "967a7acf-ecd0-49dc-8bd3-bf68d97f5162",
                        "language_id": "cs",
                        "currency_id": "CZK",
                        "default_currency_rate": 1,
                        "prices_with_vat_yn": True,
                        "status_id": 23,
                        "status": "Připraveno k odeslání",
                        "paid_date": "2025-05-27",
                        "tracking_code": "55998877",
                        "tracking_url": "https://tracking.packeta.com/cs_CZ/?id=55998877",
                        "statistics_yn": True,
                        "resolved_yn": True,
                        "oss_yn": False,
                        "internal_note": None,
                        "last_update_time": "2025-05-27T18:20:07+02:00",
                        "creation_time": "2025-05-27T09:19:01+02:00",
                        "variable_symbol": "2205022",
                        "dimensions": {
                            "width": None,
                            "length": None,
                            "height": None
                        },
                        "total_weight": 120,
                        "order_total": 577,
                        "order_total_before_round": 577,
                        "order_total_rest": 0,
                        "invoice_number": "I2500485",
                        "origin": "frontend",
                        "admin_url": "https://eshopname.admin.s1.upgates.com/links/orders/967a7acf-ecd0-49dc-8bd3-bf68d97f5162",
                        "customer": {
                            "email": "email-of-customer@example.com",
                            "phone": "+420 777789896",
                            "code": "C05335",
                            "customer_id": 5324,
                            "customer_pricelist_id": 1,
                            "pricelist_name": "Výchozí",
                            "pricelist_percent": None,
                            "firstname_invoice": "Jan",
                            "surname_invoice": "Novák",
                            "street_invoice": None,
                            "city_invoice": None,
                            "state_invoice": None,
                            "zip_invoice": None,
                            "country_id_invoice": "cz",
                            "postal_yn": True,
                            "firstname_postal": "Jan",
                            "surname_postal": "Novák",
                            "street_postal": "Hlavní 53",
                            "city_postal": "Praha",
                            "state_postal": None,
                            "zip_postal": "15000",
                            "country_id_postal": "cz",
                            "company_postal": "Zásilkovna - Elektro Helkon",
                            "company_yn": False,
                            "company": None,
                            "ico": None,
                            "dic": None,
                            "vat_payer_yn": False,
                            "customer_note": "",
                            "agreements": [
                                {
                                    "name": "Obchodní podmínky",
                                    "valid_to": None,
                                    "status": True
                                },
                                {
                                    "name": "Heureka odmitnuti",
                                    "valid_to": "2026-05-27T09:19:02+02:00",
                                    "status": False
                                }
                            ]
                        },
                        "products": [
                            {
                                "product_id": 241,
                                "option_set_id": 2629,
                                "type": "product",
                                "uuid": "bf229209-ba4a-4bb8-aa99-64834b67c7c2",
                                "parent_uuid": None,
                                "code": "P00199-14",
                                "code_supplier": "WLJ-767M",
                                "supplier": None,
                                "ean": "8596445056174",
                                "title": "Lasting středně silné merino ponožky WLJ",
                                "adult_yn": False,
                                "unit": "ks",
                                "length": None,
                                "length_unit": "ks",
                                "quantity": 1,
                                "price_per_unit": 249,
                                "price_per_unit_with_vat": 249,
                                "price_per_unit_without_vat": 205.79,
                                "price": 249,
                                "price_with_vat": 249,
                                "price_without_vat": 205.79,
                                "vat": 21,
                                "buy_price": 50.04,
                                "recycling_fee": None,
                                "weight": 60,
                                "availability": "Skladem",
                                "stock_position": None,
                                "invoice_info": "",
                                "parameters": [
                                    {
                                        "name": "Velikost",
                                        "value": "38-41"
                                    },
                                    {
                                        "name": "Barva",
                                        "value": "Tmavě zelená"
                                    }
                                ],
                                "configurations": [],
                                "categories": [
                                    {
                                        "category_id": 41,
                                        "code": None
                                    },
                                    {
                                        "category_id": 62,
                                        "code": None
                                    },
                                    {
                                        "category_id": 102,
                                        "code": None
                                    },
                                    {
                                        "category_id": 150,
                                        "code": None
                                    },
                                    {
                                        "category_id": 162,
                                        "code": None
                                    }
                                ],
                                "image_url": "https://eshopname.s1.cdn-upgates.com/r/r65689bbde7534-lasting-merino-ponozky-wlj-zelene.webp"
                            },
                            {
                                "product_id": 241,
                                "option_set_id": 2433,
                                "type": "product",
                                "uuid": "5f62996e-79a4-47a1-b272-661e38e671de",
                                "parent_uuid": None,
                                "code": "P00199-10",
                                "code_supplier": "WLJ-858M",
                                "supplier": None,
                                "ean": "8596445056211",
                                "title": "Lasting středně silné merino ponožky WLJ",
                                "adult_yn": False,
                                "unit": "ks",
                                "length": None,
                                "length_unit": "ks",
                                "quantity": 1,
                                "price_per_unit": 249,
                                "price_per_unit_with_vat": 249,
                                "price_per_unit_without_vat": 205.79,
                                "price": 249,
                                "price_with_vat": 249,
                                "price_without_vat": 205.79,
                                "vat": 21,
                                "buy_price": 50.04,
                                "recycling_fee": None,
                                "weight": 60,
                                "availability": "Poslední kusy",
                                "stock_position": None,
                                "invoice_info": "",
                                "parameters": [
                                    {
                                        "name": "Velikost",
                                        "value": "38-41"
                                    },
                                    {
                                        "name": "Barva",
                                        "value": "Šedá"
                                    }
                                ],
                                "configurations": [],
                                "categories": [
                                    {
                                        "category_id": 41,
                                        "code": None
                                    },
                                    {
                                        "category_id": 62,
                                        "code": None
                                    },
                                    {
                                        "category_id": 102,
                                        "code": None
                                    },
                                    {
                                        "category_id": 150,
                                        "code": None
                                    },
                                    {
                                        "category_id": 162,
                                        "code": None
                                    }
                                ],
                                "image_url": "https://eshopname.s1.cdn-upgates.com/j/j6533d8b04973f-lasting-merino-ponozky-wlj-sede.webp"
                            }
                        ],
                        "discount_voucher": None,
                        "quantity_discount": None,
                        "loyalty_points": None,
                        "shipment": {
                            "id": 5,
                            "code": "ZAS",
                            "name": "Zásilkovna",
                            "price": 79,
                            "price_with_vat": 79,
                            "price_without_vat": 65.29,
                            "vat": 21,
                            "affiliate_id": "548",
                            "affiliate_name": "Elektro Helkon",
                            "type": "zasilkovna",
                            "packeta_carrier_id": 0
                        },
                        "payment": {
                            "id": 23,
                            "code": None,
                            "name": "Comgate",
                            "price": 0,
                            "price_with_vat": 0,
                            "price_without_vat": 0,
                            "vat": 21,
                            "eet_yn": False,
                            "type": "comgate"
                        },
                        "attachments": [],
                        "metas": [
                            {
                                "key": "invoice_note",
                                "type": "textarea",
                                "value": ""
                            }
                        ]
                    }
                ]
            }
            self.wfile.write(json.dumps(dummy_orders_response).encode('utf-8'))
        # Handle /products/simple endpoint directly
        elif '/products/simple' in self.path:
            self._set_headers(200, 'application/json')
            dummy_orders_response = {
                "current_page": 1,
                "current_page_items": 1,
                "number_of_pages": 1,
                "number_of_items": 1,
                "products": [
                    {
                        "code": "P00147",
                        "product_id": 180,
                        "code_supplier": "Optimus",
                        "supplier": None,
                        "ean": None,
                        "active_yn": True,
                        "archived_yn": False,
                        "replacement_product_code": None,
                        "can_add_to_basket_yn": True,
                        "adult_yn": False,
                        "set_yn": False,
                        "in_set_yn": False,
                        "exclude_from_search_yn": False,
                        "manufacturer": "Voxx",
                        "stock": 0,
                        "stock_position": None,
                        "availability_id": 3,
                        "availability": "Není skladem",
                        "availability_type": "NotAvailable",
                        "limit_orders": None,
                        "weight": 50,
                        "shipment_group": None,
                        "stocks": [],
                        "groups": [],
                        "variants": [
                            {
                                "code": "P00147-1",
                                "variant_id": 1303,
                                "code_supplier": None,
                                "ean": "8596281055584",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 3,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": 46,
                                "image": "https://eshoppage.s1.cdn-upgates.com/t/t64f8989fe9438-optimus-cerna.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-2",
                                "variant_id": 1304,
                                "code_supplier": None,
                                "ean": "8596281055669",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 6,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": 50,
                                "image": "https://eshoppage.s1.cdn-upgates.com/t/t64f8989fe9438-optimus-cerna.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-3",
                                "variant_id": 1305,
                                "code_supplier": None,
                                "ean": "8596281055737",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 3,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": 57,
                                "image": "https://eshoppage.s1.cdn-upgates.com/t/t64f8989fe9438-optimus-cerna.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-4",
                                "variant_id": 1306,
                                "code_supplier": None,
                                "ean": "8596281055522",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 2,
                                "stock_position": None,
                                "availability_id": 4,
                                "availability": "Poslední kusy",
                                "availability_type": "InStock",
                                "weight": 45,
                                "image": "https://eshoppage.s1.cdn-upgates.com/z/z64f898a16c8f3-optimus-modro-zelena.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-5",
                                "variant_id": 1307,
                                "code_supplier": None,
                                "ean": "8596281055607",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 5,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": 50,
                                "image": "https://eshoppage.s1.cdn-upgates.com/z/z64f898a16c8f3-optimus-modro-zelena.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-6",
                                "variant_id": 1308,
                                "code_supplier": None,
                                "ean": "8596281055683",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 3,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": 57,
                                "image": "https://eshoppage.s1.cdn-upgates.com/z/z64f898a16c8f3-optimus-modro-zelena.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-7",
                                "variant_id": 1309,
                                "code_supplier": None,
                                "ean": "8596281055515",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 3,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": 45,
                                "image": "https://eshoppage.s1.cdn-upgates.com/f/f64f898a1151be-optimus-bila.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-8",
                                "variant_id": 1310,
                                "code_supplier": None,
                                "ean": "8596281055591",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 6,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": 50,
                                "image": "https://eshoppage.s1.cdn-upgates.com/f/f64f898a1151be-optimus-bila.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-9",
                                "variant_id": 1311,
                                "code_supplier": None,
                                "ean": "8596281055676",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 5,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": 50,
                                "image": "https://eshoppage.s1.cdn-upgates.com/f/f64f898a1151be-optimus-bila.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-10",
                                "variant_id": 1935,
                                "code_supplier": None,
                                "ean": "8596281055645",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 6,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/j/j64f898a03175f-optimus-tm-modra.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-11",
                                "variant_id": 1936,
                                "code_supplier": None,
                                "ean": "8596281055713",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 3,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/j/j64f898a03175f-optimus-tm-modra.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-12",
                                "variant_id": 2179,
                                "code_supplier": None,
                                "ean": "8596281055577",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 4,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/1/164f898a04c4a7-optimus-tm-seda.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-13",
                                "variant_id": 2180,
                                "code_supplier": None,
                                "ean": "8596281055652",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 7,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/1/164f898a04c4a7-optimus-tm-seda.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-14",
                                "variant_id": 2181,
                                "code_supplier": None,
                                "ean": "8596281055720",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 6,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/1/164f898a04c4a7-optimus-tm-seda.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-15",
                                "variant_id": 2229,
                                "code_supplier": None,
                                "ean": "8596281055553",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 2,
                                "stock_position": None,
                                "availability_id": 4,
                                "availability": "Poslední kusy",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/v/v64f898a076b15-optimus-seda.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-16",
                                "variant_id": 2230,
                                "code_supplier": None,
                                "ean": "8596281055638",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 6,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/v/v64f898a076b15-optimus-seda.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-17",
                                "variant_id": 2231,
                                "code_supplier": None,
                                "ean": "8596281055706",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 6,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/v/v64f898a076b15-optimus-seda.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-18",
                                "variant_id": 2232,
                                "code_supplier": None,
                                "ean": "8596281055546",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 2,
                                "stock_position": None,
                                "availability_id": 4,
                                "availability": "Poslední kusy",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/c/c64f898a14657a-optimus-ruzova.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-19",
                                "variant_id": 2233,
                                "code_supplier": None,
                                "ean": "8596281055621",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 5,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/c/c64f898a14657a-optimus-ruzova.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-20",
                                "variant_id": 2234,
                                "code_supplier": None,
                                "ean": None,
                                "active_yn": False,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 0,
                                "stock_position": None,
                                "availability_id": 3,
                                "availability": "Není skladem",
                                "availability_type": "NotAvailable",
                                "weight": None,
                                "image": None,
                                "stocks": []
                            },
                            {
                                "code": "P00147-21",
                                "variant_id": 2235,
                                "code_supplier": None,
                                "ean": "8596281055539",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 2,
                                "stock_position": None,
                                "availability_id": 4,
                                "availability": "Poslední kusy",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/v/v64f898a0153eb-optimus-modra.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-22",
                                "variant_id": 2236,
                                "code_supplier": None,
                                "ean": "8596281055614",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 7,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/v/v64f898a0153eb-optimus-modra.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-23",
                                "variant_id": 2237,
                                "code_supplier": None,
                                "ean": "8596281055690",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 3,
                                "stock_position": None,
                                "availability_id": 2,
                                "availability": "Skladem",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/v/v64f898a0153eb-optimus-modra.webp",
                                "stocks": []
                            },
                            {
                                "code": "P00147-24",
                                "variant_id": 2712,
                                "code_supplier": None,
                                "ean": "8596281055560",
                                "active_yn": None,
                                "main_yn": False,
                                "can_add_to_basket_yn": None,
                                "stock": 1,
                                "stock_position": None,
                                "availability_id": 4,
                                "availability": "Poslední kusy",
                                "availability_type": "InStock",
                                "weight": None,
                                "image": "https://eshoppage.s1.cdn-upgates.com/j/j64f898a03175f-optimus-tm-modra.webp",
                                "stocks": []
                            }
                        ],
                        "creation_time": "2022-01-11T22:06:00+01:00",
                        "last_update_time": "2025-05-28T14:02:13+02:00",
                        "admin_url": "https://eshoppage.admin.s1.upgates.com/manager/products/main/default/180"
                    }
                ]
            }
            self.wfile.write(json.dumps(dummy_orders_response).encode('utf-8'))
        else:
            # Default response for other endpoints
            self._set_headers()
            response_data = {'message': 'GET request received', 'path': self.path}
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

if __name__ == "__main__":
    # Avoid "Address already in use" error by allowing port reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), RequestLoggerHandler) as httpd:
        logger.info(f"Serving HTTP request logger on port {PORT}")
        logger.info(f"Open http://localhost:{PORT} in your browser to test GET.")
        logger.info(f"Point your API client to http://localhost:{PORT}/api/some/endpoint")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("\nShutting down the server...")
            httpd.server_close()

import http.server
import socketserver
import json
import logging
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

    def do_GET(self):
        logger.info(f"\n--- GET Request ---")
        logger.info(f"Path: {self.path}")
        logger.info(f"Headers:\n{self.headers}")

        # Handle /orders endpoint directly
        if '/orders' in self.path:
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

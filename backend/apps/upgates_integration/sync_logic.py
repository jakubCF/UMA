import logging
from datetime import datetime
from django.db import transaction, IntegrityError
from django.utils import timezone
import pytz # Import pytz

from apps.orders.models import Order, OrderItem
from apps.products.models import Product, ProductVariant, ProductStockAdjustment
from .api_client import UpgatesAPIClient
from .feed_client import UpgatesFeedClient
from .xml_parser import UpgatesProductXMLParser 

logger = logging.getLogger(__name__)

def sync_orders_from_api(creation_time_from=None, status_ids=None):
    """
    Retrieves orders from the Upgates API, optionally filtering by creation_time_from.
    """
    client = UpgatesAPIClient()
    # Start at page 1 for the API
    current_page = 1 
    # Initialize total pages to a value that ensures the loop runs at least once
    number_of_pages = 1

    synced_count = 0 # Count of successfully synced orders

    # Define the Prague timezone
    prague_tz = pytz.timezone('Europe/Prague')

    while current_page <= number_of_pages:
        params = {'page': current_page} 
        if creation_time_from:
            # 'creation_time_from' or similar to filter orders
            params['creation_time_from'] = creation_time_from.isoformat()
        if status_ids:
            params['status_ids'] = status_ids
        try:
            orders_response, return_code = client.get_orders(**params)

            # --- UPDATED PAGINATION CHECK ---
            orders_list = orders_response.get('orders', []) # Actual list of order data
            # Update number_of_pages based on the API response, if available
            # This ensures the loop correctly identifies the total number of pages
            if 'number_of_pages' in orders_response:
                number_of_pages = orders_response['number_of_pages']
            # --------------------------------

            logger.info(f"Retrieved {len(orders_list)} orders from Upgates API (page {current_page}/{number_of_pages}).")

            if not orders_list:
                # If the current page returns no orders, and it's not the last expected page, something might be off,
                # but if current_page > number_of_pages, the loop will naturally end.
                break 

            for order_api_data in orders_list:
                try:
                    with transaction.atomic():
                        order_number = order_api_data.get('order_number')
                        if not order_number:
                            logger.warning("Skipping order with no order_number.")
                            continue

                        # Convert datetime strings from API to datetime objects
                        creation_time_str = order_api_data.get('creation_time')
                        last_update_time_str = order_api_data.get('last_update_time')
                        paid_date_str = order_api_data.get('paid_date')

                        if creation_time_str:
                            dt_object = datetime.fromisoformat(creation_time_str)
                            if dt_object.tzinfo is None:
                                creation_time = prague_tz.localize(dt_object)
                            else:
                                creation_time = dt_object
                        else:
                            creation_time = None
                        
                        if last_update_time_str:
                            dt_object = datetime.fromisoformat(last_update_time_str)
                            if dt_object.tzinfo is None:
                                last_update_time = prague_tz.localize(dt_object)
                            else:
                                last_update_time = dt_object
                        else:
                            last_update_time = None
                        
                        if paid_date_str:
                            dt_object = datetime.fromisoformat(paid_date_str)
                            if dt_object.tzinfo is None:
                                paid_date = prague_tz.localize(dt_object)
                            else:
                                paid_date = dt_object
                        else:
                            paid_date = None

                        # Map API JSON fields to your Django model fields
                        order_defaults = {
                            'order_id': order_api_data.get('order_id'), # Assuming this is an int
                            'case_number': order_api_data.get('case_number'),
                            'external_order_number': order_api_data.get('external_order_number'),
                            'uuid': order_api_data.get('uuid'),
                            'language_id': order_api_data.get('language_id'),
                            'currency_id': order_api_data.get('currency_id'),
                            'default_currency_rate': order_api_data.get('default_currency_rate'),
                            'prices_with_vat_yn': order_api_data.get('prices_with_vat_yn'),
                            'status_id': order_api_data.get('status_id'),
                            'status': order_api_data.get('status'),
                            'paid_date': paid_date,
                            'tracking_code': order_api_data.get('tracking_code'),
                            'tracking_url': order_api_data.get('tracking_url'),
                            'statistics_yn': order_api_data.get('statistics_yn'),
                            'resolved_yn': order_api_data.get('resolved_yn'),
                            'oss_yn': order_api_data.get('oss_yn'),
                            'internal_note': order_api_data.get('internal_note'),
                            'last_update_time': last_update_time,
                            'creation_time': creation_time,
                            'variable_symbol': order_api_data.get('variable_symbol'),
                            'total_weight': order_api_data.get('total_weight'),
                            'order_total': order_api_data.get('order_total'),
                            'order_total_before_round': order_api_data.get('order_total_before_round'),
                            'order_total_rest': order_api_data.get('order_total_rest'),
                            'invoice_number': order_api_data.get('invoice_number'),
                            'admin_url': order_api_data.get('admin_url'),

                            # JSONFields - store the raw dictionary/list
                            'customer': order_api_data.get('customer'),
                            'discount_voucher': order_api_data.get('discount_voucher'),
                            'quantity_discount': order_api_data.get('quantity_discount'),
                            'loyalty_points': order_api_data.get('loyalty_points'),
                            'shipment': order_api_data.get('shipment'),
                            'payment': order_api_data.get('payment'),
                            'attachments': order_api_data.get('attachments'),
                            'metas': order_api_data.get('metas'),

                            # Your internal fields
                            # 'pg_status': This would be updated by your fullfilment logic
                            'uma_updated_at': timezone.now(),
                        }
                        order_obj, created = Order.objects.update_or_create(
                            order_number=order_number, # Use a unique external identifier
                            defaults=order_defaults
                        )
                        if created:
                            logger.info(f"Created new Order: {order_obj.order_number}")
                        else:
                            logger.debug(f"Updated Order: {order_obj.order_number}")

                        # --- Sync Order Items ---
                        api_items = order_api_data.get('products', [])
                        # Delete existing items for this order that are not in the API response (simplest for full sync)
                        # More complex: update_or_create for each, then delete any remaining in DB not in API list
                        order_obj.items.exclude(uuid__in=[item['uuid'] for item in api_items if 'uuid' in item]).delete() # Be careful with this!

                        for item_api_data in api_items:
                            # Map item fields
                            item_defaults = {
                                'product_id': item_api_data.get('product_id'),
                                'options_set_id': item_api_data.get('options_set_id'),
                                'type': item_api_data.get('type'),
                                'uuid': item_api_data.get('uuid'),
                                'parent_uuid': item_api_data.get('parent_uuid'),
                                'code': item_api_data.get('code'),
                                'code_supplier': item_api_data.get('code_supplier'),
                                'supplier': item_api_data.get('supplier'),
                                'ean': item_api_data.get('ean'),
                                'title': item_api_data.get('title'),
                                'adult_yn': item_api_data.get('adult_yn', False), # Provide default for boolean
                                'unit': item_api_data.get('unit'),
                                'length': item_api_data.get('length'),
                                'length_unit': item_api_data.get('length_unit'),
                                'quantity': item_api_data.get('quantity'),
                                'price_per_unit': item_api_data.get('price_per_unit'),
                                'price_per_unit_with_vat': item_api_data.get('price_per_unit_with_vat'),
                                'price_per_unit_without_vat': item_api_data.get('price_per_unit_without_vat'),
                                'price': item_api_data.get('price'),
                                'price_with_vat': item_api_data.get('price_with_vat'),
                                'price_without_vat': item_api_data.get('price_without_vat'),
                                'vat': item_api_data.get('vat'),
                                'buy_price': item_api_data.get('buy_price'),
                                'recycling_fee': item_api_data.get('recycling_fee'),
                                'weight': item_api_data.get('weight'),
                                'availability': item_api_data.get('availability'),
                                'stock_position': item_api_data.get('stock_position'),
                                'invoice_info': item_api_data.get('invoice_info'),
                                'parameters': item_api_data.get('parameters'),
                                'configurations': item_api_data.get('configurations'),
                                'categories': item_api_data.get('categories'),
                                'image_url': item_api_data.get('image_url'),
                            }
                            # Use a combination of order and API-provided product_id/uuid for uniqueness
                            OrderItem.objects.update_or_create(
                                order=order_obj,
                                # Assuming product_id from API is unique per order item
                                uuid=item_api_data.get('uuid'),
                                defaults=item_defaults
                            )
                        synced_count += 1

                except IntegrityError as ie:
                    logger.error(f"Integrity error during order sync for order_number {order_number}: {ie}")
                    # Could happen if multiple syncs create the same order
                except Exception as e:
                    logger.error(f"Unhandled error during order sync for order_number {order_number}: {e}")
                    # Continue to next order even if one fails

            current_page += 1 # Move to the next page

        except Exception as e:
            logger.error(f"Failed to retrieve orders from Upgates API (page {current_page}): {e}")
            number_of_pages = 0 # Stop on error

    logger.info(f"Order synchronization complete. Synced {synced_count} orders.")
    return True

def sync_orders_status_to_api(orderids, status_id):
    client = UpgatesAPIClient()

    if not status_id:
        logger.error("No status_id provided for order status update.")
        return False
    if not isinstance(orderids, list):
        logger.warning(f"Order IDs provided are not a list: {orderids}")
        return False
    
    data = {'send_emails_yn': False, 'send_sms_yn': False, 'orders': []}

    for order_id in orderids:
        try:
            order = Order.objects.get(id=order_id)
            data['orders'].append({
                'order_number': order.order_number,
                'status_id': status_id,
            })
        except Order.DoesNotExist:
            logger.error(f"Order with ID {order_id} does not exist.")
            continue

    response, return_code = client.put_order_data(data)

    if return_code == 200:
        logger.info(f"Successfully updated order statuses in Upgates API for orders: {orderids}")
        return True
    else:
        logger.error(f"Failed to update order statuses in Upgates API: {response.get('error', 'Unknown error')}")
        return False

def sync_products_simple_from_api(codes=None):
    """
    Retrieves products from the Upgates API, optionally filtering by product_ids
    """
    client = UpgatesAPIClient()
    # Start at page 1 for the API
    current_page = 1 
    # Initialize total pages to a value that ensures the loop runs at least once
    number_of_pages = 1

    synced_count = 0 # Count of successfully synced products

    # if codes is list, convert to comma-separated string for API
    if isinstance(codes, list):
        codes = ';'.join(codes)
    elif isinstance(codes, str):
        # check if it's string of codes separated by semicolons
        codes = codes.strip().replace(' ', '') # Clean up spaces
        if ',' in codes:
            codes = codes.replace(',', ';') # Convert commas to semicolons if needed

    while current_page <= number_of_pages:
        params = {'page': current_page} 
        if codes:
            params['codes'] = codes

        try:
            response, return_code = client.get_products_simple(**params)

            # --- UPDATED PAGINATION CHECK ---
            products_list = response.get('products', [])
            # Update number_of_pages based on the API response, if available
            # This ensures the loop correctly identifies the total number of pages
            if 'number_of_pages' in response:
                number_of_pages = response['number_of_pages']
            # --------------------------------

            logger.info(f"Retrieved {len(products_list)} products from Upgates API (page {current_page}/{number_of_pages}).")

            if not products_list:
                # If the current page returns no products, and it's not the last expected page, something might be off,
                # but if current_page > number_of_pages, the loop will naturally end.
                break 

            for product_api_data in products_list:
                try:
                    with transaction.atomic():
                        product_code = product_api_data.get('code')
                        if not product_code:
                            logger.warning("Skipping product with no code.")
                            continue

                        # Map API JSON fields to your Django model fields
                        product_defaults = {
                            'code_supplier': product_api_data.get('code_supplier'),
                            'ean': product_api_data.get('ean'),
                            'product_id': product_api_data.get('product_id'),
                            'manufacturer': product_api_data.get('manufacturer'),
                            'availability_id': product_api_data.get('availability_id'),
                            'availability': product_api_data.get('availability'),
                            'stock': product_api_data.get('stock', 0),
                            'stock_position': product_api_data.get('stock_position'),
                            'weight': product_api_data.get('weight'),
                            'uma_is_active': True,
                            'uma_last_synced_at': timezone.now(),
                        }
                        # Use the unique code as the identifier
                        product_obj, created = Product.objects.update_or_create(
                            code=product_code, # Use 'code' as the unique identifier
                            defaults=product_defaults
                        )
                        if created:
                            logger.info(f"Created new Product: {product_obj.title} (Code: {product_obj.code})")
                        else:
                            logger.debug(f"Updated Product: {product_obj.title} (Code: {product_obj.code})")
                        
                        # --- Sync Product Variants ---
                        variants_data = product_api_data.get('variants', [])
                        for variant_data in variants_data:
                            variant_code = variant_data.get('code')
                            if not variant_code:
                                logger.warning(f"Skipping variant with no CODE for product {product_code}: {variant_data}")
                                continue

                            variant_defaults = {
                                'product': product_obj, # Link to the parent product
                                'code_supplier': variant_data.get('code_supplier'),
                                'ean': variant_data.get('ean'),
                                'variant_id': variant_data.get('variant_id'),
                                'stock': variant_data.get('stock', 0),
                                'stock_position': variant_data.get('stock_position'),
                                'availability_id': variant_data.get('availability_id'),
                                'availability': variant_data.get('availability'),
                            }
                            # Use 'code' as the unique identifier for variant
                            variant_obj, v_created = ProductVariant.objects.update_or_create(
                                code=variant_code, # Use 'code' as the unique identifier for variant
                                defaults=variant_defaults
                            )
                            if v_created:
                                logger.info(f"  Created new Variant: {variant_obj.code} (Product: {product_obj.code})")
                            else:
                                logger.debug(f"  Updated Variant: {variant_obj.code} (Product: {product_obj.code})")
                                
                        synced_count += 1 # Increment synced count for each product
                except IntegrityError as ie:
                    logger.error(f"Integrity error during product sync for product_code {product_code}: {ie}")
                    # Could happen if multiple syncs create the same product
                except Exception as e:
                    logger.error(f"Unhandled error during product sync for product_code {product_code}: {e}")
                    # Continue to next product even if one fails

            current_page += 1 # Move to the next page

        except Exception as e:
            logger.error(f"Failed to retrieve products from Upgates API (page {current_page}): {e}")
            number_of_pages = 0 # Stop on error

    logger.info(f"Product synchronization complete. Synced {synced_count} products.")
    return True

def sync_products_from_full_feed ():
    """
    Retrieves the full product XML feed, parses it, and syncs products/variants.
    """
    feed_client = UpgatesFeedClient()
    try:
        xml_root = feed_client.get_full_products_xml_feed()
        logger.info("Successfully retrieved Upgates product XML feed.")
    except Exception as e:
        logger.error(f"Failed to retrieve Upgates product feed: {e}")
        return False

    parser = UpgatesProductXMLParser(xml_root)
    all_products_data = parser.get_all_products_data()

    # Keep track of product and variant codes found in this sync to deactivate missing ones
    synced_product_codes = set()
    synced_variant_codes = set()

    for product_data in all_products_data:
        product_code = product_data.get('code')
        if not product_code:
            logger.warning(f"Skipping product with no CODE: {product_data}")
            continue
        synced_product_codes.add(product_code)

        try:
            with transaction.atomic():
                
                # --- Sync Product ---
                product_defaults = {
                    'product_id': product_data.get('product_id'),
                    'title': product_data.get('title'),
                    'manufacturer': product_data.get('manufacturer'),
                    'code_supplier': product_data.get('supplier_code'),
                    'ean': product_data.get('ean'),
                    'availability_id': None, # TODO: Map this to API /availabilities based on availability text
                    'availability': product_data.get('availability'),
                    'stock': product_data.get('stock', 0),
                    'stock_position': product_data.get('stock_position'),
                    'weight': product_data.get('weight'),
                    'unit': product_data.get('unit'),
                    'image_url': product_data.get('image_url'),
                    'uma_is_active': True,
                    'uma_last_synced_at': timezone.now(),
                }
                product_obj, created = Product.objects.update_or_create(
                    code=product_code, # Use 'code' as the unique identifier
                    defaults=product_defaults
                )
                if created:
                    logger.info(f"Created new product: {product_obj.title} (Code: {product_obj.code})")
                else:
                    logger.debug(f"Updated product: {product_obj.title} (Code: {product_obj.code})")

                # --- Sync Product Variants ---
                product_variants_data = product_data.get('variants', [])
                current_product_variant_codes = set() # Track variants for this specific product

                for variant_data in product_variants_data:
                    variant_code = variant_data.get('code')
                    if not variant_code:
                        logger.warning(f"Skipping variant with no CODE for product {product_code}: {variant_data}")
                        continue
                    synced_variant_codes.add(variant_code)
                    current_product_variant_codes.add(variant_code)

                    try:
                        variant_defaults = {
                            'product': product_obj, # Link to the parent product
                            'variant_id': variant_data.get('variant_id'),
                            'code_supplier': variant_data.get('supplier_code'),
                            'ean': variant_data.get('ean'),
                            'availability_id': None, # TODO: Map this to API /availabilities based on availability text
                            'availability': variant_data.get('availability'),
                            'stock': variant_data.get('stock', 0),
                            'stock_position': variant_data.get('stock_position'),
                            'weight': variant_data.get('weight'),
                            'image_url': variant_data.get('image_url'),
                            'price_original': variant_data.get('prices', {}).get('price_original'),
                            'price_with_vat': variant_data.get('prices', {}).get('price_with_vat'),
                            'price_without_vat': variant_data.get('prices', {}).get('price_without_vat'),
                            'price_purchase': variant_data.get('prices', {}).get('price_purchase'),
                            'currency': variant_data.get('prices', {}).get('currency'),
                            'parameters': variant_data.get('parameters'), # Store parsed parameters
                            'uma_is_active': True,
                            'uma_last_synced_at': timezone.now(),
                        }
                        variant_obj, v_created = ProductVariant.objects.update_or_create(
                            code=variant_code, # Use 'code' as the unique identifier for variant
                            defaults=variant_defaults
                        )
                        if v_created:
                            logger.info(f"  Created new variant: {variant_obj.code} (Product: {product_obj.code})")
                        else:
                            logger.debug(f"  Updated variant: {variant_obj.code} (Product: {product_obj.code})")

                    except IntegrityError as ie:
                        logger.error(f"Integrity error during variant sync for CODE {variant_code}: {ie}")
                    except Exception as ve:
                        logger.error(f"Unhandled error syncing variant {variant_code} for product {product_code}: {ve}")
                        continue

                # Deactivate variants of this specific product that were not found in the current feed
                product_obj.variants.exclude(code__in=list(current_product_variant_codes)).update(uma_is_active=False)

        except IntegrityError as ie:
            logger.error(f"Integrity error during product sync for CODE {product_code}: {ie}")
        except Exception as e:
            logger.error(f"Unhandled error during product sync for CODE {product_code}: {e}")
            continue

    # Deactivate products that were not found in the current feed
    # This should only be done if the feed is truly comprehensive and represents ALL active products
    Product.objects.exclude(code__in=list(synced_product_codes)).update(uma_is_active=False)

    logger.info("Product synchronization complete.")
    return True

# --- PARTIAL PRODUCT SYNC ---
def sync_products_from_partial_feed():
    """
    Retrieves the partial product XML feed and updates specific fields (e.g., stock, price).
    This only updates existing products/variants and does NOT deactivate missing ones.
    """
    feed_client = UpgatesFeedClient()
    try:
        xml_root = feed_client.get_partial_products_xml_feed()
        if xml_root is None:
            return False # Partial feed URL not configured or fetch failed
        logger.info("Successfully retrieved Upgates PARTIAL product XML feed.")
    except Exception as e:
        logger.error(f"Failed to retrieve Upgates PARTIAL product feed: {e}")
        return False

    parser = UpgatesProductXMLParser(xml_root)
    all_products_data = parser.get_all_products_data() # Use the same parser, it handles missing tags gracefully

    updated_count = 0
    created_count = 0

    for product_data in all_products_data:
        product_code = product_data.get('code')
        if not product_code:
            logger.warning(f"Skipping product with no CODE from partial feed: {product_data}")
            continue

        try:
            with transaction.atomic():
                # Attempt to get the product first
                product_obj = Product.objects.filter(code=product_code).first()

                if product_obj:
                    # Construct defaults ONLY with fields present in the partial feed and meant to be updated
                    # Use .get() with None as default for safety, then filter out Nones
                    product_defaults_partial = {
                        'product_id': product_data.get('product_id'),
                        'stock': product_data.get('stock'),
                        'availability': product_data.get('availability'),
                    }
                    # Filter out None values so we don't accidentally nullify existing data
                    product_defaults_partial = {k: v for k, v in product_defaults_partial.items() if v is not None}

                    if product_defaults_partial: # Only update if there's actually data to update
                        for field, value in product_defaults_partial.items():
                            setattr(product_obj, field, value)
                        product_obj.uma_last_synced_at = timezone.now() # Update last synced time
                        product_obj.save(update_fields=list(product_defaults_partial.keys()) + ['uma_last_synced_at'])
                        updated_count += 1
                        logger.debug(f"Partially updated product: {product_obj.code}")
                    else:
                        logger.debug(f"No relevant fields to update for product {product_code} from partial feed.")

                else:
                    # If product not found in DB, it might be a new product.
                    # Create it, but only with data from the partial feed.
                    # Full sync will fill missing details.
                    # This decision depends on if partial feeds can introduce new products.
                    # For now, let's assume partial feeds are only for updates to existing items.
                    logger.warning(f"Product {product_code} not found in DB for partial update. Skipping creation from partial feed.")
                    continue


                # --- Sync Product Variants ---
                product_variants_data = product_data.get('variants', [])
                if not product_variants_data and product_obj:
                    # If the partial feed only contains product-level info, skip variant loop
                    continue

                for variant_data in product_variants_data:
                    variant_code = variant_data.get('code')
                    if not variant_code:
                        logger.warning(f"Skipping variant with no CODE for product {product_code} from partial feed: {variant_data}")
                        continue

                    # Attempt to get the variant
                    variant_obj = ProductVariant.objects.filter(code=variant_code).first()

                    if variant_obj:
                        variant_defaults_partial = {
                            'stock': variant_data.get('stock'),
                            'availability': variant_data.get('availability'),
                        }
                        # Filter out None values
                        variant_defaults_partial = {k: v for k, v in variant_defaults_partial.items() if v is not None}

                        if variant_defaults_partial:
                            for field, value in variant_defaults_partial.items():
                                setattr(variant_obj, field, value)
                            variant_obj.uma_last_synced_at = timezone.now()
                            variant_obj.save(update_fields=list(variant_defaults_partial.keys()) + ['uma_last_synced_at'])
                            updated_count += 1
                            logger.debug(f"  Partially updated variant: {variant_obj.code}")
                        else:
                            logger.debug(f"  No relevant fields to update for variant {variant_code} from partial feed.")
                    else:
                        logger.warning(f"Variant {variant_code} not found in DB for partial update. Skipping creation from partial feed.")
                        # This means the product or variant needs a full sync first.
                        # You could potentially queue a full sync for this product here if the business logic allows.

        except IntegrityError as ie:
            logger.error(f"Integrity error during product sync for CODE {product_code} from partial feed: {ie}")
        except Exception as e:
            logger.error(f"Unhandled error during product sync for CODE {product_code} from partial feed: {e}")
            continue

    logger.info(f"PARTIAL Product synchronization complete. Updated {updated_count} existing items.")
    return True

# --- Core logic for processing stock adjustments ---
def process_stock_adjustments():
    """
    Processes pending stock adjustments from the ProductStockAdjustment table in a batch.
    1. Collects all pending adjustments.
    2. Syncs current stock for all relevant items from Upgates API.
    3. Calculates new stock levels for each.
    4. Sends a single batch PUT request to Upgates API.
    5. Updates ProductStockAdjustment records based on batch API response (or success/failure).
    6. Verifies updates by re-syncing and checking last_synced_at.??? maybe not needed
    """
    api_client = UpgatesAPIClient()
    
    # Get all pending adjustments. Order by created_at to process oldest first.
    pending_adjustments = ProductStockAdjustment.objects.filter(status='pending').order_by('created_at')
    
    if not pending_adjustments.exists():
        logger.info("No pending product stock adjustments to process.")
        return True

    logger.info(f"Found {pending_adjustments.count()} pending product stock adjustments.")

    # Collect all unique codes for the initial sync
    all_codes_to_sync = set()
    for adjustment in pending_adjustments:
        if adjustment.variant:
            all_codes_to_sync.add(adjustment.variant.code)
        elif adjustment.product:
            all_codes_to_sync.add(adjustment.product.code)
        else:
            # Log and mark as failed if neither product nor variant is set
            logger.error(f"ProductStockAdjustment {adjustment.pk} has neither product nor variant set. Marking as failed.")
            adjustment.status = 'failed'
            adjustment.error_message = "Neither product nor variant specified."
            adjustment.save(update_fields=['status', 'error_message'])
            continue # Skip this adjustment

    if not all_codes_to_sync:
        logger.info("No valid product/variant codes found in pending adjustments after initial check.")
        return True
    
    logger.info(f"Syncing current stock for {len(all_codes_to_sync)} items from simple API before batch adjustment.")
    try:
        sync_success = sync_products_simple_from_api(codes=list(all_codes_to_sync))
        if not sync_success:
            # If initial sync fails, we can't reliably calculate new stock.
            # Mark all relevant adjustments as failed or retry the whole task.
            raise Exception("Failed to perform initial stock sync from Upgates API. Cannot proceed with adjustments.")
    except Exception as e:
        # Mark all currently selected adjustments as failed due to sync error
        for adjustment in pending_adjustments:
            # Ensure the adjustment is still pending before marking failed (could have been processed by another task)
            if adjustment.status == 'pending': 
                adjustment.status = 'failed'
                adjustment.error_message = f"Initial stock sync failed: {e}"
                adjustment.save(update_fields=['status', 'error_message'])
        logger.error(f"Critical error during initial stock sync for batch adjustments: {e}", exc_info=True)
        return False # Indicate overall failure
    
    # Prepare batch update payload and update adjustment statuses to 'processing'
    batch_update_payload = []
    adjustments_to_process = [] # Keep track of adjustments that will be part of the batch
    
    # Re-fetch pending adjustments to ensure they are still in 'pending' status
    # (in case another process tried to grab them between initial fetch and sync)
    # Using the IDs collected from the initial query.
    re_fetched_adjustments = ProductStockAdjustment.objects.filter(
        pk__in=[adj.pk for adj in pending_adjustments],
        status='pending' # Only consider those still pending
    ).order_by('created_at').select_for_update()

    for adjustment in re_fetched_adjustments:
        # Use a nested transaction for each individual adjustment's status update
        # This allows us to mark individual adjustments as processing/completed/failed
        # even if the batch API call itself fails for some items.
        with transaction.atomic():
            target_obj = None
            current_local_stock = None
            item_type_for_api = None
            target_code = None

            if adjustment.variant:
                target_obj = ProductVariant.objects.get(pk=adjustment.variant.pk) # Get latest from DB
                current_local_stock = target_obj.stock
                item_type_for_api = 'variant'
                target_code = target_obj.code
            elif adjustment.product:
                target_obj = Product.objects.get(pk=adjustment.product.pk) # Get latest from DB
                current_local_stock = target_obj.stock
                item_type_for_api = 'product'
                target_code = target_obj.code
            else:
                # Should be caught by earlier clean() or explicit check
                logger.error(f"Adjustment {adjustment.pk} has no valid target after initial sync. Marking failed.")
                adjustment.status = 'failed'
                adjustment.error_message = "No valid product/variant target found."
                adjustment.save(update_fields=['status', 'error_message'])
                continue # Skip to next adjustment

            if current_local_stock is None:
                logger.error(f"Current stock for {target_code} is None after API sync. Marking adjustment {adjustment.pk} as failed.")
                adjustment.status = 'failed'
                adjustment.error_message = f"Current stock for {target_code} is null after sync."
                adjustment.save(update_fields=['status', 'error_message'])
                continue

            new_stock_level = current_local_stock + adjustment.adjustment_quantity
            logger.info(f"Preparing adjustment {adjustment.pk} for {target_code}: {current_local_stock} + {adjustment.adjustment_quantity} = {new_stock_level}")

            # Prepare item for batch payload (ASSUMED STRUCTURE)
            batch_item = {
                "code": target_code,
                "stock": new_stock_level,
                "type": item_type_for_api, # Indicate if it's a product or variant
            }
            # # If variant, you might need product_code in the batch item based on Upgates API.
            # if item_type_for_api == 'variant':
            #      batch_item['product_code'] = target_obj.product.code # Assumed Upgates requires parent product code for variant updates

            batch_update_payload.append(batch_item)
            adjustments_to_process.append(adjustment) # Keep track of which adjustment corresponds to which item in payload
            
            # Mark as processing (status change will be saved later in this atomic block)
            adjustment.status = 'processing'
            adjustment.processed_at = timezone.now()
            adjustment.save(update_fields=['status', 'processed_at'])

    # If no valid adjustments to process, return early
    if not batch_update_payload:
        logger.info("No valid adjustments to process in batch after pre-checks.")
        return True # Nothing to do
    
    # Send batch update to Upgates API
    try:
        logger.info(f"Sending batch update to Upgates API for {len(batch_update_payload)} items.")
        # transform batch_update_payload to match Upgates API expected structure
        # API expects a list of products with their updated stock and list of variants
        products = [item for item in batch_update_payload if item['type'] == 'product']
        varinats = [item for item in batch_update_payload if item['type'] == 'variant']

        if not products:
            products = None
        if not varinats:
            varinats = None

        batch_update_payload = {
            "products": products,
            "variants": varinats 
        }

        response, return_code = api_client.put_product_data(data=batch_update_payload)
        
        # Check if the response indicates success
        logger.info(f"Batch update response: {response}")

        if not response:
            raise Exception("Batch update failed with no success flag in response.")
    
    except Exception as e:
        logger.error(f"Batch update to Upgates API failed: {e}", exc_info=True)
        # Mark all adjustments as failed due to API error
        for adjustment in adjustments_to_process:
            if adjustment.status == 'processing':
                adjustment.status = 'failed'
                adjustment.error_message = f"Batch update failed: {e}"
                adjustment.save(update_fields=['status', 'error_message'])
        return False

    response_item_lookup = {}
    for item in response.get('products', []):
        # Add the product itself to the lookup (if it has a code)
        if 'code' in item:
            response_item_lookup[item['code']] = item

        # Add its variants to the lookup
        if 'variants' in item and item['variants']:
            for variant in item['variants']:
                if 'code' in variant:
                    response_item_lookup[variant['code']] = variant
    
    processed_adjustments = []
    for adjustment in adjustments_to_process:
        adjustment_code = adjustment.variant.code if adjustment.variant.code else adjustment.product.code
        if adjustment_code is None:
            logger.error(f"Adjustment {adjustment} has no valid code after API sync. Marking as failed.")
            adjustment.status = 'failed'
            adjustment.error_message = "No valid product/variant code found."
            adjustment.save(update_fields=['status', 'error_message'])
            continue
        corresponding_item = response_item_lookup.get(adjustment_code) # Use .get() to avoid KeyError

        if corresponding_item is None:
            logger.warning(f"No corresponding item found in API response for adjustment {adjustment.pk} with code '{adjustment_code}'.")
            adjustment.status = 'failed'
            adjustment.error_message = f"No corresponding product/variant found in API response for code '{adjustment_code}'."
            adjustment.save(update_fields=['status', 'error_message'])
            continue

        if corresponding_item['updated_yn']:
            logger.info(f"Found match for '{adjustment_code}': {corresponding_item['code']}")
            processed_adjustments.append({
                'adjustment': adjustment,
                'matched_item': corresponding_item
            })
            with transaction.atomic():
                try:
                    adjustment_item = adjustment.variant if adjustment.variant else adjustment.product
                    if adjustment_item:
                        # Update the stock in the local DB
                        adjustment_item.stock = adjustment_item.stock + adjustment.adjustment_quantity
                        adjustment_item.save(update_fields=['stock', 'uma_last_synced_at'])
                except Exception as e:
                    logger.error(f"Error updating stock for adjustment {adjustment.pk} with code '{adjustment_code}': {e}")
                    adjustment.status = 'failed'
                    adjustment.error_message = f"Error updating stock: {e}"
                    adjustment.save(update_fields=['status', 'error_message'])
                    continue
                # Update the adjustment status to 'completed'
                adjustment.status = 'completed'
                adjustment.processed_at = timezone.now()
                adjustment.api_response_data = corresponding_item
                adjustment.save(update_fields=['status', 'processed_at', 'api_response_data'])
        if not corresponding_item['updated_yn']:
            logger.warning(f"Item '{adjustment_code}' was not updated in the API response. Marking adjustment as failed.")
            adjustment.status = 'failed'
            adjustment.error_message = f"Item '{adjustment_code}' was not updated in the API response."
            adjustment.api_response_data = corresponding_item
            adjustment.save(update_fields=['status', 'error_message', 'api_response_data'])

    if not batch_update_payload:
        logger.info("No valid adjustments to process in batch after pre-checks.")
        return True
    return True
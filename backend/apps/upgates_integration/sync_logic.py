import logging
from datetime import datetime
from django.db import transaction, IntegrityError
from django.utils import timezone
import pytz # Import pytz

from apps.orders.models import Order, OrderItem
from apps.products.models import Product, ProductVariant
from .api_client import UpgatesAPIClient
from .feed_client import UpgatesFeedClient
from .xml_parser import UpgatesProductXMLParser 

logger = logging.getLogger(__name__)

def sync_orders_from_api(creation_time_from=None):
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

        try:
            orders_response = client.get_orders(**params)

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
                            'pg_updated_at': timezone.now(),
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
                    'supplier_code': product_data.get('supplier_code'),
                    'ean': product_data.get('ean'),
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
                            'supplier_code': variant_data.get('supplier_code'),
                            'ean': variant_data.get('ean'),
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

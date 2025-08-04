from datetime import datetime
from celery import shared_task
from django.utils import timezone
import logging

from .sync_logic import *

logger = logging.getLogger(__name__)

@shared_task(bind=True, default_retry_delay=300, max_retries=5)
def sync_orders_task(self, creation_time_from=None, status_ids=None):
    """
    Celery task to synchronize orders from Upgates API.
    `creation_time_from` can be passed as ISO format string if triggered from API.
    """
    logger.info("Starting Upgates order sync task.")
    try:
        # Convert string to datetime object if provided
        if creation_time_from:
            creation_time_from = datetime.fromisoformat(creation_time_from) # Assuming ISO format string
        else:
            # Default to one day ago if no timestamp is provided
            creation_time_from = timezone.now() - timezone.timedelta(days=1)
            # strip time part for consistency
            creation_time_from = creation_time_from.replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)

        success = sync_orders_from_api(creation_time_from=creation_time_from, status_ids=status_ids)
        if success:
            logger.info("Upgates order sync task completed successfully.")
        else:
            logger.warning("Upgates order sync task completed with some issues.")
            # self.retry(countdown=600)
    except Exception as e:
        logger.error(f"Upgates order sync task failed: {e}", exc_info=True)
        raise self.retry(exc=e)

@shared_task(bind=True, default_retry_delay=300, max_retries=5)
def sync_orders_status_to_api_task(self, orderids=None, status_id=None):
    """
    Celery task to synchronize order status to Upgates API.
    `orderids` can be passed as list of orderids if triggered from API.
    """
    logger.info("Starting Upgates order status sync task.")
    try:
        success = sync_orders_status_to_api(orderids=orderids, status_id=status_id)
        if success:
            logger.info("Upgates order status sync task completed successfully.")
        else:
            logger.warning("Upgates order status sync task completed with some issues.")
            # self.retry(countdown=600)
    except Exception as e:
        logger.error(f"Upgates order status sync task failed: {e}", exc_info=True)
        raise self.retry(exc=e)

@shared_task
def debug_task():
    logger.info("🥳 Debug task executed successfully!")
    print("DEBUG TASK RAN TO CONSOLE!") # Also print to console for direct visibility

@shared_task(bind=True, default_retry_delay=300, max_retries=5)
def sync_full_products_task(self):
    """
    Celery task to synchronize FULL product data from Upgates XML feed.
    """
    logger.info("Starting Upgates FULL product sync task.")
    try:
        success = sync_products_from_full_feed()
        if success:
            logger.info("Upgates FULL product sync task completed successfully.")
        else:
            logger.warning("Upgates FULL product sync task completed with some issues.")
    except Exception as e:
        logger.error(f"Upgates FULL product sync task failed: {e}", exc_info=True)
        raise self.retry(exc=e)

@shared_task(bind=True, default_retry_delay=60, max_retries=3) # Shorter retry for more frequent updates
def sync_partial_products_task(self):
    """
    Celery task to synchronize PARTIAL product data (e.g., stock/price) from Upgates XML feed.
    """
    logger.info("Starting Upgates PARTIAL product sync task.")
    try:
        success = sync_products_from_partial_feed()
        if success:
            logger.info("Upgates PARTIAL product sync task completed successfully.")
        else:
            logger.warning("Upgates PARTIAL product sync task completed with some issues.")
    except Exception as e:
        logger.error(f"Upgates PARTIAL product sync task failed: {e}", exc_info=True)
        raise self.retry(exc=e)
    
@shared_task(bind=True, default_retry_delay=300, max_retries=5)
def sync_products_simple_task(self, codes=None):
    """
    Celery task to synchronize products from Upgates API.
    `codes` can be passed as string if triggered from API.
    """
    logger.info("Starting Upgates products sync task.")
    try:        
        success = sync_products_simple_from_api(codes)
        if success:
            logger.info("Upgates products sync task completed successfully.")
        else:
            logger.warning("Upgates products sync task completed with some issues.")
            # self.retry(countdown=600)
    except Exception as e:
        logger.error(f"Upgates products sync task failed: {e}", exc_info=True)
        raise self.retry(exc=e)

@shared_task(bind=True, default_retry_delay=300, max_retries=5)
def process_stock_adjustments_task(self):
    """
    Celery task to process stock adjustments from Upgates API.
    This will call the sync logic to handle adjustments.
    """
    logger.info("Starting Upgates stock adjustments processing task.")
    try:
        success = process_stock_adjustments()
        if success:
            logger.info("Upgates stock adjustments processing task completed successfully.")
        else:
            logger.warning("Upgates stock adjustments processing task completed with some issues.")
            # self.retry(countdown=600)
    except Exception as e:
        logger.error(f"Upgates stock adjustments processing task failed: {e}", exc_info=True)
        raise self.retry(exc=e)
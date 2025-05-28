from datetime import datetime
from celery import shared_task
from django.utils import timezone
import logging

from .sync_logic import sync_orders_from_api

logger = logging.getLogger(__name__)

@shared_task(bind=True, default_retry_delay=300, max_retries=5)
def sync_orders_task(self, creation_time_from=None):
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
        
        success = sync_orders_from_api(creation_time_from)
        if success:
            logger.info("Upgates order sync task completed successfully.")
        else:
            logger.warning("Upgates order sync task completed with some issues.")
            # self.retry(countdown=600)
    except Exception as e:
        logger.error(f"Upgates order sync task failed: {e}", exc_info=True)
        raise self.retry(exc=e)
    
# apps/upgates_integration/tasks.py
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def debug_task():
    logger.info("🥳 Debug task executed successfully!")
    print("DEBUG TASK RAN TO CONSOLE!") # Also print to console for direct visibility

# Your existing sync_orders_task below this
# @shared_task
# def sync_orders_task(...):
#    ...
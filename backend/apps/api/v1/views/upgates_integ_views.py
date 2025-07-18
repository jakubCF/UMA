from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser # Or define your own
from django.utils import timezone

from apps.upgates_integration.tasks import sync_orders_task, sync_full_products_task, sync_partial_products_task, sync_products_simple_task
from apps.djangocore.utils import get_app_setting

class SyncDataTriggerAPIView(APIView):
    # Only allow authenticated admin users to trigger syncs
    # permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, *args, **kwargs):
        data_type = request.data.get('type') # 'products' or 'orders'
        # if data_type == 'products':
        #     sync_products_task.delay()
        #     message = "Product synchronization started in background."

        if data_type == 'orders':
            # Optionally pass a timestamp 
            # Default is one day ago if not provided
            creation_time_from_str = request.data.get('creation_time_from') # e.g., "2024-05-20T10:00:00Z"
            data_status_ids = request.data.get('status_ids') # Optional, e.g., "1;2;3" for specific order statuses
            status_ids = get_app_setting('UPGATES_ORDER_STATUS_IDS', default="1") # Fetch order status IDs from settings
            if data_status_ids:
                status_ids = data_status_ids
            
            sync_orders_task.delay(creation_time_from=creation_time_from_str, status_ids=status_ids)#creation_time_from=creation_time_from_str)
            message = "Order synchronization started in background."
        elif data_type == 'products_simple':
            # Trigger simple product sync task
            data_codes = request.data.get('codes') # Optional, e.g., "code1;code2;code3"
            sync_products_simple_task.delay(codes=data_codes)
            message = "Simple product synchronization started in background."
        elif data_type == 'products_full':
            sync_full_products_task.delay()
            message = "FULL product synchronization started in background."
        elif data_type == 'products_partial':
            sync_partial_products_task.delay()
            message = "PARTIAL product synchronization started in background."
        else:
            return Response(
                {"detail": "Invalid sync type. Must be 'products_simple', 'products_full', 'products_partial' or 'orders'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": message}, status=status.HTTP_202_ACCEPTED) # 202 Accepted means processing has begun
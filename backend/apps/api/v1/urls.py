from django.urls import path
from .views import product_views, order_views, upgates_integ_views


urlpatterns = [
    # Example: path('', views.product_list, name='product_list'),
    # You'll add your DRF API routes here later
    path('orders/sync/', upgates_integ_views.SyncDataTriggerAPIView.as_view(), name='upgates_sync_orders'),
]